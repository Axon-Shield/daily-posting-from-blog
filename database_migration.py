#!/usr/bin/env python3
"""
Database migration script to add scheduling support.
"""
import sqlite3
import sys
from config import Config


def migrate_database():
    """Add scheduled_for column to posted_messages table."""
    db_path = Config.DATABASE_PATH
    
    print(f"Migrating database: {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if column already exists
            cursor.execute("PRAGMA table_info(posted_messages)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'scheduled_for' in columns:
                print("✓ Column 'scheduled_for' already exists. No migration needed.")
                return
            
            # Add scheduled_for column
            cursor.execute("""
                ALTER TABLE posted_messages 
                ADD COLUMN scheduled_for TEXT
            """)
            
            conn.commit()
            print("✓ Successfully added 'scheduled_for' column to posted_messages table")
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()

