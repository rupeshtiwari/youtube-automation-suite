"""
Simple script to authenticate YouTube and create token.json
Run this before downloading videos.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


def authenticate_youtube():
    """Authenticate with YouTube and create token.json."""
    print("=" * 80)
    print("YouTube Authentication")
    print("=" * 80)
    print()

    # Check if client_secret.json exists
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ {CLIENT_SECRET_FILE} not found!")
        print("   Please download your OAuth credentials from Google Cloud Console")
        return False

    print(f"✅ Found {CLIENT_SECRET_FILE}")

    creds = None

    # Check if token already exists
    if os.path.exists(TOKEN_FILE):
        print(f"✅ Found existing {TOKEN_FILE}")
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print("   Checking if token is valid...")
        except Exception as e:
            print(f"   ⚠️  Token file is invalid: {e}")
            creds = None

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   Token expired. Refreshing...")
            try:
                creds.refresh(Request())
                print("   ✅ Token refreshed successfully")
            except Exception as e:
                print(f"   ❌ Failed to refresh token: {e}")
                creds = None

        if not creds:
            print()
            print("🔐 Starting OAuth flow...")
            print("   A browser window will open for authentication")
            print("   Please sign in with your Google account and grant permissions")
            print()

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES
                )
                creds = flow.run_local_server(port=8080, open_browser=True)
                print()
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return False

        # Save credentials
        try:
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            print(f"✅ Saved credentials to {TOKEN_FILE}")
        except Exception as e:
            print(f"❌ Failed to save token: {e}")
            return False
    else:
        print("✅ Token is valid")

    # Test the connection
    print()
    print("Testing YouTube API connection...")
    try:
        youtube = build("youtube", "v3", credentials=creds)
        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()

        if response.get("items"):
            channel = response["items"][0]
            channel_name = channel["snippet"]["title"]
            print(f"✅ Connected to YouTube channel: {channel_name}")
            print()
            print("=" * 80)
            print("✅ Authentication Complete!")
            print("=" * 80)
            print()
            print("You can now run the download script:")
            print("  python scripts/download_shorts_playlists.py")
            print()
            return True
        else:
            print("⚠️  No channel found. Please make sure you have a YouTube channel.")
            return False

    except Exception as e:
        print(f"❌ Failed to connect to YouTube: {e}")
        return False


if __name__ == "__main__":
    success = authenticate_youtube()
    sys.exit(0 if success else 1)
