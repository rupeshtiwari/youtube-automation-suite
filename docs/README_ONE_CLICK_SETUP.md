# 🚀 One-Click Setup Guide

## Complete Automated Setup for Mac → NAS Deployment

---

## 📋 Quick Start

### For Mac (Development):
```bash
./one_click_setup_mac.sh
```

**That's it!** This script:
- ✅ Adds DNS entry to `/etc/hosts` (prompts for password)
- ✅ Flushes DNS cache
- ✅ Builds React app
- ✅ Checks dependencies
- ✅ Shows all OAuth URLs
- ✅ Verifies everything

### For NAS (Production):
```bash
./one_click_deploy_nas.sh
```

**Then deploy:**
```bash
./deploy_to_nas.sh <NAS_IP> [username] [directory]
```

---

## 🎯 Complete Checklist

### ✅ Mac Setup (Run First)

1. **Run one-click setup:**
   ```bash
   ./one_click_setup_mac.sh
   ```

2. **Configure OAuth Providers:**
   - Copy OAuth URLs from script output
   - Add to Google Cloud Console
   - Add to LinkedIn Developer Portal
   - Add to Facebook Developers

3. **Start Flask server:**
   ```bash
   python3 run.py
   ```

4. **Access app:**
   - http://youtube-automation.local:5001

### ✅ NAS Deployment (After Mac Setup)

1. **Prepare deployment:**
   ```bash
   ./one_click_deploy_nas.sh
   ```
   - Enter NAS IP, username, directory when prompted

2. **Deploy to NAS:**
   ```bash
   ./deploy_to_nas.sh <NAS_IP>
   ```
   Or follow manual steps in `NAS_DEPLOYMENT_INSTRUCTIONS.md`

3. **Set up DNS Server on Synology:**
   - Install DNS Server package
   - Create `local` zone
   - Add A record: `youtube-automation` → NAS IP

4. **Run on NAS:**
   ```bash
   python3 run.py
   ```

5. **Access:**
   - http://youtube-automation.local:5001

---

## 📋 What Each Script Does

### `one_click_setup_mac.sh`
- ✅ DNS configuration (`/etc/hosts`)
- ✅ DNS cache flush
- ✅ Dependency checking
- ✅ React app build
- ✅ OAuth URLs display
- ✅ Complete verification

### `one_click_deploy_nas.sh`
- ✅ Creates deployment package
- ✅ Gathers NAS information
- ✅ Creates deployment instructions
- ✅ Creates automated deploy script

### `deploy_to_nas.sh`
- ✅ Transfers files to NAS
- ✅ Extracts on NAS
- ✅ Installs dependencies
- ✅ Ready to run

---

## 🔧 OAuth URLs (Same Everywhere)

**Google:**
- `http://youtube-automation.local/oauth2callback`

**LinkedIn:**
- `http://youtube-automation.local:5001/api/linkedin/oauth/callback`

**Facebook/Instagram:**
- `http://youtube-automation.local:5001/api/facebook/oauth/callback`

**Configure once, use everywhere!**

---

## 📚 Documentation Files

- `README_ONE_CLICK_SETUP.md` - This file (overview)
- `COMPLETE_OAUTH_SETUP.md` - Detailed OAuth guide
- `SETUP_SUMMARY.md` - What's configured
- `NAS_DEPLOYMENT_INSTRUCTIONS.md` - NAS deployment steps (auto-generated)
- `DS224_SYNOLOGY_DNS.md` - DNS Server setup details

---

## ✅ Verification

After Mac setup:
```bash
./verify_setup.sh
```

After NAS deployment:
- Test DNS: `nslookup youtube-automation.local`
- Test app: `http://youtube-automation.local:5001`
- Test OAuth: Try connecting platforms

---

## 🎯 Summary

1. **Mac:** Run `./one_click_setup_mac.sh` → Configure OAuth → Done!
2. **NAS:** Run `./one_click_deploy_nas.sh` → Deploy → Set up DNS → Done!

**Everything automated - just run the scripts!** 🚀

