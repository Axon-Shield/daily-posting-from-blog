#!/bin/bash

# Setup script for GitHub repository creation and configuration
# This script helps automate the initial GitHub setup

set -e

echo "================================================"
echo "Blog Post Automation - GitHub Setup"
echo "================================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    echo ""
    echo "On macOS: brew install gh"
    echo "On Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo ""
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "You need to authenticate with GitHub first."
    echo "Running: gh auth login"
    echo ""
    gh auth login
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository details
read -p "Enter repository name (default: daily-posting-from-blog): " REPO_NAME
REPO_NAME=${REPO_NAME:-daily-posting-from-blog}

read -p "Make repository public? (y/N): " IS_PUBLIC
if [[ $IS_PUBLIC =~ ^[Yy]$ ]]; then
    VISIBILITY="--public"
else
    VISIBILITY="--private"
fi

echo ""
echo "Creating repository: $REPO_NAME"
echo ""

# Create repository
gh repo create "$REPO_NAME" $VISIBILITY --source=. --remote=origin --push

echo ""
echo "✅ Repository created successfully!"
echo ""

# Configure secrets
echo "================================================"
echo "Configuring GitHub Secrets"
echo "================================================"
echo ""
echo "You'll need to provide the following API credentials."
echo "Press Enter to skip any credential you don't have yet."
echo ""

read -p "Blog RSS Feed URL: " BLOG_RSS_FEED_URL
if [ ! -z "$BLOG_RSS_FEED_URL" ]; then
    echo "$BLOG_RSS_FEED_URL" | gh secret set BLOG_RSS_FEED_URL
    echo "✅ Set BLOG_RSS_FEED_URL"
fi

read -p "Anthropic API Key: " ANTHROPIC_API_KEY
if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo "$ANTHROPIC_API_KEY" | gh secret set ANTHROPIC_API_KEY
    echo "✅ Set ANTHROPIC_API_KEY"
fi

echo ""
echo "--- LinkedIn Credentials (optional) ---"
read -p "LinkedIn Access Token: " LINKEDIN_ACCESS_TOKEN
if [ ! -z "$LINKEDIN_ACCESS_TOKEN" ]; then
    echo "$LINKEDIN_ACCESS_TOKEN" | gh secret set LINKEDIN_ACCESS_TOKEN
    echo "✅ Set LINKEDIN_ACCESS_TOKEN"
fi

read -p "LinkedIn User ID: " LINKEDIN_USER_ID
if [ ! -z "$LINKEDIN_USER_ID" ]; then
    echo "$LINKEDIN_USER_ID" | gh secret set LINKEDIN_USER_ID
    echo "✅ Set LINKEDIN_USER_ID"
fi

echo ""
echo "--- X (Twitter) Credentials (optional) ---"
read -p "X API Key: " X_API_KEY
if [ ! -z "$X_API_KEY" ]; then
    echo "$X_API_KEY" | gh secret set X_API_KEY
    echo "✅ Set X_API_KEY"
fi

read -p "X API Secret: " X_API_SECRET
if [ ! -z "$X_API_SECRET" ]; then
    echo "$X_API_SECRET" | gh secret set X_API_SECRET
    echo "✅ Set X_API_SECRET"
fi

read -p "X Access Token: " X_ACCESS_TOKEN
if [ ! -z "$X_ACCESS_TOKEN" ]; then
    echo "$X_ACCESS_TOKEN" | gh secret set X_ACCESS_TOKEN
    echo "✅ Set X_ACCESS_TOKEN"
fi

read -p "X Access Token Secret: " X_ACCESS_TOKEN_SECRET
if [ ! -z "$X_ACCESS_TOKEN_SECRET" ]; then
    echo "$X_ACCESS_TOKEN_SECRET" | gh secret set X_ACCESS_TOKEN_SECRET
    echo "✅ Set X_ACCESS_TOKEN_SECRET"
fi

read -p "X Bearer Token: " X_BEARER_TOKEN
if [ ! -z "$X_BEARER_TOKEN" ]; then
    echo "$X_BEARER_TOKEN" | gh secret set X_BEARER_TOKEN
    echo "✅ Set X_BEARER_TOKEN"
fi

echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Verify secrets in GitHub: Settings → Secrets and variables → Actions"
echo "2. Enable GitHub Actions (if not already enabled)"
echo "3. Test locally: python main.py --test"
echo "4. Fetch posts: python main.py --fetch-posts"
echo "5. Test posting: python main.py --post-daily"
echo "6. Go to Actions tab to manually trigger workflows"
echo ""
echo "Repository URL: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')"
echo ""

