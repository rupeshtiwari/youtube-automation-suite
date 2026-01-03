@app.route('/api/status')
def api_status():
    """Get complete application status - what's configured, what's missing."""
    try:
        settings = load_settings()
        api_keys = settings.get('api_keys', {})
        
        status = {
            'youtube': {
                'configured': os.path.exists('client_secret.json'),
                'authenticated': os.path.exists('token.json'),
                'redirect_uri': f'http://youtube-automation.local/oauth2callback',
                'status': 'ready' if os.path.exists('client_secret.json') and os.path.exists('token.json') else 'needs_setup'
            },
            'linkedin': {
                'configured': bool(api_keys.get('linkedin_client_id') and api_keys.get('linkedin_client_secret')),
                'authenticated': bool(api_keys.get('linkedin_access_token')),
                'redirect_uri': f'http://youtube-automation.local:5001/api/linkedin/oauth/callback',
                'status': 'ready' if api_keys.get('linkedin_access_token') else ('configured' if api_keys.get('linkedin_client_id') else 'needs_setup')
            },
            'facebook': {
                'configured': bool(api_keys.get('facebook_page_access_token') and api_keys.get('facebook_page_id')),
                'authenticated': bool(api_keys.get('facebook_page_access_token')),
                'redirect_uri': f'http://youtube-automation.local:5001/api/facebook/oauth/callback',
                'status': 'ready' if api_keys.get('facebook_page_access_token') else 'needs_setup'
            },
            'instagram': {
                'configured': bool(api_keys.get('instagram_business_account_id')),
                'authenticated': bool(api_keys.get('facebook_page_access_token')),  # Uses Facebook token
                'redirect_uri': f'http://youtube-automation.local:5001/api/facebook/oauth/callback',
                'status': 'ready' if (api_keys.get('instagram_business_account_id') and api_keys.get('facebook_page_access_token')) else 'needs_setup'
            },
            'database': {
                'configured': True,
                'path': os.path.join(os.path.dirname(__file__), 'youtube_automation.db'),
                'status': 'ready'
            }
        }
        
        # Calculate overall status
        ready_count = sum(1 for s in status.values() if s.get('status') == 'ready')
        total_count = len([s for s in status.values() if s.get('status') != 'database'])
        status['overall'] = {
            'ready': ready_count,
            'total': total_count,
            'percentage': int((ready_count / total_count * 100)) if total_count > 0 else 0
        }
        
        return jsonify(status)
    except Exception as e:
        app.logger.error(f"Error getting status: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
