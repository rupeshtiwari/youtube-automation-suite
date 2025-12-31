# Web Interface Guide

## 🚀 Quick Start

1. **Start the web server:**
   ```bash
   python app.py
   # Or use the convenience script:
   ./start_server.sh
   ```

2. **Open in browser:**
   ```
   http://localhost:5000
   ```

3. **Configure:**
   - Go to Configuration page
   - Enter all API keys
   - Set scheduling preferences
   - Save settings

4. **Monitor:**
   - Check Dashboard for status
   - View last run and next scheduled run
   - Manually trigger runs if needed

## 📋 Configuration Page

### API Keys Section

Enter credentials for:
- **LinkedIn**: Access Token + Person URN
- **Facebook**: Page Access Token + Page ID
- **Instagram**: Business Account ID + Access Token
- **Ayrshare** (Optional): Unified API key

**Test Connections** button validates your API keys.

### Scheduling Settings

- **Enable Daily Automation**: Toggle to start/stop automatic runs
- **Videos Per Day**: Number of videos to process (1-10)
- **Schedule Day**: Day of week to run (Monday-Sunday)
- **YouTube Schedule Time**: Time to schedule videos (IST, default: 23:00)
- **Social Media Schedule Time**: Time to post (IST, default: 19:30)
- **Playlist ID**: YouTube playlist ID for scheduling (optional)
- **Export Type**: All playlists or Shorts only

### Social Media Posting

- **Auto-post Social**: Enable automatic posting
- **Platform Selection**: Choose LinkedIn, Facebook, Instagram

## 🎯 How It Works

1. **Settings Storage**: All settings saved to `automation_settings.json`
2. **Environment Sync**: Automatically updates `.env` file for script compatibility
3. **Background Scheduler**: Uses APScheduler to run tasks automatically
4. **Daily Automation Flow**:
   - Export videos to Excel
   - Schedule YouTube videos (if playlist ID set)
   - Post to social media (if enabled)

## 🔧 Advanced Usage

### Manual Execution

Click "Run Now" on Dashboard to trigger automation immediately.

### API Endpoints

- `GET /api/status` - Get automation status
- `POST /api/run-now` - Trigger manual run
- `POST /api/test-connection` - Test API connection

### Running in Production

For production deployment:

1. **Change secret key:**
   ```python
   app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
   ```

2. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up as systemd service** (Linux) or use PM2 (Node.js process manager)

## 📊 Monitoring

The Dashboard shows:
- **Automation Status**: Active/Inactive
- **Last Run**: Timestamp of last execution
- **Next Run**: When automation will run next
- **Current Settings**: Summary of configuration

## ⚠️ Troubleshooting

**Server won't start:**
- Check if port 5000 is available
- Ensure all dependencies are installed
- Check Python version (3.8+)

**Automation not running:**
- Verify "Enable Daily Automation" is checked
- Check schedule day and time
- Review server logs for errors

**API connections fail:**
- Verify API keys are correct
- Check API key permissions/scopes
- Ensure tokens haven't expired

## 🔒 Security Notes

- API keys are stored in `automation_settings.json` (plain text)
- For production, consider encrypting sensitive data
- Use environment variables for sensitive keys
- Don't commit `automation_settings.json` to version control

