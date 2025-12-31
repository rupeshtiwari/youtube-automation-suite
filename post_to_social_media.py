"""
Post content to LinkedIn, Facebook, and Instagram, then update Excel file
with actual scheduled dates and status.

Supports two methods:
1. Native APIs (LinkedIn, Facebook Graph API, Instagram Graph API)
2. Ayrshare API (simpler, unified interface)

Usage:
    python post_to_social_media.py --excel youtube_shorts_export.xlsx --platforms linkedin facebook instagram
"""

from __future__ import annotations

import os
import sys
import argparse
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")  # Format: urn:li:person:xxxxx

FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")  # Same as Facebook Page Token

AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")

# API endpoints (will be constructed dynamically)
LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"


class SocialMediaPoster:
    """Handle posting to social media platforms."""
    
    def __init__(self, use_ayrshare: bool = False):
        self.use_ayrshare = use_ayrshare
        if use_ayrshare:
            try:
                from ayrshare import SocialPost
                self.ayrshare = SocialPost(AYRSHARE_API_KEY) if AYRSHARE_API_KEY else None
            except ImportError:
                print("Warning: ayrshare package not installed. Install with: pip install social-post-api")
                self.ayrshare = None
                self.use_ayrshare = False
    
    def post_to_linkedin(self, content: str, schedule_date: Optional[str] = None) -> Dict[str, Any]:
        """Post to LinkedIn using native API."""
        if self.use_ayrshare and self.ayrshare:
            return self._post_via_ayrshare(content, ["linkedin"], schedule_date)
        
        if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
            return {
                "success": False,
                "error": "LinkedIn credentials not configured. Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env"
            }
        
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # LinkedIn UGC Post structure
        post_data = {
            "author": LINKEDIN_PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(LINKEDIN_API_URL, headers=headers, json=post_data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "post_id": result.get("id", ""),
                "scheduled_date": schedule_date or datetime.now().isoformat(),
                "status": "scheduled" if schedule_date else "published"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }
    
    def post_to_facebook(self, content: str, schedule_date: Optional[str] = None) -> Dict[str, Any]:
        """Post to Facebook Page using Graph API."""
        if self.use_ayrshare and self.ayrshare:
            return self._post_via_ayrshare(content, ["facebook"], schedule_date)
        
        if not FACEBOOK_PAGE_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            return {
                "success": False,
                "error": "Facebook credentials not configured. Set FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env"
            }
        
        # Construct API URL dynamically
        facebook_api_url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/feed"
        
        params = {
            "message": content,
            "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
        }
        
        # If scheduling, add published=false and scheduled_publish_time
        if schedule_date:
            try:
                # Convert schedule_date to Unix timestamp
                dt = datetime.fromisoformat(schedule_date.replace('Z', '+00:00'))
                params["published"] = "false"
                params["scheduled_publish_time"] = int(dt.timestamp())
            except:
                pass
        
        try:
            response = requests.post(facebook_api_url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "post_id": result.get("id", ""),
                "scheduled_date": schedule_date or datetime.now().isoformat(),
                "status": "scheduled" if schedule_date else "published"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }
    
    def post_to_instagram(self, content: str, image_url: Optional[str] = None, schedule_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Instagram Business Account.
        Note: Instagram requires an image. If no image_url provided, will use a default or skip.
        """
        if self.use_ayrshare and self.ayrshare:
            return self._post_via_ayrshare(content, ["instagram"], schedule_date)
        
        if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
            return {
                "success": False,
                "error": "Instagram credentials not configured. Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env"
            }
        
        # Instagram requires an image. For text-only posts, we'll create a container but it may fail.
        # In production, you'd want to generate an image from the text or use a default image.
        if not image_url:
            return {
                "success": False,
                "error": "Instagram requires an image. Provide image_url or use Ayrshare which handles this automatically.",
                "status": "error"
            }
        
        # Construct API URL dynamically
        instagram_api_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
        
        # Step 1: Create media container
        container_params = {
            "image_url": image_url,
            "caption": content,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        
        try:
            # Create container
            container_response = requests.post(instagram_api_url, params=container_params, timeout=30)
            container_response.raise_for_status()
            container_id = container_response.json().get("id")
            
            if not container_id:
                return {
                    "success": False,
                    "error": "Failed to create Instagram media container",
                    "status": "error"
                }
            
            # Step 2: Publish the container
            publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
            publish_params = {
                "creation_id": container_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }
            
            publish_response = requests.post(publish_url, params=publish_params, timeout=30)
            publish_response.raise_for_status()
            result = publish_response.json()
            
            return {
                "success": True,
                "post_id": result.get("id", ""),
                "scheduled_date": schedule_date or datetime.now().isoformat(),
                "status": "published"  # Instagram doesn't support scheduling via API directly
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }
    
    def _post_via_ayrshare(self, content: str, platforms: List[str], schedule_date: Optional[str] = None) -> Dict[str, Any]:
        """Post via Ayrshare API (unified interface)."""
        if not self.ayrshare:
            return {
                "success": False,
                "error": "Ayrshare not configured. Set AYRSHARE_API_KEY in .env",
                "status": "error"
            }
        
        post_data = {
            "post": content,
            "platforms": platforms
        }
        
        if schedule_date:
            try:
                # Ayrshare expects schedule date in specific format
                dt = datetime.fromisoformat(schedule_date.replace('Z', '+00:00'))
                post_data["scheduleDate"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        try:
            result = self.ayrshare.post(post_data)
            
            # Ayrshare returns different structure
            if result.get("status") == "success":
                return {
                    "success": True,
                    "post_id": result.get("id", ""),
                    "scheduled_date": schedule_date or datetime.now().isoformat(),
                    "status": "scheduled" if schedule_date else "published"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "status": "error"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }


def update_excel_with_posting_results(
    excel_path: str,
    sheet_name: str,
    row_index: int,
    platform: str,
    result: Dict[str, Any]
):
    """Update Excel file with posting results."""
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(excel_path, engine='openpyxl')
        df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
        
        # Update columns based on platform
        if platform.lower() == "linkedin":
            df.at[row_index, "LinkedIn Actual Scheduled Date"] = result.get("scheduled_date", "")
            df.at[row_index, "LinkedIn Status"] = result.get("status", "error")
        elif platform.lower() == "facebook":
            df.at[row_index, "Facebook Actual Scheduled Date"] = result.get("scheduled_date", "")
            df.at[row_index, "Facebook Status"] = result.get("status", "error")
        elif platform.lower() == "instagram":
            df.at[row_index, "Instagram Actual Scheduled Date"] = result.get("scheduled_date", "")
            df.at[row_index, "Instagram Status"] = result.get("status", "error")
        
        # Write back to Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write all sheets
            for sheet in excel_file.sheet_names:
                if sheet == sheet_name:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # Preserve other sheets
                    other_df = pd.read_excel(excel_file, sheet_name=sheet, engine='openpyxl')
                    other_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True
    except Exception as e:
        print(f"Error updating Excel: {e}")
        return False


def post_from_excel(
    excel_path: str,
    platforms: List[str],
    sheet_name: Optional[str] = None,
    start_row: int = 0,
    end_row: Optional[int] = None,
    use_ayrshare: bool = False,
    dry_run: bool = False
):
    """
    Read Excel file and post to social media platforms.
    
    Args:
        excel_path: Path to Excel file
        platforms: List of platforms to post to (linkedin, facebook, instagram)
        sheet_name: Specific sheet to process (None = all sheets)
        start_row: Starting row index (0-based)
        end_row: Ending row index (None = all rows)
        use_ayrshare: Use Ayrshare API instead of native APIs
        dry_run: If True, don't actually post, just show what would be posted
    """
    poster = SocialMediaPoster(use_ayrshare=use_ayrshare)
    
    # Read Excel file
    excel_file = pd.ExcelFile(excel_path, engine='openpyxl')
    sheets_to_process = [sheet_name] if sheet_name else excel_file.sheet_names
    
    for sheet in sheets_to_process:
        print(f"\n📊 Processing sheet: {sheet}")
        df = pd.read_excel(excel_file, sheet_name=sheet, engine='openpyxl')
        
        # Determine row range
        rows_to_process = range(start_row, min(end_row or len(df), len(df)))
        
        for idx in rows_to_process:
            row = df.iloc[idx]
            
            # Get post content and schedule dates
            linkedin_post = str(row.get("LinkedIn Post", ""))
            facebook_post = str(row.get("Facebook Post", ""))
            instagram_post = str(row.get("Instagram Post", ""))
            
            linkedin_schedule = str(row.get("LinkedIn Schedule Date", "")) if pd.notna(row.get("LinkedIn Schedule Date")) else None
            facebook_schedule = str(row.get("Facebook Schedule Date", "")) if pd.notna(row.get("Facebook Schedule Date")) else None
            instagram_schedule = str(row.get("Instagram Schedule Date", "")) if pd.notna(row.get("Instagram Schedule Date")) else None
            
            # Get video title for reference
            video_title = row.get("Title", f"Video {idx+1}")
            
            print(f"\n🎬 [{idx+1}/{len(df)}] {video_title}")
            
            # Post to each platform
            for platform in platforms:
                platform_lower = platform.lower()
                
                if platform_lower == "linkedin":
                    content = linkedin_post
                    schedule = linkedin_schedule
                    status_col = "LinkedIn Status"
                elif platform_lower == "facebook":
                    content = facebook_post
                    schedule = facebook_schedule
                    status_col = "Facebook Status"
                elif platform_lower == "instagram":
                    content = instagram_post
                    schedule = instagram_schedule
                    status_col = "Instagram Status"
                else:
                    print(f"  ⚠️  Unknown platform: {platform}")
                    continue
                
                # Skip if already posted/scheduled
                current_status = str(row.get(status_col, "pending"))
                if current_status in ["scheduled", "published"] and not dry_run:
                    print(f"  ⏭️  {platform.capitalize()}: Already {current_status}, skipping...")
                    continue
                
                if not content or content == "nan":
                    print(f"  ⚠️  {platform.capitalize()}: No content to post")
                    continue
                
                print(f"  📤 Posting to {platform.capitalize()}...")
                
                if dry_run:
                    print(f"     [DRY RUN] Would post: {content[:100]}...")
                    print(f"     Schedule: {schedule or 'Immediate'}")
                    continue
                
                # Post to platform
                if platform_lower == "linkedin":
                    result = poster.post_to_linkedin(content, schedule)
                elif platform_lower == "facebook":
                    result = poster.post_to_facebook(content, schedule)
                elif platform_lower == "instagram":
                    # Instagram requires image - you may want to use YouTube thumbnail
                    youtube_url = row.get("YouTube URL", "")
                    image_url = None  # In production, extract thumbnail from YouTube URL
                    result = poster.post_to_instagram(content, image_url, schedule)
                
                # Update Excel
                if result.get("success"):
                    print(f"     ✅ Success! Post ID: {result.get('post_id', 'N/A')}")
                    update_excel_with_posting_results(excel_path, sheet, idx, platform_lower, result)
                else:
                    print(f"     ❌ Failed: {result.get('error', 'Unknown error')}")
                    update_excel_with_posting_results(excel_path, sheet, idx, platform_lower, result)
                
                # Rate limiting - be nice to APIs
                time.sleep(2)
    
    print(f"\n✅ Finished processing {excel_path}")


def main():
    parser = argparse.ArgumentParser(description="Post to social media from Excel file")
    parser.add_argument("--excel", required=True, help="Path to Excel file")
    parser.add_argument("--platforms", nargs="+", required=True, 
                       choices=["linkedin", "facebook", "instagram"],
                       help="Platforms to post to")
    parser.add_argument("--sheet", help="Specific sheet name (default: all sheets)")
    parser.add_argument("--start-row", type=int, default=0, help="Starting row (0-based)")
    parser.add_argument("--end-row", type=int, help="Ending row (0-based, default: all)")
    parser.add_argument("--use-ayrshare", action="store_true", 
                       help="Use Ayrshare API instead of native APIs")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run - don't actually post")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.excel):
        print(f"❌ Error: Excel file not found: {args.excel}")
        sys.exit(1)
    
    post_from_excel(
        excel_path=args.excel,
        platforms=args.platforms,
        sheet_name=args.sheet,
        start_row=args.start_row,
        end_row=args.end_row,
        use_ayrshare=args.use_ayrshare,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()

