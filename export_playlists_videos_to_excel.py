"""
Export all playlists from the authenticated user's YouTube channel
and all videos within those playlists into a single Excel file.
Each playlist gets its own tab in the Excel file.

Fields exported per video:
- Video Name (videoId)
- Title
- Description
- Tags
- Schedule/Published Date
- Type (derived: leadership/sys design)
- Role (derived: dir, mgr, vp, sa)
- LinkedIn Post (SEO-optimized post text)
- Facebook Post (viral-style post text)
- Instagram Post (hashtag-optimized post text)

Auth: OAuth (youtube.readonly)
"""

from __future__ import annotations

import os
import time
import json
import re
import random
from datetime import datetime
from typing import Dict, List, Any, Iterable, Optional

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

CLIENT_SECRET_FILE = "client_secret.json"  # put OAuth JSON here
TOKEN_FILE = "token.json"
OUTPUT_XLSX = "youtube_playlists_videos_export.xlsx"


def validate_client_secret_file(path: str) -> None:
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
        raise RuntimeError(
            f"{path} is empty (0 bytes).\n\n"
            "Fix: re-download the OAuth JSON and overwrite this file."
        )

    # Common mistake: user saved an HTML page instead of JSON
    if raw.lower().startswith("<!doctype html") or raw.lower().startswith("<html"):
        raise RuntimeError(
            f"{path} looks like HTML, not JSON.\n\n"
            "Fix: you probably downloaded a web page. Re-download the OAuth JSON from Google Cloud Console."
        )

    if not raw.startswith("{"):
        raise RuntimeError(
            f"{path} does not look like JSON.\n\n"
            "Fix: re-download the OAuth JSON from Google Cloud Console."
        )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"{path} is not valid JSON: {e}\n\n"
            "Fix: re-download the OAuth JSON and overwrite this file."
        ) from e

    # Expect either "installed" or "web"
    if "installed" not in data and "web" not in data:
        raise RuntimeError(
            f"{path} JSON is valid, but doesn't contain expected keys 'installed' or 'web'.\n\n"
            "Fix: download the correct OAuth client JSON (prefer 'Desktop app')."
        )


def safe_execute(callable_fn, max_retries: int = 6):
    """Retry wrapper for transient YouTube API errors."""
    for attempt in range(max_retries):
        try:
            return callable_fn()
        except HttpError as e:
            status = getattr(e.resp, "status", None)
            # Retry on transient/rate-limited errors
            if status in (403, 429, 500, 503):
                time.sleep(2**attempt)
                continue
            raise
    raise RuntimeError("Max retries exceeded (YouTube API). Try again in a minute.")


def get_youtube_client():
    validate_client_secret_file(CLIENT_SECRET_FILE)

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            # Opens local browser for consent
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
    resp = safe_execute(lambda: youtube.channels().list(part="id", mine=True).execute())
    items = resp.get("items", [])
    if not items:
        raise RuntimeError(
            "No channel found for this account. Are you logged into the right Google account?"
        )
    return items[0]["id"]


def fetch_all_playlists(youtube, channel_id: str) -> List[Dict[str, Any]]:
    playlists = []
    for pl in paged_request(
        youtube.playlists().list,
        part="id,snippet,contentDetails",
        channelId=channel_id,
        maxResults=50,
    ):
        snippet = pl.get("snippet", {})
        playlists.append(
            {
                "playlistId": pl["id"],
                "playlistTitle": snippet.get("title", ""),
                "playlistItemCount": pl.get("contentDetails", {}).get(
                    "itemCount", None
                ),
                "publishedAt": snippet.get("publishedAt", ""),
            }
        )
    # Sort by publishedAt (latest first)
    playlists.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    return playlists


