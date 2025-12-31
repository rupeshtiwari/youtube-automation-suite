#!/bin/bash

# Script to push YouTube Automation to GitHub
# Usage: ./push_to_github.sh YOUR_GITHUB_USERNAME

set -e

if [ -z "$1" ]; then
    echo "❌ Error: GitHub username required"
    echo "Usage: ./push_to_github.sh YOUR_GITHUB_USERNAME"
    echo ""
    echo "Or manually:"
    echo "1. Create private repo at https://github.com/new"
    echo "2. Then run: git remote add origin https://github.com/YOUR_USERNAME/youtube-automation.git"
    echo "3. Then run: git push -u origin main"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="youtube-automation"

echo "🚀 Setting up GitHub repository..."
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists"
    echo "Current remote: $(git remote get-url origin)"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    else
        echo "Keeping existing remote"
    fi
else
    echo "➕ Adding remote repository..."
    git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
fi

echo ""
echo "📋 Next steps:"
echo ""
echo "1. Create a PRIVATE repository on GitHub:"
echo "   👉 https://github.com/new"
echo ""
echo "   Repository name: ${REPO_NAME}"
echo "   Description: Automated YouTube content management and social media distribution"
echo "   Visibility: ⚠️  PRIVATE (important!)"
echo "   ⚠️  DO NOT initialize with README, .gitignore, or license"
echo ""
echo "2. Once created, press Enter to push your code..."
read -p "Press Enter when repository is created on GitHub..."

echo ""
echo "📤 Pushing to GitHub..."
git branch -M main

# Try to push
if git push -u origin main; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🔗 View your repository:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "🔒 Remember: Keep this repository PRIVATE to protect your API keys structure"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Repository doesn't exist yet (create it first)"
    echo "   - Authentication required (use GitHub token or SSH)"
    echo "   - Wrong repository name or username"
    echo ""
    echo "💡 Alternative: Use SSH instead:"
    echo "   git remote set-url origin git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
    echo "   git push -u origin main"
fi

