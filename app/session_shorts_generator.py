"""
Intelligent session-to-shorts script generator.
Analyzes coaching sessions to create thought-provoking, clickbait-style shorts scripts.
"""

import re
from typing import Dict, List, Optional, Tuple
from app.tagging import derive_type_enhanced, derive_role_enhanced


def analyze_session(session_content: str) -> Dict[str, any]:
    """
    Deeply analyze a coaching session to extract:
    - Candidate's pressing issue/problem
    - What they wanted to achieve
    - Their mistakes/challenges
    - Unique solutions/teachings
    - Role and type (interview type)
    - Key insights that can be used for marketing
    """
    analysis = {
        'pressing_issue': '',
        'goal': '',
        'mistakes': [],
        'solutions': [],
        'unique_teachings': [],
        'key_insights': [],
        'role': '',
        'type': '',
        'tech_stack': [],
        'context': ''
    }
    
    content_lower = session_content.lower()
    lines = session_content.split('\n')
    
    # Extract role and type from filename/content
    analysis['role'] = extract_role_from_content(session_content)
    analysis['type'] = extract_type_from_content(session_content)
    analysis['tech_stack'] = extract_tech_stack(session_content)
    
    # Extract pressing issue (look for patterns like "struggling with", "having trouble", "need help", "problem")
    issue_patterns = [
        r'(?:struggling|struggle|having trouble|trouble with|problem with|issue with|challenge|difficulty|failing|failed|rejected|couldn\'t|can\'t|cannot) (?:with|to|in|at)?\s*([^.?!]+[.?!])',
        r'(?:need help|need assistance|help with|looking for help|want to|trying to|attempting to)\s+([^.?!]+[.?!])',
        r'(?:concern|worry|anxious|nervous|stressed) (?:about|with|that)\s+([^.?!]+[.?!])'
    ]
    
    for pattern in issue_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        if matches:
            analysis['pressing_issue'] = matches[0].strip()
            break
    
    # Extract goal/objective
    goal_patterns = [
        r'(?:goal|objective|want to|trying to|aiming to|planning to|hoping to|target)\s+([^.?!]+[.?!])',
        r'(?:preparing for|preparing to|interview for|applying for|applying to)\s+([^.?!]+[.?!])'
    ]
    
    for pattern in goal_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        if matches:
            analysis['goal'] = matches[0].strip()
            break
    
    # Extract mistakes (look for patterns indicating errors, wrong approaches, misconceptions)
    mistake_patterns = [
        r'(?:mistake|error|wrong|incorrect|misconception|didn\'t understand|didn\'t realize|shouldn\'t have|should have)\s+([^.?!]+[.?!])',
        r'(?:was doing|were doing|was saying|were saying)\s+([^.?!]+[.?!])\s+(?:but|however|instead)',
        r'(?:don\'t do|avoid|stop|never)\s+([^.?!]+[.?!])'
    ]
    
    for pattern in mistake_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        analysis['mistakes'].extend([m.strip() for m in matches[:3]])  # Top 3 mistakes
    
    # Extract solutions and unique teachings
    solution_patterns = [
        r'(?:solution|fix|approach|strategy|framework|method|technique|way to|how to)\s+([^.?!]+[.?!])',
        r'(?:taught|showed|explained|helped|guided)\s+([^.?!]+[.?!])',
        r'(?:instead|better|correct|right way|proper)\s+([^.?!]+[.?!])',
        r'(?:key|important|critical|essential|crucial)\s+(?:point|insight|takeaway|learning|lesson)\s+([^.?!]+[.?!])'
    ]
    
    for pattern in solution_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        analysis['solutions'].extend([m.strip() for m in matches[:5]])  # Top 5 solutions
    
    # Extract unique teachings (frameworks, strategies, unique insights)
    unique_patterns = [
        r'(?:framework|strategy|approach|method|technique|principle|concept)\s+(?:that|which|to)\s+([^.?!]+[.?!])',
        r'(?:unique|different|better|proven|effective|powerful)\s+([^.?!]+[.?!])',
        r'(?:insight|perspective|angle|viewpoint)\s+([^.?!]+[.?!])'
    ]
    
    for pattern in unique_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        analysis['unique_teachings'].extend([m.strip() for m in matches[:3]])
    
    # Extract key insights for marketing
    insight_keywords = ['breakthrough', 'ah-ha moment', 'realized', 'understood', 'learned', 'discovered']
    for keyword in insight_keywords:
        pattern = rf'{keyword}\s+([^.?!]+[.?!])'
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        analysis['key_insights'].extend([m.strip() for m in matches[:3]])
    
    # Extract context (interview type, company, role level)
    if 'amazon' in content_lower or 'aws' in content_lower:
        analysis['context'] += 'Amazon/AWS '
    if 'google' in content_lower or 'meta' in content_lower or 'facebook' in content_lower:
        analysis['context'] += 'FAANG '
    if 'system design' in content_lower or 'sys design' in content_lower:
        analysis['context'] += 'System Design '
    if 'behavioral' in content_lower or 'behavior' in content_lower:
        analysis['context'] += 'Behavioral Interview '
    if 'leadership' in content_lower:
        analysis['context'] += 'Leadership '
    if 'resume' in content_lower or 'cv' in content_lower:
        analysis['context'] += 'Resume Review '
    if 'salary' in content_lower or 'negotiation' in content_lower:
        analysis['context'] += 'Salary Negotiation '
    
    return analysis


