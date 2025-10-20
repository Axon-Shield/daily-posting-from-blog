# 🐙 GitHub Repository Setup

Your local git repository has been initialized and all files are committed. Now let's push to GitHub!

## Current Status

✅ Git repository initialized  
✅ All files committed locally  
✅ Main branch created  
⚠️  Need to authenticate with GitHub and create remote repository

## Option 1: Using GitHub CLI (Recommended)

### Step 1: Authenticate with GitHub CLI

```bash
gh auth login
```

Follow the prompts:
1. Choose "GitHub.com"
2. Choose "HTTPS" as your preferred protocol
3. Choose "Login with a web browser"
4. Copy the one-time code shown
5. Press Enter to open browser
6. Paste the code and authorize

### Step 2: Create and Push Repository

Once authenticated, run:

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog
gh repo create daily-posting-from-blog --public --source=. --remote=origin --push
```

Or for a private repository:

```bash
gh repo create daily-posting-from-blog --private --source=. --remote=origin --push
```

### Step 3: Configure Secrets (Automated)

Run the setup script:

```bash
./setup_github.sh
```

This will guide you through setting up all required API keys as GitHub secrets.

## Option 2: Manual Setup via GitHub Website

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `daily-posting-from-blog`
3. Description: "Automated blog post distribution to LinkedIn and X using AI"
4. Choose Public or Private
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Push Local Repository

GitHub will show you instructions. Run these commands:

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog
git remote add origin https://github.com/YOUR_USERNAME/daily-posting-from-blog.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 3: Configure Secrets Manually

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret one by one:

#### Required Secrets:

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `BLOG_RSS_FEED_URL` | Your blog's RSS feed URL | Your blog settings |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | https://console.anthropic.com/ |

#### Optional (LinkedIn):

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn OAuth token | See SETUP_GUIDE.md |
| `LINKEDIN_USER_ID` | Your LinkedIn user ID (numbers only) | LinkedIn API |

#### Optional (X/Twitter):

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `X_API_KEY` | X API Consumer Key | https://developer.twitter.com/ |
| `X_API_SECRET` | X API Consumer Secret | Twitter Developer Portal |
| `X_ACCESS_TOKEN` | X Access Token | Twitter Developer Portal |
| `X_ACCESS_TOKEN_SECRET` | X Access Token Secret | Twitter Developer Portal |
| `X_BEARER_TOKEN` | X Bearer Token | Twitter Developer Portal |

## Verify Setup

After creating the repository and configuring secrets:

### 1. Check Repository

Visit: `https://github.com/YOUR_USERNAME/daily-posting-from-blog`

You should see all your files there.

### 2. Enable GitHub Actions

1. Go to the **Actions** tab
2. If prompted, click "I understand my workflows, go ahead and enable them"
3. You should see two workflows:
   - "Daily Social Media Post"
   - "Fetch New Blog Posts"

### 3. Test Workflows

#### Test Fetch Workflow:

1. Click on "Fetch New Blog Posts" workflow
2. Click "Run workflow" dropdown (right side)
3. Click the green "Run workflow" button
4. Wait ~1-2 minutes
5. Check for green checkmark (success) or red X (error)
6. If error, click on the run to see logs

#### Test Daily Post Workflow:

1. First ensure you have posts (run fetch workflow first)
2. Click on "Daily Social Media Post" workflow
3. Click "Run workflow"
4. Wait for completion
5. Check your social media accounts!

## Next Steps

Once your repository is set up:

1. **Local Testing** (optional):
   ```bash
   # Create .env file
   cp env.example .env
   nano .env  # Add your API keys
   
   # Test the system
   python test_system.py
   
   # Fetch posts
   python main.py --fetch-posts
   
   # Test posting
   python main.py --post-daily
   ```

2. **Monitor Automation**:
   - Check Actions tab daily for any failures
   - Review posted content quality
   - Adjust schedules in `.github/workflows/*.yml` if needed

3. **Customize**:
   - Edit hashtags in `main.py`
   - Adjust AI prompts in `content_extractor.py`
   - Change posting schedule in workflow files

## Troubleshooting

### "gh auth login" fails

Try refreshing authentication:
```bash
gh auth logout
gh auth login
```

### "Permission denied" when pushing

Make sure you selected the correct protocol (HTTPS or SSH) during `gh auth login`.

For HTTPS:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/daily-posting-from-blog.git
```

For SSH:
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/daily-posting-from-blog.git
```

### GitHub Actions not running

1. Verify Actions are enabled (Settings → Actions → General → Allow all actions)
2. Check that secrets are configured correctly
3. Try manual workflow trigger first

### Secrets not working

1. Secret names must match exactly (case-sensitive)
2. No leading/trailing spaces in secret values
3. Re-enter secrets if unsure

## Getting API Keys

See `SETUP_GUIDE.md` for detailed instructions on obtaining:
- Anthropic API key
- LinkedIn API credentials
- X (Twitter) API credentials

## Success Checklist

- [ ] Repository created on GitHub
- [ ] Local code pushed to GitHub
- [ ] All required secrets configured
- [ ] GitHub Actions enabled
- [ ] Fetch workflow tested successfully
- [ ] Daily post workflow tested successfully
- [ ] First post appeared on social media!

---

**Ready to automate!** 🚀

Once everything is set up, the system will:
- Fetch new blog posts daily (11:30 AM UK time / 7:30 AM EST)
- Post daily messages (Daily 9 AM UTC)
- Track all posts in database
- Never duplicate posts

You can adjust these schedules in the workflow files.

