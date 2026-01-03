"""
Google Analytics 4 (GA4) Integration
Fetches analytics data from Google Analytics using the Reporting API
"""
import os
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import json


def get_ga4_service(credentials_path=None):
    """Initialize Google Analytics 4 Reporting API service."""
    try:
        # Try to use OAuth credentials first (from token.json)
        token_file = credentials_path or "token.json"
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(
                token_file,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
            if creds and creds.valid:
                return build('analyticsreporting', 'v4', credentials=creds)
        
        # Try service account credentials
        service_account_file = os.getenv('GOOGLE_ANALYTICS_SERVICE_ACCOUNT_FILE')
        if service_account_file and os.path.exists(service_account_file):
            creds = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
            return build('analyticsreporting', 'v4', credentials=creds)
        
        return None
    except Exception as e:
        print(f"Error initializing GA4 service: {e}")
        return None


def get_ga4_data(property_id=None, view_id=None):
    """
    Get Google Analytics 4 data.
    
    Args:
        property_id: GA4 Property ID (format: properties/123456789)
        view_id: GA4 View ID (legacy, for GA4 use property_id)
    
    Returns:
        dict with analytics data or error message
    """
    try:
        # Get property ID from settings or environment
        if not property_id:
            from app.main import load_settings
            settings = load_settings()
            api_keys = settings.get('api_keys', {})
            property_id = api_keys.get('google_analytics_property_id') or os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
        
        if not property_id:
            return {'error': 'Google Analytics Property ID not configured. Add it in Settings.'}
        
        # Ensure property_id is in correct format
        if not property_id.startswith('properties/'):
            property_id = f'properties/{property_id}'
        
        service = get_ga4_service()
        if not service:
            return {'error': 'Google Analytics API not authenticated. Please configure OAuth credentials.'}
        
        # Get date range (last 30 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Get basic metrics
        request_body = {
            'reportRequests': [
                {
                    'viewId': view_id or property_id.split('/')[-1],  # Use property ID as fallback
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [
                        {'expression': 'ga:sessions'},
                        {'expression': 'ga:users'},
                        {'expression': 'ga:pageviews'},
                        {'expression': 'ga:bounceRate'},
                        {'expression': 'ga:avgSessionDuration'}
                    ],
                    'dimensions': [{'name': 'ga:date'}]
                }
            ]
        }
        
        # For GA4, we need to use the Data API instead
        # Let's use the GA4 Data API
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
        
        # Try GA4 Data API
        try:
            # For GA4, we need service account or OAuth with GA4 scopes
            # This is a simplified version - you'll need proper GA4 credentials
            return {
                'error': 'GA4 Data API requires specific setup. Using YouTube Analytics instead.',
                'note': 'Configure Google Analytics 4 Property ID in Settings for full GA4 integration.'
            }
        except Exception as e:
            return {'error': f'GA4 API error: {str(e)}'}
        
    except HttpError as e:
        error_content = e.content.decode('utf-8') if e.content else str(e)
        return {'error': f'Google Analytics API error: {error_content[:200]}'}
    except Exception as e:
        return {'error': f'Error getting Google Analytics data: {str(e)}'}


def get_website_analytics_summary():
    """Get a summary of website analytics if GA4 is configured."""
    try:
        from app.main import load_settings
        settings = load_settings()
        api_keys = settings.get('api_keys', {})
        property_id = api_keys.get('google_analytics_property_id')
        
        if not property_id:
            return None
        
        # Return placeholder - full implementation requires GA4 Data API setup
        return {
            'property_id': property_id,
            'note': 'GA4 integration requires additional setup. Configure in Settings.',
            'status': 'configured_but_not_fully_implemented'
        }
    except Exception as e:
        return {'error': str(e)}

