# 🚀 Complete Setup Guide

This guide walks you through setting up the automated blog post distribution system from scratch.

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.11 or higher installed
- [ ] A blog with an RSS feed
- [ ] GitHub account
- [ ] GitHub CLI (`gh`) installed (optional, but recommended)

## 🔑 API Setup Instructions

### 1. Anthropic API (Required)

**Cost**: Pay-as-you-go (very affordable for this use case)

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Click "Create Key"
5. Name it "Blog Automation"
6. Copy the key and save it securely

**Estimated cost**: ~$0.01-0.05 per blog post processed

### 2. xAI Grok API (Optional but Recommended)

**Cost**: Pay-as-you-go ($0.07 per image)

The xAI Grok API generates professional AI images for your social media posts, making them much more engaging.

1. Go to [xAI API Portal](https://x.ai/api)
2. Sign up for API access
3. Once approved, navigate to API Keys
4. Create a new API key
5. Copy and save the key securely

**Estimated cost**: ~$0.35 per blog post (5 images × $0.07), about $1.50/month for 4 blog posts

**Why it's worth it**:
- Posts with images get 2-3x more engagement
- Professional, custom AI-generated visuals
- Automatically tailored to each message
- Extremely affordable for the value

**To disable**: Set `GENERATE_IMAGES=false` in your environment variables (not recommended)

### 3. LinkedIn API (Optional)

**Complexity**: Medium (requires app approval)

#### Step-by-Step:

1. **Create LinkedIn App**
   - Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
   - Click "Create App"
   - Fill in app details:
     - App name: "Blog Post Automation"
     - LinkedIn Page: Your company page or personal page
     - App logo: Any logo (square, min 300x300px)
   - Agree to terms and create

2. **Request Access to Products**
   - In your app dashboard, go to "Products" tab
   - Request access to:
     - "Share on LinkedIn"
     - "Sign In with LinkedIn using OpenID Connect"
   - Wait for approval (usually instant for Share on LinkedIn)

3. **Get Credentials**
   - Go to "Auth" tab
   - Copy your "Client ID" and "Client Secret"

4. **Generate Access Token**
   
   **Option A: Using OAuth Playground**
   - Go to [LinkedIn OAuth Test Console](https://www.linkedin.com/developers/tools/oauth)
   - Select scopes: `w_member_social`, `r_liteprofile`
   - Generate token

   **Option B: Manual OAuth Flow**
   ```bash
   # Step 1: Get authorization code
   # Open in browser:
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=w_member_social%20r_liteprofile
   
   # Step 2: Exchange code for token
   curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
     -d grant_type=authorization_code \
     -d code=YOUR_AUTH_CODE \
     -d redirect_uri=YOUR_REDIRECT_URI \
     -d client_id=YOUR_CLIENT_ID \
     -d client_secret=YOUR_CLIENT_SECRET
   ```

5. **Get Your User ID**
   ```bash
   curl -X GET https://api.linkedin.com/v2/userinfo \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```
   - Look for the `sub` field - that's your user ID
   - Remove the `urn:li:person:` prefix if present

**Note**: LinkedIn access tokens expire. For production use, implement token refresh or use a long-lived token.

### 4. X (Twitter) API (Optional)

**Complexity**: Medium (requires developer account approval)

#### Step-by-Step:

1. **Apply for Developer Account**
   - Go to [Twitter Developer Portal](https://developer.twitter.com/)
   - Click "Sign up for Free Account"
   - Fill out the application:
     - Use case: "Content distribution from blog"
     - Describe your automation intentions clearly
   - Wait for approval (can take 1-3 days)

2. **Create Project and App**
   - After approval, log into Developer Portal
   - Click "Create Project"
   - Name: "Blog Post Automation"
   - Use case: Select appropriate category
   - Project description: Describe your automation
   - Create App within the project
   - App name: "Blog Poster"

3. **Set Up Authentication**
   - In your app dashboard, go to "Keys and tokens"
   - Generate:
     - API Key and Secret (OAuth 1.0a)
     - Access Token and Secret
     - Bearer Token (OAuth 2.0)
   - **IMPORTANT**: Copy all credentials immediately - they won't be shown again!

4. **Configure App Permissions**
   - Go to "User authentication settings"
   - Set up OAuth 1.0a
   - App permissions: Read and Write
   - Type of App: Web App
   - Add callback URL (can be localhost for this use case)
   - Save changes

5. **Test Credentials**
   ```bash
   # Using curl to test
   curl -X POST "https://api.twitter.com/2/tweets" \
     -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text":"Test tweet"}'
   ```

**Required Credentials**:
- API Key (Consumer Key)
- API Secret (Consumer Secret)  
- Access Token
- Access Token Secret
- Bearer Token

## 🐙 GitHub Repository Setup

### Option 1: Using GitHub CLI (Recommended)

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Make setup script executable
chmod +x setup_github.sh

# Run the automated setup
./setup_github.sh
```

The script will:
- Create the GitHub repository
- Push your code
- Configure all secrets
- Guide you through the process

### Option 2: Manual Setup

#### A. Create Repository

1. Go to [GitHub](https://github.com/new)
2. Repository name: `daily-posting-from-blog`
3. Description: "Automated blog post distribution to social media"
4. Choose Public or Private
5. Do NOT initialize with README (we already have files)
6. Click "Create repository"

#### B. Push Code

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Initialize git (if not already done)
git init

# Add files
git add .
git commit -m "Initial commit: Blog post automation system"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/daily-posting-from-blog.git

# Push code
git branch -M main
git push -u origin main
```

#### C. Configure Secrets

1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret:

| Secret Name | Value | Required |
|------------|-------|----------|
| `BLOG_RSS_FEED_URL` | Your blog RSS feed URL | Yes |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |
| `XAI_API_KEY` | xAI Grok API key for images | Recommended |
| `GENERATE_IMAGES` | Set to `true` or `false` | Optional (default: true) |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn access token | For LinkedIn |
| `LINKEDIN_USER_ID` | LinkedIn user ID (numbers only) | For LinkedIn |
| `X_API_KEY` | X API key | For Twitter |
| `X_API_SECRET` | X API secret | For Twitter |
| `X_ACCESS_TOKEN` | X access token | For Twitter |
| `X_ACCESS_TOKEN_SECRET` | X access token secret | For Twitter |
| `X_BEARER_TOKEN` | X bearer token | For Twitter |

## 🧪 Local Testing

### 1. Set Up Local Environment

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Create .env File

Create a file named `.env` in the project root:

```bash
# Copy the example
cat > .env << 'EOF'
# Blog Configuration
BLOG_RSS_FEED_URL=https://yourblog.com/feed

# Anthropic API (for content extraction)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# xAI Grok API (for image generation - recommended)
XAI_API_KEY=xai-xxxxx
GENERATE_IMAGES=true

# LinkedIn API (optional)
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_ID=your_user_id

# X (Twitter) API (optional)
X_API_KEY=your_key
X_API_SECRET=your_secret
X_ACCESS_TOKEN=your_token
X_ACCESS_TOKEN_SECRET=your_secret
X_BEARER_TOKEN=your_bearer_token

# Database
DATABASE_PATH=./data/posts.db
POSTS_PER_BLOG=5
EOF

# Edit with your actual values
nano .env  # or vim, code, etc.
```

### 3. Test the System

```bash
# Test API connections
python main.py --test

# Expected output:
# ✓ RSS Feed working
# ✓ Anthropic API working
# ✓ LinkedIn credentials valid (if configured)
# ✓ X credentials valid (if configured)
```

### 4. Fetch Your First Post

```bash
# Fetch and process blog posts
python main.py --fetch-posts

# Check what was extracted
python main.py --status
```

### 5. Test Posting

```bash
# Post to social media (do a real post!)
python main.py --post-daily

# Check results
python main.py --status
```

## ⚙️ GitHub Actions Configuration

### 1. Enable GitHub Actions

1. Go to your repository
2. Click "Actions" tab
3. If prompted, enable Actions
4. You should see two workflows:
   - "Daily Social Media Post"
   - "Fetch New Blog Posts"

### 2. Test Workflows Manually

#### Test Fetch Workflow:

1. Go to Actions tab
2. Click "Fetch New Blog Posts"
3. Click "Run workflow" dropdown
4. Click green "Run workflow" button
5. Wait for completion (~1-2 minutes)
6. Check logs for any errors

#### Test Daily Post Workflow:

1. First, make sure you have posts in database (run fetch workflow)
2. Go to Actions tab
3. Click "Daily Social Media Post"
4. Click "Run workflow"
5. Wait for completion
6. Check your LinkedIn/X accounts for the post!

### 3. Customize Schedule

Edit `.github/workflows/daily-post.yml`:

```yaml
schedule:
  # Change from 9 AM UTC to your preferred time
  # Format: 'minute hour day month weekday'
  - cron: '0 9 * * *'  # 9 AM UTC daily
  
  # Examples:
  # - cron: '0 14 * * *'  # 2 PM UTC daily
  # - cron: '30 8 * * 1-5'  # 8:30 AM UTC, Monday-Friday
  # - cron: '0 */6 * * *'  # Every 6 hours
```

**Time Zone Conversion**:
- UTC to EST: UTC - 5 hours (- 4 during DST)
- UTC to PST: UTC - 8 hours (- 7 during DST)
- Use [crontab.guru](https://crontab.guru/) to build cron expressions

## 🎯 Production Checklist

Before going live with automation:

- [ ] All API credentials tested and working
- [ ] At least one blog post fetched and processed
- [ ] Test post successful on all platforms
- [ ] GitHub Actions workflows tested manually
- [ ] Reviewed extracted messages for quality
- [ ] Schedule configured for desired posting time
- [ ] Monitoring plan in place (check Actions tab daily)

## 🔍 Monitoring & Maintenance

### Daily Checks

```bash
# Quick status check
python main.py --status
```

Or check GitHub Actions:
1. Go to repository → Actions tab
2. Look for green checkmarks (success) or red X's (failure)
3. Click on any run to see detailed logs

### Weekly Maintenance

1. Review posted content quality
2. Check remaining message count
3. Verify new blog posts are being fetched
4. Monitor API usage/costs

### Monthly Maintenance

1. Rotate API keys (security best practice)
2. Review and update hashtags if needed
3. Adjust message extraction prompts if quality decreases
4. Check API rate limits and quotas

## 🆘 Troubleshooting

### "No posts found in RSS feed"

**Solutions**:
- Verify RSS URL is correct
- Test RSS feed in browser
- Check if feed is publicly accessible
- Try different RSS reader to validate format

### "Anthropic API error"

**Solutions**:
- Verify API key is correct
- Check account has credits
- Test with smaller content
- Check API status at status.anthropic.com

### "LinkedIn posting failed"

**Solutions**:
- Verify access token is still valid
- Check if app has required permissions
- Verify user ID format (numbers only)
- Generate new access token

### "X (Twitter) posting failed"

**Solutions**:
- Verify all 5 credentials are correct
- Check app permissions (Read and Write)
- Verify account is in good standing
- Check rate limits (500 tweets per day limit)

### GitHub Actions not running

**Solutions**:
- Verify Actions are enabled (Settings → Actions)
- Check all secrets are configured
- Manually trigger workflow to test
- Check workflow YAML syntax

## 💡 Tips & Best Practices

1. **Start Small**: Test with one platform first (e.g., just LinkedIn or X)
2. **Monitor Quality**: Review extracted messages before full automation
3. **Adjust Prompts**: Customize `content_extractor.py` prompts for your style
4. **Backup Database**: GitHub Actions automatically saves database as artifact
5. **Rate Limits**: Be aware of platform posting limits
6. **Content Review**: Periodically check that AI extractions are high quality

## 📚 Additional Resources

- [Anthropic API Docs](https://docs.anthropic.com/)
- [LinkedIn API Docs](https://learn.microsoft.com/en-us/linkedin/)
- [X API Docs](https://developer.twitter.com/en/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Cron Expression Guide](https://crontab.guru/)

## ✅ Success!

If you've completed this guide, you now have:
- ✅ A fully automated blog post distribution system
- ✅ AI-powered content extraction
- ✅ Daily social media posts to LinkedIn and X
- ✅ GitHub Actions automation
- ✅ Proper monitoring and maintenance plan

**Congratulations! Your automation is live! 🎉**

---

Need help? Review the troubleshooting section or check the GitHub Actions logs for detailed error messages.

