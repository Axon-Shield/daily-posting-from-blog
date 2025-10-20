# ⚠️ GitHub Actions Restrictions & Limits

## Overview

This document outlines GitHub Actions usage limits that could affect your automated posting system and how to stay within them.

---

## 🔢 Usage Limits (Free Tier)

### Workflow Execution
| Limit | Free (Public Repos) | Free (Private Repos) |
|-------|---------------------|----------------------|
| **Job execution time** | 6 hours max per job | 6 hours max per job |
| **Workflow run time** | 35 days max | 35 days max |
| **API requests** | 1,000/hour per repository | 1,000/hour per repository |
| **Concurrent jobs** | 20 (Linux) | 5 (Linux) |
| **Workflow queue time** | 45 days | 45 days |

### Storage & Minutes
| Resource | Free (Public) | Free (Private) |
|----------|---------------|----------------|
| **Minutes/month** | Unlimited | 2,000 minutes |
| **Storage** | 500 MB | 500 MB |
| **Artifact retention** | Default 90 days (max) | Default 90 days (max) |

**Good News:** Since `Axon-Shield/daily-posting-from-blog` is a **public repository**, you get:
- ✅ **Unlimited free minutes**
- ✅ **500 MB storage** (plenty for your SQLite database)
- ✅ **20 concurrent jobs** (way more than needed)

---

## 📊 Current System Usage

### Daily Execution Schedule

**Fetch Posts (Daily):**
- Runs: 1x per day (11:30 AM UK time)
- Duration: ~30-60 seconds per run
- Cost: ~30 seconds/day = **~15 minutes/month**

**Post Messages (4x Daily):**
- Runs: 4x per day (9am, 11am, 1pm, 3pm EST), Mon-Fri only
- Duration: ~15-30 seconds per run
- Cost: 4 runs × 20 seconds × ~22 business days = **~30 minutes/month**

**Total Monthly Usage: ~45 minutes** (0.1% of free private repo limit, 0% of public repo limit)

### Storage Usage

**Database Artifact:**
- Size: ~50-100 KB for 100+ blog posts
- Retention: 90 days
- Total: < 1 MB (0.2% of 500 MB limit)

**Generated Images (Not Stored):**
- Temporary files only
- Deleted after upload to LinkedIn/X
- No GitHub storage used ✅

---

## 🚨 Potential Issues & Solutions

### 1. **Artifact Download Failures**

**Symptom:**
```
Error: Unable to download artifact(s): Artifact not found for name: posts-database
```

**Causes:**
- First-time run (no artifact exists yet)
- Artifact expired (90 days old)
- Workflow modified artifact name

**Solution:**
```yaml
- name: Download database from artifacts (if exists)
  uses: actions/download-artifact@v4
  with:
    name: posts-database
    path: data/
  continue-on-error: true  # ✅ Already configured
```

This is **expected behavior** on first run and handled gracefully with `continue-on-error: true`.

---

### 2. **Cron Schedule Precision**

**Limitation:** GitHub Actions scheduled workflows may run **up to 10 minutes late** during high load periods.

**Impact on Your System:**
- ✅ **Minimal** - The scheduler checks `scheduled_for` times dynamically
- ✅ **No duplicates** - Even if delayed, posts won't duplicate
- ⚠️ Posting times may shift by ~5-10 minutes (e.g., 9:05 AM instead of 9:00 AM)

**Workaround:** The system is designed to be time-tolerant. Messages scheduled for 9:00 AM will post whenever the workflow runs after 9:00 AM.

---

### 3. **API Rate Limits**

**GitHub API:** 1,000 requests/hour per repository

**Your Usage:**
- Fetch Posts: ~10 API calls/run = 10/day
- Post Messages: ~5 API calls/run = 20/day
- Total: ~30 GitHub API calls/day (3% of limit)

**External APIs:**
| Service | Rate Limit | Your Usage |
|---------|------------|------------|
| **Anthropic Claude** | Tier-dependent | 1-5 calls/day |
| **xAI Grok** | Tier-dependent | 1-5 images/day |
| **LinkedIn API** | 500 posts/day per app | 1-4 posts/day |
| **X (Twitter) API** | 300 posts/day (Free tier) | 1-4 posts/day |

