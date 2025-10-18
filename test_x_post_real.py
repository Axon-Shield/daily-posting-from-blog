#!/usr/bin/env python3
"""
Real-world X posting test using actual blog content.
Fetches blog, extracts message, generates image, posts to X, then cleans up.
"""
import sys
import os
import traceback
from pathlib import Path
from config import Config
from database import Database
from rss_parser import RSSParser
from content_extractor import ContentExtractor
from image_generator import ImageGenerator
from x_poster import XPoster


def test_x_post_real():
    """Test complete X posting flow with real blog content."""
    print("\n" + "="*60)
    print("REAL-WORLD X POSTING TEST")
    print("="*60 + "\n")
    
    # Validate configuration
    if not Config.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not configured")
        sys.exit(1)
    
    if not Config.X_API_KEY:
        print("❌ X API credentials not configured")
        sys.exit(1)
    
    if not Config.BLOG_RSS_FEED_URL:
        print("❌ BLOG_RSS_FEED_URL not configured")
        sys.exit(1)
    
    print("✅ Configuration validated\n")
    
    # Ensure data directory exists (extract from database path)
    db_path = Config.DATABASE_PATH
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        print(f"✓ Created data directory: {db_dir}")
    print(f"✓ Database path: {db_path}\n")
    
    # Initialize components
    db = Database()
    rss_parser = RSSParser()
    content_extractor = ContentExtractor()
    image_generator = ImageGenerator() if Config.XAI_API_KEY and Config.GENERATE_IMAGES else None
    x_poster = XPoster()
    
    test_post_id = None
    
    try:
        # Step 1: Fetch latest blog post
        print("Step 1: Fetching latest blog post from RSS feed...")
        posts = rss_parser.fetch_latest_posts(limit=1)
        
        if not posts:
            print("❌ No posts found in RSS feed")
            sys.exit(1)
        
        post = posts[0]
        print(f"✅ Fetched blog post: {post['title']}")
        print(f"   URL: {post['url']}")
        print(f"   Published: {post['published_date']}\n")
        
        # Step 2: Extract ONE test message with Claude
        print("Step 2: Extracting one message with Claude...")
        messages = content_extractor.extract_daily_messages(
            title=post['title'],
            content=post['content'],
            num_messages=1
        )
        
        if not messages:
            print("❌ Failed to extract messages")
            sys.exit(1)
        
        test_message = messages[0]
        print(f"✅ Extracted message:\n{test_message}\n")
        
        # Step 3: Generate AI image with Grok
        image_path = None
        if image_generator:
            print("Step 3: Generating AI image with Grok...")
            try:
                image_path = image_generator.generate_image_for_message(
                    blog_title=post['title'],
                    message_text=test_message,
                    message_id=None
                )
                
                if image_path:
                    print(f"✅ Generated image: {image_path}\n")
                else:
                    print("⚠️  Image generation failed, posting without image\n")
            except Exception as e:
                print(f"⚠️  Error generating image: {e}")
                print("Continuing without image...\n")
        else:
            print("Step 3: Skipping image generation (not configured)\n")
        
        # Step 4: Save to database temporarily
        print("Step 4: Saving to database temporarily...")
        test_post_id = db.save_blog_post(
            url=post['url'],
            title=post['title'],
            content=post['content'],
            published_date=post['published_date'],
            messages=[test_message]
        )
        print(f"✅ Saved to database with ID: {test_post_id}\n")
        
        # Step 5: Enhance message for X
        print("Step 5: Optimizing message for X (Twitter)...")
        enhanced_message = content_extractor.enhance_for_platform(
            message=test_message,
            platform='x',
            blog_url=post['url'],
            hashtags=['AI', 'Tech']
        )
        print(f"✅ Enhanced message:\n{enhanced_message}\n")
        
        # Step 6: Post to X with image
        print("Step 6: Posting to X (Twitter)...")
        result = x_poster.post(enhanced_message, image_url=image_path)
        
        if result['success']:
            print(f"✅ Successfully posted to X!")
            print(f"   Tweet ID: {result.get('tweet_id')}")
            if image_path:
                print(f"   Posted with AI-generated image")
            print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!\n")
            
            # Step 7: Clean up database
            print("Step 7: Cleaning up database...")
            db.delete_blog_post(test_post_id)
            print("✅ Removed test data from database\n")
            
            return True
        else:
            print(f"❌ Failed to post to X: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        traceback.print_exc()
        
        # Clean up on error
        if test_post_id:
            print("\nCleaning up database...")
            try:
                db.delete_blog_post(test_post_id)
                print("✅ Removed test data")
            except:
                pass
        
        sys.exit(1)


if __name__ == "__main__":
    try:
        test_x_post_real()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)

