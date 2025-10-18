#!/usr/bin/env python3
"""
Clear all unposted messages from the database.
Use this to reset the schedule before re-fetching blog posts.
"""
import sqlite3
import sys
from config import Config


def clear_unposted_messages():
    """Remove all messages that haven't been fully posted."""
    db_path = Config.DATABASE_PATH
    
    print(f"Clearing unposted messages from: {db_path}")
    print("=" * 60)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get counts before deletion
            cursor.execute("""
                SELECT COUNT(*) FROM posted_messages 
                WHERE posted_to_linkedin = 0 OR posted_to_x = 0
            """)
            unposted_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM posted_messages")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM posted_messages 
                WHERE posted_to_linkedin = 1 AND posted_to_x = 1
            """)
            posted_count = cursor.fetchone()[0]
            
            if unposted_count == 0:
                print("✓ No unposted messages found. Nothing to clear.")
                return
            
            print(f"Current status:")
            print(f"  Total messages: {total_count}")
            print(f"  Fully posted: {posted_count}")
            print(f"  Unposted: {unposted_count}")
            print()
            
            # Delete unposted messages
            cursor.execute("""
                DELETE FROM posted_messages 
                WHERE posted_to_linkedin = 0 OR posted_to_x = 0
            """)
            
            deleted_count = cursor.rowcount
            
            # Clean up blog posts with no remaining messages
            cursor.execute("""
                DELETE FROM blog_posts 
                WHERE id NOT IN (
                    SELECT DISTINCT blog_post_id FROM posted_messages
                )
            """)
            
            deleted_posts = cursor.rowcount
            
            conn.commit()
            
            print("✓ Successfully cleared unposted messages")
            print(f"  Deleted {deleted_count} unposted message(s)")
            print(f"  Cleaned up {deleted_posts} blog post(s) with no remaining messages")
            print()
            
            # Show final counts
            cursor.execute("SELECT COUNT(*) FROM posted_messages")
            remaining = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM blog_posts")
            posts_remaining = cursor.fetchone()[0]
            
            print(f"Remaining in database:")
            print(f"  Messages: {remaining}")
            print(f"  Blog posts: {posts_remaining}")
            print()
            print("=" * 60)
            print("✓ Database cleared. Ready for fresh blog post fetch.")
            
    except Exception as e:
        print(f"✗ Error clearing database: {e}")
        sys.exit(1)


def clear_all_messages():
    """Remove ALL messages (including posted ones). Use with caution!"""
    db_path = Config.DATABASE_PATH
    
    print(f"⚠️  WARNING: Clearing ALL messages from: {db_path}")
    print("=" * 60)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM posted_messages")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM blog_posts")
            total_posts = cursor.fetchone()[0]
            
            if total_messages == 0:
                print("✓ Database is already empty.")
                return
            
            print(f"About to delete:")
            print(f"  {total_messages} message(s)")
            print(f"  {total_posts} blog post(s)")
            print()
            
            # Delete everything
            cursor.execute("DELETE FROM posted_messages")
            deleted_messages = cursor.rowcount
            
            cursor.execute("DELETE FROM blog_posts")
            deleted_posts = cursor.rowcount
            
            conn.commit()
            
            print("✓ Successfully cleared all data")
            print(f"  Deleted {deleted_messages} message(s)")
            print(f"  Deleted {deleted_posts} blog post(s)")
            print()
            print("=" * 60)
            print("✓ Database is now empty.")
            
    except Exception as e:
        print(f"✗ Error clearing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clear messages from the database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_unposted.py               Clear only unposted messages (safe)
  python clear_unposted.py --all         Clear ALL messages including posted (dangerous!)
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clear ALL messages including posted ones (use with caution!)'
    )
    
    args = parser.parse_args()
    
    if args.all:
        response = input("⚠️  This will delete ALL messages including posted ones. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
        clear_all_messages()
    else:
        clear_unposted_messages()

