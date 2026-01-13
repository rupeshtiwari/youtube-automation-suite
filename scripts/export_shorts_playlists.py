#!/usr/bin/env python3
"""
Export YouTube Shorts Playlists to Excel
Downloads all playlists with "short" in the name and exports video information to Excel.
Each playlist gets its own tab with: title, description, tags, playlist ID, video URL, playlist URL
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import pickle

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def get_authenticated_service():
    """Authenticate and return YouTube API service."""
    creds = None
    token_path = Path(__file__).parent.parent / "config" / "token.json"
    client_secret_path = Path(__file__).parent.parent / "config" / "client_secret.json"

    # Token file stores the user's access and refresh tokens
    if token_path.exists():
        try:
            with open(token_path, "r") as token:
                token_data = json.load(token)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}")

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not client_secret_path.exists():
                print(f"❌ Error: client_secret.json not found at {client_secret_path}")
                print("Please set up OAuth credentials first.")
                sys.exit(1)

            print("Starting OAuth authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def get_my_playlists(youtube):
    """Fetch all playlists from the authenticated user's channel."""
    playlists = []
    next_page_token = None

    print("Fetching your playlists...")

    while True:
        try:
            request = youtube.playlists().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()

            playlists.extend(response.get("items", []))
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        except HttpError as e:
            print(f"❌ Error fetching playlists: {e}")
            break

    return playlists


def get_playlist_videos(youtube, playlist_id):
    """Fetch all videos from a specific playlist."""
    videos = []
    next_page_token = None

    while True:
        try:
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()

            videos.extend(response.get("items", []))
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        except HttpError as e:
            print(f"❌ Error fetching videos from playlist {playlist_id}: {e}")
            break

    return videos


def get_video_details(youtube, video_ids):
    """Fetch detailed information for videos including tags."""
    if not video_ids:
        return []

    video_details = []

    # YouTube API allows max 50 video IDs per request
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i : i + 50]
        try:
            request = youtube.videos().list(part="snippet", id=",".join(batch_ids))
            response = request.execute()
            video_details.extend(response.get("items", []))
        except HttpError as e:
            print(f"❌ Error fetching video details: {e}")

    return video_details


def export_to_excel(playlists_data, output_file):
    """Export playlist data to Excel with one tab per playlist."""

    if not playlists_data:
        print("❌ No playlist data to export")
        return

    print(f"\n📊 Creating Excel file: {output_file}")

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for playlist_info in playlists_data:
            playlist_name = playlist_info["name"]
            videos = playlist_info["videos"]
            playlist_id = playlist_info["playlist_id"]
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

            # Create dataframe for this playlist
            df_data = []
            for video in videos:
                df_data.append(
                    {
                        "Title": video["title"],
                        "Description": video["description"],
                        "Tags": video["tags"],
                        "Playlist ID": playlist_id,
                        "Video URL": video["video_url"],
                        "Playlist URL": playlist_url,
                    }
                )

            df = pd.DataFrame(df_data)

            # Sanitize sheet name (Excel has limitations)
            sheet_name = playlist_name[:31]  # Excel sheet name limit is 31 chars
            # Remove invalid characters for Excel sheet names
            invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
            for char in invalid_chars:
                sheet_name = sheet_name.replace(char, "_")

            # Write to Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col))
                # Set a reasonable max width
                max_length = min(max_length, 100)
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

            print(f"   ✅ Added sheet: {sheet_name} ({len(df)} videos)")

    print(f"\n✅ Excel file created successfully!")
    print(f"   Location: {output_file}")


def main():
    """Main function to export Shorts playlists to Excel."""
    print("=" * 60)
    print("YouTube Shorts Playlists Exporter")
    print("=" * 60)

    # Authenticate
    try:
        youtube = get_authenticated_service()
        print("✅ Authenticated successfully\n")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # Get all playlists
    all_playlists = get_my_playlists(youtube)
    print(f"📋 Found {len(all_playlists)} total playlists\n")

    # Filter playlists with "short" in the name (case-insensitive)
    shorts_playlists = [
        p for p in all_playlists if "short" in p["snippet"]["title"].lower()
    ]

    if not shorts_playlists:
        print("❌ No playlists found with 'short' in the name")
        return

    print(f"🎯 Found {len(shorts_playlists)} Shorts playlists:")
    for p in shorts_playlists:
        print(f"   - {p['snippet']['title']}")
    print()

    # Fetch videos for each Shorts playlist
    playlists_data = []

    for idx, playlist in enumerate(shorts_playlists, 1):
        playlist_title = playlist["snippet"]["title"]
        playlist_id = playlist["id"]

        print(f"[{idx}/{len(shorts_playlists)}] Processing: {playlist_title}")

        # Get videos in this playlist
        playlist_videos = get_playlist_videos(youtube, playlist_id)
        print(f"   Found {len(playlist_videos)} videos")

        if not playlist_videos:
            continue

        # Get video IDs
        video_ids = [v["contentDetails"]["videoId"] for v in playlist_videos]

        # Get detailed video information (including tags)
        print(f"   Fetching video details...")
        video_details = get_video_details(youtube, video_ids)

        # Create a mapping of video ID to details
        details_map = {v["id"]: v for v in video_details}

        # Compile video information
        videos_info = []
        for video in playlist_videos:
            video_id = video["contentDetails"]["videoId"]
            snippet = video["snippet"]

            # Get tags from detailed info
            tags = []
            if video_id in details_map:
                tags = details_map[video_id]["snippet"].get("tags", [])

            videos_info.append(
                {
                    "title": snippet.get("title", "N/A"),
                    "description": snippet.get("description", ""),
                    "tags": ", ".join(tags),  # Comma-separated tags
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

        playlists_data.append(
            {"name": playlist_title, "playlist_id": playlist_id, "videos": videos_info}
        )
        print(f"   ✅ Processed {len(videos_info)} videos\n")

    # Export to Excel
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"shorts_playlists_{timestamp}.xlsx"

    export_to_excel(playlists_data, str(output_file))

    print(f"\n🎉 Export complete!")
    print(f"   Playlists: {len(playlists_data)}")
    print(f"   Total videos: {sum(len(p['videos']) for p in playlists_data)}")


if __name__ == "__main__":
    main()
