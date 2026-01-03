# DS224 Synology NAS - DNS Server Setup

## 🎯 Goal
Set up local DNS on DS224 so `youtube-automation.local` resolves to your NAS IP.

---

## 📦 Step 1: Install DNS Server Package

1. **Open Synology DSM**
2. **Go to Package Center**
3. **Search:** "DNS Server"
4. **Install** the DNS Server package
5. **Open** DNS Server application

---

## ⚙️ Step 2: Create DNS Zone

1. **Open DNS Server**
2. **Go to "Zones" tab**
3. **Click "Create"** → **"Master zone"**

### Zone Configuration:
- **Zone name:** `local`
- **Master DNS server:** (Leave default or enter your NAS hostname)
- **Email:** (Optional, your email)
- Click **"Next"**

### DNS Forwarder (Optional):
- Leave default or configure if you want internet DNS resolution
- Click **"Next"**

### Review:
- Review settings
- Click **"Apply"**

---

## 📝 Step 3: Add A Record

1. **Select the `local` zone** you just created
2. **Click "Create"** → **"A Record"**

### A Record Configuration:
- **Hostname:** `youtube-automation`
  - This creates: `youtube-automation.local`
- **IPv4 Address:** Your NAS IP address
  - Example: `192.168.1.100`
  - Find your NAS IP: Control Panel → Network → Network Interface
- **TTL:** (Leave default, usually 3600)
- Click **"OK"**

---

## 🔍 Step 4: Verify DNS Resolution

### From NAS (SSH or Terminal):
```bash
nslookup youtube-automation.local
# Should return your NAS IP
```

### From Mac (after configuring router DNS):
```bash
nslookup youtube-automation.local
# Should return your NAS IP
```

---

## 🌐 Step 5: Configure Router DNS (Optional but Recommended)

To make `youtube-automation.local` work from all devices on your network:

### Option A: Router DNS Settings
1. **Access router admin panel** (usually `192.168.1.1` or `192.168.0.1`)
2. **Go to DNS settings**
3. **Set Primary DNS:** Your NAS IP (e.g., `192.168.1.100`)
4. **Set Secondary DNS:** `8.8.8.8` (Google) or `1.1.1.1` (Cloudflare)
5. **Save and restart router**

### Option B: Device-Specific DNS
On each device, set DNS to:
- **Primary:** NAS IP
- **Secondary:** `8.8.8.8`

**Mac:** System Preferences → Network → Advanced → DNS

---

## ✅ Verification

### Test from Mac:
```bash
# Flush DNS cache first
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Test resolution
nslookup youtube-automation.local
# Should return: NAS IP (e.g., 192.168.1.100)

# Test access
curl http://youtube-automation.local:5001
# Should connect to your Flask app on NAS
```

### Test from Browser:
- Open: `http://youtube-automation.local:5001`
- Should load your app from NAS

---

## 🔧 Troubleshooting

### DNS not resolving:
1. **Check DNS Server is running:** Package Center → DNS Server → Running
2. **Check A record exists:** DNS Server → Zones → local → Should see `youtube-automation`
3. **Flush DNS cache on client:** 
   - Mac: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
   - Windows: `ipconfig /flushdns`
4. **Check router DNS:** Make sure router/device is using NAS as DNS server

### Can't access app:
1. **Check Flask is running on NAS:** Port 5001
2. **Check firewall:** Allow port 5001 on NAS
3. **Check NAS IP:** Make sure A record points to correct IP

### OAuth not working:
1. **Verify OAuth URIs match:** Must be exactly `http://youtube-automation.local/oauth2callback`
2. **Check port:** Make sure port 5001 is included if needed
3. **Test locally first:** Make sure it works on Mac before deploying to NAS

---

## 📋 Quick Checklist

- [ ] DNS Server package installed
- [ ] `local` zone created
- [ ] `youtube-automation` A record added → NAS IP
- [ ] DNS resolution tested (`nslookup youtube-automation.local`)
- [ ] Router DNS configured (optional, for network-wide access)
- [ ] OAuth configured with `.local` domain
- [ ] App accessible at `http://youtube-automation.local:5001`

---

## 🎯 Summary

1. **Install DNS Server** on DS224
2. **Create `local` zone**
3. **Add A record:** `youtube-automation` → NAS IP
4. **Configure router DNS** (optional, for all devices)
5. **Access:** `http://youtube-automation.local:5001`

**Same OAuth config works on Mac and NAS!** 🎉

