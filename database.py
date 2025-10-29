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
        self.image_generator = ImageGenerator() if Config.GENERATE_IMAGES > 0 else None
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
    
    def get_post_id_by_url(self, url: str) -> Optional[int]:
        """Get post ID by URL if it exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM blog_posts WHERE post_url = ?", (url,))
            result = cursor.fetchone()
            return result[0] if result else None
    
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
            
            # Check if we can schedule the FIRST message within the max days limit
            # (Subsequent messages can extend beyond the limit)
            max_days = Config.MAX_SCHEDULE_DAYS_AHEAD
            can_schedule = self.scheduler.can_schedule_within_days(
                num_messages=1,  # Only check if first message fits
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
            
            # Schedule the messages intelligently
            # First message is within max_days, subsequent messages can extend beyond
            scheduled_times = self.scheduler.schedule_messages(
                num_messages=len(messages),
                existing_schedules=existing_schedules
                # No max_days constraint - allow messages to extend beyond if needed
            )
            
            # Insert messages with scheduled times and generate images
            for idx, (message, scheduled_time) in enumerate(zip(messages, scheduled_times)):
                # Generate image based on probability
                image_url = None
                if self.image_generator and Config.GENERATE_IMAGES > 0:
                    import random
                    if random.random() < Config.GENERATE_IMAGES:
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
            
            # Get current date in Eastern timezone for comparison
            from pytz import timezone
            eastern = timezone('US/Eastern')
            current_time = datetime.now(eastern)
            current_date = current_time.date().isoformat()  # e.g., '2025-10-29'
            
            # Debug: Show messages scheduled for today or later
            print(f"\n🔍 Messages scheduled for {current_date} or later:")
            cursor.execute("""
                SELECT 
                    pm.id,
                    pm.scheduled_for,
                    pm.posted_to_linkedin,
                    pm.posted_to_x
                FROM posted_messages pm
                WHERE pm.posted_to_linkedin = 0 
                  AND pm.posted_to_x = 0
                  AND pm.scheduled_for IS NOT NULL
                  AND date(substr(pm.scheduled_for, 1, 10)) >= ?
                ORDER BY pm.scheduled_for ASC
            """, (current_date,))
            
            debug_messages = cursor.fetchall()
            if debug_messages:
                print(f"   Found {len(debug_messages)} messages:")
                for msg_id, sched, linkedin, x in debug_messages:
                    print(f"   - ID {msg_id}: {sched} (L:{linkedin}, X:{x})")
            else:
                print(f"   No messages found")
            print()
            
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
                WHERE pm.posted_to_linkedin = 0 AND pm.posted_to_x = 0
                  AND pm.scheduled_for IS NOT NULL
                  AND date(substr(pm.scheduled_for, 1, 10)) >= ?
                ORDER BY pm.scheduled_for ASC
                LIMIT 1
            """, (current_date,))
            
            row = cursor.fetchone()
            if not row:
                print(f"\n❌ No messages found after applying filter")
                print(f"   Current date: {current_date}")
                print(f"   Query filter: date(substr(scheduled_for, 1, 10)) >= '{current_date}'")
                return None
            
            # row[5] is scheduled_for, not row[4]!
            scheduled_time = datetime.fromisoformat(row[5])
            
            print(f"📋 Found message ID {row[0]}: {row[8]}")
            print(f"   Scheduled for: {scheduled_time}")
            print(f"   Current time: {current_time}")
            
            # Check if it's time to post
            is_ready = self.scheduler.is_time_to_post(scheduled_time, current_time)
            print(f"   Is ready to post: {is_ready}")
            
            if not is_ready:
                print("⏸️  Message found but not ready to post yet (wrong time slot)")
                return None  # Not time yet
            
            print("✅ Message is ready to post!")
            
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
            # Force write to disk
            cursor.execute("PRAGMA wal_checkpoint(FULL)")
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
            # Force write to disk
            cursor.execute("PRAGMA wal_checkpoint(FULL)")
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
    
    def get_message_status(self, message_id: int) -> Optional[Dict]:
        """Get posted flags and image path for a specific message id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT posted_to_linkedin, posted_to_x, image_url
                FROM posted_messages
                WHERE id = ?
                """,
                (message_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'posted_to_linkedin': bool(row[0]),
                'posted_to_x': bool(row[1]),
                'image_url': row[2],
            }
    
    def clear_image_for_message(self, message_id: int):
        """Clear image path for a message after successful posting and cleanup."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE posted_messages
                SET image_url = NULL
                WHERE id = ?
                """,
                (message_id,)
            )
            conn.commit()
    
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
    
    def get_unposted_messages(self) -> List[Dict]:
        """Get all unposted messages (not posted to any platform)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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
                    bp.title as blog_title,
                    bp.post_url as blog_url
                FROM posted_messages pm
                JOIN blog_posts bp ON pm.blog_post_id = bp.id
                WHERE pm.posted_to_linkedin = 0 AND pm.posted_to_x = 0
                ORDER BY pm.scheduled_for ASC
            """)
            
            rows = cursor.fetchall()
            return [
                {
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
                for row in rows
            ]
    
    def update_message_image(self, message_id: int, image_path: str):
        """Update the image URL for a specific message."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE posted_messages SET image_url = ? WHERE id = ?",
                (image_path, message_id)
            )
            conn.commit()
    
    def update_message_text(self, message_id: int, new_text: str):
        """Update the message text for a specific message."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE posted_messages SET message_text = ? WHERE id = ?",
                (new_text, message_id)
            )
            conn.commit()
            print(f"✅ Updated message {message_id} in database")

