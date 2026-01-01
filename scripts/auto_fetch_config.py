#!/usr/bin/env python3
"""
Automated script to fetch Facebook/Instagram config using existing tokens or API.
This tries multiple methods to get all configuration data.
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db, save_settings_to_db

def try_get_instagram_account_id(page_id, page_token):
    """Try to get Instagram Business Account ID using Page Access Token."""
    print(f"🔍 Trying to fetch Instagram Account ID for Page: {page_id}")
    
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        'fields': 'instagram_business_account{id,username}',
        'access_token': page_token
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            ig_account = data.get('instagram_business_account')
            
            if ig_account:
                account_id = ig_account.get('id')
                username = ig_account.get('username')
                print(f"✅ Found Instagram Business Account!")
                print(f"   Account ID: {account_id}")
                print(f"   Username: @{username}")
                return account_id, username
            else:
                print("⚠️  No Instagram Business Account found.")
                print("   Make sure:")
                print("   1. Instagram is a Business Account (not Personal)")
                print("   2. Instagram is connected to Facebook Page")
                return None, None
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"❌ API Error: {error_msg}")
            
            if response.status_code == 401:
                print("   Token is expired or invalid.")
            elif response.status_code == 400:
                print("   Invalid request. Check Page ID and permissions.")
            
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None, None

def auto_fetch_config():
    """Automatically fetch config using available methods."""
    print("=" * 70)
    print("🔍 Auto-Fetch Facebook/Instagram Configuration")
    print("=" * 70)
    print()
    
    # Load existing settings
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    app_id = api_keys.get('facebook_app_id')
    page_id = api_keys.get('facebook_page_id')
    page_token = api_keys.get('facebook_page_access_token')
    
    if not app_id:
        print("❌ Facebook App ID not found in config.")
        return False
    
    if not page_id:
        print("❌ Facebook Page ID not found in config.")
        return False
    
    if not page_token:
        print("❌ Facebook Page Access Token not found in config.")
        print()
        print("💡 To get a new token, run:")
        print("   python3 scripts/fetch_facebook_config.py")
        print()
        print("   This will open a browser for OAuth authorization.")
        return False
    
    print(f"📱 App ID: {app_id}")
    print(f"📄 Page ID: {page_id}")
    print(f"🔑 Page Token: {page_token[:30]}...")
    print()
    
    # Try to get Instagram Account ID
    ig_account_id, ig_username = try_get_instagram_account_id(page_id, page_token)
    
    # Update config if we got Instagram data
    updated = False
    if ig_account_id:
        api_keys['instagram_business_account_id'] = ig_account_id
        updated = True
    
    if updated:
        settings['api_keys'] = api_keys
        save_settings_to_db(settings)
        
        # Also update MY_CONFIG.json
        config_file = Path('MY_CONFIG.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if ig_account_id:
                    config['api_keys']['instagram_business_account_id'] = ig_account_id
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print()
                print("✅ Updated MY_CONFIG.json!")
            except Exception as e:
                print(f"⚠️  Could not update MY_CONFIG.json: {e}")
        
        print()
        print("=" * 70)
        print("✅ Configuration Updated!")
        print("=" * 70)
        print()
        print("📝 Summary:")
        if ig_account_id:
            print(f"   ✅ Instagram Business Account ID: {ig_account_id}")
            print(f"   ✅ Instagram Username: @{ig_username}")
        print()
        print("🚀 Next steps:")
        print("   1. If token is expired, run: python3 scripts/fetch_facebook_config.py")
        print("   2. Test video uploads when ready!")
    else:
        print()
        print("⚠️  Could not fetch Instagram Account ID.")
        print()
        print("💡 Possible reasons:")
        print("   1. Facebook Page Access Token is expired")
        print("   2. Instagram is not connected to Facebook Page")
        print("   3. Instagram account is not a Business Account")
        print()
        print("🔧 To fix:")
        print("   1. Get new token: python3 scripts/fetch_facebook_config.py")
        print("   2. Connect Instagram: Facebook Page → Settings → Instagram")
        print("   3. Convert to Business: Instagram App → Account Type")
    
    return updated

if __name__ == '__main__':
    try:
        success = auto_fetch_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

