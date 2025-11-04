#!/usr/bin/env python3
"""
Script to regenerate all unposted messages in the database using the updated prompt.
Only processes messages that haven't been posted to any platform yet.
Also reschedules messages that were scheduled for dates in the past.
"""
import os
import sys
import sqlite3
from datetime import datetime
import pytz
from database import Database
from content_extractor import ContentExtractor
from config import Config

def find_unposted_messages(db):
    """
    Find all messages that haven't been posted yet.
    
    Args:
        db: Database instance
    
    Returns:
        List of message records that need regeneration
    """
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
        pm.posted_to_linkedin = 0 
        AND pm.posted_to_x = 0
        AND pm.scheduled_for IS NOT NULL
    ORDER BY pm.scheduled_for ASC
    """
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

def regenerate_message(extractor, original_text, blog_title, blog_content):
    """
    Regenerate a message using Anthropic with the updated prompt.
    
    Args:
        extractor: ContentExtractor instance
        original_text: Original message text
        blog_title: Blog post title
        blog_content: Blog post content
    
    Returns:
        New regenerated message text
    """
    # Use the updated prompt from content_extractor
    # This creates a new message in the same style as the extraction prompt
    prompt = f"""You are a social media content strategist. I have a blog post that I want to promote on LinkedIn and X (Twitter).

Blog Title: {blog_title}

Blog Content:
{blog_content[:3000]}

I have an existing social media message from this blog post that I'd like you to regenerate with fresh, engaging content:

Existing Message: {original_text}

Please create a new, distinct social media message that:
1. Is standalone and makes sense without context
2. Is suitable for both LinkedIn and X (Twitter)
3. Is between 100-200 words for optimal engagement and readability
4. Highlights a key insight, statistic, or takeaway from the post
5. Is written in an engaging, professional tone
6. Includes a call-to-action or thought-provoking element where appropriate
7. Provides enough detail to be valuable while remaining concise
8. Important! Combine business terms with technical terms  to appeal to both executives and engineers
9. Important! Use a problem-to-solution tone: Start by describing a common challenge or pain point, then transition to how the insight resolves it
10. Important! Follow a narrative structure or story format: Begin with a relatable scenario or example, build tension around the problem, and end with a resolution or key takeaway

Return only the new message text, no additional formatting, numbering, hashtags, emojis, or explanations."""

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
    """Main function to process unposted messages."""
    print("🔄 Regenerating unposted messages with updated prompt...")
    print("=" * 60)
    
    # Initialize database and content extractor
    db = Database()
    extractor = ContentExtractor()
    
    # Find all unposted messages
    unposted_messages = find_unposted_messages(db)
    
    if not unposted_messages:
        print("✅ No unposted messages found!")
        print("   (All messages have been posted or are not scheduled)")
        return
    
    print(f"📝 Found {len(unposted_messages)} unposted messages")
    print(f"   (Messages that haven't been posted to any platform yet)")
    print()
    
    regenerated_count = 0
    failed_count = 0
    rescheduled_count = 0
    
    # Get current time in Eastern timezone for comparison
    eastern = pytz.timezone('US/Eastern')
    current_time = datetime.now(eastern)
    current_date = current_time.date()
    
    # Process each unposted message
    for i, message_record in enumerate(unposted_messages, 1):
        msg_id, blog_post_id, msg_index, original_text, scheduled_for_str, blog_title, blog_content, blog_url = message_record
        
        print(f"📋 Message {i}/{len(unposted_messages)} (ID: {msg_id})")
        print(f"   Blog: {blog_title}")
        print(f"   Current length: {len(original_text)} characters")
        
        # Parse scheduled_for date
        scheduled_for = None
        needs_reschedule = False
        if scheduled_for_str:
            try:
                scheduled_for = datetime.fromisoformat(scheduled_for_str)
                # Make timezone-aware if needed
                if scheduled_for.tzinfo is None:
                    scheduled_for = eastern.localize(scheduled_for)
                else:
                    scheduled_for = scheduled_for.astimezone(eastern)
                
                scheduled_date = scheduled_for.date()
                print(f"   Scheduled for: {scheduled_for_str} ({scheduled_date})")
                
                # Check if scheduled date is in the past
                if scheduled_date < current_date:
                    needs_reschedule = True
                    print(f"   ⚠️  Scheduled date is in the past! Will reschedule to future slot.")
                else:
                    print(f"   ✅ Scheduled date is in the future")
            except (ValueError, TypeError) as e:
                print(f"   ⚠️  Could not parse scheduled_for: {scheduled_for_str}")
                needs_reschedule = True
        else:
            print(f"   ⚠️  No scheduled_for date set")
            needs_reschedule = True
        
        print()
        
        # Reschedule if needed
        if needs_reschedule:
            print("📅 Rescheduling to future available slot...")
            try:
                # Get all existing scheduled times (excluding this message by ID)
                with sqlite3.connect(db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT scheduled_for FROM posted_messages 
                        WHERE scheduled_for IS NOT NULL AND id != ?
                    """, (msg_id,))
                    
                    other_scheduled = []
                    for row in cursor.fetchall():
                        try:
                            dt = datetime.fromisoformat(row[0])
                            if dt.tzinfo is None:
                                dt = eastern.localize(dt)
                            else:
                                dt = dt.astimezone(eastern)
                            other_scheduled.append(dt)
                        except (ValueError, TypeError):
                            continue
                
                # Find a new slot starting from tomorrow
                new_schedules = db.scheduler.schedule_messages(
                    num_messages=1,
                    existing_schedules=other_scheduled,
                    start_date=None  # Defaults to tomorrow
                )
                
                if new_schedules:
                    new_schedule_time = new_schedules[0]
                    db.update_message_schedule(msg_id, new_schedule_time)
                    scheduled_for = new_schedule_time
                    print(f"   ✅ Rescheduled to: {new_schedule_time.isoformat()}")
                    rescheduled_count += 1
                else:
                    print(f"   ❌ Could not find available slot. Schedule may be full.")
                    print(f"   ⚠️  Message will keep old schedule but may not be posted.")
            except Exception as e:
                print(f"   ❌ Failed to reschedule: {e}")
                print(f"   ⚠️  Message will keep old schedule but may not be posted.")
            print()
        
        print("📄 Current Message:")
        print("-" * 40)
        print(original_text[:200] + ("..." if len(original_text) > 200 else ""))
        print()
        
        # Regenerate the message
        print("🔄 Regenerating with updated prompt...")
        new_text = regenerate_message(extractor, original_text, blog_title, blog_content)
        
        if new_text:
            print("✅ Successfully regenerated!")
            print()
            print("📄 New Message:")
            print("-" * 40)
            print(new_text[:200] + ("..." if len(new_text) > 200 else ""))
            print()
            print(f"📊 New length: {len(new_text)} characters ({extractor._count_words(new_text)} words)")
            print()
            
            # Update the database with the new message
            try:
                db.update_message_text(msg_id, new_text)
                print(f"💾 Message {msg_id} updated in database")
                regenerated_count += 1
            except Exception as e:
                print(f"❌ Failed to update database: {e}")
                failed_count += 1
        else:
            print("❌ Failed to regenerate message")
            failed_count += 1
        
        print("=" * 60)
        print()
    
    print(f"🎉 Regeneration complete!")
    print(f"   ✅ Successfully regenerated: {regenerated_count} messages")
    if rescheduled_count > 0:
        print(f"   📅 Rescheduled to future slots: {rescheduled_count} messages")
    if failed_count > 0:
        print(f"   ❌ Failed: {failed_count} messages")
    print(f"💾 All regenerated messages have been updated in the database")
    print(f"📝 Messages now use the updated prompt style")
    if rescheduled_count > 0:
        print(f"📅 Messages scheduled for past dates have been moved to future available slots")

if __name__ == "__main__":
    main()

