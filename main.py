#!/usr/bin/env python3
"""
Main orchestration script for automated blog post distribution.
"""
import sys
import argparse
from typing import List, Dict
from datetime import datetime

from config import Config
from database import Database
from rss_parser import RSSParser
from content_extractor import ContentExtractor
from linkedin_poster import LinkedInPoster
from x_poster import XPoster
import os


class BlogPostAutomation:
    """Main automation orchestrator."""
    
    def __init__(self):
        """Initialize the automation system."""
        print("Initializing automation system...", flush=True)
        
        print("Validating configuration...", flush=True)
        Config.validate()
        
        print("Initializing database...", flush=True)
        self.db = Database()
        
        print("Initializing RSS parser...", flush=True)
        self.rss_parser = RSSParser()
        
        print("Initializing content extractor (Anthropic)...", flush=True)
        self.content_extractor = ContentExtractor()
        
        print("Initializing social media posters...", flush=True)
        self.linkedin_poster = LinkedInPoster()
        self.x_poster = XPoster()
        
        print("✅ Initialization complete!", flush=True)
    
    def fetch_and_process_new_posts(self):
        """Fetch new blog posts and extract messaging points."""
        print("\n" + "="*60, flush=True)
        print("FETCHING NEW BLOG POSTS", flush=True)
        print("="*60, flush=True)
        print(f"RSS Feed: {Config.BLOG_RSS_FEED_URL[:50]}...", flush=True)
        print(f"Cutoff Date: {Config.MINIMUM_POST_DATE}", flush=True)
        print("Fetching latest blog posts...", flush=True)
        sys.stdout.flush()
        
        posts = self.rss_parser.fetch_latest_posts(limit=5)
        
        if not posts:
            print("No posts found in RSS feed.")
            return
        
        print(f"Found {len(posts)} posts in feed.")
        
        processed_count = 0
        skipped_count = 0
        
        for post in posts:
            print(f"\nProcessing: {post['title']}")
            print(f"Published: {post['published_date']}")
            
            # Check if we already have this post
            try:
                # Extract key messages
                print("Extracting key messaging points...")
                messages = self.content_extractor.extract_daily_messages(
                    title=post['title'],
                    content=post['content'],
                    num_messages=Config.POSTS_PER_BLOG
                )
                
                print(f"Extracted {len(messages)} messages")
                
                # Try to save to database (may be skipped if schedule is full)
                post_id = self.db.save_blog_post(
                    url=post['url'],
                    title=post['title'],
                    content=post['content'],
                    published_date=post['published_date'],
                    messages=messages
                )
                
                if post_id:
                    print(f"✅ Saved to database with ID: {post_id}")
                    processed_count += 1
                else:
                    print(f"⏸️  Skipped (schedule full)")
                    skipped_count += 1
                    # Stop processing older posts if schedule is full
                    print(f"\n⚠️  Schedule is full. Stopping fetch.")
                    print(f"   Older posts will be retried when schedule clears.")
                    break
                
            except Exception as e:
                print(f"❌ Error processing post: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"FETCH SUMMARY")
        print(f"{'='*60}")
        print(f"Posts processed: {processed_count}")
        print(f"Posts skipped: {skipped_count}")
        print(f"{'='*60}")
    
    def post_daily_message(self):
        """Post the next message to social media platforms."""
        print("\n" + "="*60)
        print("DAILY POSTING ROUTINE")
        print("="*60 + "\n")
        
        # Get next message to post
        message_data = self.db.get_next_message_to_post()
        
        if not message_data:
            print("No messages available to post.")
            print("Try running: python main.py --fetch-posts")
            return
        
        print(f"Blog Post: {message_data['blog_title']}")
        print(f"Message #{message_data['message_index'] + 1}")
        print(f"URL: {message_data['blog_url']}")
        if message_data.get('image_url'):
            print(f"Image: {message_data['image_url'][:60]}...")
        print(f"\nBase Message:\n{message_data['message_text']}\n")
        
        # Post to LinkedIn
        if Config.LINKEDIN_ENABLED and not message_data['posted_to_linkedin'] and Config.LINKEDIN_ACCESS_TOKEN:
            print("\n--- Posting to LinkedIn ---")
            try:
                # Enhance message for LinkedIn
                enhanced_message = self.content_extractor.enhance_for_platform(
                    message=message_data['message_text'],
                    platform='linkedin',
                    blog_url=message_data['blog_url'],
                    hashtags=['blog', 'insights']
                )
                
                print(f"LinkedIn Message:\n{enhanced_message}\n")
                
                result = self.linkedin_poster.post(enhanced_message, image_url=message_data.get('image_url'))
                
                if result['success']:
                    print("✓ Successfully posted to LinkedIn")
                    self.db.mark_posted_to_linkedin(message_data['id'])
                else:
                    print(f"✗ Failed to post to LinkedIn: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"✗ Error posting to LinkedIn: {e}")
        elif not Config.LINKEDIN_ENABLED:
            print("⊘ LinkedIn posting disabled (set LINKEDIN_ENABLED=true to enable)")
        else:
            if message_data['posted_to_linkedin']:
                print("✓ Already posted to LinkedIn")
            else:
                print("⊘ LinkedIn not configured (skipping)")
        
        # Post to X (Twitter)
        if not message_data['posted_to_x'] and Config.X_API_KEY:
            print("\n--- Posting to X (Twitter) ---")
            try:
                # Enhance message for X
                enhanced_message = self.content_extractor.enhance_for_platform(
                    message=message_data['message_text'],
                    platform='x',
                    blog_url=message_data['blog_url'],
                    hashtags=['blog', 'tech']
                )
                
                print(f"X Message:\n{enhanced_message}\n")
                
                result = self.x_poster.post(enhanced_message, image_url=message_data.get('image_url'))
                
                if result['success']:
                    print(f"✓ Successfully posted to X (Tweet ID: {result.get('tweet_id')})")
                    self.db.mark_posted_to_x(message_data['id'])
                else:
                    print(f"✗ Failed to post to X: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"✗ Error posting to X: {e}")
        else:
            if message_data['posted_to_x']:
                print("✓ Already posted to X")
            else:
                print("⊘ X (Twitter) not configured (skipping)")
        
        # If both platforms are now posted, clean up image file and clear path
        try:
            status = self.db.get_message_status(message_data['id'])
            if status and status['posted_to_linkedin'] and status['posted_to_x'] and status.get('image_url'):
                image_path = status['image_url']
                if os.path.isfile(image_path):
                    try:
                        os.remove(image_path)
                        print(f"🧹 Removed image file: {image_path}")
                    except Exception as e:
                        print(f"Warning: Failed to remove image file: {e}")
                # Clear stored image path regardless
                self.db.clear_image_for_message(message_data['id'])
        except Exception as e:
            print(f"Warning: Cleanup check failed: {e}")

        print("\n" + "="*60)
        print(f"Daily posting completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
    
    def show_status(self):
        """Display current status of the automation."""
        print("\n" + "="*60)
        print("AUTOMATION STATUS")
        print("="*60 + "\n")
        
        total_messages = self.db.get_all_messages_count()
        posted_messages = self.db.get_posted_messages_count()
        
        print(f"Total messages in database: {total_messages}")
        print(f"Fully posted messages: {posted_messages}")
        print(f"Remaining messages: {total_messages - posted_messages}")
        
        # Check API credentials
        print("\n--- API Configuration ---")
        print(f"Blog RSS Feed: {'✓ Configured' if Config.BLOG_RSS_FEED_URL else '✗ Not configured'}")
        print(f"Anthropic API: {'✓ Configured' if Config.ANTHROPIC_API_KEY else '✗ Not configured'}")
        print(f"LinkedIn API: {'✓ Configured' if Config.LINKEDIN_ACCESS_TOKEN else '✗ Not configured'}")
        print(f"X (Twitter) API: {'✓ Configured' if Config.X_API_KEY else '✗ Not configured'}")
        
        # Show next scheduled message
        next_message = self.db.get_next_message_to_post()
        if next_message:
            print("\n--- Next Message Due Now ---")
            print(f"Blog: {next_message['blog_title']}")
            print(f"Scheduled for: {next_message.get('scheduled_for', 'Not scheduled')}")
            print(f"Message: {next_message['message_text'][:100]}...")
            print(f"LinkedIn: {'Posted' if next_message['posted_to_linkedin'] else 'Pending'}")
            print(f"X: {'Posted' if next_message['posted_to_x'] else 'Pending'}")
        else:
            print("\n--- Next Message Due Now ---")
            print("No messages due at this time")
        
        # Show upcoming schedule
        upcoming = self.db.get_upcoming_schedule(limit=5)
        if upcoming:
            print("\n--- Upcoming Schedule (Next 5) ---")
            for idx, post in enumerate(upcoming, 1):
                from datetime import datetime
                import pytz
                scheduled = datetime.fromisoformat(post['scheduled_for'])
                eastern = pytz.timezone('US/Eastern')
                scheduled_et = scheduled.astimezone(eastern)
                date_str = scheduled_et.strftime('%a %m/%d at %I:%M %p ET')
                print(f"{idx}. {date_str}")
                print(f"   {post['blog_title'][:50]}...")
                print(f"   \"{post['message_preview']}\"")
        
        print("\n" + "="*60 + "\n")
    
    def test_apis(self):
        """Test API connections."""
        print("\n" + "="*60)
        print("API CONNECTION TESTS")
        print("="*60 + "\n")
        
        # Test RSS Feed
        print("Testing RSS Feed...")
        try:
            posts = self.rss_parser.fetch_latest_posts(limit=1)
            if posts:
                print(f"✓ RSS Feed working (found {len(posts)} post(s))")
            else:
                print("✗ RSS Feed returned no posts")
        except Exception as e:
            print(f"✗ RSS Feed error: {e}")
        
        # Test Anthropic API
        print("\nTesting Anthropic API...")
        try:
            test_messages = self.content_extractor.extract_daily_messages(
                title="Test Post",
                content="This is a test blog post about technology and innovation.",
                num_messages=2
            )
            if test_messages:
                print(f"✓ Anthropic API working (extracted {len(test_messages)} message(s))")
            else:
                print("✗ Anthropic API returned no messages")
        except Exception as e:
            print(f"✗ Anthropic API error: {e}")
        
        # Test LinkedIn
        print("\nTesting LinkedIn API...")
        if Config.LINKEDIN_ACCESS_TOKEN:
            try:
                if self.linkedin_poster.verify_credentials():
                    print("✓ LinkedIn credentials valid")
                else:
                    print("✗ LinkedIn credentials invalid")
            except Exception as e:
                print(f"✗ LinkedIn API error: {e}")
        else:
            print("⊘ LinkedIn not configured")
        
        # Test X (Twitter)
        print("\nTesting X (Twitter) API...")
        if Config.X_API_KEY:
            try:
                if self.x_poster.verify_credentials():
                    print("✓ X (Twitter) credentials valid")
                else:
                    print("✗ X (Twitter) credentials invalid")
            except Exception as e:
                print(f"✗ X (Twitter) API error: {e}")
        else:
            print("⊘ X (Twitter) not configured")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main entry point."""
    print("="*60, flush=True)
    print("BLOG POST AUTOMATION STARTING", flush=True)
    print("="*60, flush=True)
    sys.stdout.flush()
    
    parser = argparse.ArgumentParser(
        description='Automated blog post distribution to social media',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --fetch-posts    Fetch and process new blog posts
  python main.py --post-daily     Post the next daily message
  python main.py --status         Show automation status
  python main.py --test           Test API connections
        """
    )
    
    parser.add_argument(
        '--fetch-posts',
        action='store_true',
        help='Fetch new blog posts and extract messaging points'
    )
    
    parser.add_argument(
        '--post-daily',
        action='store_true',
        help='Post the next daily message to social media'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show automation status'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test API connections'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any([args.fetch_posts, args.post_daily, args.status, args.test]):
        parser.print_help()
        sys.exit(0)
    
    try:
        automation = BlogPostAutomation()
        
        if args.fetch_posts:
            automation.fetch_and_process_new_posts()
        
        if args.post_daily:
            automation.post_daily_message()
        
        if args.status:
            automation.show_status()
        
        if args.test:
            automation.test_apis()
    
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