**Risk: Very Low** - You're using <2% of all rate limits.

---

### 4. **Workflow Concurrency**

**Limitation:** Max 20 concurrent jobs (public repos)

**Your Usage:** Max 2 workflows running simultaneously
- Fetch Posts (daily)
- Post Messages (4x daily)

**Risk: None** - You're using <10% of concurrent job limit.

---

### 5. **Database Artifact Expiry**

**Risk:** If no workflows run for 90 days, the database artifact expires and is deleted.

**Impact:**
- All scheduling history lost
- Messages would need to be re-extracted from blog posts
- Duplicate prevention would reset

**Mitigation:**
1. System runs daily → artifact refreshed every day
2. If you pause for 90+ days, existing messages would be lost (but blog posts would be re-fetched on next run)

**Recommendation:** If pausing for >60 days, manually download `posts.db` from latest workflow run.

---

### 6. **Network & Timeout Issues**

**Symptom:** Workflows fail with timeout errors

**Causes:**
- Anthropic/xAI/LinkedIn/X API slow responses
- Network connectivity issues
- Image generation taking >60 seconds

**Current Timeouts:**
```python
# image_generator.py
response = requests.post(..., timeout=60)  # 60 seconds

# linkedin_poster.py, x_poster.py
# No explicit timeout (uses default ~10-30 seconds)
```

**Solution:** All API calls include `try/except` blocks with graceful degradation:
- Image generation fails → post without image
- LinkedIn fails → still post to X
- X fails → still post to LinkedIn

---

## 📈 Scaling Considerations

### If You Increase Posting Frequency

**Scenario:** 10 blog posts/week × 5 messages = 50 messages

**Current System:** 4 time slots/day × 5 days = 20 messages/week
- Would take 2.5 weeks to post all messages ✅

**To Post Faster:**
1. Increase `MAX_POSTS_PER_DAY` in `scheduler.py` (currently 4)
2. Add more cron schedules to `daily-post.yml` (e.g., 5pm, 7pm EST)
3. Still well within all GitHub Actions limits

---

## ✅ Recommendations

### Monitoring
1. **Check Actions Tab Weekly:**
   - Go to: `https://github.com/Axon-Shield/daily-posting-from-blog/actions`
   - Look for red ❌ failures
   - Review logs for warnings

2. **Set Up Notifications:**
   - Go to repository → Settings → Notifications
   - Enable email alerts for workflow failures

3. **Review Logs Monthly:**
   ```bash
   # View recent workflow runs
   gh run list --repo Axon-Shield/daily-posting-from-blog --limit 30
   
   # View specific run logs
   gh run view <run-id> --repo Axon-Shield/daily-posting-from-blog --log
   ```

### Best Practices
1. ✅ **Keep repo public** - Unlimited free minutes
2. ✅ **Monitor artifact size** - Currently <1 MB, plenty of headroom
3. ✅ **Test manually first** - Use workflow_dispatch before relying on cron
4. ✅ **Graceful degradation** - All failures are caught and logged, not fatal

---

## 🎯 Summary

**Current Status: ✅ Excellent**

Your system is **well within all GitHub Actions limits**:
- Using <1% of storage
- Using <5% of API calls
- Using ~45 minutes/month (unlimited on public repos)
- No risk of hitting rate limits

**Risk Level: 🟢 Low**

The only realistic concern is external API failures (Anthropic/xAI/LinkedIn/X), which are already handled with fallbacks and error logging.

**Recommended Actions:**
1. ✅ None required - system is optimally configured
2. 📊 Review Actions tab weekly for the first month
3. 🔔 Enable GitHub notifications for workflow failures
4. 📥 Manually download database backup monthly (optional)

---

**Last Updated:** October 20, 2025  
**System Version:** 1.0  
**Repository:** [Axon-Shield/daily-posting-from-blog](https://github.com/Axon-Shield/daily-posting-from-blog)