def extract_role_from_content(content: str) -> str:
    """Extract role from session content using tagging system."""
    # Use tagging system
    role = derive_role_enhanced('', '', content, '')
    
    # Fallback: look for role keywords
    if not role:
        role_patterns = {
            'sa': r'\b(solutions? architect|sa|architect)\b',
            'swe': r'\b(software engineer|swe|sde)\b',
            'pm': r'\b(product manager|pm)\b',
            'tpm': r'\b(technical program manager|tpm|program manager)\b',
            'csm': r'\b(customer solutions? manager|csm)\b',
            'em': r'\b(engineering manager|em)\b',
            'mgr': r'\b(manager|mgr)\b',
            'dir': r'\b(director|dir)\b',
            'vp': r'\b(vp|vice president)\b',
            'data_engineer': r'\b(data engineer|de)\b',
            'sre': r'\b(site reliability|sre)\b'
        }
        
        content_lower = content.lower()
        for role_key, pattern in role_patterns.items():
            if re.search(pattern, content_lower):
                return role_key
    
    return role or ''


def extract_type_from_content(content: str) -> str:
    """Extract interview/coaching type from session content."""
    type_val = derive_type_enhanced('', '', content, '')
    
    if not type_val:
        type_patterns = {
            'sys_design': r'\b(system design|sys design|architecture interview)\b',
            'behavioral': r'\b(behavioral|behavior|leadership principles)\b',
            'resume_review': r'\b(resume|cv|resume review)\b',
            'salary_negotiation': r'\b(salary|negotiation|compensation)\b',
            'leadership': r'\b(leadership|management|team leadership)\b',
            'career_coaching': r'\b(career|roadmap|growth)\b',
            'data_engineering': r'\b(data engineering|data pipeline|etl)\b'
        }
        
        content_lower = content.lower()
        for type_key, pattern in type_patterns.items():
            if re.search(pattern, content_lower):
                return type_key
    
    return type_val or 'interview'


def extract_tech_stack(content: str) -> List[str]:
    """Extract tech stack mentions from content."""
    tech_keywords = [
        'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'kafka', 'spark',
        'python', 'java', 'javascript', 'react', 'node', 'microservices',
        'database', 'sql', 'nosql', 'dynamodb', 's3', 'lambda', 'api'
    ]
    
    found_tech = []
    content_lower = content.lower()
    for tech in tech_keywords:
        if tech in content_lower:
            found_tech.append(tech)
    
    return found_tech


