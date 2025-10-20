# 🔄 How Scheduled Posting Works

## TL;DR

**Short Answer:** Posts are scheduled in advance (Phase 1), then GitHub Actions runs every few hours to check if any messages are due and posts them in real-time (Phase 2).

**It's NOT:** "Set it and forget it" with automatic posting at exact times  
**It IS:** "Check and post" - GitHub Actions checks periodically and posts what's due

## 📋 Two-Phase System

### Phase 1: Creating the Schedule (One-Time)

**When:** You run `--fetch-posts` (daily via GitHub Actions, or manually)

**What Happens:**
```
1. Fetch blog posts from RSS feed
2. AI extracts 5 messages per post
3. Scheduler calculates optimal times:
   - Message 1 → Sept 4 at 9:00 AM EST
   - Message 2 → Sept 5 at 9:00 AM EST
   - Message 3 → Sept 8 at 9:00 AM EST
   - etc.
4. Store schedule in database (scheduled_for column)
5. NOTHING IS POSTED YET
```

**Database After Scheduling:**
```sql
id | message_text              | scheduled_for           | posted_to_linkedin | posted_to_x
---|---------------------------|-------------------------|--------------------|--------------
1  | "Can you provide..."      | 2025-09-04T09:00:00-04 | 0                  | 0
2  | "Two startups, same..."   | 2025-09-05T09:00:00-04 | 0                  | 0
3  | "Infrastructure vis..."   | 2025-09-08T09:00:00-04 | 0                  | 0
```

### Phase 2: Executing the Schedule (Continuous)

**When:** GitHub Actions runs on cron schedule (4 times daily)

**Cron Schedule:**
- 9:00 AM EST
- 11:00 AM EST
- 1:00 PM EST
- 3:00 PM EST
- **Every business day** (Mon-Fri)

**What Happens Each Time GitHub Actions Runs:**
```
1. GitHub Actions triggers (e.g., at 9:00 AM EST)
2. Download database from artifact storage
3. Query database:
   SELECT * FROM posted_messages 
   WHERE scheduled_for <= NOW()
   AND (posted_to_linkedin = 0 OR posted_to_x = 0)
   ORDER BY scheduled_for ASC
4. IF message is due:
   - Post to LinkedIn/X
   - Mark as posted in database
   - Upload database back to artifact storage
5. IF no messages due:
   - Do nothing, exit
```

## ⏰ Timeline Example

### Sept 3, 8:00 PM - Fetch Posts
```
ACTION: python main.py --fetch-posts
RESULT: 15 messages scheduled for Sept 4-10
STATUS: Nothing posted yet
```

### Sept 4, 9:00 AM - First GitHub Actions Run
```
TIME: 9:00 AM EST (GitHub Actions triggers)
CHECK: Is any message scheduled for <= 9:00 AM on Sept 4?
FOUND: Yes! Post 1, Message 1 (scheduled for 9:00 AM)
ACTION: Post to LinkedIn & X
RESULT: Message posted
UPDATE: marked posted_to_linkedin=1, posted_to_x=1
```

### Sept 4, 11:00 AM - Second GitHub Actions Run
```
TIME: 11:00 AM EST (GitHub Actions triggers)
CHECK: Is any message scheduled for <= 11:00 AM on Sept 4?
FOUND: Yes! Post 2, Message 1 (scheduled for 11:00 AM)
ACTION: Post to LinkedIn & X
RESULT: Message posted
```

### Sept 4, 1:00 PM - Third GitHub Actions Run
```
TIME: 1:00 PM EST (GitHub Actions triggers)
CHECK: Is any message scheduled for <= 1:00 PM on Sept 4?
FOUND: Yes! Post 3, Message 1 (scheduled for 1:00 PM)
ACTION: Post to LinkedIn & X
RESULT: Message posted
```

### Sept 4, 3:00 PM - Fourth GitHub Actions Run
```
TIME: 3:00 PM EST (GitHub Actions triggers)
CHECK: Is any message scheduled for <= 3:00 PM?
FOUND: No messages scheduled for today
ACTION: Nothing to do
RESULT: Exit
```

## 🔍 The Key Check: Is It Time to Post?

**Code in `database.py` (lines 139-143):**
```python
scheduled_time = datetime.fromisoformat(row[4])

# Check if it's time to post
if not self.scheduler.is_time_to_post(scheduled_time):
    return None  # Not time yet
```

