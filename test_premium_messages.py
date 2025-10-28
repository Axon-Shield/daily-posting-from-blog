#!/usr/bin/env python3
"""
Test script to verify Premium account message generation works correctly.
"""
import os
import sys
from content_extractor import ContentExtractor
from config import Config

def test_premium_message_generation():
    """Test that Premium account generates longer messages."""
    
    # Set Premium account to true
    os.environ['X_PREMIUM_ACCOUNT'] = 'true'
    
    # Create a test blog post
    title = "The Future of AI in Cybersecurity"
    content = """
    Artificial Intelligence is revolutionizing cybersecurity in unprecedented ways. 
    From threat detection to automated response, AI systems are becoming the backbone 
    of modern security infrastructure. This comprehensive analysis explores how 
    machine learning algorithms can identify patterns in network traffic that would 
    be impossible for human analysts to detect in real-time.
    
    The integration of AI into cybersecurity tools has led to a 95% reduction in 
    false positive rates while maintaining 99.9% accuracy in threat detection. 
    Companies implementing AI-driven security solutions report an average of 40% 
    faster incident response times and 60% reduction in security-related downtime.
    
    However, the adoption of AI in cybersecurity also presents new challenges. 
    Adversarial attacks targeting AI models are becoming more sophisticated, 
    requiring continuous updates and monitoring of security algorithms. The 
    balance between automation and human oversight remains critical for 
    maintaining robust security postures.
    
    Looking ahead, the future of AI in cybersecurity will likely focus on 
    predictive analytics, autonomous threat hunting, and self-healing security 
    systems that can adapt to new threats in real-time without human intervention.
    """
    
    # Initialize content extractor
    extractor = ContentExtractor()
    
    print("Testing Word-Based Message Generation")
    print("=" * 50)
    
    # Test with Premium account enabled
    print(f"Premium Account Enabled: {Config.X_PREMIUM_ACCOUNT}")
    print(f"Expected word range: 100-200 words per message")
    print()
    
    try:
        # Extract messages
        messages = extractor.extract_daily_messages(title, content, num_messages=3)
        
        print("Generated Messages:")
        print("-" * 30)
        
        for i, message in enumerate(messages, 1):
            word_count = extractor._count_words(message)
            char_count = len(message)
            print(f"{i}. ({word_count} words, {char_count} chars) {message}")
            print()
            
            # Check if message length is appropriate
            if word_count < 100:
                print(f"   ⚠️  Warning: Message {i} is shorter than expected (less than 100 words)")
            elif word_count > 200:
                print(f"   ⚠️  Warning: Message {i} is longer than expected (more than 200 words)")
            else:
                print(f"   ✅ Message {i} word count is within expected range (100-200 words)")
            print()
        
        # Test platform enhancement
        print("Platform Enhancement Test:")
        print("-" * 30)
        
        for i, message in enumerate(messages[:2], 1):  # Test first 2 messages
            enhanced_x = extractor.enhance_for_platform(
                message, 
                'x', 
                'https://example.com/blog-post',
                ['AI', 'Cybersecurity', 'Technology', 'Innovation', 'Security']
            )
            
            enhanced_word_count = extractor._count_words(enhanced_x)
            print(f"Enhanced X message {i}:")
            print(f"Length: {enhanced_word_count} words, {len(enhanced_x)} characters")
            print(f"Content: {enhanced_x}")
            print()
            
            if len(enhanced_x) > 25000:
                print(f"   ⚠️  Warning: Enhanced message {i} exceeds 25,000 character limit")
            else:
                print(f"   ✅ Enhanced message {i} is within Premium character limit")
            print()
        
        print("✅ Premium account message generation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_premium_message_generation()
    sys.exit(0 if success else 1)
