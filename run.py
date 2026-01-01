#!/usr/bin/env python3
"""
Entry point for running the Flask application.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == '__main__':
    # SSL configuration (for development with self-signed cert)
    ssl_context = None
    cert_file = os.getenv('SSL_CERT_FILE', 'cert.pem')
    key_file = os.getenv('SSL_KEY_FILE', 'key.pem')
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)
        print(f"✅ SSL enabled: Using {cert_file} and {key_file}")
    else:
        print("ℹ️  SSL not configured. Run in production with nginx/Cloudflare for HTTPS.")
    
    # Performance optimizations
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year for static files
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
    
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        ssl_context=ssl_context,
        threaded=True  # Enable threading for better performance
    )


