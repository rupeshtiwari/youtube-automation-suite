"""
Facebook automatic setup - OAuth flow to fetch all required tokens automatically.
No manual copy-paste needed - just login and we auto-fetch everything.
"""

from flask import (
    Blueprint,
    render_template_string,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
import requests
from urllib.parse import urlencode, quote
import os

facebook_auto_setup_bp = Blueprint("facebook_auto_setup", __name__)


def load_settings():
    """Load settings from database."""
    from app.database import load_settings_from_db

    return load_settings_from_db() or {}


def save_settings(settings):
    """Save settings to database."""
    from app.database import save_settings_to_db

    save_settings_to_db(settings)


FACEBOOK_AUTO_SETUP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Auto Setup - One Click Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #1877f2;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            color: #65676b;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .feature-list {
            background: #f0f2f5;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .feature {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 14px;
            color: #50596c;
        }
        .feature:last-child {
            margin-bottom: 0;
        }
        .feature svg {
            flex-shrink: 0;
            color: #31a24c;
            width: 20px;
            height: 20px;
        }
        .button-group {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: all 0.3s ease;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-primary {
            background: #1877f2;
            color: white;
        }
        .btn-primary:hover {
            background: #165ac6;
            box-shadow: 0 4px 12px rgba(24,119,242,0.4);
        }
        .btn-secondary {
            background: #e4e6eb;
            color: #050505;
        }
        .btn-secondary:hover {
            background: #d0d2d7;
        }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #1877f2;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
            color: #0a66c2;
            margin-top: 20px;
        }
        .error-box {
            background: #ffebee;
            border-left: 4px solid #d32f2f;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
            color: #c62828;
            margin-bottom: 20px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #65676b;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #1877f2;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 12px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #1877f2;
            text-decoration: none;
            font-size: 14px;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Facebook Auto Setup</h1>
        <p class="subtitle">One-click login to auto-fetch all required tokens</p>
        
        <div class="feature-list">
            <div class="feature">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Fetch Page Access Token automatically</span>
            </div>
            <div class="feature">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Get your Facebook Page ID</span>
            </div>
            <div class="feature">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Fetch Instagram Business Account ID</span>
            </div>
            <div class="feature">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Save everything automatically - no copy-paste needed!</span>
            </div>
        </div>
        
        <div class="button-group">
            <a href="/api/facebook/oauth/start-auto" class="btn btn-primary">
                <svg fill="currentColor" viewBox="0 0 24 24" width="20" height="20">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Login with Meta Account
            </a>
            <a href="/facebook-token-helper" class="btn btn-secondary">
                📋 Manual Setup (Copy-Paste Method)
            </a>
        </div>
        
        <div class="info-box">
            ℹ️ <strong>Privacy Note:</strong> We only request access to your Page and Instagram Business accounts. We will never post without your permission.
        </div>
        
        <div class="back-link">
            <a href="/settings">← Back to Settings</a>
        </div>
    </div>
</body>
</html>
"""


@facebook_auto_setup_bp.route("/facebook-auto-setup")
def facebook_auto_setup():
    """Show Facebook auto-setup page with login button."""
    return render_template_string(FACEBOOK_AUTO_SETUP_HTML)


@facebook_auto_setup_bp.route("/api/facebook/oauth/start-auto")
def start_facebook_auto_oauth():
    """Start Facebook OAuth flow for automatic setup."""
    try:
        settings = load_settings()
        api_keys = settings.get("api_keys", {})

        # Get Facebook App ID from environment or settings
        facebook_app_id = os.getenv("FACEBOOK_APP_ID") or api_keys.get(
            "facebook_app_id", ""
        )
        facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET") or api_keys.get(
            "facebook_app_secret", ""
        )

        # If App Secret is missing, show a simpler setup page
        if not facebook_app_secret:
            return render_template_string(FACEBOOK_APP_SECRET_MISSING)

        if not facebook_app_id:
            return render_template_string(FACEBOOK_OAUTH_SETUP_INSTRUCTIONS)

        # Build Facebook OAuth URL
        redirect_uri = request.url_root.rstrip("/") + "/api/facebook/oauth/callback"
        scope = "pages_read_engagement,pages_read_user_content,pages_manage_posts,instagram_basic,instagram_manage_insights"

        fb_oauth_url = "https://www.facebook.com/v18.0/dialog/oauth?" + urlencode(
            {
                "client_id": facebook_app_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "response_type": "code",
                "state": os.urandom(16).hex(),
            }
        )

        # Save state for verification
        session["facebook_oauth_state"] = fb_oauth_url.split("state=")[1].split("&")[0]

        return redirect(fb_oauth_url)

    except Exception as e:
        return render_template_string(FACEBOOK_OAUTH_ERROR.replace("{error}", str(e)))


@facebook_auto_setup_bp.route("/api/facebook/oauth/callback")
def facebook_oauth_callback():
    """Handle Facebook OAuth callback - fetch tokens and save automatically."""
    try:
        code = request.args.get("code")
        state = request.args.get("state")

        if not code:
            error = request.args.get("error_description", "Unknown error")
            return f"""
            <html>
                <head><title>Error</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                    <h1>❌ Facebook Login Failed</h1>
                    <p>{error}</p>
                    <a href="/facebook-auto-setup" style="color: #1877f2;">Try Again</a>
                </body>
            </html>
            """

        settings = load_settings()
        api_keys = settings.get("api_keys", {})
        facebook_app_id = os.getenv("FACEBOOK_APP_ID") or api_keys.get(
            "facebook_app_id", ""
        )
        facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET") or api_keys.get(
            "facebook_app_secret", ""
        )

        # Step 1: Exchange code for user access token
        redirect_uri = request.url_root.rstrip("/") + "/api/facebook/oauth/callback"
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"

        token_response = requests.get(
            token_url,
            params={
                "client_id": facebook_app_id,
                "client_secret": facebook_app_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )

        token_data = token_response.json()
        if "error" in token_data:
            return f"""
            <html>
                <head><title>Error</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                    <h1>❌ Token Exchange Failed</h1>
                    <p>{token_data['error']['message']}</p>
                    <a href="/facebook-auto-setup" style="color: #1877f2;">Try Again</a>
                </body>
            </html>
            """

        user_access_token = token_data.get("access_token")

        # Step 2: Get user's pages
        pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
        pages_response = requests.get(
            pages_url,
            params={
                "fields": "id,name,access_token",
                "access_token": user_access_token,
            },
        )

        pages_data = pages_response.json()
        if "error" in pages_data:
            return f"""
            <html>
                <head><title>Error</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                    <h1>❌ Failed to Fetch Pages</h1>
                    <p>{pages_data['error']['message']}</p>
                    <a href="/facebook-auto-setup" style="color: #1877f2;">Try Again</a>
                </body>
            </html>
            """

        pages = pages_data.get("data", [])
        if not pages:
            return """
            <html>
                <head><title>Error</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                    <h1>❌ No Pages Found</h1>
                    <p>Your account doesn't have any Facebook Pages. Please create one first.</p>
                    <a href="/facebook-auto-setup" style="color: #1877f2;">Try Again</a>
                </body>
            </html>
            """

        # Use first page (or let user choose in UI)
        page = pages[0]
        facebook_page_id = page["id"]
        facebook_page_access_token = page["access_token"]

        # Step 3: Get Instagram Business Account ID
        instagram_account_id = ""
        ig_url = f"https://graph.facebook.com/v18.0/{facebook_page_id}"
        ig_response = requests.get(
            ig_url,
            params={
                "fields": "instagram_business_account",
                "access_token": facebook_page_access_token,
            },
        )

        ig_data = ig_response.json()
        if "instagram_business_account" in ig_data:
            instagram_account_id = ig_data["instagram_business_account"]["id"]

        # Step 4: Save everything to database
        api_keys["facebook_page_id"] = facebook_page_id
        api_keys["facebook_page_access_token"] = facebook_page_access_token
        api_keys["instagram_business_account_id"] = instagram_account_id

        settings["api_keys"] = api_keys
        save_settings(settings)

        # Return success page with redirect
        return f"""
        <html>
            <head>
                <title>✅ Setup Complete</title>
                <script>
                    setTimeout(function() {{
                        window.location.href = '/settings#social-media-connections';
                    }}, 2000);
                </script>
            </head>
            <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                <h1>✅ Facebook Setup Complete!</h1>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; color: #0369a1;">
                    <p><strong>Automatically fetched and saved:</strong></p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>✓ Facebook Page ID: {facebook_page_id}</li>
                        <li>✓ Facebook Page Access Token: {facebook_page_access_token[:20]}...</li>
                        {'<li>✓ Instagram Business Account ID: ' + instagram_account_id + '</li>' if instagram_account_id else '<li>ℹ️ Instagram account not linked to this page</li>'}
                    </ul>
                </div>
                <p style="color: #666;">Redirecting to Settings in 2 seconds...</p>
                <a href="/settings#social-media-connections" style="display: inline-block; background: #1877f2; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none;">Go to Settings Now</a>
            </body>
        </html>
        """

    except Exception as e:
        import traceback

        return f"""
        <html>
            <head><title>Error</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 40px;">
                <h1>❌ Error During Setup</h1>
                <p>{str(e)}</p>
                <pre style="background: #f5f5f5; padding: 10px; text-align: left; border-radius: 4px;">{traceback.format_exc()}</pre>
                <a href="/facebook-auto-setup" style="color: #1877f2;">Try Again</a>
            </body>
        </html>
        """


FACEBOOK_APP_SECRET_MISSING = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook App Secret Required</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #1877f2;
            margin-bottom: 10px;
        }
        .warning-box {
            background: #fef3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            color: #856404;
        }
        .step {
            background: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #1877f2;
            border-radius: 4px;
        }
        .code-block {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            overflow-x: auto;
            margin: 10px 0;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #1877f2;
            color: white;
        }
        .btn-primary:hover {
            background: #0a66c2;
        }
        .btn-secondary {
            background: #e9ecef;
            color: #333;
        }
        .btn-secondary:hover {
            background: #dee2e6;
        }
        .note {
            background: #d1ecf1;
            border-left: 4px solid #0c5460;
            padding: 15px;
            border-radius: 4px;
            color: #0c5460;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Facebook App Secret Required</h1>
        
        <div class="warning-box">
            <strong>⚠️ Setup Incomplete</strong><br>
            Your system has the Facebook App ID, but the App Secret is missing. This is needed to complete the OAuth login flow.
        </div>
        
        <div class="step">
            <strong>Quick Fix (1 minute):</strong>
            <p>Add your Facebook App Secret to the system:</p>
            <div class="code-block">FACEBOOK_APP_SECRET=your_secret_here</div>
            <p><small>📍 Location: <code>.env</code> file or environment variables</small></p>
        </div>
        
        <div class="step">
            <strong>How to Get Your App Secret:</strong>
            <ol>
                <li>Go to <a href="https://developers.facebook.com/apps/421181512329379/settings/basic" target="_blank">Facebook App Settings</a></li>
                <li>Scroll down to "App Secret"</li>
                <li>Click "Show" to reveal it</li>
                <li>Copy the full string</li>
            </ol>
        </div>
        
        <div class="note">
            💡 <strong>Why is this needed?</strong> The App Secret securely exchanges your login code for tokens. Without it, we can't authenticate with Facebook.
        </div>
        
        <div class="button-group">
            <a href="/facebook-token-helper" class="btn btn-secondary">📋 Use Manual Method</a>
            <button class="btn btn-primary" onclick="reloadPage()">🔄 Reload After Setup</button>
        </div>
        
        <script>
            function reloadPage() {
                setTimeout(() => location.reload(), 1000);
            }
        </script>
    </div>
</body>
</html>
"""

FACEBOOK_OAUTH_SETUP_INSTRUCTIONS = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook OAuth Setup</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1877f2;
            border-bottom: 3px solid #1877f2;
            padding-bottom: 10px;
        }
        .step {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #1877f2;
            border-radius: 4px;
        }
        .step-number {
            display: inline-block;
            background: #1877f2;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 10px;
        }
        .code-block {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }
        .button {
            display: inline-block;
            background: #1877f2;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            margin: 10px 5px;
        }
        .button:hover {
            background: #166fe5;
        }
        .note {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Facebook OAuth Setup Required</h1>
        <p>To enable one-click automatic Facebook/Instagram token fetching, your app needs to be registered with Facebook.</p>
        
        <div class="note">
            <strong>⚠️ Current Status:</strong> Facebook App ID is not configured. For now, you can use the manual copy-paste method instead.
        </div>
        
        <h2>Option 1: Enable Automatic Setup (Requires Setup)</h2>
        <p>If you're interested in one-click auto setup, follow these steps:</p>
        
        <div class="step">
            <span class="step-number">1</span>
            <strong>Create Facebook App</strong>
            <p>Go to <a href="https://developers.facebook.com/apps" target="_blank">Facebook Developer Console</a></p>
            <p>Click "My Apps" → "Create App" → Select "Consumer" type</p>
        </div>
        
        <div class="step">
            <span class="step-number">2</span>
            <strong>Add Products</strong>
            <p>In your app settings, add these products:</p>
            <ul>
                <li>Facebook Login</li>
                <li>Facebook Graph API</li>
            </ul>
        </div>
        
        <div class="step">
            <span class="step-number">3</span>
            <strong>Configure OAuth Redirect URL</strong>
            <p>In Settings → Basic, add your app credentials to this system.</p>
            <p>Then set the Redirect URI in Facebook App Settings:</p>
            <div class="code-block">http://localhost:5001/api/facebook/oauth/callback</div>
        </div>
        
        <div class="step">
            <span class="step-number">4</span>
            <strong>Add Configuration</strong>
            <p>Contact the app admin to add your Facebook App ID and Secret to the system.</p>
        </div>
        
        <h2>Option 2: Use Manual Setup (Recommended for Now)</h2>
        <p>For now, you can use the step-by-step manual method:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/facebook-token-helper" class="button">📋 Go to Manual Token Helper</a>
            <p style="margin-top: 10px; color: #666;">This method works perfectly - just copy and paste tokens when ready!</p>
        </div>
        
        <div class="note">
            <strong>💡 Tip:</strong> The manual method is actually more secure for single-user deployments, as you control your tokens directly.
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/settings" style="color: #1877f2; text-decoration: none;">← Back to Settings</a>
        </div>
    </div>
</body>
</html>
"""

FACEBOOK_OAUTH_ERROR = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .error-box {
            background: #ffebee;
            border-left: 4px solid #d32f2f;
            padding: 15px;
            border-radius: 4px;
            color: #c62828;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚠️ Error</h1>
        <div class="error-box">
            {error}
        </div>
        <p><a href="/facebook-auto-setup">← Go Back</a></p>
    </div>
</body>
</html>
"""
