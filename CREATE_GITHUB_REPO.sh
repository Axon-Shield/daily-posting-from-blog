#!/bin/bash

# Quick script to create GitHub repository
# Run this after authenticating with GitHub CLI

set -e

echo "=========================================="
echo "Creating GitHub Repository"
echo "=========================================="
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not installed."
    echo "Install: https://cli.github.com/"
    echo ""
    echo "macOS: brew install gh"
    exit 1
fi

# Check auth
echo "Checking GitHub authentication..."
if ! gh auth status &> /dev/null; then
    echo "⚠️  Not authenticated with GitHub."
    echo "Authenticating now..."
    gh auth login
fi

echo "✅ Authenticated with GitHub"
echo ""

# Prompt for repo type
read -p "Make repository public? (y/N): " IS_PUBLIC
if [[ $IS_PUBLIC =~ ^[Yy]$ ]]; then
    VISIBILITY="--public"
    echo "→ Creating PUBLIC repository"
else
    VISIBILITY="--private"
    echo "→ Creating PRIVATE repository"
fi

echo ""
echo "Creating repository 'daily-posting-from-blog'..."

# Create and push
gh repo create daily-posting-from-blog $VISIBILITY --source=. --remote=origin --push

echo ""
echo "✅ Repository created and pushed!"
echo ""
echo "View at: $(gh repo view --json url -q .url)"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Configure API secrets (run ./setup_github.sh)"
echo "   OR manually in: Settings → Secrets → Actions"
echo ""
echo "2. Go to Actions tab and enable workflows"
echo ""
echo "3. Test by running 'Fetch New Blog Posts' workflow"
echo ""
echo "4. Test posting with 'Daily Social Media Post' workflow"
echo ""
echo "See QUICK_START.md for detailed instructions"
echo ""

