#!/usr/bin/env python3
"""
Get Facebook Page Access Token using Graph API Explorer method.
This bypasses the OAuth flow and uses a simpler approach.
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db, save_settings_to_db

def get_token_via_graph_explorer(user_token=None):
    """
    Guide user to get token via Graph API Explorer (most reliable method).
    This is the recommended way when OAuth is unavailable.
    """
    print("=" * 70)
    print("🔑 Get Facebook Page Access Token (Graph API Explorer Method)")
    print("=" * 70)
    print()
    print("📋 This method uses Facebook's Graph API Explorer (no OAuth needed).")
    print()
    
    # Load existing settings
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    app_id = api_keys.get('facebook_app_id', '421181512329379')
    page_id = api_keys.get('facebook_page_id', '617021748762367')
    
    print(f"📱 App ID: {app_id}")
    print(f"📄 Page ID: {page_id}")
    print()
    
    # If token not provided, show instructions
    if not user_token:
        print("=" * 70)
        print("📋 Step-by-Step Instructions")
        print("=" * 70)
        print()
        print("Step 1: Open Graph API Explorer")
        print("   👉 https://developers.facebook.com/tools/explorer/")
        print()
        print("Step 2: Select Your App")
        print(f"   - Click the dropdown (top right) that says 'Meta App' or 'Select an app'")
        print(f"   - Select your app: {app_id}")
        print()
        print("Step 3: Get User Access Token")
        print("   - Click 'Get Token' button (top right)")
        print("   - Select 'Get User Access Token'")
        print("   - In the popup, check these permissions:")
        print("     ✅ pages_manage_posts")
        print("     ✅ pages_read_engagement")
        print("     ✅ pages_show_list")
        print("     ✅ instagram_basic")
        print("     ✅ instagram_content_publish")
        print("     ✅ business_management")
        print("   - Click 'Generate Access Token'")
        print("   - Authorize if prompted")
        print("   - Copy the token that appears")
        print()
        print("=" * 70)
        print()
        print("💡 Usage:")
        print("   python3 scripts/get_facebook_token_v2.py <your-user-token>")
        print()
        print("   Or provide token as environment variable:")
        print("   FACEBOOK_USER_TOKEN=your_token python3 scripts/get_facebook_token_v2.py")
        print()
        return False
    
    user_token = user_token.strip()
    
    if user_token:
        print()
        print("Step 4: Getting Page Access Token...")
        print()
        
        # Get pages
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
                print("❌ No pages found.")
                print("   Make sure you have admin access to a Facebook Page.")
                return False
            
            print(f"✅ Found {len(pages)} page(s):")
            print()
            
            # Find target page
            target_page = None
            if page_id:
                target_page = next((p for p in pages if p.get('id') == page_id), None)
            
            if not target_page and len(pages) == 1:
                target_page = pages[0]
            elif not target_page:
                print("Available pages:")
                for i, page in enumerate(pages, 1):
                    marker = "👉" if page.get('id') == page_id else "  "
                    print(f"   {marker} {i}. {page.get('name')} (ID: {page.get('id')})")
                print()
                target_page = pages[0]
                print(f"Using: {target_page.get('name')}")
            
            page_token = target_page.get('access_token')
            page_id_found = target_page.get('id')
            page_name = target_page.get('name')
            
            print()
            print(f"✅ Got Page Access Token for: {page_name}")
            print(f"   Page ID: {page_id_found}")
            print(f"   Token: {page_token[:30]}...")
            print()
            
            # Try to get Instagram Account ID
            print("Step 5: Getting Instagram Business Account ID...")
            print()
            
            ig_url = f"https://graph.facebook.com/v18.0/{page_id_found}"
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
            except Exception as e:
                print(f"⚠️  Could not fetch Instagram: {e}")
                print("   You can add it manually later.")
            
            # Save to config
            print()
            print("Step 6: Saving Configuration...")
            print()
            
            api_keys['facebook_page_access_token'] = page_token
            api_keys['facebook_page_id'] = page_id_found
            
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
                config['api_keys']['facebook_page_id'] = page_id_found
                
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
            print(f"   ✅ Facebook Page ID: {page_id_found}")
            if ig_account_id:
                print(f"   ✅ Instagram Business Account ID: {ig_account_id}")
                print(f"   ✅ Instagram Username: @{ig_username}")
            print()
            print("🚀 You're ready to test video uploads!")
            
            return True
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error: {e}")
            if e.response.status_code == 401:
                print("   Your User Access Token is invalid or expired.")
                print("   Please get a new token from Graph API Explorer.")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("❌ No token provided.")
        return False


if __name__ == '__main__':
    try:
        success = get_token_via_graph_explorer()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

