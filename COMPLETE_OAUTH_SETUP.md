# Complete OAuth Setup Guide - All Platforms

## 🌐 Domain Configuration

**Domain:** `youtube-automation.local`  
**Base URL:** `http://youtube-automation.local:5001`  
**HTTPS (Production):** `https://youtube-automation.local` (when using reverse proxy)

---

## 📋 All OAuth Redirect URLs

### 1. Google OAuth (YouTube Data API & Analytics API)

**Platform:** Google Cloud Console  
**OAuth Client Type:** Web application

#### Authorized JavaScript origins:
```
http://youtube-automation.local
http://youtube-automation.local:5001
https://youtube-automation.local
```

#### Authorized redirect URIs:
```
http://youtube-automation.local/oauth2callback
http://youtube-automation.local:5001/oauth2callback
https://youtube-automation.local/oauth2callback
```

**Note:** Google uses `InstalledAppFlow` which automatically uses `/oauth2callback` path.

---

### 2. LinkedIn OAuth

**Platform:** LinkedIn Developer Portal  
**App Type:** Web application

#### Authorized redirect URLs:
```
http://youtube-automation.local:5001/api/linkedin/oauth/callback
https://youtube-automation.local/api/linkedin/oauth/callback
```

**Full callback URL:** `http://youtube-automation.local:5001/api/linkedin/oauth/callback`

**Required Scopes:**
- `openid`
- `profile`
- `email`
- `w_member_social` (requires Marketing Developer Platform product)

**Note:** Make sure Marketing Developer Platform is enabled in LinkedIn app settings.

---

### 3. Facebook OAuth

**Platform:** Facebook Developers  
**App Type:** Web

#### Valid OAuth Redirect URIs:
```
http://youtube-automation.local:5001/api/facebook/oauth/callback
https://youtube-automation.local/api/facebook/oauth/callback
```

**Full callback URL:** `http://youtube-automation.local:5001/api/facebook/oauth/callback`

**Required Permissions:**
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`
- `instagram_basic`
- `instagram_content_publish`
- `business_management`

---

### 4. Instagram OAuth

**Platform:** Facebook Developers (same app as Facebook)  
**Note:** Instagram uses Facebook OAuth flow

#### Valid OAuth Redirect URIs:
```
http://youtube-automation.local:5001/api/facebook/oauth/callback
https://youtube-automation.local/api/facebook/oauth/callback
```

**Same as Facebook** - Instagram uses Facebook's OAuth callback.

---

## 🔧 Local DNS Setup (Mac)

**Status:** ✅ Configured

**Hosts file entry:**
```
127.0.0.1    youtube-automation.local
```

**Verify:**
```bash
ping youtube-automation.local
# Should ping 127.0.0.1
```

**Access app:**
- `http://youtube-automation.local:5001`

---

## 🗄️ Synology DS224 Setup (Future)

**DNS Server Configuration:**
- Zone: `local`
- A Record: `youtube-automation` → NAS IP (e.g., `192.168.1.100`)

**Result:** `youtube-automation.local` resolves to NAS IP

**No OAuth changes needed** - same redirect URLs work!

---

## 📝 Quick Reference Table

| Platform | Redirect URI | Status |
|----------|--------------|--------|
| **Google** | `http://youtube-automation.local/oauth2callback` | ✅ Ready |
| **LinkedIn** | `http://youtube-automation.local:5001/api/linkedin/oauth/callback` | ✅ Ready |
| **Facebook** | `http://youtube-automation.local:5001/api/facebook/oauth/callback` | ✅ Ready |
| **Instagram** | `http://youtube-automation.local:5001/api/facebook/oauth/callback` | ✅ Ready |

---

## ✅ Setup Checklist

### Google OAuth:
- [ ] Create OAuth Client ID in Google Cloud Console
- [ ] Application type: **Web application**
- [ ] Add JavaScript origins (see above)
- [ ] Add redirect URIs (see above)
- [ ] Download `client_secret.json`
- [ ] Place in project root
- [ ] Enable APIs: YouTube Data API v3, YouTube Analytics API

### LinkedIn OAuth:
- [ ] Create app in LinkedIn Developer Portal
- [ ] Add redirect URL: `http://youtube-automation.local:5001/api/linkedin/oauth/callback`
- [ ] Enable Marketing Developer Platform product
- [ ] Add required scopes
- [ ] Save Client ID and Secret in app config

### Facebook/Instagram OAuth:
- [ ] Create app in Facebook Developers
- [ ] Add redirect URI: `http://youtube-automation.local:5001/api/facebook/oauth/callback`
- [ ] Add required permissions
- [ ] ] Save App ID and Secret in app config

### Local DNS:
- [x] ✅ Added to `/etc/hosts`: `127.0.0.1 youtube-automation.local`
- [ ] Test: `ping youtube-automation.local`

---

## 🚀 Testing OAuth Flows

### Google:
1. Access app: `http://youtube-automation.local:5001`
2. First YouTube API call will trigger OAuth
3. Browser opens for authorization
4. Token saved to `token.json`

### LinkedIn:
1. Go to Settings page
2. Click "Connect LinkedIn"
3. Authorize in browser
4. Token and Person URN saved automatically

### Facebook:
1. Go to Settings page
2. Click "Connect Facebook"
3. Authorize in browser
4. Page Access Token and Page ID saved automatically

---

## 📚 Related Documentation

- `LOCAL_DNS_SETUP.md` - Local DNS overview
- `DS224_SYNOLOGY_DNS.md` - Synology NAS setup
- `OAUTH_MIGRATION_GUIDE.md` - Migration from Mac to NAS
- `GOOGLE_OAUTH_CONFIG.md` - Google OAuth details
- `GET_LINKEDIN_TOKEN.md` - LinkedIn setup guide
- `GET_FACEBOOK_TOKEN.md` - Facebook setup guide

---

## 🔄 Migration to Synology

**When moving to DS224 NAS:**

1. **Set up DNS Server** (see `DS224_SYNOLOGY_DNS.md`)
2. **Point domain to NAS IP** (DNS Server A record)
3. **Deploy code** (same OAuth config!)
4. **Access:** `http://youtube-automation.local:5001`

**No OAuth changes needed** - same redirect URLs work everywhere!

---

## ⚠️ Important Notes

1. **Domain Consistency:** Use `youtube-automation.local` everywhere
2. **Port 5001:** Default Flask port (changeable via `PORT` env var)
3. **HTTPS:** Add HTTPS URLs when using reverse proxy (Nginx/Caddy)
4. **Local Development:** Works via `/etc/hosts` on Mac
5. **Production:** Works via DNS Server on Synology

---

## 🎯 Summary

- **Domain:** `youtube-automation.local` (same everywhere)
- **OAuth URLs:** Configure once, use everywhere
- **Local:** `/etc/hosts` → `127.0.0.1`
- **NAS:** DNS Server → NAS IP
- **No changes needed** when migrating!

