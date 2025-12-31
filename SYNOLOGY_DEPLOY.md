# 🎯 Synology One-Click Deployment Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Copy Files to NAS

**Option A: Using File Station (Easiest)**
1. Open **File Station** on your Synology
2. Navigate to `/docker/` folder (create if doesn't exist)
3. Upload the entire `youtube-automation` folder
4. Extract if it's a zip file

**Option B: Using SCP (Command Line)**
```bash
# From your computer
scp -r * admin@your-nas-ip:/volume1/docker/youtube-automation/
```

**Option C: Using Git (If you have Git on NAS)**
```bash
# SSH into NAS
ssh admin@your-nas-ip

# Clone repository
cd /volume1/docker
git clone https://github.com/yourusername/youtube-automation.git
cd youtube-automation
```

### Step 2: Make Script Executable

**Using SSH:**
```bash
ssh admin@your-nas-ip
cd /volume1/docker/youtube-automation
chmod +x synology_one_click.sh
```

**Using File Station:**
1. Right-click `synology_one_click.sh`
2. Properties → Permissions
3. Enable execute for owner

### Step 3: Run One-Click Deployment

**Using SSH (Recommended):**
```bash
ssh admin@your-nas-ip
cd /volume1/docker/youtube-automation
./synology_one_click.sh
```

**Using Task Scheduler (GUI):**
1. Control Panel → Task Scheduler
2. Create → Scheduled Task → User-defined script
3. Task: `Deploy YouTube Automation`
4. User: `root`
5. Run command:
   ```bash
   /volume1/docker/youtube-automation/synology_one_click.sh
   ```
6. Save and Run Now

## 🎬 What the Script Does

The one-click script automatically:
1. ✅ Checks Docker is installed
2. ✅ Creates necessary directories
3. ✅ Copies all files to correct location
4. ✅ Creates template .env file if needed
5. ✅ Builds Docker image
6. ✅ Starts the container
7. ✅ Shows you the access URL

## 📱 Access Your App

After deployment:
- **Local Network**: `http://your-nas-ip:5000`
- **QuickConnect**: `http://your-quickconnect-id.quickconnect.to:5000`

## 🔄 Updates

To update the app:
```bash
cd /volume1/docker/youtube-automation
git pull  # If using git
# Or upload new files via File Station
./synology_one_click.sh  # Run again
```

## 🛠️ Manual Docker Commands (Alternative)

If you prefer manual control:

```bash
cd /volume1/docker/youtube-automation

# Build
docker build -t youtube-automation:latest .

# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

## 📊 Container Management via DSM

1. **Docker** → **Container**
2. Find `youtube-automation`
3. Right-click for options:
   - Start/Stop
   - View Logs
   - Open Terminal
   - Settings

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Check if port 5000 is in use
netstat -tuln | grep 5000

# Try different port (edit docker-compose.yml)
ports:
  - "5001:5000"  # Change 5000 to 5001
```

### Permission Issues
```bash
# Fix permissions
chown -R admin:users /volume1/docker/youtube-automation
chmod -R 755 /volume1/docker/youtube-automation
```

### Database Issues
```bash
# Check database file
ls -la /volume1/docker/youtube-automation/data/

# Reset database (if needed)
rm /volume1/docker/youtube-automation/data/youtube_automation.db
# Restart container - it will recreate
```

## 🔒 Security

1. **Change Default Port**: Edit `docker-compose.yml` port mapping
2. **Use Reverse Proxy**: Control Panel → Application Portal
3. **Enable Firewall**: Control Panel → Security → Firewall
4. **Use HTTPS**: Set up SSL certificate

## 📈 Monitoring

### Check Status
```bash
docker ps | grep youtube-automation
```

### View Logs
```bash
docker-compose logs -f youtube-automation
```

### Resource Usage
- Docker → Container → youtube-automation → Resource Monitor

## 💾 Backup

### Manual Backup
```bash
# Backup database
cp /volume1/docker/youtube-automation/data/youtube_automation.db \
   /volume1/backup/youtube-automation-$(date +%Y%m%d).db
```

### Automated Backup (Synology Hyper Backup)
1. Control Panel → Hyper Backup
2. Create backup task
3. Select: `/volume1/docker/youtube-automation/data/`
4. Schedule daily backups

## 🎯 Next Steps After Deployment

1. ✅ Open web interface: `http://your-nas-ip:5000`
2. ✅ Go to Configuration page
3. ✅ Enter your API keys
4. ✅ Set up automation schedule
5. ✅ Test "Run Now" button
6. ✅ Verify database is created

## 🆘 Need Help?

- Check logs: `docker-compose logs -f`
- Health check: `http://your-nas-ip:5000/health`
- Container status: Docker → Container

---

**That's it! Your app is now running on your NAS! 🎉**

