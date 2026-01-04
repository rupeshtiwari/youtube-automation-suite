# OAuth Migration: Mac → Synology DS224

## ✅ Short Answer: NO CHANGES NEEDED!

**Domain:** `youtube-automation.local` (SAME everywhere)  
**Redirect URL:** `http://youtube-automation.local/oauth2callback` (SAME everywhere)  
**OAuth Config:** Configure ONCE, use FOREVER

---

## 🎯 How It Works

### Mac (Development - Now)
- **Domain:** `youtube-automation.local`
- **Resolves to:** `127.0.0.1` (via `/etc/hosts`)
- **Access:** `http://youtube-automation.local:5001`
- **OAuth Redirect:** `http://youtube-automation.local/oauth2callback`

### Synology DS224 (Production - Tomorrow)
- **Domain:** `youtube-automation.local` ← **SAME!**
- **Resolves to:** NAS IP (e.g., `192.168.1.100`) via DNS Server
- **Access:** `http://youtube-automation.local:5001` ← **SAME!**
- **OAuth Redirect:** `http://youtube-automation.local/oauth2callback` ← **SAME!**

---

## 📋 What Changes vs What Stays the Same

### ✅ STAYS THE SAME:
- Domain name: `youtube-automation.local`
- OAuth redirect URL: `http://youtube-automation.local/oauth2callback`
- Google OAuth Console configuration
- Application code
- Port: `5001`

### 🔄 WHAT CHANGES:
- **Only DNS resolution:**
  - Mac: `/etc/hosts` → `127.0.0.1`
  - Synology: DNS Server → NAS IP
- **Physical location:** Mac → NAS (but domain stays same!)

---

## 🚀 Migration Steps

### Step 1: Mac Setup (Today)
1. Run: `./setup_local_dns_mac.sh`
2. Configure Google OAuth with:
   - **Redirect URI:** `http://youtube-automation.local/oauth2callback`
3. Test locally: `http://youtube-automation.local:5001`

### Step 2: Synology Setup (Tomorrow)
1. Install DNS Server on DS224
2. Create `local` zone
3. Add A record: `youtube-automation` → NAS IP
4. Deploy same code (no OAuth changes!)
5. Access: `http://youtube-automation.local:5001`

**That's it!** OAuth works immediately because domain is the same.

---

## ❓ FAQ

### Q: Do I need to change the domain when moving to Synology?
**A: NO!** Keep `youtube-automation.local` everywhere.

### Q: Do I need to change the redirect URL in Google OAuth?
**A: NO!** Use `http://youtube-automation.local/oauth2callback` everywhere.

### Q: Do I need to update OAuth settings when deploying to NAS?
**A: NO!** Same OAuth config works on Mac and NAS.

### Q: What if I want a different domain on NAS?
**A: You can, but you'd need to:**
- Update Google OAuth Console (add new redirect URIs)
- Update DNS on NAS
- More work, not recommended

**Better:** Use same domain everywhere (easier, simpler).

---

## ✅ Summary

| Item | Mac | Synology | Change? |
|------|-----|----------|---------|
| Domain | `youtube-automation.local` | `youtube-automation.local` | ❌ NO |
| Redirect URI | `http://youtube-automation.local/oauth2callback` | `http://youtube-automation.local/oauth2callback` | ❌ NO |
| OAuth Config | Configure once | Same config | ❌ NO |
| DNS Resolution | `/etc/hosts` → `127.0.0.1` | DNS Server → NAS IP | ✅ YES (automatic) |

**Result:** Configure OAuth once, use everywhere. No changes needed! 🎉

