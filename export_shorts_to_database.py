"""
Export YouTube Shorts to SQLite database instead of Excel.
This is the database-first version that stores directly to SQLite,
then can export to Excel when needed.
"""

from __future__ import annotations

import os
import time
import json
import re
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Iterable, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Import database functions
from database import (
    init_database, insert_or_update_video, insert_or_update_social_post,
    log_automation_run
)

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

# IST timezone: UTC+05:30
IST = timezone(timedelta(hours=5, minutes=30))

# Starting date for social media scheduling: January 7, 2025, 7:30pm IST
START_SCHEDULE_DATE = datetime(2025, 1, 7, 19, 30, 0, tzinfo=IST)


def validate_client_secret_file(path: str) -> None:
    """Validate client secret file exists and is valid JSON."""
    if not os.path.exists(path):
        raise RuntimeError(
            f"Missing {path}.\n\n"
            "Fix:\n"
            "1) Google Cloud Console -> APIs & Services -> Credentials\n"
            "2) Create/Use OAuth Client ID of type 'Desktop app'\n"
            "3) Download JSON and save it as client_secret.json in this folder.\n"
        )

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        raise RuntimeError(f"{path} is empty. Re-download the OAuth JSON.")

    if raw.lower().startswith("<!doctype html") or raw.lower().startswith("<html"):
        raise RuntimeError(f"{path} looks like HTML, not JSON. Re-download from Google Cloud Console.")

    if not raw.startswith("{"):
        raise RuntimeError(f"{path} does not look like JSON. Re-download from Google Cloud Console.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"{path} is not valid JSON: {e}") from e

    if "installed" not in data and "web" not in data:
        raise RuntimeError(f"{path} JSON doesn't contain expected keys 'installed' or 'web'.")


def safe_execute(callable_fn, max_retries: int = 6):
    """Retry wrapper for transient YouTube API errors."""
    for attempt in range(max_retries):
        try:
            return callable_fn()
        except HttpError as e:
            status = getattr(e.resp, "status", None)
            if status in (403, 429, 500, 503):
                time.sleep(2**attempt)
                continue
            raise
    raise RuntimeError("Max retries exceeded (YouTube API). Try again in a minute.")


def get_youtube_client():
    """Get authenticated YouTube API client."""
    validate_client_secret_file(CLIENT_SECRET_FILE)

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def paged_request(request_fn, **kwargs) -> Iterable[Dict[str, Any]]:
    """Generic paginator for YouTube API list endpoints."""
    page_token = None
    while True:
        resp = safe_execute(
            lambda: request_fn(pageToken=page_token, **kwargs).execute()
        )
        for item in resp.get("items", []):
            yield item
        page_token = resp.get("nextPageToken")
        if not page_token:
            break


def get_my_channel_id(youtube) -> str:
    """Get authenticated user's channel ID."""
    resp = safe_execute(lambda: youtube.channels().list(part="id", mine=True).execute())
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("No channel found. Are you logged into the right Google account?")
    return items[0]["id"]


def fetch_all_playlists(youtube, channel_id: str) -> List[Dict[str, Any]]:
    """Fetch all playlists containing 'shorts' in the name."""
    playlists = []
    for pl in paged_request(
        youtube.playlists().list,
        part="id,snippet,contentDetails",
        channelId=channel_id,
        maxResults=50,
    ):
        snippet = pl.get("snippet", {})
        playlist_title = snippet.get("title", "").lower()
        
        if "shorts" in playlist_title:
            playlists.append({
                "playlistId": pl["id"],
                "playlistTitle": snippet.get("title", ""),
                "playlistItemCount": pl.get("contentDetails", {}).get("itemCount", None),
                "publishedAt": snippet.get("publishedAt", ""),
            })
    
    playlists.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    return playlists


def fetch_all_playlist_video_ids(youtube, playlist_id: str) -> List[str]:
    """Fetch all video IDs from a playlist."""
    video_ids = []
    for it in paged_request(
        youtube.playlistItems().list,
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50,
    ):
        vid = it.get("contentDetails", {}).get("videoId")
        if vid:
            video_ids.append(vid)
    return video_ids


def chunked(lst: List[str], size: int) -> Iterable[List[str]]:
    """Split list into chunks."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def fetch_video_details(youtube, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch video details from YouTube API."""
    out: Dict[str, Dict[str, Any]] = {}
    if not video_ids:
        return out

    for batch in chunked(video_ids, 50):
        resp = safe_execute(
            lambda: youtube.videos()
            .list(part="snippet,status", id=",".join(batch), maxResults=50)
            .execute()
        )

        for v in resp.get("items", []):
            vid = v.get("id", "")
            snippet = v.get("snippet", {}) or {}
            status = v.get("status", {}) or {}
            privacy_status = status.get("privacyStatus", "")
            publish_at = status.get("publishAt", "")
            
            if privacy_status == "public" or (privacy_status == "private" and publish_at):
                out[vid] = {
                    "videoTitle": snippet.get("title", ""),
                    "videoDescription": snippet.get("description", ""),
                    "videoTags": ",".join(snippet.get("tags", []) or []),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "publishAt": publish_at,
                    "privacyStatus": privacy_status,
                }
    return out


# Import helper functions from export_shorts_to_excel.py
# (These are the same functions, so we can reuse them)
import sys
sys.path.insert(0, os.path.dirname(__file__))

# We'll import these functions - they're the same logic
from export_shorts_to_excel import (
    derive_type, derive_role, analyze_video_description,
    calculate_social_media_schedule_date,
    generate_viral_linkedin_post, generate_viral_facebook_post, generate_viral_instagram_post,
    format_date
)


def main():
    """Main function to export Shorts to database."""
    # Initialize database
    init_database()
    
    youtube = get_youtube_client()
    channel_id = get_my_channel_id(youtube)

    playlists = fetch_all_playlists(youtube, channel_id)
    if not playlists:
        print("No playlists with 'shorts' in the name found on this channel.")
        log_automation_run("export_shorts", "completed", "No shorts playlists found", 0, 0)
        return

    print(f"Found {len(playlists)} shorts playlists. Processing from latest to oldest...")
    
    global_video_index = 0
    total_videos = 0
    total_posts = 0
    
    try:
        for idx, pl in enumerate(playlists, 1):
            playlist_id = pl["playlistId"]
            playlist_title = pl["playlistTitle"]
            
            print(f"[{idx}/{len(playlists)}] Processing playlist: {playlist_title}")

            video_ids = fetch_all_playlist_video_ids(youtube, playlist_id)
            
            if not video_ids:
                print(f"  ⚠️  No videos found in this playlist. Skipping...")
                continue

            details_map = fetch_video_details(youtube, list(dict.fromkeys(video_ids)))

            for vid in video_ids:
                d = details_map.get(vid, {})
                if not d:
                    continue
                
                video_title = d.get("videoTitle", "")
                video_description = d.get("videoDescription", "")
                video_tags = d.get("videoTags", "")
                
                # Derive type and role
                video_type = derive_type(playlist_title, video_title, video_description, video_tags)
                role = derive_role(playlist_title, video_title, video_description, video_tags)
                
                # Analyze description
                analysis = analyze_video_description(video_description)
                
                # Format YouTube date
                youtube_schedule_date = format_date(
                    d.get("publishAt", ""), 
                    d.get("publishedAt", "")
                )
                
                # Generate enhanced viral posts
                linkedin_post = generate_viral_linkedin_post(video_title, video_description, video_type, role, analysis)
                facebook_post = generate_viral_facebook_post(video_title, video_description, video_type, role, analysis)
                instagram_post = generate_viral_instagram_post(video_title, video_description, video_type, role, analysis)
                
                # Calculate schedule dates
                linkedin_schedule = calculate_social_media_schedule_date(global_video_index)
                facebook_schedule = calculate_social_media_schedule_date(global_video_index)
                instagram_schedule = calculate_social_media_schedule_date(global_video_index)
                
                # YouTube URL
                youtube_url = f"https://www.youtube.com/watch?v={vid}"
                
                # Store video in database
                video_data = {
                    'video_id': vid,
                    'playlist_id': playlist_id,
                    'playlist_name': playlist_title,
                    'title': video_title,
                    'description': video_description,
                    'tags': video_tags,
                    'youtube_schedule_date': d.get("publishAt", ""),
                    'youtube_published_date': d.get("publishedAt", ""),
                    'privacy_status': d.get("privacyStatus", ""),
                    'video_type': video_type,
                    'role': role,
                    'youtube_url': youtube_url
                }
                
                insert_or_update_video(video_data)
                total_videos += 1
                
                # Store social media posts
                platforms_data = [
                    ('linkedin', linkedin_post, linkedin_schedule),
                    ('facebook', facebook_post, facebook_schedule),
                    ('instagram', instagram_post, instagram_schedule)
                ]
                
                for platform, post_content, schedule_date in platforms_data:
                    post_data = {
                        'post_content': post_content,
                        'schedule_date': schedule_date,
                        'status': 'pending'
                    }
                    insert_or_update_social_post(vid, platform, post_data)
                    total_posts += 1
                
                global_video_index += 1

            print(f"  ✅ Processed {len([v for v in video_ids if v in details_map])} videos from {playlist_title}")

        print(f"\n✅ Exported all shorts playlists to database")
        print(f"Total videos: {total_videos}")
        print(f"Total social posts: {total_posts}")
        
        log_automation_run(
            "export_shorts",
            "completed",
            f"Exported {total_videos} videos and {total_posts} posts",
            total_videos,
            total_posts
        )
        
        # Optionally export to Excel for manual review
        print("\n💡 Tip: Use database.export_to_excel() to create Excel file for manual review")
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: {error_msg}")
        log_automation_run("export_shorts", "error", error_msg, total_videos, total_posts, error_msg)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n❌ ERROR\n")
        print(str(e))
        print("\nIf this is the OAuth file issue, fix client_secret.json and re-run.\n")
        raise

