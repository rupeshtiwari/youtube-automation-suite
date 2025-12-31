"""
Export YouTube Shorts playlists (playlists containing "shorts" in name) 
from the authenticated user's YouTube channel into a single Excel file.
Each playlist gets its own tab in the Excel file.

Fields exported per video:
- Video Name (videoId)
- Title
- Description
- Tags
- YouTube Schedule/Published Date (Wednesday 11pm IST)
- Privacy Status
- Type (derived: leadership/sys design)
- Role (derived: dir, mgr, vp, sa)
- LinkedIn Post (enhanced viral version)
- Facebook Post (enhanced viral version)
- Instagram Post (enhanced viral version)
- LinkedIn Schedule Date (Wednesday 7:30pm IST - calculated, starting Jan 7, 2025)
- Facebook Schedule Date (Wednesday 7:30pm IST - calculated, starting Jan 7, 2025)
- Instagram Schedule Date (Wednesday 7:30pm IST - calculated, starting Jan 7, 2025)
- LinkedIn Actual Scheduled Date (updated after posting)
- Facebook Actual Scheduled Date (updated after posting)
- Instagram Actual Scheduled Date (updated after posting)
- LinkedIn Status (pending/scheduled/error - updated after posting)
- Facebook Status (pending/scheduled/error - updated after posting)
- Instagram Status (pending/scheduled/error - updated after posting)
- YouTube URL (for reference)

Auth: OAuth (youtube.readonly)
"""

from __future__ import annotations

import os
import time
import json
import re
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Iterable, Optional

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"
OUTPUT_XLSX = "youtube_shorts_export.xlsx"

# IST timezone: UTC+05:30
IST = timezone(timedelta(hours=5, minutes=30))

# Starting date for social media scheduling: January 7, 2025, 7:30pm IST
START_SCHEDULE_DATE = datetime(2025, 1, 7, 19, 30, 0, tzinfo=IST)


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
    """Fetch all playlists and filter for those containing 'shorts' in the name."""
    playlists = []
    for pl in paged_request(
        youtube.playlists().list,
        part="id,snippet,contentDetails",
        channelId=channel_id,
        maxResults=50,
    ):
        snippet = pl.get("snippet", {})
        playlist_title = snippet.get("title", "").lower()
        
        # Filter for playlists containing "shorts" (case-insensitive)
        if "shorts" in playlist_title:
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
    Only includes public or scheduled videos.
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
            privacy_status = status.get("privacyStatus", "")
            publish_at = status.get("publishAt", "")
            
            # Only include public or scheduled videos
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


def derive_type(playlist_title: str, video_title: str, video_description: str, video_tags: str) -> str:
    """Derive video type: 'leadership' or 'sys design' based on content."""
    text = f"{playlist_title} {video_title} {video_description} {video_tags}".lower()
    
    sys_design_keywords = ["system design", "sys design", "system architecture", "architecture", 
                          "design pattern", "scalability", "distributed system", "microservices",
                          "database design", "api design", "infrastructure"]
    
    leadership_keywords = ["leadership", "management", "team", "people", "career", 
                          "mentor", "coaching", "strategy", "executive", "decision"]
    
    has_sys_design = any(keyword in text for keyword in sys_design_keywords)
    has_leadership = any(keyword in text for keyword in leadership_keywords)
    
    if has_sys_design and not has_leadership:
        return "sys design"
    elif has_leadership and not has_sys_design:
        return "leadership"
    elif has_sys_design and has_leadership:
        sys_count = sum(text.count(kw) for kw in sys_design_keywords)
        lead_count = sum(text.count(kw) for kw in leadership_keywords)
        return "sys design" if sys_count >= lead_count else "leadership"
    else:
        return ""


def derive_role(playlist_title: str, video_title: str, video_description: str, video_tags: str) -> str:
    """Derive role: 'dir', 'mgr', 'vp', 'sa' based on content."""
    text = f"{playlist_title} {video_title} {video_description} {video_tags}".lower()
    
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


