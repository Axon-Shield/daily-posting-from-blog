#!/usr/bin/env python3
"""
Quick fix to add missing image_url column to existing database.
"""
import sqlite3
import os
from config import Config

def fix_database():
    """Add image_url column if it doesn't exist."""
    db_path = Config.DATABASE_PATH
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    print(f"Fixing database schema: {db_path}")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if image_url column exists
        cursor.execute("PRAGMA table_info(posted_messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        if 'image_url' not in columns:
            print("Adding image_url column...")
            cursor.execute("""
                ALTER TABLE posted_messages 
                ADD COLUMN image_url TEXT
            """)
            conn.commit()
            print("✅ Added image_url column")
        else:
            print("✅ image_url column already exists")
        
        # Verify
        cursor.execute("PRAGMA table_info(posted_messages)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Updated columns: {columns}")

if __name__ == "__main__":
    fix_database()

