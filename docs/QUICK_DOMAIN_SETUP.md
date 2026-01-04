# Quick Domain Setup for OAuth (5 Minutes)

## 🎯 Goal
Configure OAuth once, use everywhere (local, NAS, cloud) - **no more changing redirect URIs!**

---

## 🚀 Quick Setup (Choose One)

### Option 1: Free DuckDNS (Recommended - 2 minutes)

1. **Get free domain:**
   - Go to https://www.duckdns.org/
   - Sign up (free, no credit card)
   - Get: `yoursitename.duckdns.org` (e.g., `youtube-automation.duckdns.org`)

2. **Run setup script:**
   ```bash
   ./SETUP_DOMAIN_OAUTH.sh
   ```
   Enter your domain when prompted.

3. **Update Google Cloud Console:**
   - Use the URIs shown by the script
   - Copy-paste into Google OAuth Client settings

**Done!** Works locally now, works on NAS tomorrow (just point DNS to NAS IP).

---

### Option 2: Use Existing Domain (If You Have One)

1. **Use subdomain:**
   - `youtube-automation.yourdomain.com`
   - Or: `yt-auto.yourdomain.com`

2. **Run setup script:**
   ```bash
   ./SETUP_DOMAIN_OAUTH.sh
   ```
   Enter your subdomain.

3. **Update Google Cloud Console:**
   - Use the URIs shown by the script

4. **Point DNS:**
   - Local: Add to `/etc/hosts` (script does this)
   - NAS: Point A record to NAS IP

---

## 📋 What Gets Configured

### Google Cloud Console OAuth Client:
```
Authorized JavaScript origins:
  http://yourdomain.com
  https://yourdomain.com

Authorized redirect URIs:
  http://yourdomain.com/oauth2callback
  https://yourdomain.com/oauth2callback
```

### Local `/etc/hosts`:
```
127.0.0.1    yourdomain.com
```

### Result:
- **Locally:** Access `http://yourdomain.com:5001` → Works! (via hosts file)
- **On NAS:** Access `https://yourdomain.com` → Works! (via DNS)
- **Same OAuth config** → No changes needed when moving!

---

## 🔄 Migration Tomorrow (NAS)

**When deploying to NAS:**

1. **Point DNS to NAS:**
   - DuckDNS: Update via web/API to NAS IP
   - Real domain: Update A record to NAS IP

2. **Deploy code:**
   - Same code, same OAuth config
   - No changes needed!

3. **Access:**
   - `http://yourdomain.com:5001` or `https://yourdomain.com` (with HTTPS)

**That's it!** OAuth works immediately because the domain is already configured in Google Console.

---

## ✅ Benefits

- ✅ **One-time setup:** Configure OAuth once, use forever
- ✅ **No code changes:** App automatically uses domain from request
- ✅ **Works everywhere:** Local, NAS, cloud - same config
- ✅ **Future-proof:** Easy to migrate to new servers

---

## 🎯 Recommended: DuckDNS

**Why DuckDNS?**
- ✅ Free forever
- ✅ Easy setup (2 minutes)
- ✅ Works great for personal projects
- ✅ Can upgrade to real domain later (just update DNS)

**Setup:**
1. Sign up at https://www.duckdns.org/
2. Get `yoursitename.duckdns.org`
3. Run `./SETUP_DOMAIN_OAUTH.sh`
4. Done!

---

## 📚 Full Guide

See `OAUTH_LONG_TERM_SETUP.md` for detailed instructions including HTTPS setup.

