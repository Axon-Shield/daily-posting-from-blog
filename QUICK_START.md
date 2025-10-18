# ⚡ Quick Start Guide

**Get your blog automation running in 10 minutes!**

## 🎯 What You're Building

An automated system that:
1. Reads your weekly blog posts via RSS
2. Extracts 7 key messaging points using AI (Anthropic Claude)
3. Posts one message daily to LinkedIn and X (Twitter)
4. Runs automatically via GitHub Actions

## 📋 Before You Start

Prepare these items:

- [ ] Your blog's RSS feed URL (e.g., `https://yourblog.com/feed`)
- [ ] Anthropic API key ([Get it here](https://console.anthropic.com/))
- [ ] LinkedIn API credentials (optional - see SETUP_GUIDE.md)
- [ ] X (Twitter) API credentials (optional - see SETUP_GUIDE.md)

## 🚀 5-Step Setup

### Step 1: Authenticate with GitHub (2 minutes)

```bash
# Authenticate with GitHub CLI
gh auth login
```

Follow the browser prompts to authorize.

### Step 2: Create GitHub Repository (1 minute)

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Create public repository
gh repo create daily-posting-from-blog --public --source=. --remote=origin --push

# Or private:
# gh repo create daily-posting-from-blog --private --source=. --remote=origin --push
```

### Step 3: Configure API Keys (3 minutes)

#### Option A: Automated (Recommended)

```bash
./setup_github.sh
```

The script will prompt you for each API key.

#### Option B: Manual

Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:
- `BLOG_RSS_FEED_URL` - Your blog's RSS feed URL
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- (Optional) LinkedIn and X credentials (see SETUP_GUIDE.md)

### Step 4: Test the System (2 minutes)

```bash
# Go to your GitHub repository
# Click: Actions tab → "Fetch New Blog Posts" → "Run workflow"
# Wait ~1 minute, check for green checkmark
```

### Step 5: Verify First Post (2 minutes)

```bash
# In GitHub Actions tab:
# Click: "Daily Social Media Post" → "Run workflow"
# Check your LinkedIn/X accounts for the post!
```

## ✅ Success!

Your automation is now live! It will:
- **Weekly**: Fetch new posts (Mondays 8 AM UTC)
- **Daily**: Post messages (Daily 9 AM UTC)

## 🎛️ Customization

### Change Posting Time

Edit `.github/workflows/daily-post.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change to your preferred time (UTC)
```

### Change Hashtags

Edit `main.py`, find `enhance_for_platform()` calls:

```python
hashtags=['your', 'custom', 'tags']
```

### Change Messages Per Post

In GitHub Secrets, set:
- `POSTS_PER_BLOG` = `3` (for 3 messages per post instead of 5)

## 🐛 Quick Troubleshooting

**"No posts found"**
→ Verify your RSS feed URL in GitHub Secrets

**"API Error"**
→ Run `python test_system.py` locally to test credentials

**"Workflow not running"**
→ Check Settings → Actions → General → Enable Actions

## 📚 Full Documentation

- **README.md** - Complete system documentation
- **SETUP_GUIDE.md** - Detailed API setup instructions
- **GITHUB_SETUP.md** - GitHub repository setup details

## 💡 Local Testing (Optional)

Want to test locally first?

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Add your API keys

# Test
python test_system.py

# Fetch posts
python main.py --fetch-posts

# Post message
python main.py --post-daily
```

## 🎉 What's Next?

1. **Monitor**: Check Actions tab daily for the first week
2. **Review**: Look at posted messages - adjust prompts if needed
3. **Customize**: Update hashtags, posting times, or AI prompts
4. **Relax**: Let automation handle your social media!

---

**Need help?** Check the troubleshooting sections in README.md and SETUP_GUIDE.md

**Ready to launch?** Follow Step 1 above! 🚀

