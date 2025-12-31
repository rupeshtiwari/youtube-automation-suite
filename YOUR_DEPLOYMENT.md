# 🚀 Deploy to Your NAS - 192.168.68.108

## ⚡ One Command Deployment

I've created a script with your NAS IP pre-configured. Just run:

```bash
cd /Users/rupesh/code/youtube-automation
./deploy_to_your_nas.sh
```

That's it! The script will:
1. ✅ Check NAS connection
2. ✅ Copy all files
3. ✅ Run deployment
4. ✅ Show you the access URL

## 📋 Before Running

Make sure:

1. **SSH is enabled on your NAS:**
   - Control Panel → Terminal & SNMP
   - Check "Enable SSH service"
   - Click Apply

2. **You're on the same network** as your NAS

3. **You know your NAS password** (will be prompted)

## 🎯 After Deployment

Open in browser:
```
http://192.168.68.108:5000
```

## 🔧 If Something Goes Wrong

### "Connection Refused" or "Cannot Reach NAS"
- Check NAS is powered on
- Verify IP: `192.168.68.108`
- Make sure you're on same network
- Ping test: `ping 192.168.68.108`

### "Permission Denied"
- SSH might not be enabled
- Go to: Control Panel → Terminal & SNMP → Enable SSH

### "Docker Not Found"
- Install Docker from Package Center
- Then run script again

### Manual Check
```bash
# SSH into NAS
ssh admin@192.168.68.108

# Check if files are there
ls -la /volume1/docker/youtube-automation/

# Check Docker
docker --version

# Check container
docker ps | grep youtube-automation
```

## 📊 Verify Deployment

After running the script, verify:

1. **Container is running:**
   ```bash
   ssh admin@192.168.68.108 'docker ps | grep youtube-automation'
   ```

2. **Web interface works:**
   - Open: http://192.168.68.108:5000
   - Should see dashboard

3. **Health check:**
   - Open: http://192.168.68.108:5000/health
   - Should show: `{"status": "healthy"}`

## 🆘 Need Help?

If the script fails, share:
1. The error message
2. Output of: `ssh admin@192.168.68.108 'docker ps'`
3. Output of: `ssh admin@192.168.68.108 'cd /volume1/docker/youtube-automation && docker-compose logs'`

---

**Ready? Just run: `./deploy_to_your_nas.sh` 🚀**

