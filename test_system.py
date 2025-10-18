#!/usr/bin/env python3
"""
Test script to verify the system is working correctly.
"""
import sys
from config import Config
from rss_parser import RSSParser
from content_extractor import ContentExtractor
from linkedin_poster import LinkedInPoster
from x_poster import XPoster


def test_configuration():
    """Test configuration loading."""
    print("\n--- Testing Configuration ---")
    try:
        Config.validate()
        print("✅ Configuration loaded successfully")
        print(f"   RSS Feed: {Config.BLOG_RSS_FEED_URL}")
        print(f"   Anthropic API: {'configured' if Config.ANTHROPIC_API_KEY else 'not configured'}")
        print(f"   LinkedIn: {'configured' if Config.LINKEDIN_ACCESS_TOKEN else 'not configured'}")
        print(f"   X (Twitter): {'configured' if Config.X_API_KEY else 'not configured'}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_rss_feed():
    """Test RSS feed parsing."""
    print("\n--- Testing RSS Feed ---")
    try:
        parser = RSSParser()
        posts = parser.fetch_latest_posts(limit=1)
        
        if posts:
            print(f"✅ RSS Feed working")
            print(f"   Found {len(posts)} post(s)")
            print(f"   Latest: {posts[0]['title'][:50]}...")
            return True
        else:
            print("⚠️  RSS Feed returned no posts")
            return False
    except Exception as e:
        print(f"❌ RSS Feed error: {e}")
        return False


def test_content_extraction():
    """Test AI content extraction."""
    print("\n--- Testing Content Extraction (Anthropic API) ---")
    try:
        extractor = ContentExtractor()
        messages = extractor.extract_daily_messages(
            title="Test Blog Post",
            content="This is a test blog post about technology, innovation, and best practices in software development. It covers important topics that matter to developers.",
            num_messages=2
        )
        
        if messages and len(messages) >= 2:
            print(f"✅ Content extraction working")
            print(f"   Extracted {len(messages)} messages")
            print(f"   Sample: {messages[0][:60]}...")
            return True
        else:
            print("⚠️  Content extraction returned fewer messages than expected")
            return False
    except Exception as e:
        print(f"❌ Content extraction error: {e}")
        return False


def test_linkedin():
    """Test LinkedIn API."""
    print("\n--- Testing LinkedIn API ---")
    if not Config.LINKEDIN_ACCESS_TOKEN:
        print("⊘  LinkedIn not configured (skipping)")
        return None
    
    try:
        poster = LinkedInPoster()
        if poster.verify_credentials():
            print("✅ LinkedIn credentials valid")
            return True
        else:
            print("❌ LinkedIn credentials invalid")
            return False
    except Exception as e:
        print(f"❌ LinkedIn error: {e}")
        return False


def test_x():
    """Test X (Twitter) API."""
    print("\n--- Testing X (Twitter) API ---")
    if not Config.X_API_KEY:
        print("⊘  X (Twitter) not configured (skipping)")
        return None
    
    try:
        poster = XPoster()
        if poster.verify_credentials():
            print("✅ X (Twitter) credentials valid")
            return True
        else:
            print("❌ X (Twitter) credentials invalid")
            return False
    except Exception as e:
        print(f"❌ X (Twitter) error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("SYSTEM TEST SUITE")
    print("=" * 60)
    
    results = {
        'Configuration': test_configuration(),
        'RSS Feed': test_rss_feed(),
        'Content Extraction': test_content_extraction(),
        'LinkedIn API': test_linkedin(),
        'X (Twitter) API': test_x(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}: PASS")
        elif result is False:
            print(f"❌ {test_name}: FAIL")
        else:
            print(f"⊘  {test_name}: SKIPPED")
    
    print("=" * 60)
    
    # Determine overall result
    failed_tests = [name for name, result in results.items() if result is False]
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        print("\nPlease check your configuration and API credentials.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Fetch posts: python main.py --fetch-posts")
        print("  2. Check status: python main.py --status")
        print("  3. Test posting: python main.py --post-daily")
        sys.exit(0)


if __name__ == "__main__":
    main()