def generate_shorts_scripts(analysis: Dict, booking_url: str, whatsapp_number: str, count: int = 5) -> List[Dict]:
    """
    Generate thought-provoking, clickbait-style shorts scripts (40 seconds each).
    Each script is tagged with role, type, and suggested playlist.
    """
    scripts = []
    
    # Script templates with clickbait hooks
    templates = []
    
    # Template 1: Problem-Solution (Most Effective)
    if analysis['pressing_issue'] and analysis['solutions']:
        for solution in analysis['solutions'][:2]:
            hook = generate_problem_hook(analysis['pressing_issue'], analysis['role'], analysis['type'])
            script = create_40_second_script(
                hook=hook,
                problem=analysis['pressing_issue'],
                solution=solution,
                unique_teaching=analysis['unique_teachings'][0] if analysis['unique_teachings'] else solution,
                cta_booking=booking_url,
                cta_whatsapp=whatsapp_number,
                role=analysis['role'],
                type_val=analysis['type']
            )
            if script:
                scripts.append(script)
    
    # Template 2: Mistake-Lesson (Fear-based clickbait)
    if analysis['mistakes']:
        for mistake in analysis['mistakes'][:2]:
            hook = generate_mistake_hook(mistake, analysis['role'], analysis['type'], analysis['context'])
            solution = analysis['solutions'][0] if analysis['solutions'] else "the right approach"
            script = create_40_second_script(
                hook=hook,
                problem=f"This mistake cost them their {analysis['context']}interview",
                solution=solution,
                unique_teaching=analysis['unique_teachings'][0] if analysis['unique_teachings'] else solution,
                cta_booking=booking_url,
                cta_whatsapp=whatsapp_number,
                role=analysis['role'],
                type_val=analysis['type']
            )
            if script:
                scripts.append(script)
    
    # Template 3: Insight-Revelation (Thought-provoking)
    if analysis['key_insights']:
        for insight in analysis['key_insights'][:2]:
            hook = generate_insight_hook(insight, analysis['role'], analysis['type'])
            script = create_40_second_script(
                hook=hook,
                problem="Most candidates don't realize this",
                solution=insight,
                unique_teaching=analysis['unique_teachings'][0] if analysis['unique_teachings'] else insight,
                cta_booking=booking_url,
                cta_whatsapp=whatsapp_number,
                role=analysis['role'],
                type_val=analysis['type']
            )
            if script:
                scripts.append(script)
    
    # Template 4: Unique Framework/Method (Authority-based)
    if analysis['unique_teachings']:
        for teaching in analysis['unique_teachings'][:2]:
            hook = generate_framework_hook(teaching, analysis['role'], analysis['type'])
            script = create_40_second_script(
                hook=hook,
                problem=f"The framework that works for {analysis['role']} interviews",
                solution=teaching,
                unique_teaching=teaching,
                cta_booking=booking_url,
                cta_whatsapp=whatsapp_number,
                role=analysis['role'],
                type_val=analysis['type']
            )
            if script:
                scripts.append(script)
    
    # Limit to requested count and add metadata
    for i, script_text in enumerate(scripts[:count]):
        if isinstance(script_text, dict):
            scripts[i] = script_text
        else:
            scripts[i] = {
                'script': script_text,
                'role': analysis['role'],
                'type': analysis['type'],
                'playlist_suggestion': suggest_playlist(analysis['role'], analysis['type'])
            }
    
    return scripts


def generate_problem_hook(issue: str, role: str, type_val: str) -> str:
    """Generate clickbait hook focusing on the pressing problem."""
    hooks = [
        f"❌ This {role} candidate was {issue[:50]}...",
        f"🚨 STOP making this {type_val} mistake: {issue[:40]}",
        f"💔 This candidate failed because {issue[:45]}...",
        f"⚠️ Don't let this {type_val} problem kill your interview",
        f"🔥 The #1 mistake {role} candidates make: {issue[:40]}"
    ]
    return hooks[0]  # Can randomize later


def generate_mistake_hook(mistake: str, role: str, type_val: str, context: str) -> str:
    """Generate fear-based hook about mistakes."""
    hooks = [
        f"🚫 This {type_val} mistake cost someone their {context}offer...",
        f"❌ Don't make this {role} mistake I see in 90% of interviews",
        f"⚠️ This {type_val} error will get you rejected instantly",
        f"💔 Stop doing this in {type_val} interviews: {mistake[:40]}",
        f"🔥 The fatal {type_val} mistake that ruins interviews"
    ]
    return hooks[0]


def generate_insight_hook(insight: str, role: str, type_val: str) -> str:
    """Generate thought-provoking hook about insights."""
    hooks = [
        f"💡 The {type_val} insight that changed everything",
        f"🧠 Most {role} candidates don't know: {insight[:35]}",
        f"✨ This {type_val} revelation will blow your mind",
        f"🎯 The secret {type_val} strategy nobody talks about",
        f"🔑 Unlock {type_val} success with this insight"
    ]
    return hooks[0]


def generate_framework_hook(teaching: str, role: str, type_val: str) -> str:
    """Generate authority-based hook about frameworks/methods."""
    hooks = [
        f"🎯 The {type_val} framework that gets offers",
        f"📐 My proven {role} {type_val} method: {teaching[:35]}",
        f"🏆 The {type_val} strategy that works 100% of the time",
        f"⚡ Master {type_val} with this unique framework",
        f"🎓 How I teach {role} candidates to ace {type_val}"
    ]
    return hooks[0]


