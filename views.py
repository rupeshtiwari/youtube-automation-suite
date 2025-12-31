"""
Views for displaying playlists, videos, and calendar.
"""

from typing import Dict, List, Any
import os


def get_youtube_service():
    """Get YouTube API service."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        CLIENT_SECRET_FILE = "client_secret.json"
        TOKEN_FILE = "token.json"
        
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"Error getting YouTube service: {e}")
        return None


def fetch_all_playlists_from_youtube(youtube, channel_id: str) -> List[Dict[str, Any]]:
    """Fetch all playlists from YouTube."""
    playlists = []
    page_token = None
    
    while True:
        try:
            if page_token:
                response = youtube.playlists().list(
                    part="id,snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=page_token
                ).execute()
            else:
                response = youtube.playlists().list(
                    part="id,snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=50
                ).execute()
            
            for pl in response.get("items", []):
                snippet = pl.get("snippet", {})
                playlists.append({
                    "playlistId": pl["id"],
                    "playlistTitle": snippet.get("title", ""),
                    "playlistDescription": snippet.get("description", ""),
                    "playlistUrl": f"https://www.youtube.com/playlist?list={pl['id']}",
                    "itemCount": pl.get("contentDetails", {}).get("itemCount", 0),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", "")
                })
            
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            break
    
    return playlists


def fetch_playlist_videos_from_youtube(youtube, playlist_id: str) -> List[Dict[str, Any]]:
    """Fetch all videos in a playlist from YouTube."""
    videos = []
    page_token = None
    
    while True:
        try:
            if page_token:
                response = youtube.playlistItems().list(
                    part="id,snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=page_token
                ).execute()
            else:
                response = youtube.playlistItems().list(
                    part="id,snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=50
                ).execute()
            
            video_ids = [item["contentDetails"]["videoId"] for item in response.get("items", [])]
            
            if video_ids:
                # Get video details
                videos_response = youtube.videos().list(
                    part="id,snippet,status",
                    id=",".join(video_ids),
                    maxResults=50
                ).execute()
                
                for video in videos_response.get("items", []):
                    snippet = video.get("snippet", {})
                    status = video.get("status", {})
                    video_id = video["id"]
                    
                    videos.append({
                        "videoId": video_id,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                        "publishedAt": snippet.get("publishedAt", ""),
                        "publishAt": status.get("publishAt", ""),
                        "privacyStatus": status.get("privacyStatus", ""),
                        "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
                        "tags": ", ".join(snippet.get("tags", []))
                    })
            
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Error fetching playlist videos: {e}")
            break
    
    return videos


def get_video_social_posts_from_db(video_id: str) -> Dict[str, Any]:
    """Get social media posts for a video from database."""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    posts = {}
    for platform in ['linkedin', 'facebook', 'instagram']:
        cursor.execute('''
            SELECT post_content, schedule_date, actual_scheduled_date, status
            FROM social_media_posts
            WHERE video_id = ? AND platform = ?
        ''', (video_id, platform))
        
        row = cursor.fetchone()
        if row:
            posts[platform] = {
                'post_content': row[0],
                'schedule_date': row[1],
                'actual_scheduled_date': row[2],
                'status': row[3]
            }
        else:
            posts[platform] = None
    
    conn.close()
    return posts

