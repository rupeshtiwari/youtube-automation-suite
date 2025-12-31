# 🚀 Step-by-Step Deployment Guide

## Step 1: Verify Prerequisites

### A. Check Docker is Installed

1. Open **Package Center** on your Synology
2. Search for **"Docker"**
3. If installed: ✅ You'll see it in "Installed"
4. If NOT installed: Click **Install** (this takes a few minutes)

**Tell me:** Docker installed? (Yes/No)

### B. Enable SSH

1. Open **Control Panel**
2. Go to **Terminal & SNMP**
3. Check **"Enable SSH service"**
4. Port: `22` (default is fine)
5. Click **Apply**

**Tell me:** SSH enabled? (Yes/No)

### C. Test Connection from Your Mac

Open Terminal on your Mac and run:

```bash
# Test 1: Ping test
ping -c 3 192.168.68.108
```

**Expected:** Should see replies. If you see "Request timeout", you're not on the same network.

**Tell me:** Ping works? (Yes/No)

```bash
# Test 2: SSH test
ssh rupesh@192.168.68.108
```

**Expected:** Should ask for password. Enter: `8xrBZyb6PuBFkqVfkgj6`

If it connects, type `exit` to disconnect.

**Tell me:** SSH works? (Yes/No)

## Step 2: Run Deployment

Once all checks pass, run:

```bash
cd /Users/rupesh/code/youtube-automation
./deploy_to_your_nas.sh
```

When prompted for password, enter: `8xrBZyb6PuBFkqVfkgj6`

## Step 3: Verify Deployment

After script completes:

1. **Check container is running:**
   ```bash
   ssh rupesh@192.168.68.108 'docker ps | grep youtube-automation'
   ```

2. **Open in browser:**
   ```
   http://192.168.68.108:5000
   ```

## 🆘 Common Issues

### Issue 1: "Docker not found"
**Solution:** Install Docker from Package Center

### Issue 2: "Connection refused"
**Solution:** Enable SSH in Control Panel → Terminal & SNMP

### Issue 3: "Permission denied"
**Solution:** Make sure username is "rupesh" and password is correct

### Issue 4: "Port 5000 in use"
**Solution:** We'll change the port in docker-compose.yml

---

## 📞 What to Share With Me

After running the checks, tell me:

1. Docker installed? ✅/❌
2. SSH enabled? ✅/❌  
3. Can ping NAS? ✅/❌
4. Can SSH in? ✅/❌
5. Any error messages?

Then I'll help you deploy! 🚀