def analyze_video_description(description: str) -> Dict[str, Any]:
    """
    Analyze video description to extract key topics, pain points, and value propositions.
    """
    if not description:
        return {
            "topics": [],
            "pain_points": [],
            "value_props": [],
            "key_phrases": []
        }
    
    desc_lower = description.lower()
    
    # Extract topics (common tech/leadership terms)
    topics = []
    topic_keywords = {
        "system design": ["system design", "architecture", "scalability", "distributed"],
        "interview": ["interview", "mock", "prep", "questions"],
        "career": ["career", "promotion", "advancement", "growth"],
        "leadership": ["leadership", "management", "team", "executive"],
        "coding": ["coding", "algorithm", "data structure", "leetcode"],
        "aws": ["aws", "amazon", "cloud", "s3", "lambda"],
        "behavioral": ["behavioral", "star", "situation", "example"]
    }
    
    for topic, keywords in topic_keywords.items():
        if any(kw in desc_lower for kw in keywords):
            topics.append(topic)
    
    # Extract pain points (common problem indicators)
    pain_points = []
    pain_indicators = ["fail", "reject", "struggle", "challenge", "difficult", "problem", "mistake", "error"]
    for indicator in pain_indicators:
        if indicator in desc_lower:
            # Extract sentence containing pain point
            sentences = re.split(r'[.!?]', description)
            for sent in sentences:
                if indicator in sent.lower() and len(sent.strip()) > 10:
                    pain_points.append(sent.strip()[:100])
                    break
    
    # Extract value propositions (benefit indicators)
    value_props = []
    value_indicators = ["learn", "master", "improve", "succeed", "win", "achieve", "get hired", "land"]
    for indicator in value_indicators:
        if indicator in desc_lower:
            sentences = re.split(r'[.!?]', description)
            for sent in sentences:
                if indicator in sent.lower() and len(sent.strip()) > 10:
                    value_props.append(sent.strip()[:100])
                    break
    
    # Extract key phrases (first 3 sentences)
    key_phrases = []
    sentences = [s.strip() for s in re.split(r'[.!?]', description) if s.strip()]
    key_phrases = sentences[:3]
    
    return {
        "topics": topics[:5],
        "pain_points": pain_points[:3],
        "value_props": value_props[:3],
        "key_phrases": key_phrases
    }


def extract_trending_hashtags(video_type: str, role: str, analysis: Dict[str, Any]) -> List[str]:
    """Generate relevant trending hashtags based on content."""
    hashtags = []
    
    # Base hashtags
    base_tags = ["FullStackMaster", "TechCareer", "CareerGrowth"]
    
    # Type-based tags
    if video_type == "leadership":
        hashtags.extend(["TechLeadership", "LeadershipDevelopment", "ManagementSkills", "ExecutiveCoaching"])
    elif video_type == "sys design":
        hashtags.extend(["SystemDesign", "SoftwareArchitecture", "TechInterview", "FAANGPrep"])
    
    # Role-based tags
    role_tags = {
        "vp": ["VPCareer", "ExecutiveLeadership", "TechExecutive"],
        "dir": ["DirectorLevel", "TechDirector", "EngineeringLeadership"],
        "mgr": ["TechManagement", "EngineeringManager", "TeamLeadership"],
        "sa": ["SolutionsArchitect", "CloudArchitecture", "AWSArchitect"]
    }
    hashtags.extend(role_tags.get(role, []))
    
    # Topic-based tags
    topic_tag_map = {
        "system design": ["SystemDesign", "ArchitecturePatterns", "ScalableSystems"],
        "interview": ["TechInterview", "InterviewPrep", "MockInterview"],
        "career": ["CareerAdvice", "TechCareer", "CareerGrowth"],
        "aws": ["AWS", "CloudComputing", "AmazonWebServices"],
        "coding": ["CodingInterview", "DataStructures", "Algorithms"]
    }
    
    for topic in analysis.get("topics", []):
        if topic in topic_tag_map:
            hashtags.extend(topic_tag_map[topic])
    
    # Combine and limit
    all_tags = base_tags + hashtags
    return list(dict.fromkeys(all_tags))[:15]  # Remove duplicates, limit to 15


def format_date(publish_at: str, published_at: str) -> str:
    """Format the date for display. Use publishAt (scheduled) if available, otherwise publishedAt."""
    date_str = publish_at or published_at
    if not date_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str


def calculate_social_media_schedule_date(video_index: int, base_date: Optional[datetime] = None) -> str:
    """
    Calculate schedule date for social media posts.
    Starting from Jan 7, 2025, 7:30pm IST, schedule every Wednesday 7:30pm IST.
    Each video gets the next available Wednesday.
    """
    if base_date is None:
        base_date = START_SCHEDULE_DATE
    
    # Find the first Wednesday from base_date
    days_until_wednesday = (2 - base_date.weekday()) % 7
    if days_until_wednesday == 0:
        # If it's already Wednesday, check if it's before 7:30pm
        if base_date.hour < 19 or (base_date.hour == 19 and base_date.minute < 30):
            # Use today if before 7:30pm
            first_wednesday = base_date.replace(hour=19, minute=30, second=0, microsecond=0)
        else:
            # Use next Wednesday if after 7:30pm
            first_wednesday = (base_date + timedelta(days=7)).replace(hour=19, minute=30, second=0, microsecond=0)
    else:
        # Find next Wednesday
        first_wednesday = (base_date + timedelta(days=days_until_wednesday)).replace(hour=19, minute=30, second=0, microsecond=0)
    
    # Add weeks for each video (each video gets next Wednesday)
    target_date = first_wednesday + timedelta(weeks=video_index)
    
    return target_date.strftime("%Y-%m-%d %H:%M:%S")


