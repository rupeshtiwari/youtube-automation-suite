# 🏠 NAS Deployment Guide

## 📊 Current Database Setup

**We're using SQLite** - a file-based database that's perfect for NAS:
- ✅ Single file database (`youtube_automation.db`)
- ✅ No server required
- ✅ Works great on NAS
- ✅ Easy backup (just copy the .db file)
- ✅ Handles concurrent access well

## 🎯 NAS Hosting Options

### Option 1: Direct Python on NAS (Simplest)

If your NAS supports Python (Synology, QNAP, etc.):

#### Step 1: Install Python Dependencies on NAS

```bash
# SSH into your NAS
ssh admin@your-nas-ip

# Navigate to your project folder
cd /volume1/docker/youtube-automation  # or your preferred location

# Install dependencies
pip3 install -r requirements.txt
```

#### Step 2: Configure Paths

Update paths in `app.py` to use NAS storage:

```python
# In app.py, set database path to NAS location
DB_PATH = '/volume1/data/youtube-automation/youtube_automation.db'
SETTINGS_FILE = '/volume1/data/youtube-automation/automation_settings.json'
```

#### Step 3: Run as Service

Create a systemd service file:

```bash
# /etc/systemd/system/youtube-automation.service
[Unit]
Description=YouTube Automation Web App
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/volume1/docker/youtube-automation
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /volume1/docker/youtube-automation/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable youtube-automation
sudo systemctl start youtube-automation
```

### Option 2: Docker on NAS (Recommended)

Most modern NAS devices support Docker (Synology, QNAP, etc.)

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
```

#### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  youtube-automation:
    build: .
    container_name: youtube-automation
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      # Mount NAS storage for persistent data
      - /volume1/data/youtube-automation:/app/data
      - /volume1/data/youtube-automation/client_secret.json:/app/client_secret.json:ro
      - /volume1/data/youtube-automation/.env:/app/.env:ro
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY:-change-this-in-production}
    networks:
      - youtube-automation-net

networks:
  youtube-automation-net:
    driver: bridge
```

#### Step 3: Update Code for Docker

Update `database.py` to use mounted volume:

```python
import os

# Use environment variable or default to /app/data
DATA_DIR = os.getenv('DATA_DIR', '/app/data')
DB_PATH = os.path.join(DATA_DIR, 'youtube_automation.db')
SETTINGS_FILE = os.path.join(DATA_DIR, 'automation_settings.json')
```

#### Step 4: Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Reverse Proxy Setup (For External Access)

If you want to access from outside your network:

#### Using Nginx (on NAS or separate server)

```nginx
server {
    listen 80;
    server_name youtube-automation.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Using Synology Reverse Proxy

1. Control Panel → Application Portal → Reverse Proxy
2. Add rule:
   - Source: `youtube-automation.yourdomain.com`
   - Destination: `localhost:5000`
   - Enable HTTPS (optional)

## 📁 NAS Directory Structure

Recommended structure on your NAS:

```
/volume1/data/youtube-automation/
├── app.py
├── database.py
├── requirements.txt
├── docker-compose.yml (if using Docker)
├── Dockerfile (if using Docker)
├── data/                    # Persistent data
│   ├── youtube_automation.db
│   ├── automation_settings.json
│   ├── token.json
│   └── .env
├── exports/                 # Excel exports
│   └── *.xlsx
└── logs/                    # Application logs
    └── app.log
```

## 🔧 Configuration for NAS

### Update app.py for Production

```python
# At the top of app.py
import os

# Use environment variables for paths
DATA_DIR = os.getenv('DATA_DIR', '/app/data')
DB_PATH = os.path.join(DATA_DIR, 'youtube_automation.db')
SETTINGS_FILE = os.path.join(DATA_DIR, 'automation_settings.json')

# Update database.py to use these paths
```

### Update database.py

```python
# At the top of database.py
import os

DATA_DIR = os.getenv('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'youtube_automation.db')
```

## 🔒 Security Considerations

1. **Use HTTPS**: Set up SSL certificate (Let's Encrypt)
2. **Firewall**: Only expose necessary ports
3. **Authentication**: Add login to web interface (future enhancement)
4. **Backup**: Regularly backup database file
5. **Secrets**: Keep `.env` and `client_secret.json` secure

## 📦 Backup Strategy

SQLite makes backup easy:

```bash
# Simple backup script
#!/bin/bash
BACKUP_DIR="/volume1/backup/youtube-automation"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cp /volume1/data/youtube-automation/data/youtube_automation.db \
   $BACKUP_DIR/youtube_automation_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "youtube_automation_*.db" -mtime +7 -delete
```

Schedule with cron:
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

## 🚀 Quick Start Commands

### For Synology NAS

1. **Enable SSH**: Control Panel → Terminal & SNMP → Enable SSH
2. **Install Docker**: Package Center → Docker
3. **Deploy**:
   ```bash
   # Copy files to NAS
   scp -r * admin@your-nas-ip:/volume1/docker/youtube-automation/
   
   # SSH and start
   ssh admin@your-nas-ip
   cd /volume1/docker/youtube-automation
   docker-compose up -d
   ```

### For QNAP NAS

1. **Enable SSH**: Control Panel → Network Services → Telnet/SSH
2. **Install Container Station**: App Center
3. **Deploy**: Similar to Synology

## 🔍 Monitoring

### Check if Running

```bash
# Docker
docker ps | grep youtube-automation

# Systemd
systemctl status youtube-automation

# Check logs
docker-compose logs -f
# or
journalctl -u youtube-automation -f
```

### Health Check Endpoint

Add to `app.py`:

```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': os.path.exists(DB_PATH),
        'timestamp': datetime.now().isoformat()
    })
```

## 💡 Tips

1. **Use Docker**: Easier to manage and update
2. **Persistent Volumes**: Store data on NAS, not in container
3. **Regular Backups**: SQLite file is easy to backup
4. **Monitor Logs**: Check for errors regularly
5. **Update Regularly**: Keep dependencies updated

## ❓ Troubleshooting

### Database Locked
- SQLite handles concurrent reads well
- If issues, check file permissions on NAS

### Port Already in Use
- Change port in `app.py`: `app.run(host='0.0.0.0', port=5001)`
- Update docker-compose.yml port mapping

### Permission Issues
- Ensure NAS user has read/write access to data directory
- Check file ownership: `chown -R user:group /volume1/data/youtube-automation`

## 📝 Next Steps

1. Choose deployment method (Docker recommended)
2. Set up directory structure on NAS
3. Deploy application
4. Configure reverse proxy (if needed)
5. Set up backups
6. Test automation runs

