"""
Database module for tracking blog posts and their extracted messages.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from config import Config
from scheduler import PostScheduler
from image_generator import ImageGenerator


class Database:
    """Database manager for storing post information and tracking posted messages."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or Config.DATABASE_PATH
        self.scheduler = PostScheduler()
        self.image_generator = ImageGenerator() if Config.GENERATE_IMAGES else None
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for blog posts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_url TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    published_date TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    messages_json TEXT NOT NULL
                )
            """)
            
            # Table for tracking posted messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posted_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    blog_post_id INTEGER NOT NULL,
                    message_index INTEGER NOT NULL,
                    message_text TEXT NOT NULL,
                    image_url TEXT,
                    scheduled_for TEXT,
                    posted_to_linkedin BOOLEAN DEFAULT 0,
                    posted_to_x BOOLEAN DEFAULT 0,
                    posted_at TEXT,
                    FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id),
                    UNIQUE(blog_post_id, message_index)
                )
            """)
            
            conn.commit()
    
    def save_blog_post(self, url: str, title: str, content: str, 
                      published_date: str, messages: List[str]) -> Optional[int]:
        """
        Save a blog post and its extracted messages with intelligent scheduling.
        
        Returns:
            Post ID if saved successfully, None if scheduling not possible
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if post already exists
            cursor.execute("SELECT id FROM blog_posts WHERE post_url = ?", (url,))
            existing = cursor.fetchone()
            
            if existing:
                return existing[0]
            
            # Get existing scheduled times to avoid conflicts
            existing_schedules = self.get_all_scheduled_times()
            
            # Check if we can schedule within the max days limit
            max_days = Config.MAX_SCHEDULE_DAYS_AHEAD
            can_schedule = self.scheduler.can_schedule_within_days(
                num_messages=len(messages),
                existing_schedules=existing_schedules,
                max_days=max_days
            )
            
            if not can_schedule:
                print(f"⏸️  SKIPPING: Cannot schedule '{title}' within {max_days} days")
                print(f"   Schedule is full. This post will be retried on next fetch.")
                return None
            
            # Insert new post
            cursor.execute("""
                INSERT INTO blog_posts 
                (post_url, title, content, published_date, fetched_at, messages_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                url,
                title,
                content,
                published_date,
                datetime.now().isoformat(),
                json.dumps(messages)
            ))
            
            post_id = cursor.lastrowid
            
            # Schedule the messages intelligently (we know it fits now)
            scheduled_times = self.scheduler.schedule_messages(
                num_messages=len(messages),
                existing_schedules=existing_schedules,
                max_days=max_days
            )
            
            # Insert messages with scheduled times and generate images
            for idx, (message, scheduled_time) in enumerate(zip(messages, scheduled_times)):
                # Generate image if enabled
                image_url = None
                if self.image_generator and Config.GENERATE_IMAGES:
                    try:
                        image_url = self.image_generator.generate_image_for_message(
                            blog_title=title,
                            message_text=message,
                            message_id=None  # Will get actual ID after insert
                        )
                    except Exception as e:
                        print(f"Warning: Image generation failed for message {idx}: {e}")
                
                cursor.execute("""
                    INSERT INTO posted_messages 
                    (blog_post_id, message_index, message_text, image_url, scheduled_for)
                    VALUES (?, ?, ?, ?, ?)
                """, (post_id, idx, message, image_url, scheduled_time.isoformat()))
            
            conn.commit()
            
            # Print scheduling summary
            print(f"\n{self.scheduler.format_schedule_summary(scheduled_times)}")
            
            return post_id
    
    def get_next_message_to_post(self) -> Optional[Dict]:
        """Get the next message that needs to be posted (based on schedule)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find next scheduled message that's due and not fully posted
            cursor.execute("""
                SELECT 
                    pm.id,
                    pm.blog_post_id,
                    pm.message_index,
                    pm.message_text,
                    pm.image_url,
                    pm.scheduled_for,
                    pm.posted_to_linkedin,
                    pm.posted_to_x,
                    bp.title,
                    bp.post_url
                FROM posted_messages pm
                JOIN blog_posts bp ON pm.blog_post_id = bp.id
                WHERE (pm.posted_to_linkedin = 0 OR pm.posted_to_x = 0)
                  AND pm.scheduled_for IS NOT NULL
                ORDER BY pm.scheduled_for ASC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return None
            
            scheduled_time = datetime.fromisoformat(row[4])
            
            # Check if it's time to post
            if not self.scheduler.is_time_to_post(scheduled_time):
                return None  # Not time yet
            
            return {
                'id': row[0],
                'blog_post_id': row[1],
                'message_index': row[2],
                'message_text': row[3],
                'image_url': row[4],
                'scheduled_for': row[5],
                'posted_to_linkedin': bool(row[6]),
                'posted_to_x': bool(row[7]),
                'blog_title': row[8],
                'blog_url': row[9]
            }
    
    def mark_posted_to_linkedin(self, message_id: int):
        """Mark a message as posted to LinkedIn."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE posted_messages 
                SET posted_to_linkedin = 1, posted_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), message_id))
            conn.commit()
    
    def mark_posted_to_x(self, message_id: int):
        """Mark a message as posted to X."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE posted_messages 
                SET posted_to_x = 1, posted_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), message_id))
            conn.commit()
    
    def get_all_messages_count(self) -> int:
        """Get total count of messages."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posted_messages")
            return cursor.fetchone()[0]
    
    def get_posted_messages_count(self) -> int:
        """Get count of fully posted messages (both LinkedIn and X)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM posted_messages 
                WHERE posted_to_linkedin = 1 AND posted_to_x = 1
            """)
            return cursor.fetchone()[0]
    
    def get_all_scheduled_times(self) -> List[datetime]:
        """Get all scheduled times for existing messages."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT scheduled_for FROM posted_messages 
                WHERE scheduled_for IS NOT NULL
            """)
            
            scheduled_times = []
            for row in cursor.fetchall():
                try:
                    scheduled_times.append(datetime.fromisoformat(row[0]))
                except (ValueError, TypeError):
                    continue
            
            return scheduled_times
    
    def get_upcoming_schedule(self, limit: int = 10) -> List[Dict]:
        """Get upcoming scheduled posts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    pm.id,
                    pm.scheduled_for,
                    pm.message_text,
                    pm.posted_to_linkedin,
                    pm.posted_to_x,
                    bp.title
                FROM posted_messages pm
                JOIN blog_posts bp ON pm.blog_post_id = bp.id
                WHERE pm.scheduled_for IS NOT NULL
                  AND (pm.posted_to_linkedin = 0 OR pm.posted_to_x = 0)
                ORDER BY pm.scheduled_for ASC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'scheduled_for': row[1],
                    'message_preview': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                    'posted_to_linkedin': bool(row[3]),
                    'posted_to_x': bool(row[4]),
                    'blog_title': row[5]
                })
            
            return results
    
    def delete_blog_post(self, post_id: int):
        """
        Delete a blog post and all its associated messages.
        
        Args:
            post_id: The ID of the blog post to delete
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete associated messages first (due to foreign key)
            cursor.execute("DELETE FROM posted_messages WHERE blog_post_id = ?", (post_id,))
            
            # Delete the blog post
            cursor.execute("DELETE FROM blog_posts WHERE id = ?", (post_id,))
            
            conn.commit()
            print(f"✓ Deleted blog post {post_id} and all associated messages")

