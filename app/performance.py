"""
Performance optimizations for the Flask app.
Includes caching, compression, and database optimizations.
"""

from functools import wraps
import time
import hashlib
import json
from typing import Any, Callable
from flask import g, request, Response
import gzip


# Simple in-memory cache (can be upgraded to Redis later)
_cache = {}
_cache_ttl = {}


def cached(timeout=300):
    """
    Cache decorator for expensive function calls.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in _cache:
                cache_time, cached_value = _cache[cache_key]
                if time.time() - cache_time < timeout:
                    return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = (time.time(), result)
            
            # Clean old cache entries periodically
            if len(_cache) > 1000:
                cleanup_cache()
            
            return result
        return wrapper
    return decorator


def cleanup_cache():
    """Remove expired cache entries."""
    current_time = time.time()
    expired_keys = [
        key for key, (cache_time, _) in _cache.items()
        if current_time - cache_time > 300  # Remove entries older than 5 minutes
    ]
    for key in expired_keys:
        _cache.pop(key, None)


def clear_cache(pattern: str = None):
    """Clear cache entries matching pattern."""
    if pattern is None:
        _cache.clear()
    else:
        keys_to_remove = [key for key in _cache.keys() if pattern in key]
        for key in keys_to_remove:
            _cache.pop(key, None)


def compress_response(response: Response) -> Response:
    """
    Compress response if client supports it.
    """
    if 'gzip' not in request.headers.get('Accept-Encoding', ''):
        return response
    
    if response.status_code < 200 or response.status_code >= 300:
        return response
    
    if response.content_length and response.content_length < 500:
        return response
    
    # Skip compression for passthrough responses (file downloads, streaming, etc.)
    try:
        # Check if response is in direct passthrough mode
        if hasattr(response, 'direct_passthrough') and response.direct_passthrough:
            return response
        
        # Try to get data - will raise RuntimeError if in passthrough mode
        data = response.get_data()
        
        # Compress response
        response.data = gzip.compress(data)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(response.data)
    except (RuntimeError, AttributeError):
        # If we can't compress (passthrough mode), just return as-is
        return response
    
    return response


def optimize_response_headers(response: Response) -> Response:
    """
    Add performance optimization headers.
    """
    # Cache control for static assets
    if request.endpoint and 'static' in request.path:
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
        response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT'
    else:
        # Short cache for dynamic content
        response.headers['Cache-Control'] = 'private, max-age=60'
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Performance headers
    response.headers['X-DNS-Prefetch-Control'] = 'on'
    
    return response

