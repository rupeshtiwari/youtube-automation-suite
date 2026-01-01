# Load Your Configuration

## 📝 Instructions

1. **Open the file `MY_CONFIG.json` in the editor**
2. **Fill in your API credentials and settings** (replace empty strings with your actual values)
3. **Save the file**
4. **Tell me when you're done** - I'll load it into the app

---

## 🔑 What to Fill In

### API Keys Section

#### LinkedIn
- `linkedin_client_id`: Your LinkedIn App Client ID
- `linkedin_client_secret`: Your LinkedIn App Client Secret  
- `linkedin_access_token`: (Optional) If you have one
- `linkedin_person_urn`: Format: `urn:li:person:xxxxx`

#### Facebook
- `facebook_app_id`: Your Facebook App ID
- `facebook_app_secret`: Your Facebook App Secret
- `facebook_page_access_token`: (Optional) If you have one
- `facebook_page_id`: Your Facebook Page ID

#### Instagram
- `instagram_business_account_id`: Your Instagram Business Account ID
- `instagram_access_token`: (Optional) If you have one

#### Ayrshare (Optional)
- `ayrshare_api_key`: If you're using Ayrshare

---

### Scheduling Section

- `enabled`: `true` or `false` - Enable daily automation
- `videos_per_day`: Number (1-10) - Videos to process per day
- `youtube_schedule_time`: Time like `"23:00"` - When to schedule YouTube videos
- `social_media_schedule_time`: Time like `"19:30"` - When to post on social media
- `schedule_day`: Day like `"wednesday"` - Day of week to run
- `playlist_id`: Your YouTube playlist ID (if you have one)
- `export_type`: `"shorts"` or `"all"` - What to export
- `auto_post_social`: `true` or `false` - Auto-post to social media
- `social_platforms`: Array like `["linkedin", "facebook", "instagram"]` - Which platforms
- `upload_method`: `"native"` or `"link"` - How to upload videos

---

### CTA Section

- `booking_url`: Your booking URL (default: `"https://fullstackmaster/book"`)
- `whatsapp_number`: Your WhatsApp number (default: `"+1-609-442-4081"`)
- `linkedin_url`: Your LinkedIn profile URL
- `instagram_url`: Your Instagram profile URL
- `facebook_url`: Your Facebook page URL
- `youtube_url`: Your YouTube channel URL
- `twitter_url`: Your Twitter/X profile URL
- `website_url`: Your website URL

---

## ⚠️ Security Note

**DO NOT commit `MY_CONFIG.json` to Git!** It contains your API keys.

The file is already in `.gitignore` so it won't be committed.

---

## ✅ After You Fill It In

Once you've filled in your config, tell me:
- "Config ready" or "Done"
- I'll load it into the database
- Then we can test the critical features

---

## 🧪 What We'll Test After Loading

1. **Native Video Upload**
   - Test downloading a YouTube video
   - Test uploading to LinkedIn
   - Test uploading to Facebook
   - Test uploading to Instagram

2. **Auto-Publishing**
   - Schedule a test post
   - Verify it auto-publishes

3. **End-to-End Workflow**
   - Create post → Download video → Upload → Publish

