# Long-Term OAuth Setup - Works Locally & NAS/Cloud

## 🎯 Goal
Configure OAuth redirect URIs once, use everywhere (local development, NAS, cloud) without changes.

---

## ✅ Recommended Solution: Domain + Local DNS Override

### Step 1: Get a Domain (Choose One)

**Option A: Free Dynamic DNS (Recommended for Testing)**
- **DuckDNS** (free): https://www.duckdns.org/
  - Get: `yoursitename.duckdns.org`
- **No-IP** (free tier): https://www.noip.com/
  - Get: `yoursitename.ddns.net`

**Option B: Purchase a Domain**
- Any registrar (Namecheap, Google Domains, etc.)
- Get: `yoursitename.com` or `youtube-automation.yoursitename.com`

**Example:** Let's use `youtube-automation.duckdns.org` for this guide

---

### Step 2: Configure Google Cloud Console OAuth

**Use domain-based URIs (works everywhere):**

**Authorized JavaScript origins:**
```
https://youtube-automation.duckdns.org
http://youtube-automation.duckdns.org
```

**Authorized redirect URIs:**
```
https://youtube-automation.duckdns.org/oauth2callback
http://youtube-automation.duckdns.org/oauth2callback
```

**Why both HTTP and HTTPS?**
- HTTP for local development (if not using SSL)
- HTTPS for production/NAS (with reverse proxy)

---

### Step 3: Local Development Setup (macOS/Linux)

**Edit `/etc/hosts` file:**
```bash
sudo nano /etc/hosts
```

Add this line:
```
127.0.0.1    youtube-automation.duckdns.org
```

**Result:**
- When you access `youtube-automation.duckdns.org` locally, it points to `localhost`
- OAuth redirect works with the same domain
- No code changes needed!

---

### Step 4: NAS Deployment Setup

**If using DuckDNS (or similar):**
1. Install DuckDNS client on your NAS (or configure router)
2. Point `youtube-automation.duckdns.org` → Your NAS IP
3. Set up port forwarding (if needed): `NAS_IP:5001`

**If using purchased domain:**
1. Point DNS A record: `youtube-automation.yoursitename.com` → Your NAS IP
2. Or use Cloudflare (free) for DNS management

---

### Step 5: Update Flask App to Use Domain

The app will automatically use the domain from the request hostname. No code changes needed!

But if you want to force a specific domain, you can set:
```bash
export OAUTH_REDIRECT_BASE="https://youtube-automation.duckdns.org"
```

---

## 🔧 Alternative: Environment-Based Configuration

If you prefer different domains for dev/prod, update `app/main.py`:

```python
import os

# Get OAuth redirect base from environment, or detect from request
OAUTH_REDIRECT_BASE = os.getenv('OAUTH_REDIRECT_BASE')
if not OAUTH_REDIRECT_BASE:
    # Auto-detect from request (fallback)
    OAUTH_REDIRECT_BASE = request.host_url.rstrip('/')
```

Then use this in OAuth flow configuration.

---

## 📋 Quick Setup Checklist

### For Local Development:
- [ ] Get domain (DuckDNS or purchase)
- [ ] Configure Google OAuth with domain-based URIs
- [ ] Add domain to `/etc/hosts` → `127.0.0.1`
- [ ] Run app: `python3 run.py`
- [ ] Access: `http://youtube-automation.duckdns.org:5001`

### For NAS:
- [ ] Point domain to NAS IP (DuckDNS client or DNS A record)
- [ ] Set up port forwarding (if needed)
- [ ] Deploy app to NAS
- [ ] Access: `https://youtube-automation.duckdns.org` (with HTTPS via reverse proxy)

---

## 🌐 Recommended Setup with HTTPS (Production)

For production, use HTTPS. Options:

**Option 1: Cloudflare (Free)**
- Point domain to Cloudflare
- Enable SSL/TLS (Full or Full Strict)
- Cloudflare handles HTTPS → Your NAS (HTTP internally)

**Option 2: Let's Encrypt on NAS**
- Install Certbot on NAS
- Auto-renew SSL certificates
- Nginx/Caddy reverse proxy handles HTTPS

**Option 3: Reverse Proxy (Nginx/Caddy)**
- Run on NAS
- Handles SSL termination
- Forwards to Flask app on port 5001

---

## 🔄 Migration Path

1. **Today (Local):**
   - Use domain + `/etc/hosts` override
   - OAuth configured with domain URIs
   - Test locally

2. **Tomorrow (NAS):**
   - Point domain to NAS IP
   - Deploy same code (no OAuth changes!)
   - Works immediately

3. **Future (Cloud):**
   - Point domain to cloud server IP
   - Deploy same code
   - Still works!

---

## 🎯 Why This Works

- **Same OAuth Config Everywhere:** Domain-based URIs work locally (via hosts file) and on NAS/cloud (via DNS)
- **No Code Changes:** App uses request hostname automatically
- **Easy Migration:** Just point DNS, deploy code - done!
- **Future-Proof:** Works with any deployment target

---

## 💡 Pro Tips

1. **Use DuckDNS for Testing:** Free, easy, works great for development and small deployments

2. **Upgrade to Real Domain Later:** When ready, just update DNS records and OAuth config (or keep both!)

3. **HTTPS Eventually:** Start with HTTP for testing, add HTTPS when deploying to NAS (via reverse proxy)

4. **Multiple Environments:** Can add multiple redirect URIs in Google Console (dev, staging, prod domains)

---

## 📝 Example Configuration

**Google Cloud Console OAuth Client:**
```
Authorized JavaScript origins:
  http://youtube-automation.duckdns.org
  https://youtube-automation.duckdns.org

Authorized redirect URIs:
  http://youtube-automation.duckdns.org/oauth2callback
  https://youtube-automation.duckdns.org/oauth2callback
```

**Local `/etc/hosts`:**
```
127.0.0.1    youtube-automation.duckdns.org
```

**NAS DuckDNS Client:**
```
youtube-automation.duckdns.org → YOUR_NAS_IP
```

**Result:** Same OAuth config, works everywhere! 🎉

