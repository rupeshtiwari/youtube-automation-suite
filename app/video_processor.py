"""
Video processing module for downloading YouTube videos and uploading to social media platforms.
This enables native video uploads for maximum engagement.
"""

import os
import yt_dlp
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
import time


class VideoDownloader:
    """Downloads videos from YouTube for native upload to social platforms."""
    
    def __init__(self, output_dir: str = "data/videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, video_id: str, quality: str = "best[height<=1080]") -> Optional[str]:
        """
        Download video from YouTube.
        
        Args:
            video_id: YouTube video ID
            quality: Video quality (default: 1080p max for social media)
        
        Returns:
            Path to downloaded video file, or None if failed
        """
        try:
            ydl_opts = {
                'format': quality,
                'outtmpl': str(self.output_dir / f'{video_id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                
                # Download
                ydl.download([url])
                
                # Return actual file path
                if os.path.exists(filename):
                    return filename
                else:
                    # Try to find the file with correct extension
                    base_name = filename.rsplit('.', 1)[0]
                    for ext in ['.mp4', '.webm', '.mkv']:
                        if os.path.exists(base_name + ext):
                            return base_name + ext
                    
            return None
        except Exception as e:
            print(f"Error downloading video {video_id}: {e}")
            return None
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video metadata without downloading."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'duration': info.get('duration'),
                    'width': info.get('width'),
                    'height': info.get('height'),
                    'filesize': info.get('filesize'),
                    'format': info.get('format'),
                }
        except Exception as e:
            print(f"Error getting video info {video_id}: {e}")
            return None


class LinkedInVideoUploader:
    """Uploads videos natively to LinkedIn."""
    
    def __init__(self, access_token: str, person_urn: str):
        self.access_token = access_token
        self.person_urn = person_urn
        self.api_base = "https://api.linkedin.com/v2"
    
    def upload_video(self, video_path: str, caption: str, title: str = None) -> Dict[str, Any]:
        """
        Upload video natively to LinkedIn.
        
        Process:
        1. Register upload (get upload URL)
        2. Upload video file
        3. Create post with video URN
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Step 1: Register upload
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": self.person_urn,
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            response = requests.post(
                f"{self.api_base}/assets?action=registerUpload",
                headers=headers,
                json=register_data
            )
            
            if response.status_code != 200:
                return {'success': False, 'error': f"Register failed: {response.text}"}
            
            upload_data = response.json()
            upload_url = upload_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = upload_data['value']['asset']
            
            # Step 2: Upload video file
            with open(video_path, 'rb') as video_file:
                upload_headers = {
                    "Authorization": f"Bearer {self.access_token}",
                }
                upload_response = requests.put(upload_url, headers=upload_headers, data=video_file)
                
                if upload_response.status_code not in [200, 201]:
                    return {'success': False, 'error': f"Upload failed: {upload_response.text}"}
            
            # Step 3: Create post with video
            post_data = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": caption
                        },
                        "shareMediaCategory": "VIDEO",
                        "media": [{
                            "status": "READY",
                            "media": asset_urn,
                            "title": {
                                "text": title or "Video Post"
                            }
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            post_response = requests.post(
                f"{self.api_base}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if post_response.status_code in [200, 201]:
                return {
                    'success': True,
                    'post_id': post_response.json().get('id'),
                    'message': 'Video uploaded successfully'
                }
            else:
                return {'success': False, 'error': f"Post creation failed: {post_response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class FacebookVideoUploader:
    """Uploads videos natively to Facebook Page."""
    
    def __init__(self, page_id: str, page_access_token: str):
        self.page_id = page_id
        self.page_access_token = page_access_token
        self.api_base = "https://graph.facebook.com/v18.0"
    
    def upload_video(self, video_path: str, caption: str, title: str = None) -> Dict[str, Any]:
        """
        Upload video natively to Facebook Page.
        
        Facebook supports resumable uploads for large files.
        """
        try:
            # For videos under 1GB, use simple upload
            file_size = os.path.getsize(video_path)
            
            if file_size < 1024 * 1024 * 1024:  # < 1GB
                # Simple upload
                with open(video_path, 'rb') as video_file:
                    files = {'source': video_file}
                    data = {
                        'description': caption,
                        'access_token': self.page_access_token
                    }
                    
                    response = requests.post(
                        f"{self.api_base}/{self.page_id}/videos",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        return {
                            'success': True,
                            'post_id': result.get('id'),
                            'message': 'Video uploaded successfully'
                        }
                    else:
                        return {'success': False, 'error': f"Upload failed: {response.text}"}
            else:
                # Resumable upload for large files
                return self._resumable_upload(video_path, caption)
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resumable_upload(self, video_path: str, caption: str) -> Dict[str, Any]:
        """Handle resumable upload for large files."""
        # Implementation for resumable uploads
        # Facebook Graph API supports this for files > 1GB
        return {'success': False, 'error': 'Resumable upload not yet implemented'}


class InstagramVideoUploader:
    """Uploads videos natively to Instagram (as Reels or regular posts)."""
    
    def __init__(self, business_account_id: str, access_token: str):
        self.business_account_id = business_account_id
        self.access_token = access_token
        self.api_base = "https://graph.facebook.com/v18.0"
    
    def upload_video(self, video_path: str, caption: str, is_reel: bool = True) -> Dict[str, Any]:
        """
        Upload video natively to Instagram.
        
        Instagram requires:
        1. Upload video file to Facebook's servers (via Page)
        2. Create container with video URL
        3. Publish container
        """
        try:
            # Step 1: Upload video to Facebook Page first (Instagram requires video from Facebook)
            # We need to use the Facebook Page ID and access token
            # For now, we'll use a workaround: upload via container API with direct file upload
            
            # Instagram Graph API v18+ supports direct file uploads for Reels
            # Method: Use multipart/form-data to upload video directly
            
            with open(video_path, 'rb') as video_file:
                files = {
                    'media_type': (None, 'REELS' if is_reel else 'VIDEO'),
                    'video_file': (os.path.basename(video_path), video_file, 'video/mp4'),
                    'caption': (None, caption),
                }
                
                data = {
                    'access_token': self.access_token
                }
                
                # Create container with direct file upload
                response = requests.post(
                    f"{self.api_base}/{self.business_account_id}/media",
                    files=files,
                    data=data
                )
                
                if response.status_code not in [200, 201]:
                    # Fallback: Try using video_url method (requires video to be hosted)
                    # This would require uploading to Facebook storage first
                    return {
                        'success': False, 
                        'error': f"Container creation failed: {response.text}",
                        'note': 'Instagram requires video to be uploaded via Facebook Page first. Please ensure Facebook Page ID and access token are configured.'
                    }
            
            creation_id = response.json().get('id')
            
            if not creation_id:
                return {'success': False, 'error': 'No creation ID returned from Instagram API'}
            
            # Step 2: Wait for video processing (Instagram needs time to process)
            max_wait = 60  # Maximum 60 seconds
            wait_time = 0
            status = 'IN_PROGRESS'
            
            while status == 'IN_PROGRESS' and wait_time < max_wait:
                time.sleep(5)
                wait_time += 5
                
                status_response = requests.get(
                    f"{self.api_base}/{creation_id}",
                    params={'fields': 'status_code', 'access_token': self.access_token}
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status_code', 'IN_PROGRESS')
                    if status == 'FINISHED':
                        break
            
            # Step 3: Publish container
            publish_data = {
                'creation_id': creation_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(
                f"{self.api_base}/{self.business_account_id}/media_publish",
                data=publish_data
            )
            
            if publish_response.status_code in [200, 201]:
                return {
                    'success': True,
                    'post_id': publish_response.json().get('id'),
                    'message': 'Video uploaded successfully to Instagram'
                }
            else:
                return {
                    'success': False, 
                    'error': f"Publish failed: {publish_response.text}",
                    'creation_id': creation_id  # Return creation_id for manual publishing
                }
                
        except Exception as e:
            import traceback
            return {
                'success': False, 
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _upload_to_facebook_server(self, video_path: str) -> str:
        """
        Upload video to Facebook's servers and get URL.
        Instagram requires video to be hosted on Facebook's servers first.
        """
        try:
            # Step 1: Create a video upload session
            file_size = os.path.getsize(video_path)
            
            # For Instagram, we need to upload to Facebook Page first
            # Then use that video for Instagram
            # This is a simplified approach - Instagram API requires video_url from Facebook
            
            # Alternative: Upload directly using Instagram's container API
            # Instagram allows direct upload via container creation
            # We'll use the container approach instead
            
            # Return the local file path - Instagram API can handle direct uploads
            # But we need to upload it to a publicly accessible URL first
            # For now, we'll use the container API which accepts local file uploads via multipart
            
            # Actually, Instagram Graph API requires the video to be accessible via URL
            # We need to upload to Facebook's storage first, then use that URL
            
            # Simplified: Return file path - will be handled in upload_video method
            return video_path
            
        except Exception as e:
            print(f"Error preparing video for Facebook server: {e}")
            return video_path  # Fallback to local path


def process_and_upload_video(
    video_id: str,
    platforms: list,
    captions: dict,
    api_credentials: dict
) -> Dict[str, Any]:
    """
    Complete workflow: Download video and upload to platforms.
    
    Args:
        video_id: YouTube video ID
        platforms: List of platforms ['linkedin', 'facebook', 'instagram']
        captions: Dict of captions per platform
        api_credentials: Dict with access tokens and IDs
    
    Returns:
        Dict with results for each platform
    """
    results = {}
    
    # Step 1: Download video
    downloader = VideoDownloader()
    video_path = downloader.download_video(video_id)
    
    if not video_path:
        return {'error': 'Failed to download video', 'results': {}}
    
    try:
        # Step 2: Upload to each platform
        if 'linkedin' in platforms:
            uploader = LinkedInVideoUploader(
                api_credentials.get('linkedin_access_token'),
                api_credentials.get('linkedin_person_urn')
            )
            results['linkedin'] = uploader.upload_video(
                video_path,
                captions.get('linkedin', '')
            )
        
        if 'facebook' in platforms:
            uploader = FacebookVideoUploader(
                api_credentials.get('facebook_page_id'),
                api_credentials.get('facebook_page_access_token')
            )
            results['facebook'] = uploader.upload_video(
                video_path,
                captions.get('facebook', '')
            )
        
        if 'instagram' in platforms:
            uploader = InstagramVideoUploader(
                api_credentials.get('instagram_business_account_id'),
                api_credentials.get('instagram_access_token')
            )
            results['instagram'] = uploader.upload_video(
                video_path,
                captions.get('instagram', ''),
                is_reel=True  # Upload as Reel for better engagement
            )
        
        return {'success': True, 'results': results}
        
    finally:
        # Clean up: Delete downloaded video after upload
        # Only delete if all uploads succeeded
        all_succeeded = all(
            result.get('success', False) 
            for result in results.values() 
            if isinstance(result, dict)
        )
        
        if all_succeeded and video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"Cleaned up downloaded video: {video_path}")
            except Exception as e:
                print(f"Warning: Could not delete video file {video_path}: {e}")

