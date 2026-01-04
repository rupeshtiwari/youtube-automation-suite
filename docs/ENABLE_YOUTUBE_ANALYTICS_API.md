# Enable YouTube Analytics API

The Analytics page shows all 0s because YouTube Analytics API needs to be enabled in Google Cloud Console.

## Steps to Enable YouTube Analytics API

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Select Your Project**
   - Make sure the correct project is selected (the one with your YouTube OAuth credentials)

3. **Enable YouTube Analytics API**
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Analytics API"
   - Click on it and press "ENABLE"

4. **Add Required Scopes**
   The OAuth consent screen needs these scopes:
   - `https://www.googleapis.com/auth/youtube.readonly` (already have this)
   - `https://www.googleapis.com/auth/yt-analytics.readonly` (ADD THIS)

5. **Re-authenticate**
   - Delete the current `config/token.json` file
   - Restart the server
   - Go to Settings and re-connect YouTube
   - This will request the new analytics scope

## What You'll Get

Once enabled, the Analytics page will show:

### YouTube Analytics
- **Total Views (30 days)**: Real view counts from YouTube
- **Watch Time (minutes)**: How long viewers watched
- **Total Videos**: Count from database
- **Demographics**: 
  - Age groups (age13-17, age18-24, age25-34, age35-44, age45-54, age55-64, age65+)
  - Gender breakdown (male, female, user_specified)
  - Top 5 countries viewing your content
  
### Optimal Posting Times
- Based on when your viewers are most active (hourly activity data)
- Shows top 3 hours when your audience is watching
- Helps you schedule videos for maximum engagement

## Testing

After enabling, test with:
```bash
curl http://127.0.0.1:5001/api/insights-data | python3 -m json.tool
```

You should see real analytics data instead of all 0s.

## Troubleshooting

If you see "YouTube Analytics API not enabled" error:
1. Make sure you enabled the API in Google Cloud Console
2. Wait 1-2 minutes for Google to propagate the changes
3. Delete `config/token.json` and re-authenticate

If you see "accessNotConfigured" error:
- The API is not enabled in your Google Cloud project
- Go back to step 3 above

If you see "403 Forbidden" error:
- Your OAuth app doesn't have the analytics scope
- Go back to step 4 above and re-authenticate
