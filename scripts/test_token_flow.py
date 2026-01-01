#!/usr/bin/env python3
"""
Test script to verify token processing works.
This simulates what happens when you provide a token.
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db

def test_token_processing():
    """Test the token processing logic."""
    print("=" * 70)
    print("🧪 Testing Facebook Token Processing")
    print("=" * 70)
    print()
    
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    page_id = api_keys.get('facebook_page_id', '617021748762367')
    existing_token = api_keys.get('facebook_page_access_token')
    
    print(f"📄 Target Page ID: {page_id}")
    print()
    
    if existing_token:
        print(f"🔑 Existing Token: {existing_token[:30]}...")
        print("   Testing token validity...")
        print()
        
        # Test token
        test_url = f"https://graph.facebook.com/v18.0/{page_id}"
        test_params = {
            'access_token': existing_token,
            'fields': 'id,name'
        }
        
        try:
            response = requests.get(test_url, params=test_params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Token is VALID!")
                print(f"   ✅ Can access page: {data.get('name', 'Unknown')}")
                print()
                
                # Try Instagram
                ig_url = f"https://graph.facebook.com/v18.0/{page_id}"
                ig_params = {
                    'fields': 'instagram_business_account{id,username}',
                    'access_token': existing_token
                }
                
                ig_response = requests.get(ig_url, params=ig_params, timeout=10)
                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    ig_account = ig_data.get('instagram_business_account')
                    if ig_account:
                        print(f"   ✅ Instagram Account ID: {ig_account.get('id')}")
                        print(f"   ✅ Instagram Username: @{ig_account.get('username')}")
                    else:
                        print("   ⚠️  Instagram not connected to this page")
                else:
                    print(f"   ⚠️  Could not fetch Instagram: {ig_response.status_code}")
                
                print()
                print("=" * 70)
                print("✅ Token Processing Test: PASSED")
                print("=" * 70)
                print()
                print("Your token is valid! The script will work when you provide a User Access Token.")
                return True
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Token is INVALID: {error_msg}")
                print()
                print("=" * 70)
                print("❌ Token Processing Test: FAILED (Token Invalid)")
                print("=" * 70)
                print()
                print("💡 You need a new token from Graph API Explorer")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    else:
        print("❌ No existing token found")
        print()
        print("=" * 70)
        print("⚠️  Token Processing Test: NO TOKEN")
        print("=" * 70)
        print()
        print("💡 Get a User Access Token from Graph API Explorer, then run:")
        print("   .venv/bin/python3 scripts/get_facebook_token_v2.py YOUR_TOKEN")
        return False

if __name__ == '__main__':
    test_token_processing()