def create_40_second_script(hook: str, problem: str, solution: str, unique_teaching: str,
                           cta_booking: str, cta_whatsapp: str, role: str, type_val: str) -> Dict:
    """
    Create a 40-second shorts script (approximately 100-120 words at normal speaking pace).
    Structure: Hook (3s) → Problem (10s) → Solution (20s) → CTA (7s)
    """
    # Clean and format text
    problem_clean = problem[:80] + "..." if len(problem) > 80 else problem
    solution_clean = solution[:150] + "..." if len(solution) > 150 else solution
    teaching_clean = unique_teaching[:100] + "..." if len(unique_teaching) > 100 else unique_teaching
    
    # Build script (aim for ~110 words = 40 seconds)
    script_parts = [
        hook,  # ~15 words (3 seconds)
        "",
        f"Here's what happened: {problem_clean}",  # ~20 words (5 seconds)
        "",
        f"The solution? {solution_clean}",  # ~30 words (10 seconds)
        "",
        f"Here's my unique approach: {teaching_clean}",  # ~25 words (8 seconds)
        "",
        f"Want 1-on-1 coaching? Book: {cta_booking}",  # ~10 words (2 seconds)
        f"Or WhatsApp: {cta_whatsapp}",  # ~5 words (1 second)
    ]
    
    script_text = "\n".join(script_parts)
    
    # Estimate word count
    word_count = len(script_text.split())
    
    # Adjust if too long/short (target: 100-120 words)
    if word_count > 130:
        # Shorten
        script_text = "\n".join(script_parts[:8])  # Remove some parts
    elif word_count < 90:
        # Add more detail
        script_text += f"\n\nThis framework works because it addresses the core {type_val} challenge."
    
    return {
        'script': script_text.strip(),
        'role': role,
        'type': type_val,
        'playlist_suggestion': suggest_playlist(role, type_val),
        'word_count': len(script_text.split()),
        'estimated_duration': '40 seconds'
    }


def suggest_playlist(role: str, type_val: str) -> str:
    """
    Intelligently suggest which YouTube playlist this short should go to.
    Based on role and type, match to existing playlists.
    """
    # Map of (role, type) to playlist suggestions
    playlist_map = {
        # System Design
        ('sa', 'sys_design'): 'System Design for Solutions Architects',
        ('sa', 'system_design'): 'System Design for Solutions Architects',
        ('swe', 'sys_design'): 'System Design Interview Prep',
        ('em', 'sys_design'): 'System Design for Engineering Managers',
        
        # Behavioral/Leadership
        ('em', 'behavioral'): 'Behavioral Interview for Managers',
        ('mgr', 'behavioral'): 'Behavioral Interview for Managers',
        ('dir', 'behavioral'): 'Leadership Interview Prep',
        ('vp', 'behavioral'): 'Executive Interview Prep',
        ('em', 'leadership'): 'Leadership Coaching',
        ('mgr', 'leadership'): 'Leadership Coaching',
        
        # Resume
        (None, 'resume_review'): 'Resume Review & Career Coaching',
        (None, 'resume'): 'Resume Review & Career Coaching',
        
        # Salary
        (None, 'salary_negotiation'): 'Salary Negotiation',
        
        # Data Engineering
        ('data_engineer', 'data_engineering'): 'Data Engineering Interviews',
        ('de', 'data_engineering'): 'Data Engineering Interviews',
        
        # Career
        (None, 'career_coaching'): 'Career Coaching',
        
        # Product Management
        ('pm', 'product'): 'Product Manager Interviews',
        ('tpm', 'product'): 'Technical Program Manager Interviews',
    }
    
    # Try exact match
    suggestion = playlist_map.get((role, type_val))
    if suggestion:
        return suggestion
    
    # Try role-only match
    for (r, t), playlist in playlist_map.items():
        if r == role and not t:
            return playlist
    
    # Try type-only match
    for (r, t), playlist in playlist_map.items():
        if t == type_val and not r:
            return playlist
    
    # Default based on type
    type_defaults = {
        'sys_design': 'System Design Interview Prep',
        'behavioral': 'Behavioral Interview Prep',
        'leadership': 'Leadership Coaching',
        'resume': 'Resume Review & Career Coaching',
        'salary_negotiation': 'Salary Negotiation',
        'career_coaching': 'Career Coaching'
    }
    
    return type_defaults.get(type_val, 'Interview Coaching')


def generate_shorts_from_session_enhanced(session_content: str, booking_url: str, whatsapp_number: str) -> List[Dict]:
    """
    Main function: Generate intelligent shorts scripts from session content.
    """
    # Step 1: Deep analysis
    analysis = analyze_session(session_content)
    
    # Step 2: Generate scripts
    scripts = generate_shorts_scripts(analysis, booking_url, whatsapp_number, count=5)
    
    return scripts

