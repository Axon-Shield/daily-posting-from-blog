# 📝 Automated Blog Post Distribution System

Automatically distribute key messaging points from your weekly blog posts to LinkedIn and X (Twitter) on a daily basis using AI-powered content extraction.

## 🌟 Features

- **RSS Feed Integration**: Automatically fetch new blog posts from your RSS feed
- **AI-Powered Content Extraction**: Use Anthropic's Claude to extract 7 key messaging points from each blog post
- **Multi-Platform Posting**: Automatically post to LinkedIn and X (Twitter)
- **Daily Automation**: GitHub Actions workflow posts one message per day
- **Smart Tracking**: SQLite database tracks posted messages to avoid duplicates
- **Platform Optimization**: Messages are tailored for each platform's format and character limits

## 📋 Requirements

- Python 3.11+
- Blog with RSS feed
- Anthropic API key
- LinkedIn API credentials
- X (Twitter) API credentials
- GitHub account (for automation)

## 🚀 Quick Start

### 1. Clone or Create Repository

```bash
# If starting fresh, navigate to the project directory
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Blog post automation system"
```

### 2. Create GitHub Repository

```bash
# Create a new repository on GitHub (using GitHub CLI)
gh repo create daily-posting-from-blog --public --source=. --remote=origin --push

# Or manually:
# 1. Go to https://github.com/new
# 2. Name: daily-posting-from-blog
# 3. Make it public or private
# 4. Don't initialize with README (we already have files)
# 5. Copy the repository URL and run:
git remote add origin https://github.com/YOUR_USERNAME/daily-posting-from-blog.git
git branch -M main
git push -u origin main
```

### 3. Set Up API Credentials

#### Anthropic API
1. Go to https://console.anthropic.com/
2. Create an API key
3. Copy the key for later use

#### LinkedIn API
1. Go to https://www.linkedin.com/developers/
2. Create a new app
3. Request access to the "Share on LinkedIn" and "Sign In with LinkedIn" products
4. Get your Access Token and User ID (URN format: numbers only)
5. Refer to: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication

#### X (Twitter) API
1. Go to https://developer.twitter.com/
2. Create a new project and app
3. Generate API keys and tokens (you need both OAuth 1.0a and OAuth 2.0)
4. Required credentials:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
   - Bearer Token

### 4. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

```
BLOG_RSS_FEED_URL          # Your blog's RSS feed URL
ANTHROPIC_API_KEY          # Your Anthropic API key
LINKEDIN_ACCESS_TOKEN      # LinkedIn access token
LINKEDIN_USER_ID           # LinkedIn user ID (numbers only)
X_API_KEY                  # X API key
X_API_SECRET               # X API secret
X_ACCESS_TOKEN             # X access token
X_ACCESS_TOKEN_SECRET      # X access token secret
X_BEARER_TOKEN             # X bearer token
```

### 5. Local Setup (Optional for Testing)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
BLOG_RSS_FEED_URL=https://yourblog.com/feed
ANTHROPIC_API_KEY=your_key_here
LINKEDIN_ACCESS_TOKEN=your_token_here
LINKEDIN_USER_ID=your_user_id_here
X_API_KEY=your_key_here
X_API_SECRET=your_secret_here
X_ACCESS_TOKEN=your_token_here
X_ACCESS_TOKEN_SECRET=your_secret_here
X_BEARER_TOKEN=your_bearer_token_here
DATABASE_PATH=./data/posts.db
POSTS_PER_WEEK=7
EOF

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

## 💻 Usage

### Local Testing

```bash
# Test API connections
python main.py --test

# Fetch and process new blog posts
python main.py --fetch-posts

# Post the next daily message
python main.py --post-daily

# Check status
python main.py --status
```

### Automated Execution (GitHub Actions)

The system includes two GitHub Actions workflows:

#### 1. **Daily Posting** (`.github/workflows/daily-post.yml`)
- Runs daily at 9:00 AM UTC
- Posts one message to LinkedIn and X
- Can be triggered manually from GitHub Actions tab

#### 2. **Weekly Post Fetching** (`.github/workflows/fetch-posts.yml`)
- Runs weekly on Mondays at 8:00 AM UTC
- Fetches new blog posts and extracts messages
- Can be triggered manually from GitHub Actions tab

### Manual Trigger

1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Select "Daily Social Media Post" or "Fetch New Blog Posts"
4. Click "Run workflow"

## 🏗️ Architecture

```
┌─────────────────┐
│   RSS Feed      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RSS Parser     │
│  (rss_parser.py)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Content Extract │
│ (Anthropic AI)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│  (SQLite)       │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│LinkedIn│ │   X    │
│ Poster │ │ Poster │
└────────┘ └────────┘
```

