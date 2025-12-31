# GitHub Repository Setup Guide

## 🚀 Quick Setup

### Option 1: Using GitHub Web Interface (Easiest)

1. **Create the repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `youtube-automation` (or your preferred name)
   - Description: "Automated YouTube content management and social media distribution"
   - Select **Private** repository
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Push your code:**
   ```bash
   # Add the remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/youtube-automation.git
   
   # Or if using SSH:
   git remote add origin git@github.com:YOUR_USERNAME/youtube-automation.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

### Option 2: Using GitHub CLI (if installed)

```bash
# Install GitHub CLI first (if not installed):
# macOS: brew install gh
# Then authenticate: gh auth login

# Create private repository and push
gh repo create youtube-automation --private --source=. --remote=origin --push
```

### Option 3: Manual Setup

```bash
# 1. Create repository on GitHub (via web interface)
# 2. Then run:
git remote add origin https://github.com/YOUR_USERNAME/youtube-automation.git
git branch -M main
git push -u origin main
```

## ✅ Verify Setup

After pushing, verify everything is on GitHub:
- Go to your repository: `https://github.com/YOUR_USERNAME/youtube-automation`
- Check that all files are present
- Verify sensitive files are NOT there (client_secret.json, .env, etc.)

## 🔒 Security Checklist

Before pushing, ensure these files are in `.gitignore`:
- ✅ `client_secret.json` - Google OAuth credentials
- ✅ `token.json` - OAuth token cache
- ✅ `.env` - Environment variables with API keys
- ✅ `automation_settings.json` - Web app settings with API keys
- ✅ `*.db` - Database files
- ✅ `*.xlsx` - Excel exports (optional)

## 📝 Future Updates

After making changes:

```bash
# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push
```

## 🔄 Pull Latest Changes

If working on multiple machines:

```bash
git pull origin main
```

## 🌿 Branching (Optional)

For feature development:

```bash
# Create feature branch
git checkout -b feature-name

# Make changes, commit
git add .
git commit -m "Feature description"

# Push branch
git push -u origin feature-name

# Create pull request on GitHub, then merge to main
```

## 📊 Repository Structure

Your repository should include:
- ✅ All Python scripts
- ✅ Web application (app.py, templates/)
- ✅ Database module
- ✅ Documentation (README.md, guides)
- ✅ Requirements.txt
- ✅ .gitignore (protecting sensitive files)

## 🚫 What's NOT in Repository

These files are excluded (in .gitignore):
- ❌ API keys and credentials
- ❌ Database files
- ❌ Excel exports
- ❌ Virtual environment
- ❌ IDE settings

## 💡 Tips

1. **Regular Commits**: Commit often with descriptive messages
2. **Private Repo**: Keep it private to protect your API keys structure
3. **Backup**: GitHub serves as a backup of your code
4. **Version Control**: Track all changes and rollback if needed
5. **Collaboration**: Can add collaborators later if needed

## 🔐 If You Accidentally Committed Secrets

If you accidentally committed sensitive files:

```bash
# Remove from git history (use with caution!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch client_secret.json" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (this rewrites history!)
git push origin --force --all

# Then rotate your API keys immediately!
```

**Better approach**: Use `git-secrets` or `git-hooks` to prevent committing secrets in the first place.

