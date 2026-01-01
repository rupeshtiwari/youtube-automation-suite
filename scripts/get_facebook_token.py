#!/usr/bin/env python3
"""
Interactive helper script to get Facebook Page Access Token.
This script guides you through the process step-by-step.
"""

import sys
import os
import webbrowser
import json
from urllib.parse import urlencode

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db

def get_facebook_token():
    """Interactive helper to get Facebook Page Access Token."""
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    app_id = api_keys.get('facebook_app_id', '421181512329379')
    page_id = api_keys.get('facebook_page_id', '617021748762367')
    
    print("=" * 60)
    print("🔑 Facebook Page Access Token Helper")
    print("=" * 60)
    print()
    print(f"App ID: {app_id}")
    print(f"Page ID: {page_id}")
    print()
    
    # Step 1: Open Graph API Explorer
    print("📋 Step 1: Getting User Access Token")
    print("-" * 60)
    print()
    print("I'll open the Graph API Explorer for you...")
    print()
    
    # Build Graph API Explorer URL with pre-filled parameters
    permissions = [
        'pages_manage_posts',
        'pages_read_engagement',
        'instagram_basic',
        'instagram_content_publish',
        'business_management'
    ]
    
    explorer_url = f"https://developers.facebook.com/tools/explorer/?version=v18.0"
    
    print(f"🌐 Opening: {explorer_url}")
    print()
    print("📝 Instructions:")
    print("   1. Select your App in the dropdown (top right)")
    print(f"   2. Add these permissions: {', '.join(permissions)}")
    print("   3. Click 'Generate Access Token'")
    print("   4. Authorize if prompted")
    print("   5. Copy the token that appears")
    print()
    
    try:
        webbrowser.open(explorer_url)
        print("✅ Browser opened!")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")
        print(f"   Please manually visit: {explorer_url}")
    
    print()
    input("Press Enter when you have copied the User Access Token...")
    print()
    
    # Step 2: Get Page Access Token
    print("📋 Step 2: Getting Page Access Token")
    print("-" * 60)
    print()
    user_token = input("Paste your User Access Token here: ").strip()
    
    if not user_token:
        print("❌ No token provided. Exiting.")
        return None
    
    print()
    print("🔍 Fetching your Facebook Pages...")
    print()
    
    import requests
    
    # Get user's pages
    url = f"https://graph.facebook.com/v18.0/me/accounts"
    params = {
        'access_token': user_token,
        'fields': 'id,name,access_token'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get('data', [])
        
        if not pages:
            print("❌ No pages found. Make sure you have:")
            print("   - Admin access to a Facebook Page")
            print("   - The 'pages_manage_posts' permission")
            return None
        
        print(f"✅ Found {len(pages)} page(s):")
        print()
        
        # Find the target page
        target_page = None
        for i, page in enumerate(pages, 1):
            page_id_found = page.get('id')
            page_name = page.get('name', 'Unknown')
            is_target = (page_id_found == page_id)
            
            marker = "👉" if is_target else "  "
            print(f"{marker} {i}. {page_name} (ID: {page_id_found})")
            
            if is_target:
                target_page = page
        
        print()
        
        if target_page:
            page_token = target_page.get('access_token')
            print(f"✅ Found your target page!")
            print(f"   Page: {target_page.get('name')}")
            print(f"   Page Access Token: {page_token[:30]}...")
            print()
            
            # Step 3: Exchange for long-lived token (optional)
            print("📋 Step 3: Making Token Long-Lived (Optional)")
            print("-" * 60)
            print()
            make_long = input("Make this token long-lived? (y/n, default: y): ").strip().lower()
            
            if make_long != 'n':
                app_secret = api_keys.get('facebook_app_secret')
                if not app_secret:
                    print()
                    print("⚠️  Facebook App Secret not found in config.")
                    print("   Long-lived tokens require App Secret.")
                    print("   You can:")
                    print("   1. Add 'facebook_app_secret' to MY_CONFIG.json")
                    print("   2. Or use the short-lived token (expires in ~1 hour)")
                    print()
                    use_short = input("Use short-lived token? (y/n, default: y): ").strip().lower()
                    if use_short == 'n':
                        return None
                else:
                    print()
                    print("🔄 Exchanging for long-lived token...")
                    
                    exchange_url = "https://graph.facebook.com/v18.0/oauth/access_token"
                    exchange_params = {
                        'grant_type': 'fb_exchange_token',
                        'client_id': app_id,
                        'client_secret': app_secret,
                        'fb_exchange_token': page_token
                    }
                    
                    try:
                        exchange_response = requests.get(exchange_url, params=exchange_params)
                        exchange_response.raise_for_status()
                        exchange_data = exchange_response.json()
                        page_token = exchange_data.get('access_token')
                        expires_in = exchange_data.get('expires_in', 0)
                        days = expires_in // 86400
                        print(f"✅ Long-lived token created! (expires in {days} days)")
                    except Exception as e:
                        print(f"⚠️  Could not exchange token: {e}")
                        print("   Using short-lived token instead.")
            
            # Step 4: Update config
            print()
            print("📋 Step 4: Update Configuration")
            print("-" * 60)
            print()
            print(f"Your Page Access Token:")
            print(f"  {page_token}")
            print()
            
            update = input("Update MY_CONFIG.json with this token? (y/n, default: y): ").strip().lower()
            
            if update != 'n':
                config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MY_CONFIG.json')
                
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    config['api_keys']['facebook_page_access_token'] = page_token
                    
                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    print()
                    print("✅ Updated MY_CONFIG.json!")
                    print()
                    print("📝 Next steps:")
                    print("   1. Load config: python3 scripts/load_config.py")
                    print("   2. Test Instagram: python3 scripts/get_instagram_account_id.py")
                    
                except Exception as e:
                    print(f"❌ Error updating config: {e}")
                    print()
                    print("📝 Please manually update MY_CONFIG.json:")
                    print(f'   "facebook_page_access_token": "{page_token}"')
            
            return page_token
        else:
            print(f"⚠️  Target page (ID: {page_id}) not found in your pages.")
            print()
            print("Available pages:")
            for i, page in enumerate(pages, 1):
                print(f"   {i}. {page.get('name')} (ID: {page.get('id')})")
            print()
            print("You can:")
            print("   1. Use one of the pages above (update page_id in config)")
            print("   2. Make sure you have admin access to the target page")
            
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        if e.response.status_code == 401:
            print("   Your User Access Token is invalid or expired.")
            print("   Please get a new token from Graph API Explorer.")
        else:
            error_data = e.response.json() if e.response.content else {}
            print(f"   Error details: {error_data}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    token = get_facebook_token()
    sys.exit(0 if token else 1)

