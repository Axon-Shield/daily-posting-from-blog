# 📅 Scheduling Example: 3 Blog Posts in 3 Days

## Scenario

You publish 3 blog posts on consecutive days:
- **Blog Post 1**: "Infrastructure Visibility" - Published September 1
- **Blog Post 2**: "Certificate Management" - Published September 2  
- **Blog Post 3**: "Trust Stores" - Published September 3

You fetch all posts on **September 3** evening. Here's how they get scheduled:

## Configuration

- **POSTS_PER_BLOG**: 5 messages per blog post
- **Total Messages**: 15 (3 posts × 5 messages)
- **Time Slots**: 9:00 AM, 1:00 PM, 11:00 AM, 3:00 PM EST
- **Max Per Day**: 4 posts per business day
- **Rules**: No weekends, no US holidays

## Complete Schedule

### 📅 Thursday, September 4, 2025

| Time | Post | Message | Topic |
|------|------|---------|-------|
| 9:00 AM EST | Post 1 | Message 1 | Infrastructure Visibility |
| 11:00 AM EST | Post 1 | Message 3 | Infrastructure Visibility |
| 1:00 PM EST | Post 1 | Message 2 | Infrastructure Visibility |
| 3:00 PM EST | Post 1 | Message 4 | Infrastructure Visibility |

**4 posts scheduled** ✅ (Day FULL)

---

### 📅 Friday, September 5, 2025

| Time | Post | Message | Topic |
|------|------|---------|-------|
| 9:00 AM EST | Post 1 | Message 5 | Infrastructure Visibility |
| 11:00 AM EST | Post 2 | Message 2 | Certificate Management |
| 1:00 PM EST | Post 2 | Message 1 | Certificate Management |
| 3:00 PM EST | Post 2 | Message 3 | Certificate Management |

**4 posts scheduled** ✅ (Day FULL)

---

### 🚫 Saturday-Sunday, September 6-7, 2025

**SKIPPED** - Weekend (no posting)

---

### 📅 Monday, September 8, 2025

*(Labor Day is Sept 1, so Sept 8 is a regular business day)*

| Time | Post | Message | Topic |
|------|------|---------|-------|
| 9:00 AM EST | Post 2 | Message 4 | Certificate Management |
| 11:00 AM EST | Post 3 | Message 1 | Trust Stores |
| 1:00 PM EST | Post 2 | Message 5 | Certificate Management |
| 3:00 PM EST | Post 3 | Message 2 | Trust Stores |

**4 posts scheduled** ✅ (Day FULL)

---

### 📅 Tuesday, September 9, 2025

| Time | Post | Message | Topic |
|------|------|---------|-------|
| 9:00 AM EST | Post 3 | Message 3 | Trust Stores |
| 11:00 AM EST | Post 3 | Message 5 | Trust Stores |
| 1:00 PM EST | Post 3 | Message 4 | Trust Stores |

**3 posts scheduled** ✅

---

## Summary

### By Blog Post

**📝 Blog Post 1** (Sept 1):
- Sept 4: 4 messages
- Sept 5: 1 message
- **Total**: 5 messages over 2 days

**📝 Blog Post 2** (Sept 2):
- Sept 5: 3 messages
- Sept 8: 2 messages
- **Total**: 5 messages over 2 days

**📝 Blog Post 3** (Sept 3):
- Sept 8: 2 messages
- Sept 9: 3 messages
- **Total**: 5 messages over 2 days

### Timeline

```
Sept 1 (Mon) - Publish Post 1 ───┐
Sept 2 (Tue) - Publish Post 2 ───┤ Writing/Publishing
Sept 3 (Wed) - Publish Post 3 ───┘
                                   
Sept 3 (Wed Evening) - Fetch all posts & schedule
                                   
Sept 4 (Thu) ─── 4 posts ──────┐
Sept 5 (Fri) ─── 4 posts       │
Sept 6 (Sat) ─── SKIP          │ Social Media
Sept 7 (Sun) ─── SKIP          │ Distribution
Sept 8 (Mon) ─── 4 posts       │
Sept 9 (Tue) ─── 3 posts ──────┘

Total: 15 messages posted over 4 business days
```

## Key Observations

### 🎯 Intelligent Distribution

1. **Fills days efficiently**: Uses all 4 time slots per day
2. **Respects weekends**: Automatically skips Saturday-Sunday
3. **Interleaves content**: Mixes messages from different posts
4. **Maintains quality**: Each time slot gets attention from your audience

### 📊 Posting Frequency

With this configuration:
- **Writing pace**: 3 blog posts in 3 days
- **Social media**: 15 posts over 4 business days
- **Avg frequency**: ~4 posts per day
- **Total duration**: 4 business days (1 work week)

### 💡 Benefits

**For Content Creators:**
- Batch create content when inspired
- System handles distribution automatically
- Maintains consistent social media presence

**For Your Audience:**
- Regular, predictable posting times
- Multiple topics covered each day
- Professional, never spammy (4 posts max/day)

## What If You Have More Posts?

### Scenario: 5 Blog Posts

If you published 5 blog posts instead of 3:
- **Total messages**: 25 (5 × 5)
- **Days needed**: ~6-7 business days
- **Duration**: About 1.5 work weeks

### Scenario: Weekly Blog Cadence

If you publish **1 blog per week**:
- **5 messages per post**
- **Duration**: 1.25 business days per post
- **Result**: 2-3 posts per week with gaps = natural, organic feel

## Customization Options

### Want Fewer Messages Per Day?

Change time slots in `scheduler.py`:
```python
TIME_SLOTS = [
    (9, 0),   # 9:00 AM
    (13, 0),  # 1:00 PM
]
MAX_POSTS_PER_DAY = 2  # Only 2 per day
```

### Want More Messages Per Post?

Set GitHub Secret:
```bash
POSTS_PER_BLOG=7  # 7 messages instead of 5
```

### Want Different Days?

Scheduler already handles:
- ✅ Weekends (skipped)
- ✅ US Federal Holidays (skipped)
- ✅ Business days only (Mon-Fri)

---

**This schedule is automatically generated when you run:**
```bash
python main.py --fetch-posts
```

The system analyzes existing schedules and finds optimal slots for each message!

