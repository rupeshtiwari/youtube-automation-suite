"""
Tagging and categorization utilities for videos and playlists.
"""

import re
from typing import Dict, List, Optional, Any


# Role definitions
ROLES = {
    'spo': 'Senior Product Owner',
    'spm': 'Senior Product Manager',
    'vp': 'Vice President',
    'dir': 'Director',
    'mgr': 'Manager',
    'sa': 'Senior Architect',
    'swe': 'Software Engineer',
    'em': 'Engineering Manager',
    'pm': 'Product Manager',
    'po': 'Product Owner',
    'tech_lead': 'Tech Lead',
    'staff': 'Staff Engineer',
    'principal': 'Principal Engineer'
}

# Type definitions
TYPES = {
    'sys_design': 'System Design',
    'leadership': 'Leadership',
    'interview': 'Interview Prep',
    'career': 'Career Growth',
    'technical': 'Technical',
    'management': 'Management',
    'product': 'Product Management',
    'architecture': 'Architecture'
}

# Common tags
COMMON_TAGS = [
    'mock-interview', 'system-design', 'leadership', 'career-advice',
    'interview-prep', 'product-management', 'engineering', 'architecture',
    'scalability', 'distributed-systems', 'microservices', 'api-design',
    'team-management', 'strategy', 'executive', 'senior-level'
]


def derive_role_enhanced(playlist_title: str, video_title: str, video_description: str, video_tags: str) -> str:
    """
    Enhanced role derivation supporting more roles: SPO, SPM, VP, DIR, MGR, SA, SWE, EM, etc.
    """
    text = f"{playlist_title} {video_title} {video_description} {video_tags}".lower()
    
    # Check for role keywords (order matters - more specific first)
    role_patterns = {
        'vp': r'\b(vp|vice president|vice-president|executive)\b',
        'spo': r'\b(senior product owner|spo|senior po)\b',
        'spm': r'\b(senior product manager|spm|senior pm)\b',
        'dir': r'\b(director|dir)\b',
        'em': r'\b(engineering manager|em|eng manager)\b',
        'mgr': r'\b(manager|mgr|management)\b',
        'sa': r'\b(senior architect|sa|architect)\b',
        'staff': r'\b(staff engineer|staff)\b',
        'principal': r'\b(principal engineer|principal)\b',
        'tech_lead': r'\b(tech lead|technical lead)\b',
        'swe': r'\b(software engineer|swe|engineer)\b',
        'pm': r'\b(product manager|pm)\b',
        'po': r'\b(product owner|po)\b'
    }
    
    for role, pattern in role_patterns.items():
        if re.search(pattern, text):
            return role
    
    return ""


def derive_type_enhanced(playlist_title: str, video_title: str, video_description: str, video_tags: str) -> str:
    """
    Enhanced type derivation supporting more types.
    """
    text = f"{playlist_title} {video_title} {video_description} {video_tags}".lower()
    
    type_patterns = {
        'sys_design': [
            'system design', 'sys design', 'system architecture', 'architecture',
            'design pattern', 'scalability', 'distributed system', 'microservices',
            'database design', 'api design', 'infrastructure', 'system scaling'
        ],
        'leadership': [
            'leadership', 'management', 'team', 'people', 'career',
            'mentor', 'coaching', 'strategy', 'executive', 'decision'
        ],
        'interview': [
            'interview', 'mock interview', 'interview prep', 'interview question',
            'interview tips', 'interview guide', 'interview practice'
        ],
        'career': [
            'career', 'career growth', 'career advice', 'career development',
            'promotion', 'salary', 'negotiation'
        ],
        'technical': [
            'coding', 'programming', 'algorithm', 'data structure', 'technical',
            'implementation', 'code review', 'best practices'
        ],
        'product': [
            'product management', 'product strategy', 'product roadmap',
            'feature', 'product launch', 'product metrics'
        ]
    }
    
    type_scores = {}
    for type_key, keywords in type_patterns.items():
        score = sum(text.count(kw) for kw in keywords)
        if score > 0:
            type_scores[type_key] = score
    
    if type_scores:
        return max(type_scores, key=type_scores.get)
    
    return ""


def suggest_tags(video_title: str, video_description: str, video_type: str, role: str) -> List[str]:
    """
    Suggest tags based on video content, type, and role.
    """
    tags = []
    text = f"{video_title} {video_description}".lower()
    
    # Add type-based tags
    if video_type:
        type_tag_map = {
            'sys_design': ['system-design', 'architecture', 'scalability'],
            'leadership': ['leadership', 'management', 'career-advice'],
            'interview': ['interview-prep', 'mock-interview'],
            'career': ['career-advice', 'career-growth'],
            'technical': ['technical', 'engineering'],
            'product': ['product-management']
        }
        tags.extend(type_tag_map.get(video_type, []))
    
    # Add role-based tags
    if role:
        role_tag_map = {
            'spo': ['product-management', 'senior-level'],
            'spm': ['product-management', 'senior-level'],
            'vp': ['executive', 'senior-level'],
            'dir': ['management', 'senior-level'],
            'em': ['engineering', 'management'],
            'sa': ['architecture', 'senior-level'],
            'swe': ['engineering', 'technical']
        }
        tags.extend(role_tag_map.get(role, []))
    
    # Add content-based tags
    if 'mock' in text or 'interview' in text:
        tags.append('mock-interview')
    if 'system' in text or 'architecture' in text:
        tags.append('system-design')
    if 'leadership' in text or 'management' in text:
        tags.append('leadership')
    
    # Remove duplicates and return
    return list(set(tags))


def parse_tags(tags_string: str) -> List[str]:
    """Parse comma-separated tags string into list."""
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]


def format_tags(tags_list: List[str]) -> str:
    """Format tags list into comma-separated string."""
    return ', '.join(tags_list)


def search_videos(query: str, video_type: Optional[str] = None, role: Optional[str] = None, 
                  tags: Optional[List[str]] = None) -> str:
    """
    Generate SQL WHERE clause for searching videos.
    """
    conditions = []
    
    if query:
        conditions.append("""
            (title LIKE ? OR description LIKE ? OR tags LIKE ? OR custom_tags LIKE ?)
        """)
    
    if video_type:
        conditions.append("video_type = ?")
    
    if role:
        conditions.append("role = ?")
    
    if tags:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("(custom_tags LIKE ? OR tags LIKE ?)")
        conditions.append(f"({' OR '.join(tag_conditions)})")
    
    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return ""


def get_all_tags() -> Dict[str, List[str]]:
    """Get all available tags organized by category."""
    return {
        'roles': list(ROLES.keys()),
        'types': list(TYPES.keys()),
        'common': COMMON_TAGS
    }

