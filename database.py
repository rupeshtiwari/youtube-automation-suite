"""
Database module for YouTube automation.
Uses SQLite for efficient data storage and querying.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd

# Support for NAS/Docker deployment with environment variable
DATA_DIR = os.getenv('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'youtube_automation.db')


def get_db_connection():
    """Get database connection with proper configuration."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_database():
    """Initialize database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Videos table - stores all video metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE NOT NULL,
            playlist_id TEXT,
            playlist_name TEXT,
            title TEXT,
            description TEXT,
            tags TEXT,
            youtube_schedule_date TEXT,
            youtube_published_date TEXT,
            privacy_status TEXT,
            video_type TEXT,
            role TEXT,
            custom_tags TEXT,
            youtube_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add custom_tags column if it doesn't exist (migration)
    try:
        cursor.execute('ALTER TABLE videos ADD COLUMN custom_tags TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Social media posts table - stores generated posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_media_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            post_content TEXT,
            schedule_date TEXT,
            actual_scheduled_date TEXT,
            status TEXT DEFAULT 'pending',
            post_id TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(video_id),
            UNIQUE(video_id, platform)
        )
    ''')
    
    # Playlists table - stores playlist metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id TEXT UNIQUE NOT NULL,
            playlist_name TEXT,
            item_count INTEGER,
            published_at TEXT,
            playlist_type TEXT,
            playlist_role TEXT,
            playlist_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add tag columns if they don't exist (migration)
    try:
        cursor.execute('ALTER TABLE playlists ADD COLUMN playlist_type TEXT')
        cursor.execute('ALTER TABLE playlists ADD COLUMN playlist_role TEXT')
        cursor.execute('ALTER TABLE playlists ADD COLUMN playlist_tags TEXT')
    except sqlite3.OperationalError:
        pass  # Columns already exist
    
    # Automation logs table - tracks automation runs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_type TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            videos_processed INTEGER DEFAULT 0,
            posts_created INTEGER DEFAULT 0,
            errors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_video_id ON videos(video_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_playlist_id ON videos(playlist_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_type ON videos(video_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_role ON videos(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_custom_tags ON videos(custom_tags)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_video_id ON social_media_posts(video_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_platform ON social_media_posts(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON social_media_posts(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_playlists_type ON playlists(playlist_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_playlists_role ON playlists(playlist_role)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def insert_or_update_video(video_data: Dict[str, Any]) -> int:
    """Insert or update video in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO videos (
            video_id, playlist_id, playlist_name, title, description, tags,
            youtube_schedule_date, youtube_published_date, privacy_status,
            video_type, role, youtube_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        video_data.get('video_id'),
        video_data.get('playlist_id'),
        video_data.get('playlist_name'),
        video_data.get('title'),
        video_data.get('description'),
        video_data.get('tags'),
        video_data.get('youtube_schedule_date'),
        video_data.get('youtube_published_date'),
        video_data.get('privacy_status'),
        video_data.get('video_type'),
        video_data.get('role'),
        video_data.get('youtube_url')
    ))
    
    conn.commit()
    video_db_id = cursor.lastrowid
    conn.close()
    return video_db_id


