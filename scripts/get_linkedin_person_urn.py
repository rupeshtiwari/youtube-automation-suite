#!/usr/bin/env python3
"""
Automatically fetch LinkedIn Person URN from access token.
This script uses the LinkedIn API to get your Person URN automatically.
"""

import sys
import os
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import load_settings_from_db

def get_linkedin_person_urn(access_token):
    """
    Get LinkedIn Person URN from access token.
    
    Args:
        access_token: LinkedIn access token
        
    Returns:
        Person URN (e.g., "urn:li:person:xxxxx") or None if failed
    """
    try:
        # LinkedIn API endpoint to get user profile
        url = "https://api.linkedin.com/v2/userinfo"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # The sub field contains the Person URN
            sub = data.get("sub")
            if sub:
                # Format: "urn:li:person:xxxxx"
                if not sub.startswith("urn:li:person:"):
                    return f"urn:li:person:{sub}"
                return sub
            return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching Person URN: {e}")
        return None


def get_person_urn_from_profile_api(access_token):
    """
    Alternative method: Get Person URN from profile API.
    """
    try:
        # Try the profile API endpoint
        url = "https://api.linkedin.com/v2/me"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # The id field contains the Person URN
            person_id = data.get("id")
            if person_id:
                if not person_id.startswith("urn:li:person:"):
                    return f"urn:li:person:{person_id}"
                return person_id
            return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching Person URN: {e}")
        return None


def main():
    """Main function to fetch and save LinkedIn Person URN."""
    print("=" * 70)
    print("🔍 Auto-Fetch LinkedIn Person URN")
    print("=" * 70)
    print()
    
    # Load settings from database
    settings = load_settings_from_db()
    api_keys = settings.get('api_keys', {})
    
    access_token = api_keys.get('linkedin_access_token', '')
    
    if not access_token:
        print("❌ LinkedIn Access Token not found in database!")
        print()
        print("📋 Steps to get Access Token:")
        print("1. Run: python3 scripts/get_linkedin_token.py")
        print("2. Or follow: GET_LINKEDIN_TOKEN.md")
        print()
        return
    
    print(f"✅ Found LinkedIn Access Token")
    print()
    print("🔍 Fetching Person URN...")
    print()
    
    # Try method 1: userinfo endpoint
    person_urn = get_linkedin_person_urn(access_token)
    
    # If that fails, try method 2: profile API
    if not person_urn:
        print("⚠️  Method 1 failed, trying alternative method...")
        person_urn = get_person_urn_from_profile_api(access_token)
    
    if person_urn:
        print(f"✅ Successfully fetched Person URN: {person_urn}")
        print()
        
        # Update settings
        settings['api_keys']['linkedin_person_urn'] = person_urn
        
        # Save to database
        from app.database import save_settings_to_db
        save_settings_to_db(settings)
        
        print("✅ Person URN saved to database!")
        print()
        print("📋 Next steps:")
        print("1. Restart your server to load the new settings")
        print("2. Check Config page to verify Person URN is set")
        print()
    else:
        print("❌ Failed to fetch Person URN")
        print()
        print("📋 Troubleshooting:")
        print("1. Verify your Access Token is valid")
        print("2. Check token has 'profile' or 'openid' permissions")
        print("3. Token might be expired - get a new one")
        print()
        print("💡 Manual method:")
        print("   - Go to LinkedIn OAuth Playground")
        print("   - Get your profile")
        print("   - Look for 'id' field in response")
        print("   - Format: urn:li:person:xxxxx")
        print()


if __name__ == '__main__':
    main()

