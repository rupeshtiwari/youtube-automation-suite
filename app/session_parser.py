"""
Session Parser - Reads and parses mentoring sessions from folder
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json


class SessionParser:
    """Parse mentoring session files and extract metadata"""
    
    ROLES = ['swe', 'pm', 'sa', 'tpm', 'em', 'mgr', 'dir', 'vp', 'spo', 'spm', 'engineer', 'manager', 'architect']
    TYPES = ['system-design', 'behavioral', 'coding', 'leadership', 'resume', 'salary', 'interview', 'mock']
    
    def __init__(self, sessions_path: str):
        self.sessions_path = sessions_path
        self.metadata_file = os.path.join(sessions_path, 'sessions.json')
    
    def parse_filename(self, filename: str) -> Dict:
        """Extract metadata from filename"""
        metadata = {
            'filename': filename,
            'date': None,
            'client_name': None,
            'role': None,
            'type': None,
            'status': 'unknown'
        }
        
        # Try YYYY-MM-DD format
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            metadata['date'] = date_match.group(1)
            try:
                session_date = datetime.strptime(metadata['date'], '%Y-%m-%d')
                today = datetime.now().date()
                metadata['status'] = 'upcoming' if session_date.date() >= today else 'completed'
            except:
                pass
        
        # Try to extract client name (text before date or after date)
        if metadata['date']:
            parts = filename.replace(metadata['date'], '').replace('_', ' ').split()
            # Remove extension and clean up
            parts = [p for p in parts if not p.endswith(('.txt', '.md', '.pdf'))]
            if parts:
                metadata['client_name'] = ' '.join(parts[:2])  # Take first 2 words as name
        
        # Extract role
        filename_lower = filename.lower()
        for role in self.ROLES:
            if role in filename_lower:
                metadata['role'] = role
                break
        
        # Extract type
        for session_type in self.TYPES:
            if session_type.replace('-', '') in filename_lower or session_type.replace('-', ' ') in filename_lower:
                metadata['type'] = session_type
                break
        
        return metadata
    
    def load_metadata_file(self) -> Optional[Dict]:
        """Load metadata from sessions.json if it exists"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def get_file_info(self, filepath: str) -> Dict:
        """Get file metadata (size, modified date, etc.)"""
        try:
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        except:
            return {}
    
    def scan_sessions(self) -> List[Dict]:
        """Scan sessions folder recursively and return list of sessions"""
        sessions = []
        
        if not os.path.exists(self.sessions_path):
            return sessions
        
        # Check for metadata file first
        metadata = self.load_metadata_file()
        
        # Scan all files recursively
        for root, dirs, files in os.walk(self.sessions_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in files:
                if filename.startswith('.') or filename == 'sessions.json':
                    continue
                
                item_path = os.path.join(root, filename)
                relative_path = os.path.relpath(item_path, self.sessions_path)
                
                # Only process text-based files (txt, md) and common document formats
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ['.txt', '.md', '.docx', '.pdf', '.pages']:
                    # Skip binary files like images, videos, etc. unless explicitly needed
                    if ext not in ['.png', '.jpg', '.jpeg', '.mp4', '.mp3']:
                        continue
                
                metadata_from_filename = self.parse_filename(filename)
                file_info = self.get_file_info(item_path)
                
                session = {
                    **metadata_from_filename,
                    **file_info,
                    'filepath': item_path,
                    'relative_path': relative_path,
                    'folder': os.path.basename(root) if root != self.sessions_path else ''
                }
                
                # Try to read first few lines for preview (only for text files)
                if ext in ['.txt', '.md']:
                    try:
                        with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                            preview = f.read(500)
                            session['preview'] = preview
                            session['has_content'] = len(preview.strip()) > 0
                    except:
                        session['preview'] = ''
                        session['has_content'] = False
                else:
                    session['preview'] = ''
                    session['has_content'] = False
                
                sessions.append(session)
        
        # Sort by date (upcoming first, then by date descending)
        sessions.sort(key=lambda x: (
            x['date'] is None,  # None dates go last
            x['status'] != 'upcoming',  # Upcoming first
            x['date'] or '0000-00-00'
        ), reverse=False)
        
        return sessions
    
    def get_upcoming_sessions(self, limit: int = 10) -> List[Dict]:
        """Get upcoming sessions"""
        all_sessions = self.scan_sessions()
        upcoming = [s for s in all_sessions if s.get('status') == 'upcoming']
        return sorted(upcoming, key=lambda x: x.get('date', ''))[:limit]
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recently completed sessions"""
        all_sessions = self.scan_sessions()
        completed = [s for s in all_sessions if s.get('status') == 'completed']
        return sorted(completed, key=lambda x: x.get('date', ''), reverse=True)[:limit]
    
    def get_statistics(self) -> Dict:
        """Get session statistics"""
        all_sessions = self.scan_sessions()
        
        return {
            'total': len(all_sessions),
            'upcoming': len([s for s in all_sessions if s.get('status') == 'upcoming']),
            'completed': len([s for s in all_sessions if s.get('status') == 'completed']),
            'by_role': self._count_by_field(all_sessions, 'role'),
            'by_type': self._count_by_field(all_sessions, 'type'),
        }
    
    def _count_by_field(self, sessions: List[Dict], field: str) -> Dict[str, int]:
        """Count sessions by a field"""
        counts = {}
        for session in sessions:
            value = session.get(field)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts

