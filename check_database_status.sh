#!/bin/bash
# Script to check database status locally and optionally trigger GitHub workflow.

echo "🔍 Database Status Checker"
echo "========================="
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found"
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"
        echo ""
        echo "🚀 Triggering GitHub workflow to check database status..."
        gh workflow run database-status.yml
        
        echo ""
        echo "📋 To view the workflow run:"
        echo "gh run list --workflow=database-status.yml"
        echo ""
        echo "📋 To view the latest run:"
        echo "gh run view --log"
    else
        echo "❌ GitHub CLI not authenticated"
        echo "Run: gh auth login"
    fi
else
    echo "⚠️  GitHub CLI not found"
    echo "Install it from: https://cli.github.com/"
fi

echo ""
echo "🏠 Local Database Status:"
echo "========================"

# Check local database
if [ -f "data/posts.db" ]; then
    echo "✅ Local database exists"
    echo "📊 Database size: $(du -h data/posts.db | cut -f1)"
    echo ""
    
    # Show local status
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python main.py --status
    else
        echo "⚠️  Virtual environment not found"
        echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    fi
else
    echo "❌ Local database does not exist"
    echo "Run: python main.py --fetch-posts to create initial data"
fi
