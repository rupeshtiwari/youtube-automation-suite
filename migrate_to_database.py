"""
Migration script to convert Excel files to SQLite database.
Run this once to migrate existing Excel data to the database.
"""

import pandas as pd
from database import init_database, insert_or_update_video, insert_or_update_social_post
from pathlib import Path
import sys


def migrate_excel_to_db(excel_path: str):
    """Migrate Excel file to database."""
    if not Path(excel_path).exists():
        print(f"❌ Excel file not found: {excel_path}")
        return False
    
    print(f"📊 Migrating {excel_path} to database...")
    
    # Initialize database
    init_database()
    
    # Read Excel file
    excel_file = pd.ExcelFile(excel_path, engine='openpyxl')
    
    total_videos = 0
    total_posts = 0
    
    for sheet_name in excel_file.sheet_names:
        print(f"\n  Processing sheet: {sheet_name}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
        
        for idx, row in df.iterrows():
            video_id = str(row.get('Video Name', ''))
            if not video_id or video_id == 'nan':
                continue
            
            # Extract video data
            video_data = {
                'video_id': video_id,
                'playlist_id': sheet_name,  # Use sheet name as playlist identifier
                'playlist_name': sheet_name,
                'title': str(row.get('Title', '')),
                'description': str(row.get('Description', '')),
                'tags': str(row.get('Tags', '')),
                'youtube_schedule_date': str(row.get('YouTube Schedule/Published Date', '') or row.get('Schedule/Published Date', '')),
                'youtube_published_date': str(row.get('YouTube Schedule/Published Date', '') or row.get('Schedule/Published Date', '')),
                'privacy_status': str(row.get('Privacy Status', '')),
                'video_type': str(row.get('Type', '')),
                'role': str(row.get('Role', '')),
                'youtube_url': str(row.get('YouTube URL', f"https://www.youtube.com/watch?v={video_id}"))
            }
            
            # Insert/update video
            insert_or_update_video(video_data)
            total_videos += 1
            
            # Insert/update social media posts
            platforms = ['linkedin', 'facebook', 'instagram']
            for platform in platforms:
                post_content = str(row.get(f'{platform.capitalize()} Post', ''))
                schedule_date = str(row.get(f'{platform.capitalize()} Schedule Date', ''))
                actual_date = str(row.get(f'{platform.capitalize()} Actual Scheduled Date', ''))
                status = str(row.get(f'{platform.capitalize()} Status', 'pending'))
                
                if post_content and post_content != 'nan':
                    post_data = {
                        'post_content': post_content,
                        'schedule_date': schedule_date if schedule_date != 'nan' else None,
                        'actual_scheduled_date': actual_date if actual_date != 'nan' else None,
                        'status': status if status != 'nan' else 'pending'
                    }
                    insert_or_update_social_post(video_id, platform, post_data)
                    total_posts += 1
        
        print(f"    ✅ Processed {len(df)} rows from {sheet_name}")
    
    print(f"\n✅ Migration complete!")
    print(f"   - Videos migrated: {total_videos}")
    print(f"   - Social posts migrated: {total_posts}")
    return True


def main():
    """Main migration function."""
    excel_files = [
        'youtube_shorts_export.xlsx',
        'youtube_playlists_videos_export.xlsx'
    ]
    
    migrated = False
    for excel_file in excel_files:
        if Path(excel_file).exists():
            migrate_excel_to_db(excel_file)
            migrated = True
    
    if not migrated:
        print("⚠️  No Excel files found to migrate.")
        print("   Looking for:")
        for f in excel_files:
            print(f"     - {f}")
        print("\n   Run export scripts first, or specify Excel file path:")
        print("   python migrate_to_database.py <excel_file_path>")
        
        if len(sys.argv) > 1:
            excel_path = sys.argv[1]
            migrate_excel_to_db(excel_path)
    else:
        print("\n💡 You can now use the database instead of Excel files!")
        print("   The database is: youtube_automation.db")


if __name__ == '__main__':
    main()

