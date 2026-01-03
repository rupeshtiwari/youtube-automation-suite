# Local DNS Setup for Mac → DS224 NAS

## 🎯 Goal
Use `.local` domain that works on Mac (development) and DS224 NAS (production) - **no cloud, all local!**

---

## ✅ Solution: `.local` Domain + Hosts File / Local DNS

### Step 1: Choose Your Local Domain

Pick a name like:
- `youtube-automation.local`
- `yt-auto.local`
- `youtube-scheduler.local`

**Example:** We'll use `youtube-automation.local`

---

## 🖥️ Mac Setup (Development - Now)

### Add to `/etc/hosts` file:

```bash
sudo nano /etc/hosts
```

Add this line:
```
127.0.0.1    youtube-automation.local
```

**Save and exit** (Ctrl+X, then Y, then Enter)

**Test:**
```bash
ping youtube-automation.local
# Should ping 127.0.0.1
```

**Access your app:**
- `http://youtube-automation.local:5001`

---

## 🗄️ DS224 NAS Setup (Production - Tomorrow)

### Option A: Synology DNS Server (Recommended)

1. **Install DNS Server Package:**
   - Open Synology Package Center
   - Search "DNS Server"
   - Install it

2. **Configure DNS Zone:**
   - Open DNS Server
   - Go to "Zones" tab
   - Click "Create" → "Master zone"
   - **Zone name:** `local`
   - **Master DNS server:** Leave default or set to NAS IP
   - Click "Next" → "Next" → "Apply"

3. **Add A Record:**
   - Select the `local` zone
   - Click "Create" → "A Record"
   - **Hostname:** `youtube-automation`
   - **IPv4 Address:** Your NAS IP (e.g., `192.168.1.100`)
   - Click "OK"

4. **Configure Router (Optional but Recommended):**
   - Set router's DNS to use NAS as primary DNS
   - Or configure devices to use NAS IP as DNS server
   - This makes `youtube-automation.local` resolve for all devices on network

### Option B: Simple Hosts File on NAS (If DNS Server Not Available)

If you can't install DNS Server, you can:
1. SSH into DS224
2. Edit `/etc/hosts` (if you have root access)
3. Add: `NAS_IP    youtube-automation.local`

But DNS Server is better for network-wide resolution.

---

## 🔧 Google OAuth Configuration

**Use `.local` domain in Google Cloud Console:**

**Authorized JavaScript origins:**
```
http://youtube-automation.local
http://youtube-automation.local:5001
```

**Authorized redirect URIs:**
```
http://youtube-automation.local/oauth2callback
http://youtube-automation.local:5001/oauth2callback
```

**Note:** Google OAuth works with `.local` domains for local development!

---

## 📋 Quick Setup Script for Mac

Run this to set up Mac automatically:

```bash
./setup_local_dns_mac.sh
```

---

## 🔄 Migration: Mac → DS224

**Today (Mac):**
1. Add to `/etc/hosts`: `127.0.0.1 youtube-automation.local`
2. Configure OAuth with `.local` domain
3. Develop: `http://youtube-automation.local:5001`

**Tomorrow (DS224):**
1. Set up DNS Server on NAS (or hosts file)
2. Point `youtube-automation.local` → NAS IP
3. Deploy same code (no OAuth changes!)
4. Access: `http://youtube-automation.local:5001` (from any device on network)

---

## ✅ Benefits

- ✅ **No cloud needed** - Everything local
- ✅ **Works on Mac** - Via `/etc/hosts`
- ✅ **Works on DS224** - Via DNS Server
- ✅ **Same OAuth config** - Configure once, use everywhere
- ✅ **Network-wide** - Other devices can access too (with DNS Server)

---

## 🎯 Summary

1. **Mac:** `/etc/hosts` → `127.0.0.1 youtube-automation.local`
2. **DS224:** DNS Server → `youtube-automation.local` → NAS IP
3. **OAuth:** Configure with `.local` domain once
4. **Done!** Works everywhere locally

