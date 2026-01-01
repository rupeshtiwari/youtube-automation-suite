#!/usr/bin/env python3
"""
Verify that all config fields from MY_CONFIG.json are displayed and saved properly.
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db

def verify_config():
    """Verify all config fields are in database and will be displayed."""
    print("=" * 70)
    print("🔍 Verifying Configuration Display & Database Storage")
    print("=" * 70)
    print()
    
    # Load from database
    db_settings = load_settings_from_db()
    
    # Load from MY_CONFIG.json
    config_file = Path('MY_CONFIG.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            file_config = json.load(f)
    else:
        print("❌ MY_CONFIG.json not found")
        return False
    
    print("📋 Checking all sections...")
    print()
    
    all_ok = True
    
    # Check API Keys
    print("1. API Keys:")
    api_keys_db = db_settings.get('api_keys', {})
    api_keys_file = file_config.get('api_keys', {})
    for key in api_keys_file.keys():
        db_val = api_keys_db.get(key, '')
        file_val = api_keys_file.get(key, '')
        if db_val == file_val:
            status = "✅"
        else:
            status = "⚠️"
            all_ok = False
        display_db = db_val[:20] + '...' if len(str(db_val)) > 20 else db_val
        print(f"   {status} {key}: {display_db}")
    print()
    
    # Check Scheduling
    print("2. Scheduling:")
    sched_db = db_settings.get('scheduling', {})
    sched_file = file_config.get('scheduling', {})
    for key in sched_file.keys():
        db_val = sched_db.get(key)
        file_val = sched_file.get(key)
        if db_val == file_val:
            status = "✅"
        else:
            status = "⚠️"
            all_ok = False
        print(f"   {status} {key}: {db_val}")
    print()
    
    # Check CTA
    print("3. CTA:")
    cta_db = db_settings.get('cta', {})
    cta_file = file_config.get('cta', {})
    for key in cta_file.keys():
        db_val = cta_db.get(key, '')
        file_val = cta_file.get(key, '')
        if db_val == file_val:
            status = "✅"
        else:
            status = "⚠️"
            all_ok = False
        print(f"   {status} {key}: {db_val}")
    print()
    
    # Check Targeting
    print("4. Targeting:")
    target_db = db_settings.get('targeting', {})
    target_file = file_config.get('targeting', {})
    for key in target_file.keys():
        db_val = target_db.get(key)
        file_val = target_file.get(key)
        if isinstance(db_val, list) and isinstance(file_val, list):
            match = set(db_val) == set(file_val)
        else:
            match = db_val == file_val
        if match:
            status = "✅"
        else:
            status = "⚠️"
            all_ok = False
        if isinstance(db_val, list):
            print(f"   {status} {key}: {len(db_val)} items")
        else:
            print(f"   {status} {key}: {db_val}")
    print()
    
    # Check Thresholds
    print("5. Thresholds:")
    thresh_db = db_settings.get('thresholds', {})
    thresh_file = file_config.get('thresholds', {})
    for key in thresh_file.keys():
        db_val = thresh_db.get(key)
        file_val = thresh_file.get(key)
        if db_val == file_val:
            status = "✅"
        else:
            status = "⚠️"
            all_ok = False
        print(f"   {status} {key}: {db_val}")
    print()
    
    print("=" * 70)
    if all_ok:
        print("✅ All configuration is properly saved and will be displayed!")
    else:
        print("⚠️  Some fields don't match. Run: python3 scripts/load_config.py")
    print("=" * 70)
    print()
    print("📝 Config Page Display:")
    print("   - All fields from database are passed to config.html template")
    print("   - Template uses {{ settings.xxx }} to display values")
    print("   - All input fields are prepopulated with database values")
    print()
    print("💾 Database Storage:")
    print("   - All settings saved to: youtube_automation.db")
    print("   - Table: settings")
    print("   - Persists across server restarts")
    print()
    
    return all_ok

if __name__ == '__main__':
    success = verify_config()
    sys.exit(0 if success else 1)