**Logic in `scheduler.py`:**
```python
def is_time_to_post(self, scheduled_time, current_time=None):
    if current_time is None:
        current_time = datetime.now(self.eastern)
    
    # Post if current time is past scheduled time
    return current_time >= scheduled_time
```

**What This Means:**
- Message scheduled for 9:00 AM will post when GitHub Actions runs at 9:00 AM or later
- If GitHub Actions runs at 9:05 AM, message scheduled for 9:00 AM will still post
- Once posted, it won't post again (flags prevent duplicates)

## 🎯 Why This Design?

### Advantages of "Check and Post" Model

✅ **Reliable**
- No complex job scheduling required
- Works with free GitHub Actions
- Database is source of truth

✅ **Flexible**
- Can run manually anytime
- Missed runs catch up automatically
- Easy to test locally

✅ **Fault Tolerant**
- If GitHub Actions fails, next run catches up
- Database artifact persists between runs
- No messages lost

✅ **Cost Effective**
- Uses GitHub's free tier (2,000 minutes/month)
- Each run takes ~1-2 minutes
- 4 runs/day × 22 business days = ~88 runs/month = ~176 minutes

### Trade-offs

⚠️ **Not Exact Timing**
- Posts within ~5 minutes of scheduled time
- GitHub Actions cron can have slight delays
- Close enough for social media

⚠️ **Requires GitHub Actions**
- If Actions disabled, nothing posts
- Need to monitor Actions tab occasionally
- Could miss posts if Actions fails repeatedly

## 🔧 How Components Work Together

### 1. Database (`database.py`)
```python
def get_next_message_to_post():
    # Returns message where scheduled_for <= NOW
    # Returns None if nothing is due yet
```

**Role:** Decides what's due based on schedule

### 2. Scheduler (`scheduler.py`)
```python
def is_time_to_post(scheduled_time):
    return current_time >= scheduled_time
```

**Role:** Checks if scheduled time has passed

### 3. Main Script (`main.py`)
```python
def post_daily_message():
    message = db.get_next_message_to_post()
    if message:
        # Post to LinkedIn
        # Post to X
    else:
        print("No messages due at this time")
```

**Role:** Orchestrates the posting

### 4. GitHub Actions (`.github/workflows/daily-post.yml`)
```yaml
on:
  schedule:
    - cron: '0 14 * 11-12,1-3 1-5'  # 9am EST
    - cron: '0 16 * 11-12,1-3 1-5'  # 11am EST
    - cron: '0 18 * 11-12,1-3 1-5'  # 1pm EST
    - cron: '0 20 * 11-12,1-3 1-5'  # 3pm EST
```

**Role:** Triggers the check 4 times daily

## 📊 State Management

### Database Artifact Storage

**Problem:** GitHub Actions is stateless (fresh VM each run)  
**Solution:** Store database as artifact between runs

**How it works:**
```yaml
# Download database at start
- uses: actions/download-artifact@v4
  with:
    name: posts-database

# Upload database at end
- uses: actions/upload-artifact@v4
  with:
    name: posts-database
    path: data/posts.db
```

**Result:** Database persists between runs

## 🧪 Testing

### Test Locally
```bash
# Set a message to post "now"
sqlite3 data/posts.db "
  UPDATE posted_messages 
  SET scheduled_for = datetime('now', '-1 hour') 
  WHERE id = 1
"

# Run posting
python main.py --post-daily

# Should post immediately!
```

### Test Schedule Without Posting
```bash
# View upcoming schedule
python main.py --status

# Shows next 5 messages with dates/times
```

### Manual GitHub Actions Trigger
```
1. Go to: https://github.com/Axon-Shield/daily-posting-from-blog/actions
2. Click "Social Media Posting (Scheduled)"
3. Click "Run workflow"
4. Manually triggers a check right now
```

## 🎯 Summary

**Schedule Creation:**
- ✅ Happens once when you fetch posts
- ✅ Stores `scheduled_for` timestamps in database
- ✅ No actual posting happens

**Post Execution:**
- ✅ GitHub Actions runs 4× daily on cron
- ✅ Checks if any messages are due
- ✅ Posts immediately if due
- ✅ Does nothing if not due yet

**Key Insight:** The schedule is a plan stored in the database. GitHub Actions periodically checks the plan and executes items that are due. It's like checking your calendar every few hours and doing whatever task is due.

---

**Think of it like:**
- 📅 **Phase 1 (Scheduling)**: Writing tasks on your calendar
- ⏰ **Phase 2 (Execution)**: Checking your calendar every few hours and doing tasks that are due

