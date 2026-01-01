#!/usr/bin/env python3
"""
Load configuration from MY_CONFIG.json into the database.
This allows you to populate all settings at once.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database, save_settings_to_db, load_settings_from_db

def load_config_from_file():
    """Load configuration from MY_CONFIG.json and save to database."""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MY_CONFIG.json')
    
    if not os.path.exists(config_file):
        print(f"❌ Error: {config_file} not found!")
        print("Please create MY_CONFIG.json and fill in your settings.")
        return False
    
    try:
        # Read config file
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Initialize database
        init_database()
        
        # Save to database
        save_settings_to_db(config)
        
        # Verify it was saved
        loaded = load_settings_from_db()
        if loaded:
            print("✅ Configuration loaded successfully!")
            print(f"   - API Keys: {sum(1 for v in loaded.get('api_keys', {}).values() if v)} configured")
            print(f"   - Scheduling: {'Enabled' if loaded.get('scheduling', {}).get('enabled') else 'Disabled'}")
            print(f"   - Upload Method: {loaded.get('scheduling', {}).get('upload_method', 'native')}")
            print(f"   - CTA Settings: {sum(1 for v in loaded.get('cta', {}).values() if v)} configured")
            return True
        else:
            print("❌ Error: Configuration was not saved properly!")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {config_file}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = load_config_from_file()
    sys.exit(0 if success else 1)

