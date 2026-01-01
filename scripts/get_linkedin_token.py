#!/usr/bin/env python3
"""
Get LinkedIn Access Token and Person URN via OAuth.
Similar to Facebook token script - opens browser, gets authorization.
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
    'w_member_social',  # Post, comment, and share
    'r_liteprofile',    # Read basic profile
    'r_emailaddress'    # Read email
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
                error_description = params.get('error_description', [''])[0]
                self.server.auth_error = f"{error}: {error_description}"
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html_content = f"""
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body>
                        <h1>❌ Authorization Failed</h1>
                        <p>Error: {error}</p>
                        <p>{error_description}</p>
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


def get_linkedin_token():
    """Get LinkedIn Access Token and Person URN via OAuth."""
    print("=" * 70)
    print("🔑 Get LinkedIn Access Token and Person URN")
    print("=" * 70)
    print()
    
    # Load existing settings
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    client_id = api_keys.get('linkedin_client_id')
    client_secret = api_keys.get('linkedin_client_secret')
    
    if not client_id:
        print("❌ Error: LinkedIn Client ID not found in config.")
        print("   Please add 'linkedin_client_id' to MY_CONFIG.json first.")
        return False
    
    if not client_secret:
        print("❌ Error: LinkedIn Client Secret not found in config.")
        print("   Please add 'linkedin_client_secret' to MY_CONFIG.json first.")
        return False
    
    print(f"📱 Client ID: {client_id}")
    print()
    
    print("=" * 70)
    print("📋 Option 1: Use LinkedIn OAuth Playground (Easiest)")
    print("=" * 70)
    print()
    print("1. Go to: https://www.linkedin.com/developers/tools/oauth-playground")
    print("2. Select your app in the dropdown")
    print("3. Check permissions: w_member_social, r_liteprofile")
    print("4. Click 'Request Token'")
    print("5. Copy the Access Token")
    print("6. Get Person URN: Visit https://api.linkedin.com/v2/me?oauth2_access_token=YOUR_TOKEN")
    print("7. Copy the 'id' field (Person URN)")
    print()
    
    use_playground = input("Use OAuth Playground? (y/n, default: y): ").strip().lower()
    
    if use_playground != 'n':
        print()
        print("💡 After getting your token and URN, update MY_CONFIG.json:")
        print("   {")
        print('     "api_keys": {')
        print('       "linkedin_access_token": "YOUR_TOKEN",')
        print('       "linkedin_person_urn": "urn:li:person:xxxxx"')
        print("     }")
        print("   }")
        print()
        print("Then run: python3 scripts/load_config.py")
        return False
    
    # OAuth flow
    print()
    print("=" * 70)
    print("📋 Option 2: OAuth Flow (Automated)")
    print("=" * 70)
    print()
    
    # Step 1: Get authorization code
    print("Step 1: Getting Authorization")
    print("-" * 70)
    print()
    
    state = os.urandom(16).hex()
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope={'%20'.join(SCOPES)}&"
        f"state={state}"
    )
    
    print("🌐 Opening browser for LinkedIn authorization...")
    print(f"   URL: {auth_url[:100]}...")
    print()
    print("📝 Instructions:")
    print("   1. Log in to LinkedIn if needed")
    print("   2. Authorize the app")
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
            
            # Wait for callback
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
            print("✅ Authorization code received!")
            print()
            
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user.")
            return False
        except Exception as e:
            print(f"❌ Error during authorization: {e}")
            return False
    
    # Step 2: Exchange code for access token
    print("Step 2: Getting Access Token")
    print("-" * 70)
    print()
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    print("🔄 Exchanging authorization code for access token...")
    
    try:
        response = requests.post(token_url, data=token_data, timeout=10)
        response.raise_for_status()
        
        token_response = response.json()
        access_token = token_response.get('access_token')
        
        if not access_token:
            print("❌ Failed to get access token.")
            print(f"   Response: {token_response}")
            return False
        
        expires_in = token_response.get('expires_in', 0)
        days = expires_in // 86400 if expires_in else 0
        
        print(f"✅ Got Access Token! (expires in {days} days)")
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
    
    # Step 3: Get Person URN
    print("Step 3: Getting Person URN")
    print("-" * 70)
    print()
    
    print("🔍 Fetching your LinkedIn profile...")
    
    profile_url = "https://api.linkedin.com/v2/me"
    profile_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(profile_url, headers=profile_headers, timeout=10)
        response.raise_for_status()
        
        profile_data = response.json()
        person_urn = profile_data.get('id')
        
        if not person_urn:
            print("❌ Could not get Person URN.")
            print(f"   Response: {profile_data}")
            return False
        
        first_name = profile_data.get('firstName', {}).get('localized', {}).get('en_US', '')
        last_name = profile_data.get('lastName', {}).get('localized', {}).get('en_US', '')
        
        print(f"✅ Got Person URN!")
        print(f"   URN: {person_urn}")
        if first_name or last_name:
            print(f"   Name: {first_name} {last_name}")
        print()
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error getting Person URN: {e}")
        if e.response.status_code == 401:
            print("   Your Access Token may be invalid.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 4: Save to config
    print("Step 4: Saving Configuration")
    print("-" * 70)
    print()
    
    api_keys['linkedin_access_token'] = access_token
    api_keys['linkedin_person_urn'] = person_urn
    
    settings['api_keys'] = api_keys
    save_settings_to_db(settings)
    
    # Update MY_CONFIG.json
    config_file = Path('MY_CONFIG.json')
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config['api_keys']['linkedin_access_token'] = access_token
            config['api_keys']['linkedin_person_urn'] = person_urn
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Updated MY_CONFIG.json!")
        except Exception as e:
            print(f"⚠️  Could not update MY_CONFIG.json: {e}")
    
    print()
    print("=" * 70)
    print("✅ Success!")
    print("=" * 70)
    print()
    print("📝 Summary:")
    print(f"   ✅ LinkedIn Access Token: {access_token[:30]}...")
    print(f"   ✅ LinkedIn Person URN: {person_urn}")
    print()
    print("🚀 You're ready to test LinkedIn video uploads!")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = get_linkedin_token()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