def fetch_all_playlist_video_ids(youtube, playlist_id: str) -> List[str]:
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
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def fetch_video_details(youtube, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Returns mapping: videoId -> fields (title, description, tags, publishedAt, publishAt, privacyStatus)
    videos.list supports up to 50 ids per call.
    """
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
            # Get scheduled publish time if available, otherwise use publishedAt
            publish_at = status.get("publishAt") or snippet.get("publishedAt", "")
            out[vid] = {
                "videoTitle": snippet.get("title", ""),
                "videoDescription": snippet.get("description", ""),
                "videoTags": ",".join(snippet.get("tags", []) or []),
                "publishedAt": snippet.get("publishedAt", ""),
                "publishAt": status.get("publishAt", ""),  # Scheduled time
                "privacyStatus": status.get("privacyStatus", ""),
            }
    return out


def derive_type(playlist_title: str, video_title: str, video_description: str, video_tags: str) -> str:
    """
    Derive video type: 'leadership' or 'sys design' based on content.
    """
    text = f"{playlist_title} {video_title} {video_description} {video_tags}".lower()
    
    # Check for system design keywords
    sys_design_keywords = ["system design", "sys design", "system architecture", "architecture", 
                          "design pattern", "scalability", "distributed system", "microservices",
                          "database design", "api design", "infrastructure"]
    
    # Check for leadership keywords
    leadership_keywords = ["leadership", "management", "team", "people", "career", 
                          "mentor", "coaching", "strategy", "executive", "decision"]
    
    has_sys_design = any(keyword in text for keyword in sys_design_keywords)
    has_leadership = any(keyword in text for keyword in leadership_keywords)
    
    if has_sys_design and not has_leadership:
        return "sys design"
    elif has_leadership and not has_sys_design:
        return "leadership"
    elif has_sys_design and has_leadership:
        # If both, prioritize based on which appears more
        sys_count = sum(text.count(kw) for kw in sys_design_keywords)
        lead_count = sum(text.count(kw) for kw in leadership_keywords)
        return "sys design" if sys_count >= lead_count else "leadership"
    else:
        return ""


def derive_role(playlist_title: str, video_title: str, video_description: str, video_tags: str) -> str:
    """
    Derive role: 'dir', 'mgr', 'vp', 'sa' based on content.
    """
    text = f"{playlist_title} {video_title} {video_description} {video_tags}".lower()
    
    # Check for role keywords (order matters - more specific first)
    if re.search(r'\b(vp|vice president|vice-president)\b', text):
        return "vp"
    elif re.search(r'\b(director|dir)\b', text):
        return "dir"
    elif re.search(r'\b(manager|mgr|management)\b', text):
        return "mgr"
    elif re.search(r'\b(senior architect|sa|architect)\b', text):
        return "sa"
    else:
        return ""


def format_date(publish_at: str, published_at: str) -> str:
    """
    Format the date for display. Use publishAt (scheduled) if available, otherwise publishedAt.
    """
    date_str = publish_at or published_at
    if not date_str:
        return ""
    
    try:
        # Parse ISO format date
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str


def generate_linkedin_post(video_title: str, video_description: str, video_type: str, role: str) -> str:
    """
    Generate LinkedIn post text - professional, engaging, SEO-optimized.
    """
    # Extract key points from description (first 200 chars)
    desc_snippet = video_description[:200].strip() if video_description else ""
    if desc_snippet and len(video_description) > 200:
        desc_snippet += "..."
    
    # Role-based messaging
    role_text = {
        "vp": "VP-level insights",
        "dir": "Director-level strategies",
        "mgr": "Management best practices",
        "sa": "Senior Architect expertise"
    }.get(role, "expert insights")
    
    # Type-based hook
    if video_type == "leadership":
        hook = "🚀 Ready to level up your leadership game?"
        value_prop = "Learn proven strategies that top executives use to drive results and build high-performing teams."
    elif video_type == "sys design":
        hook = "💡 Want to master system design like a FAANG engineer?"
        value_prop = "Discover the architecture patterns and design principles used at top tech companies."
    else:
        hook = "🎯 Looking to accelerate your career?"
        value_prop = "Get actionable insights from industry experts that you can apply immediately."
    
    post = f"""{hook}

In this video, I break down {role_text} that will transform how you approach your work.

📌 Key takeaways:
{desc_snippet if desc_snippet else "Watch to discover game-changing insights that top performers use."}

💼 Perfect for:
• Tech professionals looking to advance
• Leaders building scalable systems
• Engineers preparing for senior roles

🎓 Ready to take your skills to the next level?

Book a 1-on-1 session with me at fullstackmaster/book to:
✅ Get personalized career guidance
✅ Elevate your technical skills
✅ Learn advanced strategies
✅ Accelerate your growth

📱 Questions? WhatsApp me: +1-609-442-4081

#TechLeadership #SystemDesign #CareerGrowth #SoftwareEngineering #TechCareer #LeadershipDevelopment #TechMentor #CareerAdvice #FullStackMaster

Watch the full video →"""
    
    return post.strip()


def generate_facebook_post(video_title: str, video_description: str, video_type: str, role: str) -> str:
    """
    Generate Facebook post text - more casual, engaging, viral-style.
    """
    desc_snippet = video_description[:150].strip() if video_description else ""
    if desc_snippet and len(video_description) > 150:
        desc_snippet += "..."
    
    # Create engaging hooks
    hooks = [
        f"🔥 {video_title} - This changed everything for me!",
        f"💥 Just dropped: {video_title}",
        f"🚀 You NEED to see this: {video_title}",
        f"⚡ {video_title} - Game changer alert!",
    ]
    
    hook = random.choice(hooks)
    
    if video_type == "leadership":
        value = "Learn the leadership secrets that helped me and my students land VP and Director roles at top companies."
    elif video_type == "sys design":
        value = "Master system design patterns that FAANG engineers use daily. This is the content that gets you hired."
    else:
        value = "Get the insider knowledge that separates top performers from everyone else."
    
    post = f"""{hook}

{desc_snippet if desc_snippet else value}

👀 What you'll learn:
• Real-world strategies that actually work
• Insider tips from industry experts
• Actionable steps you can take today

💡 Want personalized help?

I'm offering 1-on-1 coaching sessions! Book at fullstackmaster/book to:
✨ Get custom career advice
✨ Improve your technical skills
✨ Learn from someone who's been there
✨ Fast-track your success

📱 Text me on WhatsApp: +1-609-442-4081

Tag someone who needs to see this! 👇

#TechCareer #SoftwareEngineering #CareerTips #TechJobs #LearnTech #SystemDesign #Leadership #TechMentor #CareerGrowth #FullStackMaster"""
    
    return post.strip()


def generate_instagram_post(video_title: str, video_description: str, video_type: str, role: str) -> str:
    """
    Generate Instagram post text - visual, emoji-rich, hashtag-optimized.
    """
    desc_snippet = video_description[:120].strip() if video_description else ""
    if desc_snippet and len(video_description) > 120:
        desc_snippet += "..."
    
    # Instagram-style hooks
    hooks = [
        f"✨ NEW VIDEO: {video_title}",
        f"🎬 {video_title} is LIVE!",
        f"🔥 {video_title} - Save this post!",
        f"💎 {video_title} - You don't want to miss this",
    ]
    
    hook = random.choice(hooks)
    
    if video_type == "leadership":
        value = "Level up your leadership skills with proven strategies 🚀"
    elif video_type == "sys design":
        value = "Master system design like a pro architect 🏗️"
    else:
        value = "Game-changing insights for your career growth 📈"
    
    post = f"""{hook}

{desc_snippet if desc_snippet else value}

💡 What's inside:
✅ Actionable tips
✅ Real examples
✅ Step-by-step guidance

🎯 Ready to level up?

Book a 1-on-1 session with me! 👇
🔗 Link in bio → fullstackmaster/book

Get personalized coaching to:
• Elevate your skills
• Improve your career
• Learn advanced techniques
• Accelerate your growth

📱 WhatsApp: +1-609-442-4081

Save this post for later! 📌

#TechCareer #SoftwareEngineer #SystemDesign #TechLeadership #CareerGrowth #TechTips #LearnToCode #TechMentor #CareerAdvice #FullStackMaster #TechJobs #SoftwareDevelopment #TechSkills #CareerDevelopment #TechCommunity"""
    
    return post.strip()


def main():
    youtube = get_youtube_client()
    channel_id = get_my_channel_id(youtube)

    playlists = fetch_all_playlists(youtube, channel_id)
    if not playlists:
        print("No playlists found on this channel.")
        return

    print(f"Found {len(playlists)} playlists. Processing from latest to oldest...")
    
    # Create Excel writer object
    with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
        for idx, pl in enumerate(playlists, 1):
            playlist_id = pl["playlistId"]
            playlist_title = pl["playlistTitle"]
            
            print(f"[{idx}/{len(playlists)}] Processing playlist: {playlist_title}")

            video_ids = fetch_all_playlist_video_ids(youtube, playlist_id)
            
            if not video_ids:
                print(f"  ⚠️  No videos found in this playlist. Skipping...")
                continue

            # Pull details once per playlist (dedupe IDs to reduce calls)
            details_map = fetch_video_details(youtube, list(dict.fromkeys(video_ids)))

            rows: List[Dict[str, Any]] = []
            for vid in video_ids:
                d = details_map.get(vid, {})
                video_title = d.get("videoTitle", "")
                video_description = d.get("videoDescription", "")
                video_tags = d.get("videoTags", "")
                
                # Derive type and role
                video_type = derive_type(playlist_title, video_title, video_description, video_tags)
                role = derive_role(playlist_title, video_title, video_description, video_tags)
                
                # Format date
                schedule_published_date = format_date(
                    d.get("publishAt", ""), 
                    d.get("publishedAt", "")
                )
                
                # Generate social media posts
                linkedin_post = generate_linkedin_post(video_title, video_description, video_type, role)
                facebook_post = generate_facebook_post(video_title, video_description, video_type, role)
                instagram_post = generate_instagram_post(video_title, video_description, video_type, role)
                
                rows.append(
                    {
                        "Video Name": vid,
                        "Title": video_title,
                        "Description": video_description,
                        "Tags": video_tags,
                        "Schedule/Published Date": schedule_published_date,
                        "Type": video_type,
                        "Role": role,
                        "LinkedIn Post": linkedin_post,
                        "Facebook Post": facebook_post,
                        "Instagram Post": instagram_post,
                    }
                )

            # Create DataFrame for this playlist
            df = pd.DataFrame(rows)
            
            # Clean playlist title for Excel sheet name (Excel has restrictions)
            # Excel sheet names: max 31 chars, no: \ / ? * [ ]
            sheet_name = playlist_title[:31]
            sheet_name = re.sub(r'[\\/:?*\[\]]', '_', sheet_name)
            if not sheet_name:
                sheet_name = f"Playlist_{idx}"
            
            # Write to Excel sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"  ✅ Exported {len(df)} videos to sheet: {sheet_name}")

    print(f"\n✅ Exported all playlists to: {OUTPUT_XLSX}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n❌ ERROR\n")
        print(str(e))
        print("\nIf this is the OAuth file issue, fix client_secret.json and re-run.\n")
        raise
