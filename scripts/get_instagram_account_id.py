#!/usr/bin/env python3
"""
Helper script to get Instagram Business Account ID from Facebook Page.
This uses your Facebook Page Access Token to fetch the connected Instagram account.
"""

import sys
import os
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db

def get_instagram_business_account_id():
    """Get Instagram Business Account ID from Facebook Page."""
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    page_id = api_keys.get('facebook_page_id')
    page_access_token = api_keys.get('facebook_page_access_token')
    
    if not page_id:
        print("❌ Error: Facebook Page ID not found in config")
        print("   Please add 'facebook_page_id' to MY_CONFIG.json")
        return None
    
    if not page_access_token:
        print("❌ Error: Facebook Page Access Token not found in config")
        print("   Please add 'facebook_page_access_token' to MY_CONFIG.json")
        return None
    
    print(f"📡 Fetching Instagram Business Account ID for Page: {page_id}")
    print(f"   Using Page Access Token: {page_access_token[:20]}...")
    
    # Make API call to get Instagram Business Account
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        'fields': 'instagram_business_account',
        'access_token': page_access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'instagram_business_account' in data:
            ig_account = data['instagram_business_account']
            ig_account_id = ig_account.get('id')
            ig_username = ig_account.get('username', 'N/A')
            
            print(f"\n✅ Success! Found Instagram Business Account:")
            print(f"   Account ID: {ig_account_id}")
            print(f"   Username: @{ig_username}")
            print(f"\n📝 Add this to MY_CONFIG.json:")
            print(f'   "instagram_business_account_id": "{ig_account_id}"')
            
            return ig_account_id
        else:
            print("\n❌ Error: No Instagram Business Account found")
            print("   Make sure:")
            print("   1. Your Instagram account is a Business Account (not Personal)")
            print("   2. Your Instagram Business Account is connected to your Facebook Page")
            print("   3. Go to Facebook Page → Settings → Instagram to connect")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        if e.response.status_code == 401:
            print("   Your Page Access Token may be expired or invalid")
            print("   Get a new token from: https://developers.facebook.com/tools/explorer/")
        elif e.response.status_code == 400:
            error_data = e.response.json()
            print(f"   Error details: {error_data}")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    account_id = get_instagram_business_account_id()
    sys.exit(0 if account_id else 1)

