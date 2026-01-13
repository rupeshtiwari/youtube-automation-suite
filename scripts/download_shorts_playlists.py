"""
Download all videos from YouTube Shorts playlists.
Organizes videos into folders by playlist name.
"""

import os
import sys
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import subprocess
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
DOWNLOAD_BASE_DIR = "data/shorts_downloads"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    # Remove invalid characters for filesystem
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Replace multiple spaces with single space
    filename = re.sub(r"\s+", " ", filename)
    # Trim whitespace
    filename = filename.strip()
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


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
            print("   Please authenticate via the web app Settings page first.")
            return None

    return build("youtube", "v3", credentials=creds)


def get_my_playlists(youtube):
    """Fetch all playlists from authenticated user's channel."""
    playlists = []
    next_page_token = None

    try:
        while True:
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

    except Exception as e:
        print(f"❌ Error fetching playlists: {e}")
        return []

    return playlists


def get_playlist_videos(youtube, playlist_id):
    """Get all video IDs and titles from a playlist."""
    videos = []
    next_page_token = None

    try:
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

    except Exception as e:
        print(f"   ❌ Error fetching videos from playlist: {e}")

    return videos


def check_ytdlp_installed():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ yt-dlp not found. Installing...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        print("✅ yt-dlp installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install yt-dlp: {e}")
        return False


def download_video(video_id, video_title, output_dir):
    """Download a single video using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Create sanitized filename
    safe_title = sanitize_filename(video_title)

    # yt-dlp command with options
    cmd = [
        "yt-dlp",
        "-f",
        "best",  # Best quality
        "--no-playlist",  # Don't download playlists
        "-o",
        os.path.join(output_dir, f"{safe_title}.%(ext)s"),  # Output template
        "--no-overwrites",  # Skip if file exists
        "--quiet",  # Suppress output
        "--progress",  # Show progress
        url,
    ]

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"      ❌ Failed to download: {e}")
        return False
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False


def main():
    """Main function to download all shorts playlists."""
    print("=" * 80)
    print("YouTube Shorts Playlist Downloader")
    print("=" * 80)
    print()

    # Check yt-dlp
    if not check_ytdlp_installed():
        return

    print()

    # Get YouTube service
    youtube = get_youtube_service()
    if not youtube:
        return

    print("✅ YouTube authenticated successfully")
    print()

    # Get all playlists
    print("📋 Fetching your playlists...")
    all_playlists = get_my_playlists(youtube)
    print(f"   Found {len(all_playlists)} total playlists")
    print()

    # Filter for shorts playlists
    shorts_playlists = [
        p for p in all_playlists if "short" in p["snippet"]["title"].lower()
    ]

    if not shorts_playlists:
        print("❌ No playlists found with 'short' in the name")
        return

    print(f"🎯 Found {len(shorts_playlists)} Shorts playlists:")
    for p in shorts_playlists:
        item_count = p["contentDetails"]["itemCount"]
        print(f"   • {p['snippet']['title']} ({item_count} videos)")
    print()

    # Create base download directory
    base_dir = Path(DOWNLOAD_BASE_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)

    print(f"📂 Download location: {base_dir.absolute()}")
    print()

    # Download each playlist
    total_downloaded = 0
    total_skipped = 0
    total_failed = 0

    for idx, playlist in enumerate(shorts_playlists, 1):
        playlist_title = playlist["snippet"]["title"]
        playlist_id = playlist["id"]
        item_count = playlist["contentDetails"]["itemCount"]

        print(f"[{idx}/{len(shorts_playlists)}] Processing: {playlist_title}")

        # Create playlist directory
        safe_playlist_name = sanitize_filename(playlist_title)
        playlist_dir = base_dir / safe_playlist_name
        playlist_dir.mkdir(parents=True, exist_ok=True)

        print(f"   📁 {playlist_dir}")

        # Get videos in playlist
        videos = get_playlist_videos(youtube, playlist_id)
        print(f"   📹 {len(videos)} videos to download")

        # Download each video
        for video_idx, video in enumerate(videos, 1):
            video_id = video["id"]
            video_title = video["title"]

            # Check if file already exists
            existing_files = list(
                playlist_dir.glob(f"{sanitize_filename(video_title)}.*")
            )
            if existing_files:
                print(
                    f"      [{video_idx}/{len(videos)}] ⏭️  Skipped (exists): {video_title[:50]}..."
                )
                total_skipped += 1
                continue

            print(
                f"      [{video_idx}/{len(videos)}] ⬇️  Downloading: {video_title[:50]}..."
            )

            if download_video(video_id, video_title, str(playlist_dir)):
                print(f"      ✅ Downloaded successfully")
                total_downloaded += 1
            else:
                total_failed += 1

        print()

    # Summary
    print("=" * 80)
    print("Download Summary")
    print("=" * 80)
    print(f"✅ Downloaded: {total_downloaded} videos")
    print(f"⏭️  Skipped: {total_skipped} videos (already exist)")
    print(f"❌ Failed: {total_failed} videos")
    print()
    print(f"📂 All videos saved to: {base_dir.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
