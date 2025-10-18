# 🎯 Post Selection Logic: How the System Chooses What to Publish

## Quick Answer

The system uses a **simple SQL query** that selects posts based on:
1. ✅ Has a `scheduled_for` timestamp
2. ✅ Scheduled time has passed (`scheduled_for <= NOW()`)
3. ✅ Not yet fully posted (missing LinkedIn OR X posting)
4. ✅ Ordered by scheduled time (earliest first)
5. ✅ Returns only 1 message (the next due)

## 🔍 The Selection Query

### Code in `database.py` (lines 116-133)

```python
def get_next_message_to_post(self):
    """Get the next message that needs to be posted (based on schedule)."""
    
    cursor.execute("""
        SELECT 
            pm.id,
            pm.blog_post_id,
            pm.message_index,
            pm.message_text,
            pm.scheduled_for,
            pm.posted_to_linkedin,
            pm.posted_to_x,
            bp.title,
            bp.post_url
        FROM posted_messages pm
        JOIN blog_posts bp ON pm.blog_post_id = bp.id
        WHERE (pm.posted_to_linkedin = 0 OR pm.posted_to_x = 0)
          AND pm.scheduled_for IS NOT NULL
        ORDER BY pm.scheduled_for ASC
        LIMIT 1
    """)
```

### What This Query Does

**1. Finds Unposted Messages:**
```sql
WHERE (pm.posted_to_linkedin = 0 OR pm.posted_to_x = 0)
```
- Only considers messages not yet fully posted
- Allows partial posting (posted to LinkedIn but not X)

**2. Requires Schedule:**
```sql
AND pm.scheduled_for IS NOT NULL
```
- Only messages with assigned schedule times
- Ignores any unscheduled messages

**3. Orders by Time:**
```sql
ORDER BY pm.scheduled_for ASC
```
- Earliest scheduled message comes first
- Ensures chronological posting

**4. Returns One:**
```sql
LIMIT 1
```
- Only returns the next message to post
- One at a time prevents overwhelming social media

## ⏰ The Time Check

After fetching the message, there's an additional check:

### Code in `database.py` (lines 139-143)

```python
scheduled_time = datetime.fromisoformat(row[4])

# Check if it's time to post
if not self.scheduler.is_time_to_post(scheduled_time):
    return None  # Not time yet
```

### `is_time_to_post()` in `scheduler.py`

```python
def is_time_to_post(self, scheduled_time, current_time=None):
    if current_time is None:
        current_time = datetime.now(self.eastern)
    
    # Post if current time is past scheduled time
    return current_time >= scheduled_time
```

**What This Does:**
- Compares scheduled time with current time (in Eastern timezone)
- Returns `True` if current time ≥ scheduled time
- Returns `False` if scheduled time is in the future

## 📊 Complete Decision Flow

```
┌─────────────────────────────┐
│ GitHub Actions Runs         │
│ (e.g., 9:00 AM EST)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Query Database:             │
│ SELECT next unposted        │
│ WHERE scheduled_for <= NOW  │
│ ORDER BY scheduled_for ASC  │
│ LIMIT 1                     │
└──────────┬──────────────────┘
           │
           ▼
      ┌────┴─────┐
      │ Message  │
      │ Found?   │
      └────┬─────┘
           │
    ┌──────┴───────┐
    │              │
   YES            NO
    │              │
    ▼              ▼
┌────────┐    ┌────────┐
│ Time   │    │ Exit   │
│ Check  │    │ (Done) │
└───┬────┘    └────────┘
    │
    ▼
  Is scheduled_for
  <= current_time?
    │
┌───┴────┐
│        │
YES     NO
│        │
▼        ▼
Post   Exit
to     (Not
Social  time
Media   yet)
│
▼
Mark as
Posted
```

## 🧪 Example Walkthrough

### Scenario: Sept 4, 9:00 AM

**Database State Before:**
```
id | message_text              | scheduled_for          | posted_to_linkedin | posted_to_x
---|---------------------------|------------------------|--------------------|--------------
1  | "Can you provide..."      | 2025-09-04 09:00:00   | 0                  | 0  ← DUE NOW
2  | "Infrastructure vis..."   | 2025-09-04 11:00:00   | 0                  | 0  ← FUTURE
3  | "Two startups, same..."   | 2025-09-05 09:00:00   | 0                  | 0  ← FUTURE
```

**Step 1: Query Executes**
```sql
SELECT * FROM posted_messages 
WHERE (posted_to_linkedin = 0 OR posted_to_x = 0)
  AND scheduled_for IS NOT NULL
ORDER BY scheduled_for ASC
LIMIT 1
```