def insert_or_update_social_post(video_id: str, platform: str, post_data: Dict[str, Any]) -> int:
    """Insert or update social media post."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO social_media_posts (
            video_id, platform, post_content, schedule_date,
            actual_scheduled_date, status, post_id, error_message, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        video_id,
        platform,
        post_data.get('post_content'),
        post_data.get('schedule_date'),
        post_data.get('actual_scheduled_date'),
        post_data.get('status', 'pending'),
        post_data.get('post_id'),
        post_data.get('error_message')
    ))
    
    conn.commit()
    post_db_id = cursor.lastrowid
    conn.close()
    return post_db_id


def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    """Get video by video_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_videos_by_playlist(playlist_id: str) -> List[Dict[str, Any]]:
    """Get all videos in a playlist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM videos WHERE playlist_id = ? ORDER BY created_at DESC', (playlist_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_pending_posts(platform: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all pending social media posts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if platform:
        cursor.execute('''
            SELECT smp.*, v.title, v.youtube_url 
            FROM social_media_posts smp
            JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status = 'pending' AND smp.platform = ?
            ORDER BY smp.schedule_date ASC
        ''', (platform,))
    else:
        cursor.execute('''
            SELECT smp.*, v.title, v.youtube_url 
            FROM social_media_posts smp
            JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status = 'pending'
            ORDER BY smp.schedule_date ASC
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_post_status(video_id: str, platform: str, status: str, 
                      actual_scheduled_date: Optional[str] = None,
                      post_id: Optional[str] = None,
                      error_message: Optional[str] = None):
    """Update social media post status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE social_media_posts 
        SET status = ?, actual_scheduled_date = ?, post_id = ?, 
            error_message = ?, updated_at = CURRENT_TIMESTAMP
        WHERE video_id = ? AND platform = ?
    ''', (status, actual_scheduled_date, post_id, error_message, video_id, platform))
    
    conn.commit()
    conn.close()


def get_videos_for_export(playlist_id: Optional[str] = None) -> pd.DataFrame:
    """Get videos as pandas DataFrame for Excel export."""
    conn = get_db_connection()
    
    if playlist_id:
        query = '''
            SELECT 
                v.video_id as "Video Name",
                v.title as "Title",
                v.description as "Description",
                v.tags as "Tags",
                COALESCE(v.youtube_schedule_date, v.youtube_published_date) as "Schedule/Published Date",
                v.video_type as "Type",
                v.role as "Role",
                v.youtube_url as "YouTube URL",
                smp_linkedin.post_content as "LinkedIn Post",
                smp_facebook.post_content as "Facebook Post",
                smp_instagram.post_content as "Instagram Post",
                smp_linkedin.schedule_date as "LinkedIn Schedule Date",
                smp_facebook.schedule_date as "Facebook Schedule Date",
                smp_instagram.schedule_date as "Instagram Schedule Date",
                smp_linkedin.actual_scheduled_date as "LinkedIn Actual Scheduled Date",
                smp_facebook.actual_scheduled_date as "Facebook Actual Scheduled Date",
                smp_instagram.actual_scheduled_date as "Instagram Actual Scheduled Date",
                smp_linkedin.status as "LinkedIn Status",
                smp_facebook.status as "Facebook Status",
                smp_instagram.status as "Instagram Status"
            FROM videos v
            LEFT JOIN social_media_posts smp_linkedin ON v.video_id = smp_linkedin.video_id AND smp_linkedin.platform = 'linkedin'
            LEFT JOIN social_media_posts smp_facebook ON v.video_id = smp_facebook.video_id AND smp_facebook.platform = 'facebook'
            LEFT JOIN social_media_posts smp_instagram ON v.video_id = smp_instagram.video_id AND smp_instagram.platform = 'instagram'
            WHERE v.playlist_id = ?
            ORDER BY v.created_at DESC
        '''
        df = pd.read_sql_query(query, conn, params=(playlist_id,))
    else:
        query = '''
            SELECT 
                v.video_id as "Video Name",
                v.title as "Title",
                v.description as "Description",
                v.tags as "Tags",
                COALESCE(v.youtube_schedule_date, v.youtube_published_date) as "Schedule/Published Date",
                v.video_type as "Type",
                v.role as "Role",
                v.youtube_url as "YouTube URL",
                smp_linkedin.post_content as "LinkedIn Post",
                smp_facebook.post_content as "Facebook Post",
                smp_instagram.post_content as "Instagram Post",
                smp_linkedin.schedule_date as "LinkedIn Schedule Date",
                smp_facebook.schedule_date as "Facebook Schedule Date",
                smp_instagram.schedule_date as "Instagram Schedule Date",
                smp_linkedin.actual_scheduled_date as "LinkedIn Actual Scheduled Date",
                smp_facebook.actual_scheduled_date as "Facebook Actual Scheduled Date",
                smp_instagram.actual_scheduled_date as "Instagram Actual Scheduled Date",
                smp_linkedin.status as "LinkedIn Status",
                smp_facebook.status as "Facebook Status",
                smp_instagram.status as "Instagram Status"
            FROM videos v
            LEFT JOIN social_media_posts smp_linkedin ON v.video_id = smp_linkedin.video_id AND smp_linkedin.platform = 'linkedin'
            LEFT JOIN social_media_posts smp_facebook ON v.video_id = smp_facebook.video_id AND smp_facebook.platform = 'facebook'
            LEFT JOIN social_media_posts smp_instagram ON v.video_id = smp_instagram.video_id AND smp_instagram.platform = 'instagram'
            ORDER BY v.created_at DESC
        '''
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df


def log_automation_run(run_type: str, status: str, message: str = "",
                      videos_processed: int = 0, posts_created: int = 0,
                      errors: Optional[str] = None):
    """Log automation run."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO automation_logs (
            run_type, status, message, videos_processed, posts_created, errors
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (run_type, status, message, videos_processed, posts_created, errors))
    
    conn.commit()
    conn.close()


def get_recent_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent automation logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM automation_logs 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def export_to_excel(output_path: str, playlist_id: Optional[str] = None):
    """Export videos to Excel file (for compatibility)."""
    df = get_videos_for_export(playlist_id)
    
    if playlist_id:
        # Single playlist - one sheet
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Videos', index=False)
    else:
        # Multiple playlists - one sheet per playlist
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT playlist_id, playlist_name FROM videos ORDER BY playlist_name')
        playlists = cursor.fetchall()
        conn.close()
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for pl_id, pl_name in playlists:
                df_playlist = get_videos_for_export(pl_id)
                sheet_name = pl_name[:31] if pl_name else f"Playlist_{pl_id[:8]}"
                df_playlist.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Exported to {output_path}")


# Initialize database on import
if __name__ == '__main__':
    init_database()
else:
    # Auto-initialize if database doesn't exist
    if not Path(DB_PATH).exists():
        init_database()

