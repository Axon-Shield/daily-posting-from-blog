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
- **KEY RULE**: Only 1 message per blog post per day

## Complete Schedule

### 📅 Thursday, September 4, 2025

| Time | Post | Message # | Topic |
|------|------|-----------|-------|
| 9:00 AM EST | Post 1 | Message 1 of 5 | Infrastructure Visibility |
| 11:00 AM EST | Post 2 | Message 1 of 5 | Certificate Management |
| 1:00 PM EST | Post 3 | Message 1 of 5 | Trust Stores |

**3 posts scheduled** (one from each blog post)

---

### 📅 Friday, September 5, 2025

| Time | Post | Message # | Topic |
|------|------|-----------|-------|
| 9:00 AM EST | Post 1 | Message 2 of 5 | Infrastructure Visibility |
| 11:00 AM EST | Post 2 | Message 2 of 5 | Certificate Management |
| 1:00 PM EST | Post 3 | Message 2 of 5 | Trust Stores |

**3 posts scheduled** (second message from each blog post)

---

### 🚫 Saturday-Sunday, September 6-7, 2025

**SKIPPED** - Weekend (no posting)

---

### 📅 Monday, September 8, 2025

| Time | Post | Message # | Topic |
|------|------|-----------|-------|
| 9:00 AM EST | Post 1 | Message 3 of 5 | Infrastructure Visibility |
| 11:00 AM EST | Post 2 | Message 3 of 5 | Certificate Management |
| 1:00 PM EST | Post 3 | Message 3 of 5 | Trust Stores |

**3 posts scheduled** (third message from each blog post)

---

### 📅 Tuesday, September 9, 2025

| Time | Post | Message # | Topic |
|------|------|-----------|-------|
| 9:00 AM EST | Post 1 | Message 4 of 5 | Infrastructure Visibility |
| 11:00 AM EST | Post 2 | Message 4 of 5 | Certificate Management |
| 1:00 PM EST | Post 3 | Message 4 of 5 | Trust Stores |

**3 posts scheduled** (fourth message from each blog post)

---

### 📅 Wednesday, September 10, 2025

| Time | Post | Message # | Topic |
|------|------|-----------|-------|
| 9:00 AM EST | Post 1 | Message 5 of 5 ✅ | Infrastructure Visibility |
| 11:00 AM EST | Post 2 | Message 5 of 5 ✅ | Certificate Management |
| 1:00 PM EST | Post 3 | Message 5 of 5 ✅ | Trust Stores |

**3 posts scheduled** (final message from each blog post)

**ALL POSTS COMPLETE! 🎉**

---

## Summary

### By Blog Post

**📝 Blog Post 1** (Sept 1):
- 5 messages scheduled over 5 business days (Sept 4, 5, 8, 9, 10)
- One message per day at 9:00 AM EST

**📝 Blog Post 2** (Sept 2):
- 5 messages scheduled over 5 business days (Sept 4, 5, 8, 9, 10)
- One message per day at 11:00 AM EST

**📝 Blog Post 3** (Sept 3):
- 5 messages scheduled over 5 business days (Sept 4, 5, 8, 9, 10)
- One message per day at 1:00 PM EST

### Timeline

```
Sept 1 (Mon) - Publish Post 1 ───┐
Sept 2 (Tue) - Publish Post 2 ───┤ Writing/Publishing
Sept 3 (Wed) - Publish Post 3 ───┘
                                   
Sept 3 (Wed Evening) - Fetch all posts & schedule
                                   
Sept 4 (Thu) ─── P1-M1, P2-M1, P3-M1 ──┐
Sept 5 (Fri) ─── P1-M2, P2-M2, P3-M2   │
Sept 6 (Sat) ─── SKIP                  │
Sept 7 (Sun) ─── SKIP                  │ Social Media
Sept 8 (Mon) ─── P1-M3, P2-M3, P3-M3   │ Distribution
Sept 9 (Tue) ─── P1-M4, P2-M4, P3-M4   │ (1 week)
Sept 10 (Wed) ── P1-M5, P2-M5, P3-M5 ──┘

Total: 15 messages posted over 5 business days
```

## Key Observations

### 🎯 One Message Per Blog Per Day

**Why this matters:**
1. **Sustained Engagement**: Each blog post stays in audience's mind for a full week
2. **No Cannibalization**: Messages from same post don't compete with each other
3. **Consistent Presence**: Your audience sees you daily without feeling spammed
4. **Topic Variety**: Different topics each day keeps content fresh

### 📊 Posting Pattern

**Daily Schedule:**
- 3 posts per day (one from each blog post)
- All at different times (9am, 11am, 1pm)
- Spreads throughout business hours
- Professional, not overwhelming

**Publication Pattern:**
- If you publish 3 posts in one burst (like this example)
- Social media spreads them over 1 work week (5 business days)
- Creates consistent daily presence

### 💡 Benefits

**For Content Creators:**
- Write 3 posts when inspired
- System distributes over a week
- Sustainable long-term strategy
- No daily posting pressure

**For Your Audience:**
- Daily touchpoint with your brand
- Variety of topics each day
- Predictable posting times
- Never feels spammy (3 posts/day max with multiple blogs)

## What If You Have More Posts?

### Scenario: Publishing 1 Blog Per Week

If you publish **1 blog post per week**:
- **5 messages** over **5 business days**
- **1 post per day** at same time (e.g., 9am)
- Creates a consistent "series" feel
- Natural gaps between days

**Example:**
- Monday 9am: Message 1
- Tuesday 9am: Message 2
- Wednesday 9am: Message 3
- Thursday 9am: Message 4
- Friday 9am: Message 5

### Scenario: Publishing 4+ Blogs

If you have **4 blog posts** at once:
- **20 total messages** (4 × 5)
- **5 business days** to distribute
- **4 posts per day** (fills all time slots)

**Day 1:** All 4 posts, Message 1 (9am, 11am, 1pm, 3pm)  
**Day 2:** All 4 posts, Message 2  
**Day 3:** All 4 posts, Message 3  
**Day 4:** All 4 posts, Message 4  
**Day 5:** All 4 posts, Message 5

## Customization Options

### Want Different Number of Messages?

Set `POSTS_PER_BLOG`:
```bash
POSTS_PER_BLOG=3  # Only 3 messages per blog = 3 days
POSTS_PER_BLOG=7  # 7 messages per blog = 7 days (full week)
```

### Want Different Time Slots?

Edit `scheduler.py`:
```python
TIME_SLOTS = [
    (9, 0),   # 9:00 AM
    (14, 0),  # 2:00 PM - Changed from 1pm
    (11, 0),  # 11:00 AM
    (16, 0),  # 4:00 PM - Changed from 3pm
]
```

### Want to Change Max Posts Per Day?

Edit `scheduler.py`:
```python
MAX_POSTS_PER_DAY = 3  # Reduce from 4 to 3
```

## Real-World Example: Regular Blog Cadence

**Your Publishing Schedule:**
- Every Monday: Publish 1 new blog post

**Automatic Social Schedule:**
- Monday-Friday: 1 message per day from that post
- Following Monday: New blog post + start next series
- Continuous 1-post-per-day presence

**Result:**
- Consistent daily presence
- Each blog gets full week of attention
- Sustainable, never overwhelming
- Professional social media presence

---

**This schedule is automatically generated when you run:**
```bash
python main.py --fetch-posts
```

The system ensures each blog post's messages are distributed one per day, maximizing engagement and preventing message fatigue!
