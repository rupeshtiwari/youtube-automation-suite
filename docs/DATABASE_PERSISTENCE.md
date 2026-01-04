# Database Persistence for API Keys & Credentials

## ✅ How It Works

### Primary Storage: SQLite Database
- **Location**: `app/youtube_automation.db` (or `DATA_DIR/youtube_automation.db` if set)
- **Table**: `settings` table with `setting_key = 'app_settings'`
- **Format**: All settings stored as JSON in a single row
- **Persistence**: ✅ Survives server restarts, code changes, and updates

### Backup Storage: JSON File
- **Location**: `automation_settings.json`
- **Purpose**: Secondary backup in case database fails
- **Format**: Human-readable JSON file

### Compatibility: .env File
- **Location**: `.env`
- **Purpose**: For scripts that read environment variables
- **Format**: Key-value pairs

---

## 🔒 What Gets Saved

All configuration data is saved to the database:

### API Keys & Credentials
- LinkedIn Client ID & Secret
- LinkedIn Access Token
- LinkedIn Person URN
- Facebook App ID & Secret
- Facebook Page Access Token
- Facebook Page ID
- Instagram Business Account ID
- Instagram Access Token
- Ayrshare API Key

### Scheduling Settings
- Automation enabled/disabled
- Videos per day
- Schedule day and times
- Playlist ID
- Export type
- Upload method (native vs link)

### Thresholds
- Daily limits for each platform

### Targeting
- Target audience
- Interview types
- Role levels

### CTA Settings
- Booking URL
- WhatsApp number
- Social media URLs

---

## 💾 Save Process

When you click "Save" on any section:

1. **Database Save** (PRIMARY)
   - Settings saved to SQLite database
   - Verified to ensure save succeeded
   - If fails, error is logged

2. **JSON Backup** (SECONDARY)
   - Settings saved to `automation_settings.json`
   - Always attempted as backup

3. **.env Update** (COMPATIBILITY)
   - Environment variables updated for scripts

4. **Verification**
   - At least one save must succeed
   - If both fail, an error is raised

---

## 📥 Load Process

On app startup:

1. **Load from Database** (PRIMARY)
   - Attempts to load from SQLite database
   - If found, uses database settings

2. **Fallback to JSON** (MIGRATION)
   - If database is empty, loads from JSON
   - Automatically migrates JSON → Database
   - Ensures no data loss

3. **Default Settings** (LAST RESORT)
   - If neither database nor JSON exists
   - Uses default empty settings

---

## 🛡️ Safety Features

### 1. Database Initialization
- Database is initialized on app startup
- Settings table is created if it doesn't exist
- No data loss if database is recreated

### 2. Error Handling
- Database save failures are logged
- JSON backup is always attempted
- Critical errors are raised (won't silently fail)

### 3. Verification
- Database saves are verified after write
- Settings are tested on app startup
- Logs confirm successful load

### 4. Migration Support
- Old JSON files are automatically migrated
- Settings are preserved during migration
- No manual intervention needed

---

## 📍 Database Location

### Default Location
```
app/youtube_automation.db
```

### Custom Location (via Environment Variable)
```bash
export DATA_DIR=/path/to/data
# Database will be at: /path/to/data/youtube_automation.db
```

### Check Current Location
The database path is displayed when you start the server:
```
💾 Database location: /path/to/youtube_automation.db
```

---

## ✅ Verification

### Test Database Persistence
```python
from app.database import init_database, save_settings_to_db, load_settings_from_db

# Initialize
init_database()

# Save test settings
test_settings = {
    'api_keys': {
        'linkedin_client_id': 'test123',
        'facebook_app_id': 'test456'
    }
}
save_settings_to_db(test_settings)

# Load and verify
loaded = load_settings_from_db()
assert loaded['api_keys']['linkedin_client_id'] == 'test123'
print('✅ Persistence verified!')
```

### Check Database File
```bash
ls -lh app/youtube_automation.db
# Should show file size (typically 50-200KB)
```

### View Settings in Database
```bash
sqlite3 app/youtube_automation.db
SELECT setting_key, LENGTH(setting_value) as size, updated_at FROM settings;
```

---

## 🔄 What Happens on Code Changes

### ✅ Settings Are Preserved
- Database file is NOT deleted when code changes
- Settings persist across:
  - Git pulls/updates
  - Code modifications
  - Server restarts
  - Application updates

### ⚠️ Important Notes
- **Database file is in `.gitignore`** - it won't be committed to Git
- **Backup your database** before major updates (optional)
- **Settings are local** - each installation has its own database

---

## 🚨 Troubleshooting

### Settings Not Persisting?

1. **Check Database File Exists**
   ```bash
   ls -lh app/youtube_automation.db
   ```

2. **Check Permissions**
   ```bash
   ls -l app/youtube_automation.db
   # Should be readable/writable
   ```

3. **Check Logs**
   - Look for "✅ Settings saved to database" messages
   - Check for error messages in console

4. **Verify Save Function**
   - Click "Save" on any section
   - Check console for success/error messages

### Database Errors?

1. **Reinitialize Database**
   ```python
   from app.database import init_database
   init_database()
   ```

2. **Check JSON Backup**
   ```bash
   cat automation_settings.json
   # Your settings should be here as backup
   ```

3. **Manual Migration**
   - If database is corrupted, JSON backup will be used
   - Settings will be automatically migrated back to database

---

## 📊 Current Status

✅ **Database persistence is ACTIVE**
- All API keys are saved to database
- Settings persist across restarts
- Backup to JSON file is working
- Migration from JSON → Database works

✅ **Verified Working**
- Database save/load tested
- API keys persistence verified
- Settings survive server restarts

---

## 🎯 Summary

**Your API keys and credentials are SAFE:**
- ✅ Saved to SQLite database (primary)
- ✅ Backed up to JSON file (secondary)
- ✅ Persist across server restarts
- ✅ Persist across code changes
- ✅ Automatically migrated from old JSON files
- ✅ Verified on every save operation

**You can safely:**
- Restart the server
- Update code
- Fix bugs
- Make changes

**Your settings will NOT be lost!** 🎉

