"""
Reschedule ALL videos in a given YouTube playlist to publish on the next
Wednesday at 11:00 PM IST (GMT+05:30).

Notes:
- YouTube API requires publishAt in UTC (RFC3339, with 'Z').
- To schedule, privacyStatus must be 'private' (then YouTube publishes at publishAt).
- This script updates each video's "status" via videos.update(part="status").
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# IST timezone: UTC+05:30
IST = timezone(timedelta(hours=5, minutes=30))


def next_weekday_at_time(
    now_local: datetime,
    target_weekday: int,
    hour: int,
    minute: int,
) -> datetime:
    """
    Return the next occurrence (including today if time is still ahead) of:
    weekday=target_weekday (Mon=0..Sun=6) at HH:MM in the same timezone as now_local.
    """
    if now_local.tzinfo is None:
        raise ValueError("now_local must be timezone-aware")

    candidate = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    days_ahead = (target_weekday - candidate.weekday()) % 7
    candidate = candidate + timedelta(days=days_ahead)

    # If it's today but time already passed, jump 7 days
    if candidate <= now_local:
        candidate = candidate + timedelta(days=7)

    return candidate


def to_utc_rfc3339(dt_local: datetime) -> str:
    """Convert a tz-aware datetime to UTC RFC3339 string ending with 'Z'."""
    if dt_local.tzinfo is None:
        raise ValueError("dt_local must be timezone-aware")
    dt_utc = dt_local.astimezone(timezone.utc)
    # YouTube likes format: YYYY-MM-DDTHH:MM:SSZ
    return dt_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_authenticated_service(client_secrets_file: str):
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=creds)


def list_playlist_video_ids(youtube, playlist_id: str) -> List[str]:
    video_ids: List[str] = []
    page_token: Optional[str] = None

    while True:
        resp = (
            youtube.playlistItems()
            .list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=page_token,
            )
            .execute()
        )

        for item in resp.get("items", []):
            vid = item["contentDetails"]["videoId"]
            video_ids.append(vid)

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return video_ids


def get_video_status(youtube, video_id: str) -> dict:
    resp = youtube.videos().list(part="status,snippet", id=video_id).execute()
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"Video not found or not accessible: {video_id}")
    return items[0]


def update_video_publish_time(youtube, video_id: str, publish_at_utc_rfc3339: str):
    """
    Set privacyStatus=private and publishAt=... (UTC RFC3339).
    """
    body = {
        "id": video_id,
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_utc_rfc3339,
            # keep other status fields as-is if you want; we only set what we need
        },
    }

    return youtube.videos().update(part="status", body=body).execute()


def main():
    # === REQUIRED ===
    CLIENT_SECRETS_FILE = "client_secret.json"  # download from Google Cloud Console (OAuth client)
    PLAYLIST_ID = os.environ.get("YOUTUBE_PLAYLIST_ID", "").strip()  # or hardcode

    if not PLAYLIST_ID:
        raise SystemExit(
            "Set your playlist id in env var YOUTUBE_PLAYLIST_ID, e.g.\n"
            "  export YOUTUBE_PLAYLIST_ID='PLxxxx...'\n"
        )

    # Target schedule: Wednesday 11:00 PM IST (GMT+05:30)
    TARGET_WEEKDAY = 2  # Wednesday (Mon=0, Tue=1, Wed=2)
    TARGET_HOUR = 23
    TARGET_MINUTE = 0

    youtube = get_authenticated_service(CLIENT_SECRETS_FILE)

    # Compute next Wednesday 11:00 PM IST
    now_ist = datetime.now(IST)
    publish_local_ist = next_weekday_at_time(now_ist, TARGET_WEEKDAY, TARGET_HOUR, TARGET_MINUTE)
    publish_at_utc = to_utc_rfc3339(publish_local_ist)

    # Helpful: show PST equivalent (America/Los_Angeles varies by DST; this is approximate)
    # Your stated conversion: 11:00 PM IST == 9:30 AM PST (same day). That matches standard time.

    print(f"Now (IST):              {now_ist.isoformat(timespec='seconds')}")
    print(f"Target publish (IST):   {publish_local_ist.isoformat(timespec='seconds')}")
    print(f"Target publish (UTC):   {publish_at_utc}")
    print()

    try:
        video_ids = list_playlist_video_ids(youtube, PLAYLIST_ID)
        print(f"Found {len(video_ids)} videos in playlist.")
        print()

        for idx, vid in enumerate(video_ids, start=1):
            v = get_video_status(youtube, vid)
            title = v.get("snippet", {}).get("title", "<no title>")
            status = v.get("status", {})
            current_privacy = status.get("privacyStatus")
            current_publish_at = status.get("publishAt")

            print(f"[{idx}/{len(video_ids)}] {title}")
            print(f"    Current privacy: {current_privacy}")
            print(f"    Current publishAt: {current_publish_at}")
            print(f"    Updating publishAt -> {publish_at_utc} (and privacyStatus -> private)")

            update_video_publish_time(youtube, vid, publish_at_utc)
            print("    ✅ Updated\n")

    except HttpError as e:
        # Common causes: insufficient scope, not owner of channel, video not editable, etc.
        raise SystemExit(f"YouTube API error:\n{e}")


if __name__ == "__main__":
    main()
