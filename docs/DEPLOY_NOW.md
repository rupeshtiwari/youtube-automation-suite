# 🚀 Deploy to Your NAS - Step by Step RIGHT NOW

## ⚠️ Important: I Cannot Access Your NAS Directly

For security reasons, I cannot SSH into your NAS. But I'll guide you through every step!

## 📋 Pre-Deployment Checklist

Before starting, make sure you have:
- ✅ Synology NAS with Docker installed
- ✅ SSH access enabled (Control Panel → Terminal & SNMP)
- ✅ Your NAS IP address or QuickConnect ID
- ✅ Admin username and password

## 🎯 Step-by-Step Deployment (5 Minutes)

### Step 1: Enable SSH on Your NAS

1. Open **Control Panel** on your Synology
2. Go to **Terminal & SNMP**
3. Check **Enable SSH service**
4. Port: `22` (default)
5. Click **Apply**

### Step 2: Prepare Files on Your Computer

**Option A: If you have the files locally:**
```bash
# Make sure you're in the project directory
cd /Users/rupesh/code/youtube-automation

# Verify files exist
ls -la synology_one_click.sh docker-compose.yml Dockerfile
```

**Option B: If you need to download from GitHub:**
```bash
# Clone or download the repository
git clone https://github.com/rupeshtiwari/youtube-automation-suite.git
cd youtube-automation-suite
```

### Step 3: Copy Files to NAS

**Method 1: Using SCP (Command Line) - RECOMMENDED**

```bash
# Replace YOUR_NAS_IP with your actual NAS IP
# Replace admin with your username if different

# From your Mac terminal:
cd /Users/rupesh/code/youtube-automation

# Copy all files to NAS
scp -r * admin@YOUR_NAS_IP:/volume1/docker/youtube-automation/
```

**Example:**
```bash
scp -r * admin@192.168.88.17:/volume1/docker/youtube-automation/
```

**Method 2: Using File Station (GUI)**

1. Open **File Station** on Synology
2. Navigate to `/docker/` folder (create if needed)
3. Create folder: `youtube-automation`
4. Upload all files from your computer:
   - All `.py` files
   - `requirements.txt`
   - `Dockerfile`
   - `docker-compose.yml`
   - `synology_one_click.sh`
   - `templates/` folder
   - `.dockerignore`

### Step 4: SSH into Your NAS

```bash
# Replace with your NAS IP
ssh admin@YOUR_NAS_IP

# Example:
ssh admin@192.168.88.17
```

Enter your password when prompted.

### Step 5: Navigate to Project Directory

```bash
cd /volume1/docker/youtube-automation
ls -la  # Verify files are there
```

### Step 6: Make Script Executable

```bash
chmod +x synology_one_click.sh
```

### Step 7: Run One-Click Deployment

```bash
./synology_one_click.sh
```

The script will:
- ✅ Check Docker
- ✅ Create directories
- ✅ Build Docker image
- ✅ Start container
- ✅ Show you the access URL

### Step 8: Access Your App

After deployment completes, open in browser:
```
http://YOUR_NAS_IP:5000
```

**Example:**
```
http://192.168.88.17:5000
```

Or if using QuickConnect:
```
http://YOUR_QUICKCONNECT_ID.quickconnect.to:5000
```

## 🔧 Troubleshooting

### "Permission Denied" Error
```bash
# Fix permissions
chmod +x synology_one_click.sh
chmod -R 755 /volume1/docker/youtube-automation
```

### "Docker Not Found" Error
1. Open **Package Center** on Synology
2. Search for **Docker**
3. Install it
4. Run script again

### "Port 5000 Already in Use"
Edit `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Change 5000 to 5001
```

Then access at: `http://YOUR_NAS_IP:5001`

### Files Not Copied
```bash
# Check if files exist
ls -la /volume1/docker/youtube-automation/

# If missing, copy again
# From your Mac:
scp -r * admin@YOUR_NAS_IP:/volume1/docker/youtube-automation/
```

## 📝 Manual Deployment (If Script Fails)

If the one-click script doesn't work, do it manually:

```bash
# 1. Create directories
mkdir -p /volume1/docker/youtube-automation/data
mkdir -p /volume1/docker/youtube-automation/exports

# 2. Navigate to directory
cd /volume1/docker/youtube-automation

# 3. Build Docker image
docker build -t youtube-automation:latest .

# 4. Start with docker-compose
docker-compose up -d

# 5. Check status
docker ps | grep youtube-automation
```

## ✅ Verification

After deployment, verify it's working:

1. **Check Container Status:**
   ```bash
   docker ps | grep youtube-automation
   ```

2. **View Logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Health Check:**
   Open: `http://YOUR_NAS_IP:5000/health`
   Should show: `{"status": "healthy"}`

4. **Web Interface:**
   Open: `http://YOUR_NAS_IP:5000`
   Should show the dashboard

## 🎯 Next Steps After Deployment

1. ✅ Open web interface
2. ✅ Go to Configuration page
3. ✅ Add your API keys:
   - LinkedIn credentials
   - Facebook credentials
   - Instagram credentials
   - (Or Ayrshare API key)
4. ✅ Configure automation schedule
5. ✅ Test "Run Now" button

## 🆘 Need Help?

If you get stuck, share:
1. The error message
2. Output of: `docker ps`
3. Output of: `docker-compose logs`

I'll help you troubleshoot!

---

## 🚀 Quick Command Reference

```bash
# Copy files to NAS
scp -r * admin@YOUR_NAS_IP:/volume1/docker/youtube-automation/

# SSH into NAS
ssh admin@YOUR_NAS_IP

# Deploy
cd /volume1/docker/youtube-automation
chmod +x synology_one_click.sh
./synology_one_click.sh

# Check status
docker ps | grep youtube-automation

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

---

**Ready? Let's deploy! 🚀**

