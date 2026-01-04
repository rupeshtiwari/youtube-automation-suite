"""
Facebook Token Helper - Provides step-by-step instructions for getting Facebook Page Access Token
"""
from flask import Blueprint, render_template_string

facebook_helper_bp = Blueprint('facebook_helper', __name__)

FACEBOOK_HELPER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Helper</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
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
            transition: background 0.3s;
        }
        .button:hover {
            background: #166fe5;
        }
        .button-secondary {
            background: #42b72a;
        }
        .button-secondary:hover {
            background: #36a420;
        }
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .success {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .copy-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        .copy-btn:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Facebook Page Access Token Helper</h1>
        <p>Follow these steps to get your Facebook Page Access Token. This token allows the app to post to your Facebook Page.</p>
        
        <div class="step">
            <span class="step-number">1</span>
            <strong>Open Facebook Graph API Explorer</strong>
            <p>Click the button below to open Facebook's Graph API Explorer in a new tab:</p>
            <a href="https://developers.facebook.com/tools/explorer/" target="_blank" class="button">Open Graph API Explorer</a>
        </div>
        
        <div class="step">
            <span class="step-number">2</span>
            <strong>Select Your App</strong>
            <p>In the Graph API Explorer:</p>
            <ul>
                <li>Click the dropdown next to "Meta App" at the top</li>
                <li>Select your Facebook App (or create one if you don't have one)</li>
                <li>If you don't have an app, click "Create App" and follow the prompts</li>
            </ul>
        </div>
        
        <div class="step">
            <span class="step-number">3</span>
            <strong>Generate User Access Token</strong>
            <p>Click the "Generate Access Token" button and grant these permissions:</p>
            <div class="code-block">
pages_manage_posts
pages_read_engagement
pages_show_list
business_management
            </div>
            <p>Click "Generate Access Token" and authorize the app.</p>
        </div>
        
        <div class="step">
            <span class="step-number">4</span>
            <strong>Get Your Page ID</strong>
            <p>In the Graph API Explorer:</p>
            <ol>
                <li>Change the endpoint from "me" to: <code>me/accounts</code></li>
                <li>Click "Submit"</li>
                <li>You'll see a list of pages you manage</li>
                <li>Find your page and copy the <strong>id</strong> field (this is your Page ID)</li>
            </ol>
            <div class="code-block">
GET /me/accounts
            </div>
        </div>
        
        <div class="step">
            <span class="step-number">5</span>
            <strong>Get Page Access Token</strong>
            <p>Now get the Page Access Token:</p>
            <ol>
                <li>In the response from step 4, find the <code>access_token</code> field for your page</li>
                <li>Copy this token - this is your <strong>Page Access Token</strong></li>
                <li>Or, change the endpoint to: <code>{page-id}?fields=access_token</code> (replace {page-id} with your Page ID)</li>
            </ol>
            <div class="warning">
                <strong>⚠️ Important:</strong> This token expires in about 60 days. You'll need to regenerate it when it expires.
            </div>
        </div>
        
        <div class="step">
            <span class="step-number">6</span>
            <strong>Get Instagram Business Account ID (Optional)</strong>
            <p>If you want to post to Instagram:</p>
            <ol>
                <li>Change the endpoint to: <code>{page-id}?fields=instagram_business_account</code></li>
                <li>Click "Submit"</li>
                <li>Copy the <code>id</code> from the <code>instagram_business_account</code> object</li>
            </ol>
            <div class="code-block">
GET /{page-id}?fields=instagram_business_account
            </div>
        </div>
        
        <div class="step">
            <span class="step-number">7</span>
            <strong>Enter Tokens in Settings</strong>
            <p>Go back to the app Settings page and enter:</p>
            <ul>
                <li><strong>Facebook Page Access Token:</strong> The token from step 5</li>
                <li><strong>Facebook Page ID:</strong> The ID from step 4</li>
                <li><strong>Instagram Business Account ID:</strong> The ID from step 6 (if applicable)</li>
            </ul>
            <a href="/config#social-media-connections" class="button button-secondary">Go to Settings</a>
        </div>
        
        <div class="success">
            <strong>✅ Done!</strong> Once you've entered the tokens, you can start scheduling posts to Facebook and Instagram.
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            <h3>Need Help?</h3>
            <p>If you encounter issues:</p>
            <ul>
                <li>Make sure you're an admin of the Facebook Page</li>
                <li>Ensure your Facebook App has the Pages product added</li>
                <li>Check that you granted all required permissions</li>
                <li>For Instagram, make sure your Instagram account is connected to your Facebook Page as a Business Account</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Add copy functionality to code blocks
        document.querySelectorAll('.code-block').forEach(block => {
            const button = document.createElement('button');
            button.className = 'copy-btn';
            button.textContent = 'Copy';
            button.onclick = () => {
                navigator.clipboard.writeText(block.textContent.trim()).then(() => {
                    button.textContent = 'Copied!';
                    setTimeout(() => button.textContent = 'Copy', 2000);
                });
            };
            block.style.position = 'relative';
            block.appendChild(button);
        });
    </script>
</body>
</html>
"""

@facebook_helper_bp.route('/facebook-token-helper')
def facebook_token_helper():
    """Display Facebook token helper page with step-by-step instructions."""
    return render_template_string(FACEBOOK_HELPER_HTML)