def generate_viral_linkedin_post(video_title: str, video_description: str, video_type: str, role: str, analysis: Dict[str, Any]) -> str:
    """Generate enhanced viral LinkedIn post based on video description analysis."""
    
    # Extract key insights from description
    key_phrases = analysis.get("key_phrases", [])
    pain_points = analysis.get("pain_points", [])
    value_props = analysis.get("value_props", [])
    
    # Create contextual hook based on content
    hooks = []
    if pain_points:
        hooks.append(f"❌ {pain_points[0][:50]}...")
        hooks.append(f"🚨 Most people fail here: {video_title}")
    if value_props:
        hooks.append(f"✅ {value_props[0][:50]}...")
        hooks.append(f"🎯 Want to {value_props[0].lower()[:40]}...?")
    
    # Default hooks
    if not hooks:
        if video_type == "leadership":
            hooks = ["🚀 Ready to level up your leadership game?", "💼 The secret to VP-level leadership?"]
        elif video_type == "sys design":
            hooks = ["💡 Want to master system design like a FAANG engineer?", "🏗️ Building scalable systems?"]
        else:
            hooks = ["🎯 Looking to accelerate your career?", "⚡ Game-changing insights for tech professionals"]
    
    hook = random.choice(hooks)
    
    # Build content
    content_parts = [hook, ""]
    
    if key_phrases:
        content_parts.append("📌 What you'll learn:")
        for phrase in key_phrases[:3]:
            if phrase:
                content_parts.append(f"• {phrase[:80]}")
        content_parts.append("")
    
    if pain_points:
        content_parts.append("⚠️ Common mistakes to avoid:")
        for pain in pain_points[:2]:
            if pain:
                content_parts.append(f"• {pain[:80]}")
        content_parts.append("")
    
    # CTA section
    role_text = {
        "vp": "VP-level",
        "dir": "Director-level",
        "mgr": "Management",
        "sa": "Senior Architect"
    }.get(role, "expert")
    
    content_parts.extend([
        f"💼 Perfect for {role_text} professionals looking to advance their career.",
        "",
        "🎓 Ready to take your skills to the next level?",
        "",
        f"Book a 1-on-1 session with me at https://fullstackmaster.net/book to:",
        "✅ Get personalized career guidance",
        "✅ Elevate your technical skills",
        "✅ Learn advanced strategies",
        "✅ Accelerate your growth",
        "",
        "📱 Questions? WhatsApp me: +1-609-442-4081",
        ""
    ])
    
    # Hashtags
    hashtags = extract_trending_hashtags(video_type, role, analysis)
    content_parts.append(" ".join([f"#{tag}" for tag in hashtags]))
    content_parts.append("")
    content_parts.append("Watch the full video →")
    
    return "\n".join(content_parts).strip()


def generate_viral_facebook_post(video_title: str, video_description: str, video_type: str, role: str, analysis: Dict[str, Any]) -> str:
    """Generate enhanced viral Facebook post based on video description analysis."""
    
    key_phrases = analysis.get("key_phrases", [])
    pain_points = analysis.get("pain_points", [])
    
    # Viral hooks
    hooks = [
        f"🔥 {video_title} - This changed everything!",
        f"💥 Just dropped: {video_title}",
        f"🚀 You NEED to see this: {video_title}",
        f"⚡ {video_title} - Game changer alert!",
    ]
    
    if pain_points:
        hooks.insert(0, f"❌ {pain_points[0][:60]}... Watch this!")
    
    hook = random.choice(hooks)
    
    content_parts = [hook, ""]
    
    if key_phrases:
        content_parts.append("👀 What you'll learn:")
        for phrase in key_phrases[:2]:
            if phrase:
                content_parts.append(f"• {phrase[:70]}")
        content_parts.append("")
    
    # Value proposition
    if video_type == "leadership":
        value = "Learn the leadership secrets that helped me and my students land VP and Director roles at top companies."
    elif video_type == "sys design":
        value = "Master system design patterns that FAANG engineers use daily. This is the content that gets you hired."
    else:
        value = "Get the insider knowledge that separates top performers from everyone else."
    
    content_parts.extend([
        value,
        "",
        "💡 Want personalized help?",
        "",
        f"I'm offering 1-on-1 coaching sessions! Book at https://fullstackmaster.net/book to:",
        "✨ Get custom career advice",
        "✨ Improve your technical skills",
        "✨ Learn from someone who's been there",
        "✨ Fast-track your success",
        "",
        "📱 Text me on WhatsApp: +1-609-442-4081",
        "",
        "Tag someone who needs to see this! 👇",
        ""
    ])
    
    hashtags = extract_trending_hashtags(video_type, role, analysis)
    content_parts.append(" ".join([f"#{tag}" for tag in hashtags[:10]]))
    
    return "\n".join(content_parts).strip()


