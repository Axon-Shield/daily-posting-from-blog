"""
Database module for tracking blog posts and their extracted messages.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from config import Config


class Database:
    """Database manager for storing post information and tracking posted messages."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or Config.DATABASE_PATH
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
                    posted_to_linkedin BOOLEAN DEFAULT 0,
                    posted_to_x BOOLEAN DEFAULT 0,
                    posted_at TEXT,
                    FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id),
                    UNIQUE(blog_post_id, message_index)
                )
            """)
            
            conn.commit()
    
    def save_blog_post(self, url: str, title: str, content: str, 
                      published_date: str, messages: List[str]) -> int:
        """Save a blog post and its extracted messages."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if post already exists
            cursor.execute("SELECT id FROM blog_posts WHERE post_url = ?", (url,))
            existing = cursor.fetchone()
            
            if existing:
                return existing[0]
            
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
            
            # Insert messages
            for idx, message in enumerate(messages):
                cursor.execute("""
                    INSERT INTO posted_messages 
                    (blog_post_id, message_index, message_text)
                    VALUES (?, ?, ?)
                """, (post_id, idx, message))
            
            conn.commit()
            return post_id
    
    def get_next_message_to_post(self) -> Optional[Dict]:
        """Get the next message that needs to be posted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find oldest unposted message
            cursor.execute("""
                SELECT 
                    pm.id,
                    pm.blog_post_id,
                    pm.message_index,
                    pm.message_text,
                    pm.posted_to_linkedin,
                    pm.posted_to_x,
                    bp.title,
                    bp.post_url
                FROM posted_messages pm
                JOIN blog_posts bp ON pm.blog_post_id = bp.id
                WHERE pm.posted_to_linkedin = 0 OR pm.posted_to_x = 0
                ORDER BY bp.published_date ASC, pm.message_index ASC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row[0],
                'blog_post_id': row[1],
                'message_index': row[2],
                'message_text': row[3],
                'posted_to_linkedin': bool(row[4]),
                'posted_to_x': bool(row[5]),
                'blog_title': row[6],
                'blog_url': row[7]
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

