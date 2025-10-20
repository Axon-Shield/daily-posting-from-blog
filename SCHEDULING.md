# 📅 Complete Scheduling Guide

This guide covers everything about how the system schedules and publishes your social media posts.

---

## 📋 Table of Contents

1. [Quick Overview](#quick-overview)
2. [Scheduling Rules](#scheduling-rules)
3. [Priority System (Latest First)](#priority-system)
4. [Date Filtering](#date-filtering)
5. [Configuration](#configuration)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Quick Overview

The system automatically schedules posts with these key behaviors:

- ✅ **Latest posts first** - Newest blog posts get priority
- ✅ **Business days only** - No weekends or US holidays
- ✅ **4 time slots per day** - 9am, 1pm, 11am, 3pm EST
- ✅ **7-day window** - First message starts within a week (configurable)
- ✅ **One message per blog per day** - Spreads each post over multiple days
- ✅ **Date filtering** - Only processes recent posts (since Oct 15, 2025)

---

## Scheduling Rules

### Business Days Only

- **No weekends**: Saturday/Sunday automatically skipped
- **No US holidays**: All federal holidays skipped automatically
- Includes: New Year's, MLK Day, Presidents' Day, Memorial Day, July 4th, Labor Day, Columbus Day, Veterans Day, Thanksgiving, Christmas

### Time Slots (Eastern Time)

Each business day has **4 posting slots**:

1. **9:00 AM EST** - First post of the day
2. **1:00 PM EST** - Second post
3. **11:00 AM EST** - Third post  
4. **3:00 PM EST** - Fourth post

**Maximum:** 4 posts per business day

### One Message Per Blog Per Day

Messages from the same blog post are scheduled **one per day**:

```
Blog Post "AI Security Trends" (5 messages):
  Day 1: Message 1 (9am slot)
  Day 2: Message 2 (9am slot or later if taken)
  Day 3: Message 3
  Day 4: Message 4
  Day 5: Message 5
```

This ensures your content is distributed over the week, not clustered in one day.

---

## Priority System

### Latest Posts First

RSS/JSON feeds return **newest posts first**. The system processes them in that order:

```
Feed Processing Order:
1. "Latest Post" (Oct 20, 2025) ← Processed FIRST
2. "Last Week's Post" (Oct 13) ← Second
3. "Two Weeks Ago" (Oct 6) ← Third
```

### 7-Day Schedule Limit

**Rule:** The **first message** of each blog post must start within 7 days.

**Check Before Processing:**
```
Question: "Can the first message start within 7 days?"
YES → Process the post (remaining messages can extend beyond)
NO → Skip and retry tomorrow
```

**Example:**
- Day 7 has 1 slot available
- Post needs 5 messages
- ✅ Process it! (Message 1 on day 7, messages 2-5 on days 8-11)

### Why This Works

**Benefits:**
- ✅ **Fresh content**: Latest posts always get scheduled quickly
- ✅ **No backlog**: Schedule never extends months into future
- ✅ **Self-regulating**: Automatically pauses/resumes based on capacity
- ✅ **Lower costs**: Skipped posts aren't sent to AI APIs

**Scenario:**
```
Monday: Write new blog post
Tuesday: Fetch runs
  - Check: Can first message start within 7 days? YES
  - Extract 5 messages with Claude
  - Schedule Tue-Sat (5 days)
Result: Your content starts immediately ✅
```

---

## Date Filtering

### Cutoff Date

**Default:** `2025-10-15` (October 15, 2025)

**Purpose:** Only processes posts published **on or after** this date.

**Why?** Prevents processing years of old blog posts when first running the system.

### How It Works

```python
# In rss_parser.py
published_date >= MINIMUM_POST_DATE
```

**Example:**
```
Blog posts in feed:
- "New Post" (Oct 20, 2025) → ✅ Processed
- "Recent Post" (Oct 18, 2025) → ✅ Processed
- "Old Post" (Sept 30, 2025) → ❌ Skipped (before cutoff)
```

### Changing the Cutoff

**Local (.env file):**
```bash
MINIMUM_POST_DATE=2024-01-01  # Process all posts from 2024
```

**GitHub Actions:**
```bash
gh secret set MINIMUM_POST_DATE --body '2024-01-01' \
  --repo Axon-Shield/daily-posting-from-blog
```

**Recommendations:**
- **Weekly blogger:** Last 2-3 months (default works)
- **Initial setup:** Last 3-6 months for backlog
- **Backfill evergreen content:** Set to 1-2 years ago
- **Fresh start only:** Last 30 days

---

## Configuration

### Environment Variables

```bash
# In .env or GitHub Secrets

# How many messages per blog post
POSTS_PER_BLOG=5

# How far ahead to schedule (first message must start within this)
MAX_SCHEDULE_DAYS_AHEAD=7

# Only process posts from this date onwards
MINIMUM_POST_DATE=2025-10-15
```

### Code-Level Settings

**File:** `scheduler.py`

```python
# Time slots (Eastern Time)
TIME_SLOTS = [
    (9, 0),   # 9:00 AM
    (13, 0),  # 1:00 PM
    (11, 0),  # 11:00 AM
    (15, 0),  # 3:00 PM
]

# Maximum posts per day
MAX_POSTS_PER_DAY = 4
```

**To add a 5th time slot:**
```python
TIME_SLOTS = [
    (9, 0),   # 9:00 AM
    (11, 0),  # 11:00 AM
    (13, 0),  # 1:00 PM
    (15, 0),  # 3:00 PM
    (17, 0),  # 5:00 PM  ← New!
]
MAX_POSTS_PER_DAY = 5
```

Don't forget to update `.github/workflows/daily-post.yml` with the new cron schedule!

---

## Examples

### Example 1: Weekly Blogger (Your Case)

**Setup:**
- 1 new post per week
- 5 messages per post
- MAX_SCHEDULE_DAYS_AHEAD=7

**Timeline:**
```
Week 1 (Oct 21):
  Monday: Write "Blog Post #1"
  Tuesday: Fetch runs
    - Process Post #1
    - Schedule 5 messages Tue-Mon (7 days)
  Tuesday-Monday: 1 message posts per day

Week 2 (Oct 28):
  Monday: Write "Blog Post #2"
  Tuesday: Fetch runs
    - Process Post #2
    - Schedule 5 messages Tue-Mon (next week)
  
Steady State:
  - Always 3-5 days of content queued
  - New posts scheduled within a week
  - Perfect! ✅
```

### Example 2: Multiple Posts (Busy Week)

**Scenario:** You publish 3 posts in one day

```
Oct 20: Publish 3 posts (15 messages total)

Fetch runs:
  Post 1 (Latest): 5 messages
    Check: First message within 7 days? YES
    Schedule: Oct 21-25 (5 days)
    
  Post 2 (Second): 5 messages
    Check: First message within 7 days? YES
    Schedule: Oct 21-25 (fills remaining slots)
    
  Post 3 (Third): 5 messages
    Check: First message within 7 days? YES
    Schedule: Oct 28-Nov 1 (next week)

Result:
  - All posts processed ✅
  - Week 1: 8 messages from Posts 1&2
  - Week 2: 7 messages from Posts 2&3
```

### Example 3: Schedule Full

**Scenario:** Already have 25 messages scheduled

```
Current schedule: Oct 21-Nov 5 (all slots full)
Next available: Nov 6 (day 8)

New post arrives:

Check: Can first message start within 7 days (by Oct 28)?
Answer: NO (Day 8 = Nov 6)

Action: ⏸️  SKIP this post
Output: "Schedule is full. This post will be retried on next fetch."

Tomorrow: System retries automatically when schedule clears
```

### Example 4: Holiday Handling

**Scenario:** Thanksgiving week

```
Nov 24 (Mon): Messages 1-4 post normally
Nov 25 (Tue): Messages 5-8 post normally
Nov 26 (Wed): Messages 9-12 post normally
Nov 27 (Thu): ❌ THANKSGIVING (skipped)
Nov 28 (Fri): ❌ BLACK FRIDAY (some years)
Nov 29 (Sat): ❌ Weekend
Nov 30 (Sun): ❌ Weekend
Dec 1 (Mon): Messages 13-16 post (resumes)
```

---

## Troubleshooting

### Messages Not Posting

**Check scheduled time:**
```bash
python main.py --status
```

Look for:
- "Next Message Due Now" - should show current message
- "Upcoming Schedule" - verify times are correct

**Common issues:**
- ❌ **Weekend** - No posts on Sat/Sun
- ❌ **Holiday** - Check if today is US federal holiday
- ❌ **Too early** - Message scheduled for 9am, current time is 8:45am
- ❌ **Credentials missing** - LinkedIn/X API keys not configured

### Posts Being Skipped

**Output shows:**
```
⏸️  SKIPPING: Cannot schedule 'Post Title' within 7 days
   Schedule is full. This post will be retried on next fetch.
```

**This is normal!** It means:
- Schedule is healthy and full
- Post will be retried automatically tomorrow
- Once messages post, capacity opens up
- Post will then be processed

**To fix immediately:**
```bash
# Option 1: Clear old messages
python clear_unposted.py --all

# Option 2: Increase window temporarily
gh secret set MAX_SCHEDULE_DAYS_AHEAD --body '14'
```

### View Raw Schedule

**Query database directly:**
```bash
sqlite3 data/posts.db "
  SELECT 
    datetime(scheduled_for) as time,
    substr(message_text, 1, 50) as message
  FROM posted_messages
  WHERE posted_at IS NULL
  ORDER BY scheduled_for
  LIMIT 20
"
```

### Reschedule Everything

**If you need a fresh start:**
```bash
# Backup first
cp data/posts.db data/posts.db.backup

# Clear all unposted messages
python clear_unposted.py --all

# Re-fetch and reschedule
python main.py --fetch-posts
```

---

## How Posting Works

### The Pull Model

The system uses a **"pull" model**, not "push":

**Phase 1: Schedule Creation (Fetch)**
```
1. Fetch blog post from RSS
2. Extract 5 messages with Claude
3. Generate images with Grok
4. Calculate schedule times
5. Save to database with scheduled_for times
```

**Phase 2: Publishing (Post)**
```
1. GitHub Actions runs at 9am, 11am, 1pm, 3pm EST
2. Query: "SELECT message WHERE scheduled_for <= NOW()"
3. If message found and due → Post to LinkedIn/X
4. Mark as posted in database
5. Done
```

**Key Insight:** Messages are scheduled once, then "pulled" when their time comes.

---

## API Reference

### PostScheduler Methods

```python
from scheduler import PostScheduler

scheduler = PostScheduler()

# Check if date is business day
is_business = scheduler.is_business_day(datetime(2025, 10, 21))

# Get next business day
next_day = scheduler.get_next_business_day(datetime.now())

# Schedule messages
times = scheduler.schedule_messages(
    num_messages=5,
    existing_schedules=[],
    start_date=None  # Defaults to tomorrow
)

# Check if time to post
should_post = scheduler.is_time_to_post(scheduled_time)
```

### Database Methods

```python
from database import Database

db = Database()

# Get all scheduled times (for conflict detection)
schedules = db.get_all_scheduled_times()

# Get upcoming schedule
upcoming = db.get_upcoming_schedule(limit=10)

# Get next message due now
message = db.get_next_message_to_post()
```

---

## Summary

**Your Configuration (Weekly Blogger):**
- ✅ `POSTS_PER_BLOG=5` - Five messages per post
- ✅ `MAX_SCHEDULE_DAYS_AHEAD=7` - Start within a week
- ✅ `MINIMUM_POST_DATE=2025-10-15` - Recent posts only
- ✅ Latest posts first
- ✅ Business days only (Mon-Fri)
- ✅ 4 time slots per day

**Expected Behavior:**
- Monday: Write blog post
- Tuesday: Auto-processed, 5 messages scheduled Tue-Mon
- Schedule: Always 3-7 days ahead
- Fresh content: Always promoting latest posts
- Zero maintenance required

**It just works! 🎉**

---

**Last Updated:** October 20, 2025  
**Related:** [README.md](README.md), [SETUP_GUIDE.md](SETUP_GUIDE.md), [TESTING.md](TESTING.md)
