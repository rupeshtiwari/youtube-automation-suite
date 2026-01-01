#!/usr/bin/env python3
"""
Create or refresh Facebook Page Access Token via CLI.
Checks if token exists and is valid, creates new one if needed.
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


def check_token_validity(token, page_id=None):
    """Check if a Facebook token is valid."""
    if not token:
        return False, "Token is empty"
    
    try:
        # Test token by getting user info
        url = "https://graph.facebook.com/v18.0/me"
        params = {'access_token': token}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            # If page_id provided, check if we can access that page
            if page_id:
                page_url = f"https://graph.facebook.com/v18.0/{page_id}"
                page_params = {'access_token': token, 'fields': 'id,name'}
                page_response = requests.get(page_url, params=page_params, timeout=10)
                if page_response.status_code == 200:
                    return True, "Token is valid and can access page"
                else:
                    return False, f"Token valid but cannot access page: {page_response.json().get('error', {}).get('message', 'Unknown error')}"
            return True, "Token is valid"
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            return False, f"Token invalid: {error_msg}"
    except Exception as e:
        return False, f"Error checking token: {str(e)}"


def get_user_access_token(app_id, app_secret=None):
    """Get User Access Token via OAuth."""
    print("📋 Step 1: Getting User Access Token via OAuth")
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
    print()
    print("📝 Instructions:")
    print("   1. Log in to Facebook if needed")
    print("   2. Authorize the app with all requested permissions")
    print("   3. You'll be redirected back automatically")
    print()
    
    # Start local server to receive callback
    with socketserver.TCPServer(("", 8080), OAuthCallbackHandler) as httpd:
        httpd.auth_code = None
        httpd.auth_error = None
        
        try:
            webbrowser.open(auth_url)
            print("⏳ Waiting for authorization (timeout: 5 minutes)...")
            print("   (If browser doesn't open, visit the URL manually)")
            print()
            
            # Wait for callback (timeout after 5 minutes)
            httpd.timeout = 300
            httpd.handle_request()
            
            if httpd.auth_error:
                print(f"❌ Authorization failed: {httpd.auth_error}")
                return None
            
            if not httpd.auth_code:
                print("❌ No authorization code received.")
                print("   Make sure you authorized the app and completed the flow.")
                return None
            
            auth_code = httpd.auth_code
            print("✅ Authorization code received!")
            print()
            
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user.")
            return None
        except Exception as e:
            print(f"❌ Error during authorization: {e}")
            return None
    
    # Exchange code for access token
    print("🔄 Exchanging authorization code for access token...")
    
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    token_params = {
        'client_id': app_id,
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }
    
    if app_secret:
        token_params['client_secret'] = app_secret
    
    try:
        response = requests.get(token_url, params=token_params, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        user_access_token = token_data.get('access_token')
        
        if not user_access_token:
            print("❌ Failed to get access token.")
            print(f"   Response: {token_data}")
            return None
        
        print("✅ Got User Access Token!")
        print()
        return user_access_token
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error getting access token: {e}")
        if e.response.status_code == 400:
            error_data = e.response.json()
            print(f"   Error details: {error_data}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_page_access_token(user_token, target_page_id=None):
    """Get Page Access Token from User Access Token."""
    print("📋 Step 2: Getting Page Access Token")
    print("-" * 70)
    print()
    
    print("🔍 Fetching your Facebook Pages...")
    
    pages_url = "https://graph.facebook.com/v18.0/me/accounts"
    pages_params = {
        'access_token': user_token,
        'fields': 'id,name,access_token,category'
    }
    
    try:
        response = requests.get(pages_url, params=pages_params, timeout=10)
        response.raise_for_status()
        
        pages_data = response.json()
        pages = pages_data.get('data', [])
        
        if not pages:
            print("❌ No pages found.")
            print("   Make sure you have admin access to at least one Facebook Page.")
            return None
        
        print(f"✅ Found {len(pages)} page(s):")
        print()
        
        # Find target page or let user choose
        target_page = None
        if target_page_id:
            target_page = next((p for p in pages if p.get('id') == target_page_id), None)
        
        if not target_page and len(pages) == 1:
            target_page = pages[0]
            print(f"   Using only available page: {target_page.get('name')}")
        elif not target_page:
            print("   Available pages:")
            for i, page in enumerate(pages, 1):
                marker = "👉" if page.get('id') == target_page_id else "  "
                print(f"   {marker} {i}. {page.get('name')} (ID: {page.get('id')})")
            print()
            
            if target_page_id:
                print(f"⚠️  Target page ID {target_page_id} not found.")
                print(f"   Using first available page: {pages[0].get('name')}")
                target_page = pages[0]
            else:
                target_page = pages[0]
                print(f"   Using first page: {target_page.get('name')}")
        
        if not target_page:
            print("❌ No page selected.")
            return None
        
        page_access_token = target_page.get('access_token')
        page_name = target_page.get('name')
        page_id_found = target_page.get('id')
        
        print(f"✅ Selected page: {page_name} (ID: {page_id_found})")
        print(f"   Page Access Token: {page_access_token[:30]}...")
        print()
        
        return page_access_token, page_id_found
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error fetching pages: {e}")
        if e.response.status_code == 401:
            print("   Your access token may be invalid or expired.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def exchange_for_long_lived_token(short_token, app_id, app_secret):
    """Exchange short-lived token for long-lived token."""
    if not app_secret:
        return short_token, False
    
    print("🔄 Exchanging for long-lived token...")
    
    exchange_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    exchange_params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token
    }
    
    try:
        response = requests.get(exchange_url, params=exchange_params, timeout=10)
        response.raise_for_status()
        
        exchange_data = response.json()
        long_lived_token = exchange_data.get('access_token')
        expires_in = exchange_data.get('expires_in', 0)
        days = expires_in // 86400 if expires_in else 0
        
        if long_lived_token:
            print(f"✅ Long-lived token created! (expires in {days} days)")
            return long_lived_token, True
        else:
            print("⚠️  Could not exchange token. Using short-lived token.")
            return short_token, False
    except Exception as e:
        print(f"⚠️  Could not exchange token: {e}")
        print("   Using short-lived token (expires in ~1 hour).")
        return short_token, False


def create_facebook_token():
    """Main function to create or refresh Facebook Page Access Token."""
    print("=" * 70)
    print("🔑 Create Facebook Page Access Token")
    print("=" * 70)
    print()
    
    # Load existing settings
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    app_id = api_keys.get('facebook_app_id')
    app_secret = api_keys.get('facebook_app_secret')
    existing_token = api_keys.get('facebook_page_access_token')
    page_id = api_keys.get('facebook_page_id')
    
    if not app_id:
        print("❌ Error: Facebook App ID not found in config.")
        print("   Please add 'facebook_app_id' to MY_CONFIG.json first.")
        return False
    
    print(f"📱 App ID: {app_id}")
    if page_id:
        print(f"📄 Target Page ID: {page_id}")
    if existing_token:
        print(f"🔑 Existing Token: {existing_token[:30]}...")
    print()
    
    # Check if existing token is valid
    if existing_token:
        print("🔍 Checking existing token validity...")
        is_valid, message = check_token_validity(existing_token, page_id)
        print(f"   {message}")
        print()
        
        if is_valid:
            print("✅ Existing token is valid! No need to create a new one.")
            print()
            choice = input("Create new token anyway? (y/n, default: n): ").strip().lower()
            if choice != 'y':
                print("✅ Keeping existing token.")
                return True
    
    # Get new token
    print("📋 Creating new Page Access Token...")
    print()
    
    # Step 1: Get User Access Token
    user_token = get_user_access_token(app_id, app_secret)
    if not user_token:
        return False
    
    # Step 2: Get Page Access Token
    result = get_page_access_token(user_token, page_id)
    if not result:
        return False
    
    page_token, page_id_found = result
    
    # Step 3: Exchange for long-lived token (if App Secret available)
    if app_secret:
        page_token, is_long_lived = exchange_for_long_lived_token(page_token, app_id, app_secret)
    else:
        print("⚠️  App Secret not available. Using short-lived token.")
        print("   Add App Secret to config for long-lived tokens (expires in ~60 days).")
        is_long_lived = False
        print()
    
    # Step 4: Save to config
    print("📋 Step 3: Saving Configuration")
    print("-" * 70)
    print()
    
    api_keys['facebook_page_access_token'] = page_token
    api_keys['facebook_page_id'] = page_id_found
    
    settings['api_keys'] = api_keys
    save_settings_to_db(settings)
    
    # Also update MY_CONFIG.json
    config_file = Path('MY_CONFIG.json')
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config['api_keys']['facebook_page_access_token'] = page_token
            config['api_keys']['facebook_page_id'] = page_id_found
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Updated MY_CONFIG.json!")
        except Exception as e:
            print(f"⚠️  Could not update MY_CONFIG.json: {e}")
            print("   But settings were saved to database.")
    
    print()
    print("=" * 70)
    print("✅ Token Created Successfully!")
    print("=" * 70)
    print()
    print("📝 Summary:")
    print(f"   ✅ Facebook Page Access Token: {page_token[:30]}...")
    print(f"   ✅ Facebook Page ID: {page_id_found}")
    print(f"   ✅ Token Type: {'Long-lived (~60 days)' if is_long_lived else 'Short-lived (~1 hour)'}")
    print()
    print("🚀 Next steps:")
    print("   1. Test Instagram: python3 scripts/get_instagram_account_id.py")
    print("   2. Test video uploads when ready!")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = create_facebook_token()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

