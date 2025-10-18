#!/usr/bin/env python3
"""
Test script for LinkedIn posting with image generation.
Creates a test post without using the database.
"""
import sys
from config import Config
from content_extractor import ContentExtractor
from image_generator import ImageGenerator
from linkedin_poster import LinkedInPoster


def test_linkedin_post():
    """Test the complete LinkedIn posting flow."""
    print("\n" + "="*60)
    print("LINKEDIN POSTING TEST")
    print("="*60 + "\n")
    
    # Validate configuration
    if not Config.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not configured")
        sys.exit(1)
    
    if not Config.XAI_API_KEY:
        print("⚠️  XAI_API_KEY not configured - will post without image")
    
    if not Config.LINKEDIN_ACCESS_TOKEN or not Config.LINKEDIN_USER_ID:
        print("❌ LinkedIn API credentials not configured")
        print("This test requires LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_ID to be set.")
        sys.exit(1)
    
    print("✅ Configuration validated\n")
    
    # Initialize components
    content_extractor = ContentExtractor()
    image_generator = ImageGenerator() if Config.XAI_API_KEY and Config.GENERATE_IMAGES else None
    linkedin_poster = LinkedInPoster()
    
    # Test blog post data
    test_blog_title = "Test: Automated Social Media with AI"
    test_blog_content = """
    Artificial Intelligence is revolutionizing how we manage social media.
    With AI-powered content extraction and image generation, businesses can 
    automate their social media presence while maintaining quality and engagement.
    
    Key benefits include time savings, consistent posting schedules, and 
    professional AI-generated visuals that capture attention.
    """
    
    print(f"📝 Test Blog Post: {test_blog_title}\n")
    
    # Step 1: Extract a test message
    print("Step 1: Extracting test message with Claude...")
    try:
        messages = content_extractor.extract_daily_messages(
            title=test_blog_title,
            content=test_blog_content,
            num_messages=1
        )
        
        if not messages:
            print("❌ Failed to extract messages")
            sys.exit(1)
        
        test_message = messages[0]
        print(f"✅ Extracted message:\n{test_message}\n")
    
    except Exception as e:
        print(f"❌ Error extracting message: {e}")
        sys.exit(1)
    
    # Step 2: Enhance for LinkedIn
    print("Step 2: Optimizing message for LinkedIn...")
    try:
        enhanced_message = content_extractor.enhance_for_platform(
            message=test_message,
            platform='linkedin',
            blog_url='https://blog.example.com/test',
            hashtags=['AI', 'Automation', 'SocialMedia']
        )
        print(f"✅ Enhanced message:\n{enhanced_message}\n")
    
    except Exception as e:
        print(f"❌ Error enhancing message: {e}")
        sys.exit(1)
    
    # Step 3: Generate image
    image_url = None
    if image_generator:
        print("Step 3: Generating AI image with Grok...")
        try:
            image_url = image_generator.generate_image_for_message(
                blog_title=test_blog_title,
                message_text=test_message,
                message_id=None
            )
            
            if image_url:
                print(f"✅ Generated image: {image_url}\n")
            else:
                print("⚠️  Image generation failed, posting without image\n")
        
        except Exception as e:
            print(f"⚠️  Error generating image: {e}")
            print("Continuing without image...\n")
    else:
        print("Step 3: Skipping image generation (not configured)\n")
    
    # Step 4: Post to LinkedIn
    print("Step 4: Posting to LinkedIn...")
    try:
        result = linkedin_poster.post(enhanced_message, image_url=image_url)
        
        if result['success']:
            print(f"✅ Successfully posted to LinkedIn!")
            if image_url:
                print(f"   Posted with AI-generated image")
            print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!\n")
            return True
        else:
            print(f"❌ Failed to post to LinkedIn: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error posting to LinkedIn: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        test_linkedin_post()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

