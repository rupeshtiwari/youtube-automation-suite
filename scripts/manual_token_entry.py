#!/usr/bin/env python3
"""
Manual token entry script - for when Graph API Explorer doesn't work.
Allows you to directly enter Page Access Token and Instagram Account ID.
"""

import sys
import os
import json
import requests
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db, save_settings_to_db

def manual_token_entry():
    """Allow manual entry of Facebook tokens."""
    print("=" * 70)
    print("🔑 Manual Facebook Token Entry")
    print("=" * 70)
    print()
    print("Use this when Graph API Explorer doesn't work or app is deactivated.")
    print()
    
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    page_id = api_keys.get('facebook_page_id', '617021748762367')
    existing_token = api_keys.get('facebook_page_access_token')
    
    print(f"📄 Target Page ID: {page_id}")
    if existing_token:
        print(f"🔑 Current Token: {existing_token[:30]}...")
    print()
    
    print("=" * 70)
    print("📋 Option 1: Enter Page Access Token Directly")
    print("=" * 70)
    print()
    print("You can get a Page Access Token from:")
    print("  1. Facebook Page Settings → Page Access")
    print("  2. Graph API Explorer (if app is active)")
    print("  3. Another tool that has access")
    print()
    
    # Get token from command line or environment
    page_token = None
    if len(sys.argv) > 1:
        page_token = sys.argv[1]
        print(f"✅ Using token from command line argument")
    elif os.getenv('FACEBOOK_PAGE_TOKEN'):
        page_token = os.getenv('FACEBOOK_PAGE_TOKEN')
        print(f"✅ Using token from environment variable")
    else:
        print("💡 Usage:")
        print("   python3 scripts/manual_token_entry.py YOUR_PAGE_TOKEN")
        print()
        print("   Or set environment variable:")
        print("   FACEBOOK_PAGE_TOKEN=your_token python3 scripts/manual_token_entry.py")
        print()
        return False
    
    if not page_token:
        return False
    
    page_token = page_token.strip()
    
    print()
    print("🔍 Testing token...")
    print()
    
    # Test token
    test_url = f"https://graph.facebook.com/v18.0/{page_id}"
    test_params = {
        'access_token': page_token,
        'fields': 'id,name'
    }
    
    try:
        response = requests.get(test_url, params=test_params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            page_name = data.get('name', 'Unknown')
            print(f"✅ Token is VALID!")
            print(f"✅ Can access page: {page_name}")
            print()
            
            # Try to get Instagram
            print("🔍 Fetching Instagram Business Account ID...")
            print()
            
            ig_url = f"https://graph.facebook.com/v18.0/{page_id}"
            ig_params = {
                'fields': 'instagram_business_account{id,username}',
                'access_token': page_token
            }
            
            ig_account_id = None
            ig_username = None
            
            try:
                ig_response = requests.get(ig_url, params=ig_params, timeout=10)
                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    ig_account = ig_data.get('instagram_business_account')
                    if ig_account:
                        ig_account_id = ig_account.get('id')
                        ig_username = ig_account.get('username')
                        print(f"✅ Found Instagram Business Account!")
                        print(f"   Account ID: {ig_account_id}")
                        print(f"   Username: @{ig_username}")
                    else:
                        print("⚠️  Instagram not connected to this page")
                        print("   Connect Instagram in Facebook Page → Settings → Instagram")
            except Exception as e:
                print(f"⚠️  Could not fetch Instagram: {e}")
            
            # Save to config
            print()
            print("💾 Saving configuration...")
            print()
            
            api_keys['facebook_page_access_token'] = page_token
            api_keys['facebook_page_id'] = page_id
            
            if ig_account_id:
                api_keys['instagram_business_account_id'] = ig_account_id
            
            settings['api_keys'] = api_keys
            save_settings_to_db(settings)
            
            # Update MY_CONFIG.json
            config_file = Path('MY_CONFIG.json')
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                config['api_keys']['facebook_page_access_token'] = page_token
                config['api_keys']['facebook_page_id'] = page_id
                
                if ig_account_id:
                    config['api_keys']['instagram_business_account_id'] = ig_account_id
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
            
            print("✅ Configuration saved!")
            print()
            print("=" * 70)
            print("✅ Success!")
            print("=" * 70)
            print()
            print("📝 Summary:")
            print(f"   ✅ Facebook Page Access Token: {page_token[:30]}...")
            print(f"   ✅ Facebook Page ID: {page_id}")
            if ig_account_id:
                print(f"   ✅ Instagram Business Account ID: {ig_account_id}")
                print(f"   ✅ Instagram Username: @{ig_username}")
            print()
            print("🚀 You're ready to test video uploads!")
            
            return True
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"❌ Token is INVALID: {error_msg}")
            print()
            print("💡 Make sure:")
            print("   1. Token is a Page Access Token (not User Token)")
            print("   2. Token has not expired")
            print("   3. Token has permissions for this page")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

if __name__ == '__main__':
    try:
        success = manual_token_entry()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