## 📁 Project Structure

```
daily-posting-from-blog/
├── .github/
│   └── workflows/
│       ├── daily-post.yml      # Daily posting workflow
│       └── fetch-posts.yml     # Weekly fetch workflow
├── config.py                   # Configuration management
├── database.py                 # SQLite database operations
├── rss_parser.py              # RSS feed parsing
├── content_extractor.py       # AI content extraction
├── linkedin_poster.py         # LinkedIn API integration
├── x_poster.py                # X (Twitter) API integration
├── main.py                    # Main orchestration script
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BLOG_RSS_FEED_URL` | Your blog's RSS feed URL | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn API token | For LinkedIn |
| `LINKEDIN_USER_ID` | LinkedIn user ID | For LinkedIn |
| `X_API_KEY` | X API key | For X/Twitter |
| `X_API_SECRET` | X API secret | For X/Twitter |
| `X_ACCESS_TOKEN` | X access token | For X/Twitter |
| `X_ACCESS_TOKEN_SECRET` | X access token secret | For X/Twitter |
| `X_BEARER_TOKEN` | X bearer token | For X/Twitter |
| `DATABASE_PATH` | Path to SQLite database | Optional |
| `POSTS_PER_WEEK` | Messages per post (default: 7) | Optional |

### Customizing Schedule

Edit the cron expressions in GitHub Actions workflows:

```yaml
# Daily posting at 9 AM UTC
- cron: '0 9 * * *'

# Change to 2 PM UTC:
- cron: '0 14 * * *'
```

Cron format: `minute hour day month weekday`

## 🐛 Troubleshooting

### API Issues

```bash
# Test API connections
python main.py --test
```

### Database Issues

```bash
# Delete and recreate database
rm -rf data/
python main.py --status
```

### GitHub Actions Not Running

1. Check that GitHub Actions are enabled (Settings → Actions → General)
2. Verify all secrets are configured correctly
3. Check workflow logs for errors

### No Posts Found

1. Verify RSS feed URL is correct
2. Check that RSS feed is publicly accessible
3. Test locally: `python main.py --fetch-posts`

## 📊 Monitoring

### View Status

```bash
python main.py --status
```

Output shows:
- Total messages in database
- Posted vs. pending messages
- API configuration status
- Next message to be posted

### GitHub Actions Logs

1. Go to repository → Actions tab
2. Click on a workflow run
3. View detailed logs for each step

## 🔐 Security Notes

- **Never commit `.env` file** - it's in `.gitignore`
- **Use GitHub Secrets** for all credentials in CI/CD
- **Rotate API keys** regularly
- **Use least-privilege access** for API tokens

## 🎯 Best Practices

1. **Test locally first** before deploying to GitHub Actions
2. **Start with manual triggers** to verify workflows
3. **Monitor API rate limits** (especially X/Twitter)
4. **Review extracted messages** before first automated post
5. **Backup database** regularly (GitHub Actions automatically stores as artifact)

## 📝 Customization Ideas

### Adjust Message Count
Change `POSTS_PER_WEEK` in `.env` or GitHub Secrets to extract more or fewer messages per post.

### Custom Hashtags
Edit `main.py` in the `post_daily_message()` method to customize hashtags:

```python
hashtags=['your', 'custom', 'tags']
```

### Different AI Model
Edit `content_extractor.py` to use a different Claude model:

```python
model="claude-3-5-sonnet-20241022"  # or another model
```

### Post to Additional Platforms
Create new poster modules following the pattern in `linkedin_poster.py` and `x_poster.py`.

## 📚 API Documentation

- [Anthropic API](https://docs.anthropic.com/)
- [LinkedIn API](https://learn.microsoft.com/en-us/linkedin/)
- [X (Twitter) API](https://developer.twitter.com/en/docs)

## 🤝 Contributing

Feel free to fork this project and customize it for your needs!

## 📄 License

MIT License - feel free to use this for your own blog automation!

## 🙋 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Test APIs locally with `--test` flag
4. Verify all credentials are correctly configured

## 🎉 Success Checklist

- [ ] Repository created on GitHub
- [ ] All secrets configured in GitHub
- [ ] Local testing successful (`python main.py --test`)
- [ ] First blog post fetched (`python main.py --fetch-posts`)
- [ ] Test post successful (`python main.py --post-daily`)
- [ ] GitHub Actions workflows enabled
- [ ] Manual workflow trigger successful
- [ ] Monitoring setup (check Actions tab daily)

---

**Happy Automated Posting! 🚀**

