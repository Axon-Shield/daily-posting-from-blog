# 📅 Blog Post Date Filtering

## Overview

The system includes a **date cutoff filter** to prevent processing old blog posts. Only posts published **on or after** the configured minimum date will be fetched and processed.

---

## 🎯 Current Configuration

**Default Cutoff Date:** `2025-10-15` (October 15, 2025)

This means:
- ✅ Blog posts from October 15, 2025 onwards → **Processed**
- ❌ Blog posts before October 15, 2025 → **Skipped**

---

## 💡 Why This Exists

### Problem It Solves

When you first run the automation system, your RSS feed contains **all** your blog posts (potentially years of content). Without filtering:

- System would process hundreds of old posts ❌
- Would create thousands of outdated social media messages ❌
- Could consume excessive API credits ❌
- Would flood your schedule with irrelevant content ❌

### Solution

The date filter ensures you only process **recent** content that's relevant for social media promotion.

---

## 🔧 How It Works

### Code Implementation

**In `rss_parser.py`:**

```python
def _is_post_recent_enough(self, post: Dict) -> bool:
    """
    Check if a post is recent enough based on minimum date configuration.
    """
    try:
        # Parse post's published date
        published_date = datetime.fromisoformat(post.get('published_date', ''))
        
        # Get minimum date from config
        min_date = datetime.fromisoformat(Config.MINIMUM_POST_DATE)
        
        # Compare dates
        is_recent = published_date.date() >= min_date.date()
        
        if not is_recent:
            print(f"Skipping post '{post.get('title')}' - published {published_date.date()} (before {min_date.date()})")
        
        return is_recent
        
    except Exception as e:
        print(f"Error checking post date: {e}")
        # If date parsing fails, assume post is recent enough
        return True
```

### When It Runs

The date filter is applied during:
1. **Fetch Posts workflow** (daily at 11:30 AM UK time)
2. **Manual fetch** (`python main.py --fetch-posts`)

### What Happens to Skipped Posts

Posts older than the cutoff date are:
- Not extracted for messages
- Not saved to the database
- Not scheduled for posting
- Logged in console output

Example log:
```
Skipping post 'Old Article From 2024' - published 2024-05-10 (before 2025-10-15)
```

---

## 🛠️ Changing the Cutoff Date

### Option 1: Local Development (`.env` file)

Edit your `.env` file:
```bash
# Process posts from January 1, 2024 onwards
MINIMUM_POST_DATE=2024-01-01

# Process posts from start of 2025
MINIMUM_POST_DATE=2025-01-01

# Process posts from last 30 days (manual calculation)
MINIMUM_POST_DATE=2025-09-20
```

### Option 2: GitHub Actions (Production)

Set the GitHub Secret:
```bash
# Process all posts from 2024 onwards
gh secret set MINIMUM_POST_DATE --body '2024-01-01' \
  --repo Axon-Shield/daily-posting-from-blog

# Process only very recent posts (last 6 months)
gh secret set MINIMUM_POST_DATE --body '2025-04-01' \
  --repo Axon-Shield/daily-posting-from-blog
```

**Note:** The `fetch-posts.yml` workflow is already configured to use this secret with a fallback to `2025-10-15`.

### Option 3: Command Line Override

Set environment variable before running:
```bash
export MINIMUM_POST_DATE='2024-01-01'
python main.py --fetch-posts
```

---

## 📊 Use Cases

### 1. Initial Setup - Process Recent Posts Only

**Scenario:** You're setting up automation for the first time.

**Recommendation:**
```bash
# Only process posts from the last 3 months
MINIMUM_POST_DATE=2025-07-15
```

**Why:** Gives you a manageable number of posts to test with (~12 posts = 60 messages).

---

### 2. Backfill Historical Content

**Scenario:** You want to promote older evergreen content.

**Recommendation:**
```bash
# Process all posts from 2024
MINIMUM_POST_DATE=2024-01-01
```

**Why:** Allows system to extract messages from valuable older content.

**⚠️ Warning:** 
- Could create hundreds of messages
- May take weeks to post all content (max 4 posts/day)
- Will consume more API credits during extraction

---

### 3. Fresh Content Only

**Scenario:** Only want to promote brand new posts.

**Recommendation:**
```bash
# Only posts from last 30 days
MINIMUM_POST_DATE=2025-09-20  # (manually calculate 30 days ago)
```

**Why:** Ensures social media always reflects your latest thinking.

---

### 4. Relaunch or Rebrand

**Scenario:** You've relaunched your blog/brand and want to ignore old content.

**Recommendation:**
```bash
# Only posts after relaunch date
MINIMUM_POST_DATE=2025-10-01
```

**Why:** Prevents mixing old brand messaging with new positioning.

---

## 🔍 Checking What Will Be Processed

### Test Locally First

