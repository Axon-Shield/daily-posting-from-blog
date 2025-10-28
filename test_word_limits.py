#!/usr/bin/env python3
"""
Test script to verify word-based message generation logic works correctly.
"""
import os
import sys
from content_extractor import ContentExtractor

def test_word_counting():
    """Test word counting functionality."""
    extractor = ContentExtractor()
    
    print("Testing Word Counting Functionality")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        ("Short message", 2),
        ("This is a longer message with more words to test the counting functionality", 13),
        ("Single", 1),
        ("", 0),
        ("Multiple    spaces   between    words", 4),
    ]
    
    for text, expected_words in test_cases:
        actual_words = extractor._count_words(text)
        status = "✅" if actual_words == expected_words else "❌"
        print(f"{status} '{text}' -> {actual_words} words (expected {expected_words})")
    
    print()

def test_word_truncation():
    """Test word-based truncation functionality."""
    extractor = ContentExtractor()
    
    print("Testing Word Truncation Functionality")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        ("This is a short message", 10, "This is a short message"),  # No truncation needed
        ("This is a longer message that should be truncated", 5, "This is a longer..."),  # Truncation needed
        ("One two three four five six seven eight nine ten", 8, "One two three four five six seven..."),  # Truncation needed
        ("Short", 10, "Short"),  # No truncation needed
    ]
    
    for text, max_words, expected in test_cases:
        result = extractor._truncate_to_word_limit(text, max_words)
        status = "✅" if result == expected else "❌"
        print(f"{status} Truncate '{text}' to {max_words} words")
        print(f"    Result: '{result}'")
        print(f"    Expected: '{expected}'")
        print()

def test_platform_enhancement():
    """Test platform enhancement with word limits."""
    extractor = ContentExtractor()
    
    print("Testing Platform Enhancement with Word Limits")
    print("=" * 50)
    
    # Test message (simulate 100-200 word range)
    test_message = " ".join(["word"] * 150)  # 150 words
    
    # Test LinkedIn enhancement
    linkedin_enhanced = extractor.enhance_for_platform(
        test_message, 
        'linkedin', 
        'https://example.com/blog-post',
        ['AI', 'Technology', 'Innovation']
    )
    
    linkedin_words = extractor._count_words(linkedin_enhanced)
    print(f"LinkedIn enhancement:")
    print(f"  Original: {extractor._count_words(test_message)} words")
    print(f"  Enhanced: {linkedin_words} words")
    print(f"  Status: {'✅' if linkedin_words > extractor._count_words(test_message) else '❌'}")
    print()
    
    # Test X enhancement with Premium account
    os.environ['X_PREMIUM_ACCOUNT'] = 'true'
    
    x_enhanced = extractor.enhance_for_platform(
        test_message, 
        'x', 
        'https://example.com/blog-post',
        ['AI', 'Technology', 'Innovation', 'Security', 'Future', 'Digital', 'Transformation', 'Automation', 'Intelligence', 'Data']
    )
    
    x_words = extractor._count_words(x_enhanced)
    x_chars = len(x_enhanced)
    print(f"X (Premium) enhancement:")
    print(f"  Original: {extractor._count_words(test_message)} words")
    print(f"  Enhanced: {x_words} words, {x_chars} characters")
    print(f"  Within 25k char limit: {'✅' if x_chars <= 25000 else '❌'}")
    print(f"  Status: {'✅' if x_words > extractor._count_words(test_message) else '❌'}")
    print()
    
    # Test X enhancement with standard account (should truncate)
    os.environ['X_PREMIUM_ACCOUNT'] = 'false'
    
    x_standard_enhanced = extractor.enhance_for_platform(
        test_message, 
        'x', 
        'https://example.com/blog-post',
        ['AI', 'Technology', 'Innovation']
    )
    
    x_standard_words = extractor._count_words(x_standard_enhanced)
    x_standard_chars = len(x_standard_enhanced)
    print(f"X (Standard) enhancement:")
    print(f"  Original: {extractor._count_words(test_message)} words")
    print(f"  Enhanced: {x_standard_words} words, {x_standard_chars} characters")
    print(f"  Within 280 char limit: {'✅' if x_standard_chars <= 280 else '❌'}")
    print(f"  Truncated appropriately: {'✅' if x_standard_words <= 50 else '❌'}")
    print()

def main():
    """Run all tests."""
    print("Word-Based Message Generation Tests")
    print("=" * 50)
    print()
    
    test_word_counting()
    test_word_truncation()
    test_platform_enhancement()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
