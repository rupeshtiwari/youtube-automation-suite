# 🚀 Deploy NOW - Simple Instructions

## ⚡ One Command (Fully Automated)

I've created a script with your credentials. Just run:

```bash
cd /Users/rupesh/code/youtube-automation
./deploy_automated.sh
```

**That's it!** The script will handle everything automatically.

## 📋 What It Does

1. ✅ Checks NAS connection (192.168.68.108)
2. ✅ Tests SSH (username: rupesh)
3. ✅ Creates directories
4. ✅ Copies all files
5. ✅ Builds Docker image
6. ✅ Starts container
7. ✅ Shows access URL

**Time:** About 2-3 minutes

## 🔧 If You Get "sshpass not found"

Install it first:
```bash
brew install hudochenkov/sshpass/sshpass
```

Then run the script again.

## ✅ After Deployment

Open in browser:
```
http://192.168.68.108:5000
```

## 🎯 Next Steps

1. Open web interface
2. Go to Configuration
3. Add API keys
4. Set up automation
5. Done! 🎉

---

**Ready? Run: `./deploy_automated.sh`**

