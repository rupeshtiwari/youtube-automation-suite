#!/usr/bin/env python3
"""
Test YouTube Analytics API access.
This script checks if YouTube Analytics API is properly configured and accessible.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import json


def test_youtube_analytics():
    """Test YouTube Analytics API."""
    print("=" * 60)
    print("Testing YouTube Analytics API")
    print("=" * 60)

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        TOKEN_FILE = os.path.join(
            os.path.dirname(__file__), "..", "config", "token.json"
        )

        if not os.path.exists(TOKEN_FILE):
            print("❌ ERROR: token.json not found")
            print(f"   Expected at: {TOKEN_FILE}")
            print("   Please authenticate YouTube first via the app Settings page")
            return False

        print(f"✅ Found token.json at: {TOKEN_FILE}")

        # Load credentials
        SCOPES_ANALYTICS = ["https://www.googleapis.com/auth/yt-analytics.readonly"]

        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES_ANALYTICS)
            print("✅ Loaded credentials")
        except Exception as e:
            print(f"❌ ERROR loading credentials: {e}")
            print(
                "   Token might not have analytics scope. Need to re-authenticate with analytics scope."
            )
            return False

        if not creds or not creds.valid:
            print("❌ ERROR: Credentials not valid or expired")
            print("   Please re-authenticate via the app Settings page")
            return False

        print("✅ Credentials are valid")

        # Try to build YouTube Data API service first
        try:
            youtube = build("youtube", "v3", credentials=creds)
            print("✅ YouTube Data API v3 accessible")

            # Get channel ID
            request = youtube.channels().list(part="id,snippet", mine=True)
            response = request.execute()
            if response.get("items"):
                channel_id = response["items"][0]["id"]
                channel_title = response["items"][0]["snippet"]["title"]
                print(f"✅ Channel found: {channel_title} (ID: {channel_id})")
            else:
                print("❌ ERROR: No channel found")
                return False

        except Exception as e:
            print(f"❌ ERROR with YouTube Data API: {e}")
            return False

        # Try to build YouTube Analytics API service
        try:
            analytics = build("youtubeAnalytics", "v2", credentials=creds)
            print("✅ YouTube Analytics API v2 accessible")
        except Exception as e:
            print(f"❌ ERROR building Analytics API: {e}")
            if "has not been used" in str(e) or "accessNotConfigured" in str(e):
                print("   YouTube Analytics API not enabled in Google Cloud Console.")
                print(
                    "   Enable it at: https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com"
                )
            return False

        # Try to query analytics
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\nQuerying analytics from {start_date} to {end_date}...")

        try:
            # Test basic metrics
            response = (
                analytics.reports()
                .query(
                    ids=f"channel=={channel_id}",
                    startDate=start_date,
                    endDate=end_date,
                    metrics="views,estimatedMinutesWatched",
                    dimensions="day",
                )
                .execute()
            )

            rows = response.get("rows", [])
            if rows:
                total_views = sum(row[1] for row in rows if len(row) > 1)
                total_watch_time = sum(row[2] for row in rows if len(row) > 2)
                print(f"\n✅ SUCCESS! Analytics Data Retrieved:")
                print(f"   Total Views (30 days): {total_views:,}")
                print(f"   Watch Time (minutes): {total_watch_time:,}")
                print(f"   Data points: {len(rows)} days")
            else:
                print("⚠️  No analytics data found for this period")
                print("   This is normal if your channel is new or has no views")

            # Test demographics
            try:
                demo_response = (
                    analytics.reports()
                    .query(
                        ids=f"channel=={channel_id}",
                        startDate=start_date,
                        endDate=end_date,
                        metrics="views",
                        dimensions="ageGroup,gender",
                    )
                    .execute()
                )
                demo_rows = demo_response.get("rows", [])
                if demo_rows:
                    print(
                        f"\n✅ Demographics data available: {len(demo_rows)} segments"
                    )
                else:
                    print("\n⚠️  No demographics data (normal for new/small channels)")
            except Exception as e:
                print(f"\n⚠️  Demographics query failed: {e}")

            print("\n" + "=" * 60)
            print("✅ YouTube Analytics API is working correctly!")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n❌ ERROR querying analytics: {e}")
            if "403" in str(e):
                print(
                    "   Permission denied. Check OAuth scopes include yt-analytics.readonly"
                )
            elif "404" in str(e):
                print("   Channel not found or no analytics data available")
            return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    success = test_youtube_analytics()
    print("\n")
    sys.exit(0 if success else 1)
