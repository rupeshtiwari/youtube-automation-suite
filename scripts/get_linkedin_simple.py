#!/usr/bin/env python3
"""
Simple script to get LinkedIn Access Token and Person URN.
Uses OAuth Playground method (easiest).
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db, save_settings_to_db

def get_linkedin_credentials():
    """Get LinkedIn Access Token and Person URN."""
    print("=" * 70)
    print("🔑 Get LinkedIn Access Token and Person URN")
    print("=" * 70)
    print()
    
    print("📋 Method: LinkedIn OAuth Playground (Easiest)")
    print()
    print("Step 1: Get Access Token")
    print("-" * 70)
    print("1. Go to: https://www.linkedin.com/developers/tools/oauth-playground")
    print("2. Select your app in the dropdown")
    print("3. Check permissions: w_member_social, r_liteprofile")
    print("4. Click 'Request Token'")
    print("5. Authorize if prompted")
    print("6. Copy the Access Token that appears")
    print()
    
    access_token = input("Paste your LinkedIn Access Token here: ").strip()
    
    if not access_token:
        print("❌ No access token provided. Exiting.")
        return False
    
    print()
    print("Step 2: Getting Person URN...")
    print("-" * 70)
    
    # Get Person URN
    try:
        url = "https://api.linkedin.com/v2/me"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        print("🔍 Fetching your LinkedIn profile...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        profile_data = response.json()
        person_urn = profile_data.get('id')
        
        if not person_urn:
            print("❌ Could not get Person URN from response.")
            print(f"   Response: {json.dumps(profile_data, indent=2)}")
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
            print("   Your Access Token may be invalid or expired.")
            print("   Please get a fresh token from OAuth Playground.")
        elif e.response.status_code == 403:
            print("   Your token may not have the required permissions.")
            print("   Make sure you selected 'r_liteprofile' permission.")
        else:
            try:
                error_data = e.response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save to database
    print("Step 3: Saving Configuration...")
    print("-" * 70)
    
    settings = load_settings_from_db()
    if not settings:
        settings = {}
    
    api_keys = settings.get('api_keys', {})
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
            
            if 'api_keys' not in config:
                config['api_keys'] = {}
            
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
    print("🚀 Your LinkedIn credentials are now saved!")
    print("   The app will auto-load them on next startup.")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = get_linkedin_credentials()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