def generate_viral_instagram_post(video_title: str, video_description: str, video_type: str, role: str, analysis: Dict[str, Any]) -> str:
    """Generate enhanced viral Instagram post based on video description analysis."""
    
    key_phrases = analysis.get("key_phrases", [])
    
    hooks = [
        f"✨ NEW VIDEO: {video_title}",
        f"🎬 {video_title} is LIVE!",
        f"🔥 {video_title} - Save this post!",
        f"💎 {video_title} - You don't want to miss this",
    ]
    hook = random.choice(hooks)
    
    content_parts = [hook, ""]
    
    if key_phrases:
        snippet = key_phrases[0][:100] if key_phrases else ""
        if snippet:
            content_parts.append(snippet)
            content_parts.append("")
    
    content_parts.extend([
        "💡 What's inside:",
        "✅ Actionable tips",
        "✅ Real examples",
        "✅ Step-by-step guidance",
        "",
        "🎯 Ready to level up?",
        "",
        "Book a 1-on-1 session with me! 👇",
        "🔗 Link in bio → https://fullstackmaster.net/book",
        "",
        "Get personalized coaching to:",
        "• Elevate your skills",
        "• Improve your career",
        "• Learn advanced techniques",
        "• Accelerate your growth",
        "",
        "📱 WhatsApp: +1-609-442-4081",
        "",
        "Save this post for later! 📌",
        ""
    ])
    
    hashtags = extract_trending_hashtags(video_type, role, analysis)
    content_parts.append(" ".join([f"#{tag}" for tag in hashtags]))
    
    return "\n".join(content_parts).strip()


def main():
    youtube = get_youtube_client()
    channel_id = get_my_channel_id(youtube)

    playlists = fetch_all_playlists(youtube, channel_id)
    if not playlists:
        print("No playlists with 'shorts' in the name found on this channel.")
        return

    print(f"Found {len(playlists)} shorts playlists. Processing from latest to oldest...")
    
    # Track video index for scheduling
    global_video_index = 0
    
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
                if not d:  # Skip if video was filtered out (not public/scheduled)
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
                
                # Calculate schedule dates (sequential Wednesdays starting Jan 7, 2025, 7:30pm IST)
                linkedin_schedule = calculate_social_media_schedule_date(global_video_index)
                facebook_schedule = calculate_social_media_schedule_date(global_video_index)
                instagram_schedule = calculate_social_media_schedule_date(global_video_index)
                
                # YouTube URL
                youtube_url = f"https://www.youtube.com/watch?v={vid}"
                
                rows.append(
                    {
                        "Video Name": vid,
                        "Title": video_title,
                        "Description": video_description,
                        "Tags": video_tags,
                        "YouTube Schedule/Published Date": youtube_schedule_date,
                        "Privacy Status": d.get("privacyStatus", ""),
                        "Type": video_type,
                        "Role": role,
                        "LinkedIn Post": linkedin_post,
                        "Facebook Post": facebook_post,
                        "Instagram Post": instagram_post,
                        "LinkedIn Schedule Date": linkedin_schedule,
                        "Facebook Schedule Date": facebook_schedule,
                        "Instagram Schedule Date": instagram_schedule,
                        "LinkedIn Actual Scheduled Date": "",  # Will be updated after posting
                        "Facebook Actual Scheduled Date": "",  # Will be updated after posting
                        "Instagram Actual Scheduled Date": "",  # Will be updated after posting
                        "LinkedIn Status": "pending",  # Will be updated after posting
                        "Facebook Status": "pending",  # Will be updated after posting
                        "Instagram Status": "pending",  # Will be updated after posting
                        "YouTube URL": youtube_url,
                    }
                )
                
                global_video_index += 1

            if not rows:
                print(f"  ⚠️  No public/scheduled videos found in this playlist. Skipping...")
                continue

            # Create DataFrame for this playlist
            df = pd.DataFrame(rows)
            
            # Clean playlist title for Excel sheet name (Excel has restrictions)
            sheet_name = playlist_title[:31]
            sheet_name = re.sub(r'[\\/:?*\[\]]', '_', sheet_name)
            if not sheet_name:
                sheet_name = f"Playlist_{idx}"
            
            # Write to Excel sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"  ✅ Exported {len(df)} videos to sheet: {sheet_name}")

    print(f"\n✅ Exported all shorts playlists to: {OUTPUT_XLSX}")
    print(f"Total videos scheduled: {global_video_index}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n❌ ERROR\n")
        print(str(e))
        print("\nIf this is the OAuth file issue, fix client_secret.json and re-run.\n")
        raise

