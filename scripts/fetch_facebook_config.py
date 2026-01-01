#!/usr/bin/env python3
"""
Automated script to fetch all Facebook configuration data using OAuth.
Similar to YouTube authentication - opens browser, gets authorization, fetches all data.

Usage:
    python3 scripts/fetch_facebook_config.py
    
    Or use the helper script:
    ./scripts/run_with_venv.sh fetch_facebook_config.py
"""

import sys
import os
import json
import webbrowser
import http.server
import socketserver
import urllib.parse
from urllib.parse import urlparse, parse_qs
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db, save_settings_to_db

# Configuration
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = [
    'pages_manage_posts',
    'pages_read_engagement',
    'instagram_basic',
    'instagram_content_publish',
    'business_management',
    'pages_show_list'
]

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback."""
    
    def do_GET(self):
        """Handle GET request from OAuth callback."""
        if self.path.startswith('/callback'):
            query = urlparse(self.path).query
            params = parse_qs(query)
            
            if 'code' in params:
                code = params['code'][0]
                self.server.auth_code = code
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html_content = """
                    <html>
                    <head><title>Authorization Successful</title></head>
                    <body>
                        <h1>✅ Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                        <script>setTimeout(function(){window.close();}, 3000);</script>
                    </body>
                    </html>
                """
                self.wfile.write(html_content.encode('utf-8'))
            else:
                error = params.get('error', ['Unknown error'])[0]
                self.server.auth_error = error
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html_content = f"""
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body>
                        <h1>❌ Authorization Failed</h1>
                        <p>Error: {error}</p>
                        <p>Please check the terminal for details.</p>
                    </body>
                    </html>
                """
                self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def get_facebook_config():
    """Fetch all Facebook configuration data using OAuth."""
    print("=" * 70)
    print("🔑 Facebook Configuration Auto-Fetcher")
    print("=" * 70)
    print()
    
    # Load existing settings
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    app_id = api_keys.get('facebook_app_id')
    app_secret = api_keys.get('facebook_app_secret')
    page_id = api_keys.get('facebook_page_id')
    
    if not app_id:
        print("❌ Error: Facebook App ID not found in config.")
        print("   Please add 'facebook_app_id' to MY_CONFIG.json first.")
        return False
    
    if not app_secret:
        print("⚠️  Warning: Facebook App Secret not found.")
        print("   Some features may not work. You can add it manually later.")
        print()
        app_secret = input("Enter Facebook App Secret (or press Enter to skip): ").strip()
        if app_secret:
            api_keys['facebook_app_secret'] = app_secret
            settings['api_keys'] = api_keys
            save_settings_to_db(settings)
    
    print(f"📱 App ID: {app_id}")
    if page_id:
        print(f"📄 Page ID: {page_id}")
    print()
    
    # Step 1: Get authorization code
    print("📋 Step 1: Getting Authorization")
    print("-" * 70)
    print()
    
    auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope={','.join(SCOPES)}&"
        f"response_type=code"
    )
    
    print("🌐 Opening browser for Facebook authorization...")
    print(f"   URL: {auth_url}")
    print()
    print("📝 Instructions:")
    print("   1. Log in to Facebook if needed")
    print("   2. Authorize the app")
    print("   3. You'll be redirected back automatically")
    print()
    
    # Start local server to receive callback
    with socketserver.TCPServer(("", 8080), OAuthCallbackHandler) as httpd:
        httpd.auth_code = None
        httpd.auth_error = None
        
        try:
            webbrowser.open(auth_url)
            print("⏳ Waiting for authorization...")
            print("   (If browser doesn't open, visit the URL manually)")
            print()
            
            # Wait for callback (timeout after 5 minutes)
            httpd.timeout = 300
            httpd.handle_request()
            
            if httpd.auth_error:
                print(f"❌ Authorization failed: {httpd.auth_error}")
                return False
            
            if not httpd.auth_code:
                print("❌ No authorization code received.")
                print("   Make sure you authorized the app and completed the flow.")
                return False
            
            auth_code = httpd.auth_code
            print("✅ Authorization received!")
            print()
            
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user.")
            return False
        except Exception as e:
            print(f"❌ Error during authorization: {e}")
            return False
    
    # Step 2: Exchange code for access token
    print("📋 Step 2: Getting Access Token")
    print("-" * 70)
    print()
    
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    token_params = {
        'client_id': app_id,
        'client_secret': app_secret if app_secret else '',
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }
    
    print("🔄 Exchanging authorization code for access token...")
    
    try:
        response = requests.get(token_url, params=token_params)
        response.raise_for_status()
        
        token_data = response.json()
        user_access_token = token_data.get('access_token')
        
        if not user_access_token:
            print("❌ Failed to get access token.")
            print(f"   Response: {token_data}")
            return False
        
        print("✅ Got User Access Token!")
        print()
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error getting access token: {e}")
        if e.response.status_code == 400:
            error_data = e.response.json()
            print(f"   Error details: {error_data}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 3: Get Page Access Token
    print("📋 Step 3: Getting Page Access Token")
    print("-" * 70)
    print()
    
    print("🔍 Fetching your Facebook Pages...")
    
    pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
    pages_params = {
        'access_token': user_access_token,
        'fields': 'id,name,access_token,category'
    }
    
    try:
        response = requests.get(pages_url, params=pages_params)
        response.raise_for_status()
        
        pages_data = response.json()
        pages = pages_data.get('data', [])
        
        if not pages:
            print("❌ No pages found.")
            print("   Make sure you have admin access to at least one Facebook Page.")
            return False
        
        print(f"✅ Found {len(pages)} page(s):")
        print()
        
        # Find target page or let user choose
        target_page = None
        if page_id:
            target_page = next((p for p in pages if p.get('id') == page_id), None)
        
        if not target_page and len(pages) == 1:
            target_page = pages[0]
            print(f"   Using only available page: {target_page.get('name')}")
        elif not target_page:
            print("   Available pages:")
            for i, page in enumerate(pages, 1):
                marker = "👉" if page.get('id') == page_id else "  "
                print(f"   {marker} {i}. {page.get('name')} (ID: {page.get('id')})")
            print()
            
            if page_id:
                print(f"⚠️  Target page ID {page_id} not found.")
                choice = input(f"Use page 1? (y/n, default: y): ").strip().lower()
                if choice != 'n':
                    target_page = pages[0]
            else:
                choice = input(f"Select page (1-{len(pages)}, default: 1): ").strip()
                try:
                    idx = int(choice) - 1 if choice else 0
                    target_page = pages[idx]
                except (ValueError, IndexError):
                    target_page = pages[0]
        
        if not target_page:
            print("❌ No page selected.")
            return False
        
        page_access_token = target_page.get('access_token')
        page_name = target_page.get('name')
        page_id_found = target_page.get('id')
        
        print(f"✅ Selected page: {page_name} (ID: {page_id_found})")
        print(f"   Page Access Token: {page_access_token[:30]}...")
        print()
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error fetching pages: {e}")
        if e.response.status_code == 401:
            print("   Your access token may be invalid or expired.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 4: Get Instagram Business Account ID
    print("📋 Step 4: Getting Instagram Business Account ID")
    print("-" * 70)
    print()
    
    print("🔍 Fetching Instagram Business Account...")
    
    ig_url = f"https://graph.facebook.com/v18.0/{page_id_found}"
    ig_params = {
        'access_token': page_access_token,
        'fields': 'instagram_business_account{id,username}'
    }
    
    instagram_account_id = None
    instagram_username = None
    
    try:
        response = requests.get(ig_url, params=ig_params)
        response.raise_for_status()
        
        data = response.json()
        ig_account = data.get('instagram_business_account')
        
        if ig_account:
            instagram_account_id = ig_account.get('id')
            instagram_username = ig_account.get('username')
            print(f"✅ Found Instagram Business Account!")
            print(f"   Account ID: {instagram_account_id}")
            print(f"   Username: @{instagram_username}")
        else:
            print("⚠️  No Instagram Business Account found.")
            print("   Make sure:")
            print("   1. Your Instagram account is a Business Account (not Personal)")
            print("   2. Your Instagram is connected to this Facebook Page")
            print("   3. Go to Facebook Page → Settings → Instagram to connect")
            print()
            print("   You can add the Instagram Account ID manually later.")
        
        print()
        
    except requests.exceptions.HTTPError as e:
        print(f"⚠️  Could not fetch Instagram account: {e}")
        if e.response.status_code == 401:
            print("   Your Page Access Token may not have the right permissions.")
        print("   You can add the Instagram Account ID manually later.")
        print()
    
    # Step 5: Exchange for long-lived token (optional)
    print("📋 Step 5: Making Token Long-Lived")
    print("-" * 70)
    print()
    
    if app_secret:
        print("🔄 Exchanging for long-lived token...")
        
        exchange_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        exchange_params = {
            'grant_type': 'fb_exchange_token',
            'client_id': app_id,
            'client_secret': app_secret,
            'fb_exchange_token': page_access_token
        }
        
        try:
            response = requests.get(exchange_url, params=exchange_params)
            response.raise_for_status()
            
            exchange_data = response.json()
            long_lived_token = exchange_data.get('access_token')
            expires_in = exchange_data.get('expires_in', 0)
            days = expires_in // 86400 if expires_in else 0
            
            if long_lived_token:
                page_access_token = long_lived_token
                print(f"✅ Long-lived token created! (expires in {days} days)")
            else:
                print("⚠️  Could not exchange token. Using short-lived token.")
        except Exception as e:
            print(f"⚠️  Could not exchange token: {e}")
            print("   Using short-lived token (expires in ~1 hour).")
    else:
        print("⚠️  App Secret not available. Using short-lived token.")
        print("   Add App Secret to config for long-lived tokens.")
    
    print()
    
    # Step 6: Update configuration
    print("📋 Step 6: Updating Configuration")
    print("-" * 70)
    print()
    
    # Update settings
    api_keys['facebook_page_access_token'] = page_access_token
    api_keys['facebook_page_id'] = page_id_found
    
    if app_secret:
        api_keys['facebook_app_secret'] = app_secret
    
    if instagram_account_id:
        api_keys['instagram_business_account_id'] = instagram_account_id
    
    settings['api_keys'] = api_keys
    save_settings_to_db(settings)
    
    # Also update MY_CONFIG.json
    config_file = Path('MY_CONFIG.json')
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config['api_keys']['facebook_page_access_token'] = page_access_token
            config['api_keys']['facebook_page_id'] = page_id_found
            
            if app_secret:
                config['api_keys']['facebook_app_secret'] = app_secret
            
            if instagram_account_id:
                config['api_keys']['instagram_business_account_id'] = instagram_account_id
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Updated MY_CONFIG.json!")
        except Exception as e:
            print(f"⚠️  Could not update MY_CONFIG.json: {e}")
            print("   But settings were saved to database.")
    
    print()
    print("=" * 70)
    print("✅ Configuration Complete!")
    print("=" * 70)
    print()
    print("📝 Summary:")
    print(f"   ✅ Facebook Page Access Token: {page_access_token[:30]}...")
    print(f"   ✅ Facebook Page ID: {page_id_found}")
    if app_secret:
        print(f"   ✅ Facebook App Secret: {'*' * 20}")
    if instagram_account_id:
        print(f"   ✅ Instagram Business Account ID: {instagram_account_id}")
        print(f"   ✅ Instagram Username: @{instagram_username}")
    else:
        print(f"   ⚠️  Instagram Business Account ID: Not found (add manually)")
    print()
    print("🚀 Next steps:")
    print("   1. Test Instagram: python3 scripts/get_instagram_account_id.py")
    print("   2. Test video uploads: Ready to test!")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = get_facebook_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

