# 🎯 Priority Scheduling: Latest Posts First

## Overview

The system now prioritizes **latest blog posts** and automatically pauses when the schedule is full, ensuring your most recent content always gets scheduled first.

---

## 🆕 What Changed

### Before (Old Behavior)
- Processed all blog posts from RSS feed oldest-to-newest
- Would schedule posts indefinitely far into the future
- Could have posts scheduled 3+ months out
- Older content would fill the schedule

### After (New Behavior)
- ✅ **Processes newest posts first** (RSS feed order)
- ✅ **Only schedules within 7 days** (configurable)
- ✅ **Pauses if schedule is full**
- ✅ **Retries older posts when schedule clears**

---

## 🔧 How It Works

### 1. RSS Feed Order (Newest First)

RSS/JSON feeds naturally return **newest posts first**. The system processes them in that order:

```
Fetch runs:
Post 1: "Latest Article" (Oct 20, 2025) ← Processed first
Post 2: "Week-Old Article" (Oct 13, 2025) ← Processed second
Post 3: "Old Article" (Oct 6, 2025) ← Processed third
...
```

### 2. Schedule Capacity Check

Before saving each post, the system checks:

**Question:** *Can all 5 messages from this post fit within the next 7 days?*

```python
# In database.py
can_schedule = self.scheduler.can_schedule_within_days(
    num_messages=5,
    existing_schedules=existing_schedules,
    max_days=7  # Default: 7 days
)
```

**If YES:** Process the post, extract messages, schedule them ✅

**If NO:** Skip the post, stop processing, try again tomorrow ⏸️

---

## 📊 Example Scenario

### Scenario: You have 10 blog posts in your feed

**Current Schedule Status:**
- Next 7 days have 15 available slots (Mon-Fri × 3 days × 4 slots = 12, rounded)
- Already scheduled: 10 messages

**Available capacity:** 5 slots in next 7 days

**What Happens:**

```
Post 1 (Latest): 5 messages needed
✅ Check: Can fit 5 messages in 7 days? YES (5 slots available)
✅ Action: Extract messages, schedule them
✅ Result: Processed. 0 slots remaining.

Post 2 (Second newest): 5 messages needed
❌ Check: Can fit 5 messages in 7 days? NO (0 slots available)
⏸️  Action: SKIP this post
⏸️  Result: Not processed. Will retry tomorrow.

Posts 3-10: Not reached (stopped after Post 2)
```

**Next Day:**
- 4 messages posted (schedule cleared)
- Post 2 will be retried (now has 4 slots available)
- Post 2 still won't fit (needs 5)
- System continues posting existing messages

**Day After:**
- More messages posted
- Post 2 retried again
- Now fits! Gets processed ✅

---

## 🎛️ Configuration

### MAX_SCHEDULE_DAYS_AHEAD

**Default:** `7` days

**Purpose:** Limits how far ahead the system will schedule posts.

**Configuration:**

```bash
# In .env
MAX_SCHEDULE_DAYS_AHEAD=7

# Or GitHub Secret
gh secret set MAX_SCHEDULE_DAYS_AHEAD --body '7' \
  --repo Axon-Shield/daily-posting-from-blog
```

### Recommended Values

| Use Case | Recommended | Why |
|----------|-------------|-----|
| **Weekly blogger** (default) | `7` | One week buffer, ensures fresh content |
| **Daily blogger** | `14` | Two weeks buffer, smoother operation |
| **Sporadic blogger** | `30` | One month buffer, accommodates irregular posting |
| **Testing/Development** | `3` | Quick turnaround for testing |

---

## 💡 Benefits

### 1. **Always Fresh Content**
Your social media always reflects your **latest thinking** and **current topics**.

**Example:**
- October 20: Write post about "New Feature Launch"
- October 21: Post scheduled (within 7 days)
- October 22: First social media message published ✅

vs. Old System:
- October 20: Write post
- System has 3-month backlog
- January 2026: First message published ❌ (stale!)

---

### 2. **Prevents Schedule Bloat**
Schedule never extends beyond 7 days (or your configured limit).

**Old System:**
```
Today: Oct 20
Furthest scheduled: Feb 15, 2026 (4 months out) ❌
```

**New System:**
```
Today: Oct 20
Furthest scheduled: Oct 27 (7 days out) ✅
```

---

### 3. **Self-Regulating**
System automatically adjusts to your posting cadence.

**Scenario A: Light Week**
- 1 new blog post
- Schedule has room
- Post processed immediately ✅

**Scenario B: Busy Week**
- 5 new blog posts
- Schedule fills up
- Posts 1-2 processed, posts 3-5 queued ⏸️
- Posts 3-5 automatically processed next week ✅

---

### 4. **No Manual Intervention**
You don't need to:
- Monitor schedule length
- Clear old posts
- Adjust settings

System does it automatically! 🎉

---

## 🔍 Monitoring

### Check What's Scheduled

```bash
python main.py --status
```

**Example Output:**
```
=== SYSTEM STATUS ===

Blog posts in database: 3
Total unposted messages: 15

=== UPCOMING SCHEDULE ===
Next 5 scheduled posts:

1. Monday, 2025-10-21 at 09:00 AM ET
   Blog: "Latest Post Title"
   Message: "Key insight about security..."

2. Monday, 2025-10-21 at 11:00 AM ET
   Blog: "Another Recent Post"
   Message: "Important finding about..."

[...]

Total: 15 messages scheduled over next 4 days
Furthest scheduled: 2025-10-24 (4 days from now)
```

### Check for Skipped Posts

When running fetch, look for:

