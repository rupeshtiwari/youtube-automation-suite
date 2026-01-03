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
# Database is stored in a persistent location that won't be deleted
DATA_DIR = os.getenv('DATA_DIR', os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, 'youtube_automation.db')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


# Connection pool for better performance (thread-safe)
_db_pool = {}
_max_pool_size = 10

def get_db_connection():
    """Get database connection with connection pooling and optimizations."""
    import threading
    thread_id = threading.current_thread().ident
    
    # Check if we have a connection for this thread
    if thread_id in _db_pool:
        try:
            # Test if connection is still valid
            _db_pool[thread_id].execute('SELECT 1').fetchone()
            return _db_pool[thread_id]
        except:
            # Connection is stale, remove it
            _db_pool.pop(thread_id, None)
    
    # Create new connection
    conn = sqlite3.connect(DB_PATH, timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for better concurrent performance
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    
    # Store in pool (limit pool size)
    if len(_db_pool) < _max_pool_size:
        _db_pool[thread_id] = conn
    
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
    
    # Activity logs table - tracks individual actions (detailed activity log)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            platform TEXT,
            video_id TEXT,
            video_title TEXT,
            playlist_id TEXT,
            playlist_name TEXT,
            status TEXT NOT NULL,
            message TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add indexes for activity logs
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_action_type ON activity_logs(action_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_platform ON activity_logs(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_created_at ON activity_logs(created_at)')
    
    # Settings table - stores application configuration (persistent across restarts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sessions metadata table - stores session files with linked resources
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            role TEXT,
            session_type TEXT,
            client_name TEXT,
            session_date TEXT,
            meet_recording_url TEXT,
            meet_recording_drive_id TEXT,
            gemini_transcript_url TEXT,
            gemini_transcript_drive_id TEXT,
            chatgpt_notes TEXT,
            email_thread_id TEXT,
            email_subject TEXT,
            additional_notes TEXT,
            tags TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Session content generation table - tracks AI-generated content from sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            platform TEXT,
            status TEXT DEFAULT 'draft',
            scheduled_date TEXT,
            published_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_filename) REFERENCES sessions_metadata(filename)
        )
    ''')
    
    # Add indexes for sessions
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_filename ON sessions_metadata(filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_role ON sessions_metadata(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions_metadata(session_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions_metadata(session_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_content_filename ON session_content(session_filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_content_type ON session_content(content_type)')
    
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
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(setting_key)')
    
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
            video_type, role, custom_tags, youtube_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
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
        video_data.get('custom_tags'),
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
                v.custom_tags as "Custom Tags",
                v.playlist_name as "Playlist Name",
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
                v.custom_tags as "Custom Tags",
                v.playlist_name as "Playlist Name",
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


def log_activity(action_type: str, platform: Optional[str] = None,
                video_id: Optional[str] = None, video_title: Optional[str] = None,
                playlist_id: Optional[str] = None, playlist_name: Optional[str] = None,
                status: str = 'success', message: str = '', details: Optional[str] = None):
    """Log individual activity/action."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert details to JSON string if it's a dict
    if details and isinstance(details, dict):
        details = json.dumps(details)
    
    cursor.execute('''
        INSERT INTO activity_logs (
            action_type, platform, video_id, video_title, playlist_id, 
            playlist_name, status, message, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (action_type, platform, video_id, video_title, playlist_id, 
          playlist_name, status, message, details))
    
    conn.commit()
    conn.close()


def get_activity_logs(limit: int = 100, platform: Optional[str] = None,
                     action_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get activity logs with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM activity_logs WHERE 1=1'
    params = []
    
    if platform:
        query += ' AND platform = ?'
        params.append(platform)
    
    if action_type:
        query += ' AND action_type = ?'
        params.append(action_type)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_scheduled_count_today(platform: str, date: Optional[str] = None) -> int:
    """Get count of posts scheduled today for a platform."""
    from datetime import datetime
    
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) as count FROM activity_logs
        WHERE platform = ? 
        AND action_type = 'schedule_post'
        AND status = 'success'
        AND DATE(created_at) = DATE(?)
    ''', (platform, date))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['count'] if result else 0


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


def save_settings_to_db(settings: Dict[str, Any]) -> None:
    """
    Save settings to database (persistent storage).
    This is the PRIMARY storage method - settings persist across restarts.
    CRITICAL: All API keys and credentials are saved here.
    """
    # Ensure database is initialized
    init_database()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Save entire settings as JSON in a single row
        settings_json = json.dumps(settings, indent=2)
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', ('app_settings', settings_json))
        
        conn.commit()
        
        # Verify the save worked
        cursor.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('app_settings',))
        result = cursor.fetchone()
        if not result:
            raise Exception("Failed to verify settings were saved to database")
        
        print(f"✅ Settings saved to database successfully (size: {len(settings_json)} bytes)")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Database save failed: {str(e)}")
    finally:
        conn.close()


def load_settings_from_db() -> Optional[Dict[str, Any]]:
    """
    Load settings from database (primary source).
    Returns None if no settings found or database error.
    CRITICAL: This loads all API keys and credentials from database.
    """
    try:
        # Ensure database exists
        if not Path(DB_PATH).exists():
            init_database()
            return None  # No settings yet
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT setting_value, updated_at FROM settings
            WHERE setting_key = 'app_settings'
            ORDER BY updated_at DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result['setting_value']:
            try:
                settings = json.loads(result['setting_value'])
                updated_at = result['updated_at'] if 'updated_at' in result.keys() else 'unknown'
                print(f"✅ Loaded settings from database (last updated: {updated_at})")
                return settings
            except json.JSONDecodeError as e:
                print(f"⚠️ Warning: Failed to parse settings from database: {e}")
                return None
        
        return None
    except Exception as e:
        print(f"⚠️ Warning: Failed to load settings from database: {e}")
        import traceback
        traceback.print_exc()
        return None


# Initialize database on import
if __name__ == '__main__':
    init_database()
else:
    # Auto-initialize if database doesn't exist
    if not Path(DB_PATH).exists():
        init_database()

