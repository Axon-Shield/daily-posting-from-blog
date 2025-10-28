#!/usr/bin/env python3
"""
Script to find and regenerate short messages in the database.
Only processes messages that haven't been posted to any platform yet.
"""
import os
import sys
from database import Database
from content_extractor import ContentExtractor
from config import Config

def find_short_unposted_messages(db, max_chars=280):
    """
    Find messages that are shorter than max_chars and haven't been posted yet.
    
    Args:
        db: Database instance
        max_chars: Maximum character limit to consider as "short"
    
    Returns:
        List of message records that need regeneration
    """
    import sqlite3
    
    query = """
    SELECT 
        pm.id,
        pm.blog_post_id,
        pm.message_index,
        pm.message_text,
        pm.scheduled_for,
        bp.title,
        bp.content,
        bp.post_url
    FROM posted_messages pm
    JOIN blog_posts bp ON pm.blog_post_id = bp.id
    WHERE 
        LENGTH(pm.message_text) < ?
        AND pm.posted_to_linkedin = 0 
        AND pm.posted_to_x = 0
        AND pm.scheduled_for IS NOT NULL
    ORDER BY pm.scheduled_for ASC
    """
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (max_chars,))
        return cursor.fetchall()

def regenerate_message(extractor, original_text, blog_title, blog_content):
    """
    Regenerate a message using Anthropic to make it longer and more detailed.
    
    Args:
        extractor: ContentExtractor instance
        original_text: Original short message
        blog_title: Blog post title
        blog_content: Blog post content
    
    Returns:
        New longer message text
    """
    prompt = f"""You are a social media content strategist. I have a short social media message that needs to be expanded into a more detailed, engaging post.

Original Short Message: {original_text}

Blog Title: {blog_title}

Blog Content (excerpt):
{blog_content[:2000]}

Please expand the original message into a more comprehensive, engaging social media post that:
1. Is between 100-200 words for optimal engagement
2. Maintains the core message and intent of the original
3. Adds more detail, context, and value
4. Is suitable for both LinkedIn and X (Twitter)
5. Includes a call-to-action or thought-provoking element
6. Is written in an engaging, professional tone
7. Provides enough detail to be valuable while remaining concise

Return only the expanded message text, no additional formatting or explanations."""

    try:
        message = extractor.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text.strip()
    
    except Exception as e:
        print(f"Error regenerating message: {e}")
        return None

def main():
    """Main function to process short messages."""
    print("🔍 Checking for short unposted messages...")
    print("=" * 60)
    
    # Initialize database and content extractor
    db = Database()
    extractor = ContentExtractor()
    
    # Find short unposted messages
    short_messages = find_short_unposted_messages(db, max_chars=280)
    
    if not short_messages:
        print("✅ No short unposted messages found!")
        print("   (All unposted messages are already 280+ characters)")
        return
    
    print(f"📝 Found {len(short_messages)} short unposted messages")
    print(f"   (Messages shorter than 280 characters that haven't been posted yet)")
    print()
    
    # Process each short message
    for i, message_record in enumerate(short_messages, 1):
        msg_id, blog_post_id, msg_index, original_text, scheduled_for, blog_title, blog_content, blog_url = message_record
        
        print(f"📋 Message {i}/{len(short_messages)} (ID: {msg_id})")
        print(f"   Scheduled for: {scheduled_for}")
        print(f"   Blog: {blog_title}")
        print(f"   Original length: {len(original_text)} characters")
        print()
        
        print("📄 Original Message:")
        print("-" * 40)
        print(original_text)
        print()
        
        # Regenerate the message
        print("🔄 Regenerating with Anthropic...")
        new_text = regenerate_message(extractor, original_text, blog_title, blog_content)
        
        if new_text:
            print("✅ Successfully regenerated!")
            print()
            print("📄 New Message:")
            print("-" * 40)
            print(new_text)
            print()
            print(f"📊 New length: {len(new_text)} characters ({extractor._count_words(new_text)} words)")
            print()
            
            # Show the difference
            char_diff = len(new_text) - len(original_text)
            word_diff = extractor._count_words(new_text) - extractor._count_words(original_text)
            print(f"📈 Improvement: +{char_diff} characters, +{word_diff} words")
            
            # Update the database with the new message
            try:
                db.update_message_text(msg_id, new_text)
                print(f"💾 Message {msg_id} updated in database")
            except Exception as e:
                print(f"❌ Failed to update database: {e}")
        else:
            print("❌ Failed to regenerate message")
        
        print("=" * 60)
        print()
    
    print(f"🎉 Processed {len(short_messages)} messages")
    print("💾 All regenerated messages have been updated in the database")
    print("📝 Short messages have been replaced with longer, more detailed content")

if __name__ == "__main__":
    main()