```
⏸️  SKIPPING: Cannot schedule 'Old Post Title' within 7 days
   Schedule is full. This post will be retried on next fetch.

⚠️  Schedule is full. Stopping fetch.
   Older posts will be retried when schedule clears.
```

This is **normal and expected** when you have a healthy backlog!

---

## ❓ FAQ

### Q: What happens to posts that are skipped?

**A:** They remain in your RSS feed and will be retried on the next daily fetch (tomorrow). Once the schedule clears, they'll be processed.

---

### Q: Won't I lose old posts?

**A:** No! As long as they:
1. Pass the `MINIMUM_POST_DATE` filter
2. Remain in your RSS feed (typically last 10-20 posts)

They will eventually be processed when schedule capacity becomes available.

---

### Q: What if I have an urgent new post that needs to go out immediately?

**A:** Options:

**Option 1 - Clear schedule (recommended):**
```bash
# Use GitHub Action: "Clear Unposted Messages"
# Or locally:
python clear_unposted.py --all
```
Then run fetch again - your new post will be processed.

**Option 2 - Increase limit temporarily:**
```bash
gh secret set MAX_SCHEDULE_DAYS_AHEAD --body '14'
```
Fetch will process more posts.

**Option 3 - Manual posting:**
Use the test workflows to post specific content immediately.

---

### Q: How do I know if I should increase MAX_SCHEDULE_DAYS_AHEAD?

**Signs you should increase it:**
- ✅ You post multiple times per week
- ✅ Messages are getting skipped consistently
- ✅ You want a larger content buffer

**Example:**
```bash
# Increase to 14 days for more breathing room
gh secret set MAX_SCHEDULE_DAYS_AHEAD --body '14'
```

---

### Q: Can I disable this feature and go back to unlimited scheduling?

**A:** Yes, set it very high:

```bash
gh secret set MAX_SCHEDULE_DAYS_AHEAD --body '365'
```

This effectively disables the limit (schedules up to 1 year ahead).

---

### Q: Does this affect already-scheduled posts?

**A:** No. Posts already in the database with scheduled times will continue to post normally. This only affects **new posts being fetched**.

---

### Q: What if my RSS feed only keeps the last 5 posts?

**A:** This is fine! The system processes them newest-first, so you'll always get your 5 most recent posts scheduled. Older posts naturally drop out of the feed.

---

### Q: Will this consume more Anthropic API credits?

**A:** No! Actually **less**:
- Skipped posts aren't sent to Claude for extraction
- Only posts that fit in the schedule consume API credits
- Same or lower cost than before

---

## 🎯 Best Practices

### 1. **Start with Default (7 days)**
```bash
MAX_SCHEDULE_DAYS_AHEAD=7
```
This works well for most weekly bloggers.

---

### 2. **Monitor for First Week**
Check the fetch logs daily for the first week:
- How many posts processed?
- How many skipped?
- Is the schedule staying within 7 days?

---

### 3. **Adjust Based on Cadence**

**Weekly blogger (1 post/week):**
- Keep at 7 days ✅
- Schedule stays ~1 week ahead

**2-3 posts/week:**
- Increase to 10-14 days
- Gives more buffer

**Daily blogger:**
- Increase to 14-21 days
- Prevents frequent skipping

---

### 4. **Seasonal Adjustments**

**Busy season (lots of content):**
```bash
MAX_SCHEDULE_DAYS_AHEAD=14  # More buffer
```

**Slow season (less content):**
```bash
MAX_SCHEDULE_DAYS_AHEAD=7  # Keep it tight
```

---

## 🔄 Migration from Old System

### If You Have Existing Scheduled Posts

**Scenario:** You already have 50 messages scheduled 2 months into the future.

**What Happens:**
1. Existing messages continue posting normally ✅
2. New fetch runs will skip new posts (schedule full) ⏸️
3. As old messages post, schedule clears gradually
4. New posts get processed as capacity opens up ✅

**Timeline:**
- Weeks 1-4: Posting old backlog
- Weeks 5+: System catches up, processes new posts
- Equilibrium: Schedule stays within 7 days ✅

**To Speed Up:**
```bash
# Clear old backlog if you want fresh start
python clear_unposted.py --all

# Then let system rebuild with new priority logic
python main.py --fetch-posts
```

---

## 📈 System Behavior Over Time

### Week 1 (Initial State)
```
Schedule: Empty
Fetch: Processes 5 posts
Schedule: 25 messages, ~6 days ahead ✅
```

### Week 2 (Steady State)
```
Schedule: 15 messages remaining (10 posted from week 1)
New post: 1 this week
Fetch: Processes 1 new post (5 messages)
Schedule: 20 messages, ~5 days ahead ✅
```

### Week 3 (Equilibrium)
```
Schedule: 15-20 messages at all times
Fetch: Processes new posts as capacity allows
Schedule: Always 5-7 days ahead ✅
Status: Optimal! 🎉
```

---

## 🎉 Summary

**New Behavior:**
- ✅ Newest posts always processed first
- ✅ Schedule limited to 7 days (configurable)
- ✅ Automatically pauses when full
- ✅ Retries older posts when capacity opens
- ✅ Self-regulating and low-maintenance

**For Your Use Case (Weekly Blogger):**
- ✅ Default settings (7 days) are perfect
- ✅ Each new post scheduled within 1 week
- ✅ Always promoting current content
- ✅ No action needed

**Key Insight:**
> "The system now works like a **rolling window** - always showing your freshest content to your audience, automatically managing the queue size."

---

**Last Updated:** October 20, 2025  
**Related Docs:** [SCHEDULING.md](SCHEDULING.md), [SCHEDULING_LIMITS.md](SCHEDULING_LIMITS.md)

