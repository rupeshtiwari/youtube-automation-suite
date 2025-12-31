# 🔐 Synology Docker Permissions Guide

## Important: Docker Permissions on Synology

According to [Synology's documentation](https://kb.synology.com/en-global/DSM/tutorial/How_to_login_to_DSM_with_root_permission_via_SSH_Telnet), regular users may need special permissions to run Docker commands.

## 🎯 Solution Options

### Option 1: Add User to Docker Group (Recommended)

1. **SSH into your NAS as admin:**
   ```bash
   ssh admin@192.168.68.108
   ```

2. **Switch to root:**
   ```bash
   sudo -i
   # Or use: su -
   ```

3. **Add user to docker group:**
   ```bash
   synogroup --add docker rupesh
   ```

4. **Verify:**
   ```bash
   groups rupesh
   # Should show "docker" in the list
   ```

5. **Log out and back in** for changes to take effect

### Option 2: Use Sudo (Easier, but requires password)

The deployment script now automatically detects if sudo is needed and will use it.

You may be prompted for password during deployment.

### Option 3: Use Root User (Not Recommended)

Synology discourages using root directly, but if needed:

1. Enable root login via SSH (Control Panel → Terminal & SNMP)
2. SSH as root: `ssh root@192.168.68.108`
3. Run deployment as root

**⚠️ Security Warning:** Using root is less secure. Prefer Option 1 or 2.

## 🔧 Updated Deployment Script

The `synology_one_click.sh` script now:
- ✅ Automatically detects if Docker needs sudo
- ✅ Uses appropriate commands based on permissions
- ✅ Handles both `docker` and `sudo docker` scenarios

## 📝 Quick Fix

If you get "Permission denied" errors:

**Quick fix - Add to docker group:**
```bash
ssh admin@192.168.68.108
sudo synogroup --add docker rupesh
```

Then log out and back in, and try deployment again.

## ✅ Verify Permissions

Test if you can run Docker:

```bash
ssh rupesh@192.168.68.108
docker ps
```

If it works: ✅ You're good!
If "Permission denied": Use Option 1 or 2 above.

---

**The deployment script will automatically handle sudo if needed!**

