"""
Validation utilities for the YouTube Automation app.
Provides input validation, sanitization, and error handling.
"""

import re
from typing import Optional, Dict, List, Any
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url or not isinstance(url, str):
        return False
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone or not isinstance(phone, str):
        return False
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and invalid characters."""
    if not filename or not isinstance(filename, str):
        return ""
    # Remove directory traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    # Remove invalid characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    # Limit length
    return filename[:255]


def validate_playlist_id(playlist_id: str) -> bool:
    """Validate YouTube playlist ID format."""
    if not playlist_id or not isinstance(playlist_id, str):
        return False
    # YouTube playlist IDs are typically 34 characters and start with PL
    return len(playlist_id) >= 10 and len(playlist_id) <= 50 and re.match(r'^[a-zA-Z0-9_-]+$', playlist_id)


def validate_video_id(video_id: str) -> bool:
    """Validate YouTube video ID format."""
    if not video_id or not isinstance(video_id, str):
        return False
    # YouTube video IDs are 11 characters
    return len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_id)


def validate_date_format(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
    """Validate date string format."""
    if not date_str or not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, format_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_datetime_format(datetime_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> bool:
    """Validate datetime string format."""
    if not datetime_str or not isinstance(datetime_str, str):
        return False
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_time_format(time_str: str) -> bool:
    """Validate time format (HH:MM or HH:MM:SS)."""
    if not time_str or not isinstance(time_str, str):
        return False
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'
    return bool(re.match(pattern, time_str))


def validate_json(data: Any) -> bool:
    """Validate if data is valid JSON."""
    try:
        if isinstance(data, str):
            import json
            json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, Optional[str]]:
    """Validate that all required fields are present and not empty."""
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def validate_platform(platform: str) -> bool:
    """Validate social media platform name."""
    valid_platforms = ['linkedin', 'facebook', 'instagram', 'youtube', 'twitter']
    return platform.lower() in valid_platforms if platform else False


def validate_post_status(status: str) -> bool:
    """Validate post status."""
    valid_statuses = ['draft', 'scheduled', 'published', 'failed', 'cancelled']
    return status.lower() in valid_statuses if status else False


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize user input text."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length:
        text = text[:max_length]
    
    return text


def validate_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """Validate integer value."""
    try:
        int_val = int(value)
        if min_val is not None and int_val < min_val:
            return False, f"Value must be at least {min_val}"
        if max_val is not None and int_val > max_val:
            return False, f"Value must be at most {max_val}"
        return True, None
    except (ValueError, TypeError):
        return False, "Value must be a valid integer"


def validate_string_length(text: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """Validate string length."""
    if not isinstance(text, str):
        return False, "Value must be a string"
    
    length = len(text)
    if min_length is not None and length < min_length:
        return False, f"Text must be at least {min_length} characters"
    if max_length is not None and length > max_length:
        return False, f"Text must be at most {max_length} characters"
    
    return True, None


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    if not filename or not isinstance(filename, str):
        return False
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in [ext.lower() for ext in allowed_extensions]


def validate_role(role: str) -> bool:
    """Validate session role."""
    valid_roles = [
        'Engineering Manager', 'Product Manager', 'Solutions Architect',
        'Data Engineer', 'Software Engineer', 'Staff Software Engineer',
        'Technical Program Manager', 'Site Reliability Engineer', 'Other'
    ]
    return role in valid_roles if role else False


def validate_session_type(session_type: str) -> bool:
    """Validate session type."""
    valid_types = [
        'System Design', 'Behavioral', 'Leadership', 'Career Coaching',
        'Resume Review', 'Salary Negotiation', 'Coding', 'Other'
    ]
    return session_type in valid_types if session_type else False

