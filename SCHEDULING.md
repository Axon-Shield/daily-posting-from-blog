# 📅 Intelligent Scheduling System

The blog post automation system includes sophisticated scheduling that respects business days, US holidays, and manages multiple posts per day intelligently.

## 🎯 Scheduling Rules

### Business Days Only
- **No weekends**: Posts are never scheduled on Saturday or Sunday
- **No US holidays**: Automatically skips all US federal holidays
- Uses the `holidays` Python library for accurate holiday detection

### Time Slots

Each business day has **4 posting time slots** (Eastern Time):

1. **9:00 AM EST** - First post of the day
2. **1:00 PM EST** - Second post
3. **11:00 AM EST** - Third post  
4. **3:00 PM EST** - Fourth post

**Maximum**: 4 posts per business day

### Smart Scheduling Logic

When scheduling messages from a new blog post:

1. Finds the next available business day
2. Assigns messages to the first available time slot
3. If a day already has 4 posts, moves to the next business day
4. Automatically skips weekends and holidays
5. Schedules sequentially (one per day unless needed)

## 📊 Database Schema

The `posted_messages` table includes:

```sql
scheduled_for TEXT  -- ISO format timestamp with timezone
```

Example: `2025-10-21T09:00:00-04:00` (9 AM EST on Oct 21, 2025)

## 💻 Usage

### Automatic Scheduling

When you fetch new blog posts, messages are automatically scheduled:

```bash
python main.py --fetch-posts
```

Output includes scheduling summary:
```
Scheduled Posts:
  1. Monday, 2025-10-21 at 09:00 AM ET
  2. Monday, 2025-10-21 at 01:00 PM ET
  3. Tuesday, 2025-10-22 at 09:00 AM ET
  ...
```

### View Schedule

Check upcoming scheduled posts:

```bash
python main.py --status
```

Shows:
- Next message due now
- Upcoming schedule (next 5 posts)
- Dates, times, and message previews

### Manual Query

Query the database directly:

```bash
sqlite3 data/posts.db "
  SELECT scheduled_for, message_text 
  FROM posted_messages 
  WHERE scheduled_for IS NOT NULL 
  ORDER BY scheduled_for 
  LIMIT 10
"
```

## ⚙️ Configuration

### Time Slots

Edit `scheduler.py` to modify time slots:

```python
TIME_SLOTS = [
    (9, 0),   # 9:00 AM
    (13, 0),  # 1:00 PM
    (11, 0),  # 11:00 AM
    (15, 0),  # 3:00 PM
]
```

### Maximum Posts Per Day

```python
MAX_POSTS_PER_DAY = 4
```

### Holiday Calendar

The system uses `holidays.US()` which includes:
- New Year's Day
- Martin Luther King Jr. Day
- Presidents' Day
- Memorial Day
- Independence Day
- Labor Day
- Columbus Day
- Veterans Day
- Thanksgiving
- Christmas Day

## 🤖 GitHub Actions Integration

The workflow runs at each time slot to check for due posts:

**Winter (EST - Nov-Mar)**:
- 9:00 AM EST = 14:00 UTC
- 11:00 AM EST = 16:00 UTC
- 1:00 PM EST = 18:00 UTC
- 3:00 PM EST = 20:00 UTC

**Summer (EDT - Apr-Oct)**:
- 9:00 AM EDT = 13:00 UTC
- 11:00 AM EDT = 15:00 UTC
- 1:00 PM EDT = 17:00 UTC
- 3:00 PM EDT = 19:00 UTC

The workflow:
1. Runs at each time slot (Monday-Friday only)
2. Queries for messages due at current time
3. Posts if scheduled time has passed
4. Marks as posted in database

## 📝 Examples

### Example 1: Single Blog Post (7 messages)

Scheduled over 2 business days:

```
Monday, Oct 21:
  09:00 AM - Message 1
  01:00 PM - Message 2
  11:00 AM - Message 3  (Note: 11am is 3rd slot)
  03:00 PM - Message 4

Tuesday, Oct 22:
  09:00 AM - Message 5
  01:00 PM - Message 6
  11:00 AM - Message 7
```

### Example 2: Multiple Blog Posts

If you already have 2 posts scheduled for Monday:

**Existing**:
- Monday 9am - Post A, Message 1
- Monday 1pm - Post A, Message 2

**New post** (7 messages) will schedule:
- Monday 11am - Post B, Message 1
- Monday 3pm - Post B, Message 2
- Tuesday 9am - Post B, Message 3
- Tuesday 1pm - Post B, Message 4
- Tuesday 11am - Post B, Message 5
- Wednesday 9am - Post B, Message 6
- Wednesday 1pm - Post B, Message 7

### Example 3: Holiday Handling

If Tuesday, Oct 22 is a holiday:

- Monday, Oct 21: Messages 1-4
- **Tuesday, Oct 22: SKIPPED (Holiday)**
- Wednesday, Oct 23: Messages 5-7

## 🔧 Troubleshooting

### Messages Not Posting

1. **Check if it's time**: `python main.py --status`
2. **Verify schedule**: Look at "Next Message Due Now"
3. **Check timezone**: Scheduling uses Eastern Time
4. **Business days**: Confirm it's not weekend/holiday

### Reschedule All Messages

If you need to reschedule existing messages:

```bash
# Backup first!
cp data/posts.db data/posts.db.backup

# Clear scheduled times (will reschedule on next fetch)
sqlite3 data/posts.db "UPDATE posted_messages SET scheduled_for = NULL"

# Re-run fetch to reschedule
python main.py --fetch-posts
```

### Test Scheduling Logic

```python
from scheduler import PostScheduler
from datetime import datetime
import pytz

scheduler = PostScheduler()

# Check if date is business day
date = datetime(2025, 10, 21)  # Example date
is_business = scheduler.is_business_day(date)
print(f"{date.date()} is business day: {is_business}")

# Schedule 7 messages
scheduled = scheduler.schedule_messages(num_messages=7, existing_schedules=[])
for idx, time in enumerate(scheduled, 1):
    print(f"{idx}. {time.strftime('%A, %Y-%m-%d at %I:%M %p %Z')}")
```

## 📚 API Reference

### `PostScheduler` Class

**Methods**:
- `is_business_day(date)` - Check if date is business day
- `get_next_business_day(start_date)` - Find next business day
- `schedule_messages(num_messages, existing_schedules, start_date)` - Schedule multiple messages
- `is_time_to_post(scheduled_time, current_time)` - Check if should post now
- `format_schedule_summary(scheduled_times)` - Human-readable schedule

### `Database` Methods

**Scheduling-related**:
- `get_all_scheduled_times()` - Get all scheduled datetimes
- `get_upcoming_schedule(limit)` - Get next N scheduled posts
- `get_next_message_to_post()` - Get message due now (returns None if not time yet)

## 🎉 Benefits

### For You
- **Set it and forget it**: Automatic scheduling means no manual work
- **Professional timing**: Posts go out at optimal business hours
- **No weekend noise**: Respects your audience's work schedule
- **Holiday awareness**: Never posts on major holidays

### For Your Audience
- **Consistent timing**: They know when to expect your content
- **Respects boundaries**: No weekend or holiday interruptions
- **Better engagement**: Business hours = higher engagement rates

## 🔄 Migration

If you have existing messages without schedules:

1. Run migration: `python database_migration.py`
2. Messages without `scheduled_for` won't post automatically
3. Option A: Delete old messages and re-fetch
4. Option B: Manually set schedules in database

---

**Note**: This scheduling system is timezone-aware and handles EST/EDT transitions automatically.

