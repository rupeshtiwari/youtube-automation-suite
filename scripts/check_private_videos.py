"""
Check which videos in failed playlists are private vs accessible.
This helps identify which videos need privacy settings changed.
"""

import os
import sys
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Playlists that failed to download
FAILED_PLAYLISTS = {
    "PLZed_adPqIJoBFiaJFoxF6yJ9Ly_rsK0J": "Why Directors Fail: The FAANG Bar-Raiser Secrets – Shorts",
    "PLZed_adPqIJqumVOsFf2XSER6nkAGHBhm": "Why SPOs Fail Interviews",
    "PLZed_adPqIJqbTsbcbApXmCOgcu-h-wnl": "❌ Why Amazon Rejects Strong SPMs (L6 Interview Reality)",
    "PLZed_adPqIJpeIx-pnvdEU3FJ_F4tR3gO": "Tech Resume Fixes in 60 Seconds SHORTS",
    "PLZed_adPqIJpjT9a_lfMQjSB_MfJQzg8t": "Crack Coding Interviews Fast",
}


def get_youtube_service():
    """Get authenticated YouTube API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ No valid YouTube credentials found.")
            return None
    
    return build("youtube", "v3", credentials=creds)


def get_playlist_videos(youtube, playlist_id):
    """Get all videos from a playlist."""
    videos = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()
        
        for item in response.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            video_title = item["snippet"]["title"]
            videos.append({"id": video_id, "title": video_title})
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return videos


def check_video_accessibility(video_id):
    """Check if a video can be accessed with cookies."""
    try:
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", "chrome",
            "--skip-download",
            "--quiet",
            "--print", "%(title)s",
            f"https://www.youtube.com/watch?v={video_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return "accessible"
        elif "private" in result.stderr.lower():
            return "private"
        elif "unavailable" in result.stderr.lower():
            return "unavailable"
        else:
            return "unknown"
    except subprocess.TimeoutExpired:
        return "timeout"
    except Exception:
        return "error"


def main():
    print("=" * 80)
    print("Private Video Checker")
    print("=" * 80)
    print()
    
    youtube = get_youtube_service()
    if not youtube:
        return
    
    for playlist_id, playlist_title in FAILED_PLAYLISTS.items():
        print(f"\n📋 {playlist_title}")
        print(f"   Playlist ID: {playlist_id}")
        
        try:
            videos = get_playlist_videos(youtube, playlist_id)
            print(f"   Found {len(videos)} videos")
            
            accessible = 0
            private = 0
            other = 0
            
            for i, video in enumerate(videos, 1):
                status = check_video_accessibility(video["id"])
                
                if status == "accessible":
                    accessible += 1
                    symbol = "✅"
                elif status == "private":
                    private += 1
                    symbol = "🔒"
                else:
                    other += 1
                    symbol = "❓"
                
                print(f"      [{i:2d}/{len(videos)}] {symbol} {video['title'][:60]}")
            
            print(f"\n   Summary: {accessible} accessible, {private} private, {other} other")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Recommendations:")
    print("=" * 80)
    print("🔒 Private videos: Change privacy to 'Unlisted' or 'Public' in YouTube Studio")
    print("❓ Other issues: Check video status in YouTube Studio")
    print("✅ Accessible videos: Should download successfully")


if __name__ == "__main__":
    main()
