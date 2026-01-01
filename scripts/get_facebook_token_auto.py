#!/usr/bin/env python3
"""
Automated script to get Facebook tokens - tries multiple methods automatically.
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db, save_settings_to_db

def get_page_token_from_user_token(user_token, target_page_id=None):
    """Get Page Access Token from User Access Token."""
    print("🔍 Fetching Facebook Pages...")
    
    pages_url = "https://graph.facebook.com/v18.0/me/accounts"
    params = {
        'access_token': user_token,
        'fields': 'id,name,access_token'
    }
    
    try:
        response = requests.get(pages_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get('data', [])
        
        if not pages:
            return None, None, "No pages found"
        
        # Find target page
        target_page = None
        if target_page_id:
            target_page = next((p for p in pages if p.get('id') == target_page_id), None)
        
        if not target_page:
            target_page = pages[0]
        
        page_token = target_page.get('access_token')
        page_id = target_page.get('id')
        page_name = target_page.get('name')
        
        return page_token, page_id, page_name
        
    except Exception as e:
        return None, None, str(e)

def get_instagram_account_id(page_id, page_token):
    """Get Instagram Business Account ID."""
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'fields': 'instagram_business_account{id,username}',
            'access_token': page_token
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ig_account = data.get('instagram_business_account')
            if ig_account:
                return ig_account.get('id'), ig_account.get('username')
        return None, None
    except:
        return None, None

def auto_get_tokens():
    """Automated token fetching - provides instructions and processes results."""
    print("=" * 70)
    print("🔑 Automated Facebook Token Fetcher")
    print("=" * 70)
    print()
    
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    app_id = api_keys.get('facebook_app_id', '421181512329379')
    page_id = api_keys.get('facebook_page_id', '617021748762367')
    
    print(f"📱 App ID: {app_id}")
    print(f"📄 Target Page ID: {page_id}")
    print()
    
    print("=" * 70)
    print("📋 Instructions to Get User Access Token")
    print("=" * 70)
    print()
    print("1. Open: https://developers.facebook.com/tools/explorer/")
    print("2. Select your App in the dropdown (top right)")
    print("3. Click 'Get Token' → 'Get User Access Token'")
    print("4. Check these permissions:")
    print("   ✅ pages_manage_posts")
    print("   ✅ pages_read_engagement")
    print("   ✅ pages_show_list")
    print("   ✅ instagram_basic")
    print("   ✅ instagram_content_publish")
    print("   ✅ business_management")
    print("5. Click 'Generate Access Token'")
    print("6. Authorize if prompted")
    print("7. Copy the token from the 'Access Token' field")
    print()
    print("=" * 70)
    print()
    
    # Since we can't get interactive input in automated mode, 
    # we'll check if there's a way to get token from existing config
    # or provide clear next steps
    
    existing_token = api_keys.get('facebook_page_access_token')
    
    if existing_token:
        print(f"🔑 Found existing token: {existing_token[:30]}...")
        print("   Testing if it's valid...")
        
        # Test token
        test_url = f"https://graph.facebook.com/v18.0/{page_id}"
        test_params = {'access_token': existing_token, 'fields': 'id,name'}
        
        try:
            test_response = requests.get(test_url, params=test_params, timeout=10)
            if test_response.status_code == 200:
                print("   ✅ Token is valid!")
                
                # Try to get Instagram
                ig_id, ig_username = get_instagram_account_id(page_id, existing_token)
                if ig_id:
                    print(f"   ✅ Instagram Account ID: {ig_id}")
                    if ig_username:
                        print(f"   ✅ Instagram Username: @{ig_username}")
                    
                    # Update config
                    api_keys['instagram_business_account_id'] = ig_id
                    settings['api_keys'] = api_keys
                    save_settings_to_db(settings)
                    
                    # Update MY_CONFIG.json
                    config_file = Path('MY_CONFIG.json')
                    if config_file.exists():
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        config['api_keys']['instagram_business_account_id'] = ig_id
                        with open(config_file, 'w') as f:
                            json.dump(config, f, indent=2)
                    
                    print()
                    print("✅ Configuration updated with Instagram Account ID!")
                    return True
                else:
                    print("   ⚠️  Instagram Account ID not found")
                    print("   Make sure Instagram is connected to Facebook Page")
            else:
                error_data = test_response.json() if test_response.content else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Token is invalid: {error_msg}")
                print()
                print("💡 You need to get a new token:")
                print("   1. Follow the instructions above")
                print("   2. Get User Access Token from Graph API Explorer")
                print("   3. Then run this script with the token")
        except Exception as e:
            print(f"   ❌ Error testing token: {e}")
    else:
        print("❌ No existing token found.")
        print()
        print("💡 To get a token:")
        print("   1. Follow the instructions above")
        print("   2. Get User Access Token from Graph API Explorer")
        print("   3. Then provide it to update your config")
    
    print()
    print("=" * 70)
    print("📝 Summary")
    print("=" * 70)
    print()
    print("Current Status:")
    print(f"   Facebook App ID: {app_id}")
    print(f"   Facebook Page ID: {page_id}")
    print(f"   Page Access Token: {'✅ Configured' if existing_token else '❌ Missing'}")
    print(f"   Instagram Account ID: {'✅ Configured' if api_keys.get('instagram_business_account_id') else '❌ Missing'}")
    print()
    print("Next Steps:")
    print("   1. Get User Access Token from Graph API Explorer (instructions above)")
    print("   2. Run: python3 scripts/get_facebook_token_v2.py")
    print("   3. Paste your User Access Token when prompted")
    print("   4. Script will automatically get Page Token and Instagram ID")
    print()
    
    return False

if __name__ == '__main__':
    try:
        success = auto_get_tokens()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

