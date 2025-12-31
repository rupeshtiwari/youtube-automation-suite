# 🚀 Deploy with Proper Permissions

## Important: Synology Docker Permissions

According to [Synology's SSH documentation](https://kb.synology.com/en-global/DSM/tutorial/How_to_login_to_DSM_with_root_permission_via_SSH_Telnet), you may need special permissions to run Docker.

## 🎯 Two Options

### Option 1: Setup Permissions First (Recommended)

**Add your user to docker group:**

```bash
cd /Users/rupesh/code/youtube-automation
./setup_docker_permissions.sh
```

This will:
1. SSH into your NAS
2. Add user "rupesh" to docker group
3. You'll need to log out and back in

**Then deploy:**
```bash
./deploy_to_your_nas.sh
```

### Option 2: Deploy with Sudo (Easier)

The deployment script now automatically uses `sudo` if needed.

Just run:
```bash
./deploy_to_your_nas.sh
```

You may be prompted for password during deployment.

## ✅ Quick Test

Test if you can run Docker:

```bash
ssh rupesh@192.168.68.108
docker ps
```

**If it works:** ✅ Ready to deploy!
**If "Permission denied":** Use Option 1 or 2 above

## 🔧 Manual Permission Setup

If the script doesn't work, do it manually:

```bash
# SSH as admin
ssh admin@192.168.68.108

# Switch to root
sudo -i

# Add user to docker group
synogroup --add docker rupesh

# Verify
groups rupesh
# Should show "docker" in the list

# Exit
exit
exit
```

**Then log out and back in**, and try deployment again.

## 📝 Updated Scripts

All deployment scripts now:
- ✅ Automatically detect if sudo is needed
- ✅ Use appropriate Docker commands
- ✅ Handle permission issues gracefully

---

**Ready? Run `./deploy_to_your_nas.sh` - it will handle permissions automatically!**