**Result:** Returns message ID 1 (earliest scheduled)

**Step 2: Time Check**
```python
scheduled_time = 2025-09-04 09:00:00
current_time   = 2025-09-04 09:00:00 (from GitHub Actions)

is_time_to_post(scheduled_time):
    return current_time >= scheduled_time
    return 09:00:00 >= 09:00:00
    return True  ✅
```

**Step 3: Post Message**
- Post to LinkedIn
- Post to X (Twitter)
- Update database

**Database State After:**
```
id | message_text              | scheduled_for          | posted_to_linkedin | posted_to_x
---|---------------------------|------------------------|--------------------|--------------
1  | "Can you provide..."      | 2025-09-04 09:00:00   | 1 ✅               | 1 ✅
2  | "Infrastructure vis..."   | 2025-09-04 11:00:00   | 0                  | 0  ← NEXT
3  | "Two startups, same..."   | 2025-09-05 09:00:00   | 0                  | 0
```

### Next Run: Sept 4, 11:00 AM

**Step 1: Query Executes**
- Now returns message ID 2 (message 1 is marked as posted)

**Step 2: Time Check**
```python
scheduled_time = 2025-09-04 11:00:00
current_time   = 2025-09-04 11:00:00

is_time_to_post(scheduled_time):
    return 11:00:00 >= 11:00:00
    return True  ✅
```

**Step 3: Post Message ID 2**

## 🔑 Key Selection Criteria

### 1. Scheduled Time (Primary)
```sql
ORDER BY pm.scheduled_for ASC
```
**Impact:** Posts always go out in chronological order

**Why:** Maintains narrative flow, ensures oldest content posts first

### 2. Posted Status
```sql
WHERE (pm.posted_to_linkedin = 0 OR pm.posted_to_x = 0)
```
**Impact:** Won't repost already-posted messages

**Why:** Prevents duplicates on social media

### 3. Not Null Schedule
```sql
AND pm.scheduled_for IS NOT NULL
```
**Impact:** Ignores unscheduled messages

**Why:** Only posts messages with assigned times

### 4. One at a Time
```sql
LIMIT 1
```
**Impact:** Posts one message per execution

**Why:** GitHub Actions runs multiple times per day; posting one at a time spreads content

## 🎯 What Gets Selected First?

**Priority Order:**
1. **Earliest scheduled time** (most important)
2. **Not yet posted** (both platforms)
3. **Has a schedule** (not NULL)

**This means:**
- Sept 4, 9am message posts before Sept 4, 11am message
- Sept 4 messages post before Sept 5 messages
- Already-posted messages are skipped
- Messages without schedules are never selected

## 💡 Edge Cases Handled

### Case 1: Missed Run
**Scenario:** GitHub Actions didn't run at 9am, runs at 11am instead

**Query at 11am:**
```
Messages scheduled for:
- 9:00 AM (overdue) ← SELECTED
- 11:00 AM (due now)
```

**Result:** Posts the 9am message first (oldest), then 11am on next run

### Case 2: Partial Posting
**Scenario:** Posted to LinkedIn but X API failed

**Database:**
```
id=1: posted_to_linkedin=1, posted_to_x=0
```

**Query Still Selects It:**
```sql
WHERE (posted_to_linkedin = 0 OR posted_to_x = 0)  -- This is TRUE
```

**Result:** Retries X posting on next run

### Case 3: Multiple Overdue
**Scenario:** System was down for 2 days, multiple messages overdue

**Query:**
```sql
ORDER BY scheduled_for ASC  -- Oldest first
LIMIT 1                     -- One at a time
```

**Result:** Posts oldest first, catches up one message per run

## 📝 Summary

### Selection Algorithm

```python
def what_gets_posted():
    messages = query("""
        SELECT * FROM posted_messages
        WHERE:
            - Not fully posted (LinkedIn OR X missing)
            - Has scheduled time (not NULL)
        ORDER BY:
            - Scheduled time (earliest first)
        LIMIT:
            - 1 message only
    """)
    
    for message in messages:  # Only 1 message anyway
        if current_time >= message.scheduled_for:
            post(message)
            mark_as_posted(message)
            break
        else:
            print("Not time yet")
            break
```

### In Plain English

**The system selects:**
1. The **oldest scheduled** message
2. That **hasn't been fully posted** yet
3. Whose **scheduled time has passed**
4. And posts **only one** at a time

**Think of it like:** A queue sorted by time, where we take the first item that's ready, post it, then mark it as done. Next run, we take the next item.

---

**Key Insight:** It's a simple, reliable algorithm that guarantees chronological posting, prevents duplicates, and handles failures gracefully by automatically retrying incomplete posts.