Before changing the production cutoff, test locally:

```bash
# Set desired cutoff date
export MINIMUM_POST_DATE='2024-01-01'

# Run fetch in dry-run mode (check console output)
python main.py --fetch-posts

# Check how many posts were saved
python main.py --status
```

### Expected Output

```
Fetching latest blog posts...
Found 20 posts in feed.

Processing: Recent Post Title (2025-10-18)
Extracting key messaging points...
Extracted 5 messages
Saved to database with ID: 1

Processing: Another Recent Post (2025-10-05)
Extracting key messaging points...
Extracted 5 messages
Saved to database with ID: 2

Skipping post 'Old Post' - published 2024-12-15 (before 2025-01-01)
Skipping post 'Older Post' - published 2024-08-10 (before 2025-01-01)

---
Processed 2 new posts (skipped 18 old posts)
```

---

## 🎯 Best Practices

### 1. **Set Before First Run**
Configure `MINIMUM_POST_DATE` before running `--fetch-posts` for the first time to avoid processing unwanted content.

### 2. **Be Conservative Initially**
Start with a recent date (e.g., last 3 months), then expand if needed.

### 3. **Consider Your Blog Cadence**
- **Weekly blogger:** Last 3-6 months gives ~12-24 posts
- **Daily blogger:** Last 1-2 months gives ~30-60 posts
- **Sporadic blogger:** Last 1-2 years to ensure good content volume

### 4. **Match to Social Goals**
- **Growth phase:** Use recent date to keep content fresh
- **Evergreen content:** Use older date to maximize material
- **Product launch:** Set to launch date to align messaging

### 5. **Update Periodically**
As time passes, you might want to advance the cutoff:
```bash
# Quarterly update
Q1 2025: MINIMUM_POST_DATE=2024-10-01
Q2 2025: MINIMUM_POST_DATE=2025-01-01
Q3 2025: MINIMUM_POST_DATE=2025-04-01
Q4 2025: MINIMUM_POST_DATE=2025-07-01
```

---

## ❓ FAQ

### Q: What if I don't set `MINIMUM_POST_DATE`?

**A:** Default is `2025-10-15`. System will process posts from mid-October 2025 onwards.

---

### Q: Can I disable date filtering entirely?

**A:** Yes, set a very old date:
```bash
MINIMUM_POST_DATE=2000-01-01
```

This effectively processes all posts in your feed (up to the `limit=5` newest posts per fetch run).

---

### Q: Does changing the date re-process old posts?

**A:** No. The database tracks processed posts by URL. Even if you change the cutoff date:
- ✅ Already processed posts → Skipped (prevented by database duplicate check)
- ✅ New posts within range → Processed
- ❌ Old posts outside range → Skipped (filtered before database check)

---

### Q: I want to process ONE specific old post, how?

**A:** Two options:

**Option 1 - Temporarily adjust date:**
```bash
export MINIMUM_POST_DATE='2024-01-01'  # Set before target post
python main.py --fetch-posts
```

**Option 2 - Add post directly via database:**
Not currently supported, but you could run a custom script to insert posts manually.

---

### Q: What date format is required?

**A:** ISO 8601 format: `YYYY-MM-DD`

Examples:
- ✅ `2025-10-15`
- ✅ `2024-01-01`
- ❌ `10/15/2025` (wrong format)
- ❌ `15-10-2025` (wrong format)
- ❌ `Oct 15, 2025` (wrong format)

---

### Q: Does this affect posting already-processed messages?

**A:** No. Date filtering only affects the **fetching** phase. Messages already in the database will still be posted according to their schedule, regardless of the `MINIMUM_POST_DATE` setting.

---

## 📈 Monitoring

### Check Filter Activity

View fetch logs in GitHub Actions:
1. Go to: `https://github.com/Axon-Shield/daily-posting-from-blog/actions`
2. Click on "Fetch New Blog Posts" workflow
3. View latest run logs
4. Look for "Skipping post" messages

### Local Monitoring

```bash
# See which posts are being skipped
python main.py --fetch-posts 2>&1 | grep "Skipping post"

# Count posts processed vs skipped
python main.py --status
```

---

## 🎯 Summary

**Current Setting:** `2025-10-15`

**To Change:**
- **Local:** Edit `.env` → `MINIMUM_POST_DATE=2024-01-01`
- **GitHub:** `gh secret set MINIMUM_POST_DATE --body '2024-01-01'`

**Best Practice:** Set conservatively (recent date) initially, expand if needed.

**Key Benefit:** Prevents flooding system with years of old blog content when first running automation.

---

**Last Updated:** October 20, 2025  
**Related Docs:** [SETUP_GUIDE.md](SETUP_GUIDE.md), [HOW_POSTING_WORKS.md](HOW_POSTING_WORKS.md)

