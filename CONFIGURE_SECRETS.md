# 🔐 Configure GitHub Secrets for Axon-Shield

Your repository is now live at:
**https://github.com/Axon-Shield/daily-posting-from-blog**

## Quick Setup Options

### Option 1: Automated Setup (Recommended)

Run the setup script which will configure all secrets:

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog
./setup_github.sh
```

### Option 2: Manual Setup via Web Interface

1. Go to: https://github.com/Axon-Shield/daily-posting-from-blog/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret below

### Option 3: Use GitHub CLI

```bash
# Required secrets
echo "your_blog_rss_url" | gh secret set BLOG_RSS_FEED_URL -R Axon-Shield/daily-posting-from-blog
echo "your_anthropic_key" | gh secret set ANTHROPIC_API_KEY -R Axon-Shield/daily-posting-from-blog

# Optional: LinkedIn
echo "your_linkedin_token" | gh secret set LINKEDIN_ACCESS_TOKEN -R Axon-Shield/daily-posting-from-blog
echo "your_linkedin_id" | gh secret set LINKEDIN_USER_ID -R Axon-Shield/daily-posting-from-blog

# Optional: X (Twitter)
echo "your_x_api_key" | gh secret set X_API_KEY -R Axon-Shield/daily-posting-from-blog
echo "your_x_api_secret" | gh secret set X_API_SECRET -R Axon-Shield/daily-posting-from-blog
echo "your_x_token" | gh secret set X_ACCESS_TOKEN -R Axon-Shield/daily-posting-from-blog
echo "your_x_token_secret" | gh secret set X_ACCESS_TOKEN_SECRET -R Axon-Shield/daily-posting-from-blog
echo "your_x_bearer" | gh secret set X_BEARER_TOKEN -R Axon-Shield/daily-posting-from-blog
```

## Required Secrets

| Secret Name | Description | Priority |
|------------|-------------|----------|
| `BLOG_RSS_FEED_URL` | Your blog's RSS feed URL | **Required** |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | **Required** |

## Optional Secrets (for posting)

### LinkedIn (Optional)
| Secret Name | Description |
|------------|-------------|
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn OAuth token |
| `LINKEDIN_USER_ID` | Your LinkedIn user ID (numbers only) |

### X/Twitter (Optional)
| Secret Name | Description |
|------------|-------------|
| `X_API_KEY` | X API Consumer Key |
| `X_API_SECRET` | X API Consumer Secret |
| `X_ACCESS_TOKEN` | X Access Token |
| `X_ACCESS_TOKEN_SECRET` | X Access Token Secret |
| `X_BEARER_TOKEN` | X Bearer Token |

## Where to Get API Keys

### Anthropic API
1. Visit: https://console.anthropic.com/
2. Create account or log in
3. Go to API Keys section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

### LinkedIn API
See `SETUP_GUIDE.md` for detailed instructions

### X (Twitter) API
See `SETUP_GUIDE.md` for detailed instructions

## Next Steps After Configuration

1. **Enable GitHub Actions**
   - Go to: https://github.com/Axon-Shield/daily-posting-from-blog/actions
   - Click "I understand my workflows, go ahead and enable them" if prompted

2. **Test the Fetch Workflow**
   - Go to Actions → "Fetch New Blog Posts"
   - Click "Run workflow"
   - Wait ~1-2 minutes
   - Check for green checkmark ✅

3. **Test the Posting Workflow**
   - Go to Actions → "Daily Social Media Post"
   - Click "Run workflow"
   - Check your social media accounts!

4. **Monitor**
   - Check Actions tab regularly
   - Review posted content
   - Adjust schedules in workflow files if needed

## Quick Commands

```bash
# View current secrets (names only, not values)
gh secret list -R Axon-Shield/daily-posting-from-blog

# Remove a secret
gh secret remove SECRET_NAME -R Axon-Shield/daily-posting-from-blog

# Update a secret
echo "new_value" | gh secret set SECRET_NAME -R Axon-Shield/daily-posting-from-blog
```

## Testing Locally Before GitHub Actions

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Create .env file
cp env.example .env
nano .env  # Add your API keys

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test connections
python main.py --test

# Fetch posts
python main.py --fetch-posts

# Test posting
python main.py --post-daily
```

---

**Repository**: https://github.com/Axon-Shield/daily-posting-from-blog
**Actions**: https://github.com/Axon-Shield/daily-posting-from-blog/actions
**Settings**: https://github.com/Axon-Shield/daily-posting-from-blog/settings/secrets/actions

