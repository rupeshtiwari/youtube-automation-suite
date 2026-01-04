"""
Facebook and Instagram Graph API helpers with proper error handling
"""
import requests
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class FacebookInstagramAPI:
    """Helper class for Facebook and Instagram API operations"""
    
    def __init__(self, page_access_token: str, page_id: str = None, instagram_business_account_id: str = None):
        self.page_access_token = page_access_token
        self.page_id = page_id
        self.instagram_business_account_id = instagram_business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def verify_token(self) -> Tuple[bool, Optional[str]]:
        """Verify that the access token is valid"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                params={"access_token": self.page_access_token},
                timeout=10
            )
            if response.status_code == 200:
                return True, None
            else:
                error_data = response.json().get('error', {})
                error_msg = error_data.get('message', 'Invalid token')
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def schedule_facebook_video(self, video_url: str, caption: str, scheduled_publish_time: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Schedule a Facebook video post using link sharing (for now)
        Returns: (success, error_message, response_data)
        """
        try:
            if not self.page_id:
                return False, "Facebook Page ID is required", None
            
            # For link sharing (simpler approach)
            params = {
                "access_token": self.page_access_token,
                "message": caption,
                "link": video_url,
                "scheduled_publish_time": scheduled_publish_time,
                "published": False  # Schedule it, don't publish immediately
            }
            
            response = requests.post(
                f"{self.base_url}/{self.page_id}/feed",
                params=params,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and 'id' in response_data:
                post_id = response_data['id']
                # Verify the post was created
                verify_response = requests.get(
                    f"{self.base_url}/{post_id}",
                    params={"access_token": self.page_access_token, "fields": "id,message,created_time,scheduled_publish_time"},
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    return True, None, response_data
                else:
                    return False, "Post created but verification failed", None
            
            # Handle errors
            error = response_data.get('error', {})
            error_message = error.get('message', 'Unknown error')
            error_code = error.get('code', '')
            error_subcode = error.get('error_subcode', '')
            
            # Check for token expiration (error code 190)
            if error_code == 190:
                if 'expired' in error_message.lower() or error_subcode == 463:
                    return False, "TOKEN_EXPIRED: Facebook access token has expired. Please reconnect Facebook in Settings.", None
                elif error_subcode == 467:
                    return False, "TOKEN_INVALID: Facebook access token is invalid. Please reconnect Facebook in Settings.", None
                else:
                    return False, f"TOKEN_ERROR: Facebook access token issue. Please reconnect Facebook in Settings. ({error_message})", None
            
            return False, f"Facebook API error ({error_code}): {error_message}", None
            
        except requests.exceptions.Timeout:
            return False, "Request timeout - Facebook API did not respond", None
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", None
        except Exception as e:
            logger.error(f"Error scheduling Facebook video: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}", None
    
    def schedule_instagram_reel(self, video_url: str, caption: str, scheduled_publish_time: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Schedule an Instagram Reel
        Note: Instagram API requires native video upload, not link sharing
        For now, we'll use link sharing which creates a post, not a reel
        Returns: (success, error_message, response_data)
        """
        try:
            if not self.instagram_business_account_id:
                return False, "Instagram Business Account ID is required", None
            
            # Instagram doesn't support link sharing for reels
            # We need to download and upload the video natively
            # For now, return an error explaining this
            
            # TODO: Implement native video upload using createContainer API
            return False, "Instagram Reels require native video upload. Link sharing is not supported for reels.", None
            
        except Exception as e:
            logger.error(f"Error scheduling Instagram reel: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}", None
    
    def upload_instagram_reel_native(self, video_file_path: str, caption: str, scheduled_publish_time: str = None) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Upload Instagram Reel natively using createContainer API
        This is the correct way to post to Instagram
        """
        try:
            if not self.instagram_business_account_id:
                return False, "Instagram Business Account ID is required", None
            
            # Step 1: Create container
            container_params = {
                "access_token": self.page_access_token,
                "media_type": "REELS",
                "video_url": video_file_path,  # This should be a publicly accessible URL
                "caption": caption,
            }
            
            if scheduled_publish_time:
                container_params["share_to_feed"] = True
                # Note: Instagram doesn't support scheduled_publish_time in container creation
                # You need to publish immediately or use a different approach
            
            response = requests.post(
                f"{self.base_url}/{self.instagram_business_account_id}/media",
                params=container_params,
                timeout=60
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and 'id' in response_data:
                container_id = response_data['id']
                
                # Step 2: Publish the container
                publish_params = {
                    "access_token": self.page_access_token,
                    "creation_id": container_id
                }
                
                publish_response = requests.post(
                    f"{self.base_url}/{self.instagram_business_account_id}/media_publish",
                    params=publish_params,
                    timeout=60
                )
                
                publish_data = publish_response.json()
                
                if publish_response.status_code == 200 and 'id' in publish_data:
                    return True, None, publish_data
                else:
                    error = publish_data.get('error', {})
                    error_message = error.get('message', 'Publish failed')
                    return False, f"Instagram publish error: {error_message}", None
            
            # Handle errors
            error = response_data.get('error', {})
            error_message = error.get('message', 'Unknown error')
            error_code = error.get('code', '')
            
            return False, f"Instagram API error ({error_code}): {error_message}", None
            
        except requests.exceptions.Timeout:
            return False, "Request timeout - Instagram API did not respond", None
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", None
        except Exception as e:
            logger.error(f"Error uploading Instagram reel: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}", None

