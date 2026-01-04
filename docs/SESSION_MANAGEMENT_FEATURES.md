# Session Management System - Features & Roadmap

## ✅ Completed Features

### 1. Enhanced Session View Modal
- **4 Tabs Interface:**
  - **Content Tab**: View full session text with proper formatting
  - **Attachments Tab**: Link Google Meet recordings, Gemini transcripts, and email threads
  - **Edit Metadata Tab**: Add/edit session metadata (client name, date, role, type, ChatGPT notes, tags)
  - **Generated Content Tab**: View AI-generated content from sessions (coming soon)

### 2. Session Metadata Database
- New `sessions_metadata` table stores:
  - Basic info (client name, date, role, type)
  - Linked resources (Meet recordings, transcripts, email threads)
  - ChatGPT notes and additional notes
  - Tags for organization
  - Google Drive file IDs for automatic access

### 3. API Endpoints
- `GET/PUT /api/sessions/<filename>/metadata` - Get/update session metadata
- Enhanced session viewing with metadata loading
- Attachment linking with Google Drive ID extraction

### 4. User Interface
- Click "View" on any session to see:
  - Full session content
  - All linked attachments
  - Metadata editing form
  - Content generation buttons (Shorts, Articles, Blogs)

## 🚧 Next Steps (To Build)

### Phase 1: Google Drive Integration
**Goal**: Automatically fetch Meet recordings from Google Drive

**Implementation:**
1. Add Google Drive API to requirements.txt
2. Create `app/google_drive_integration.py`:
   - List files in Drive
   - Search for Meet recordings by date/client name
   - Auto-link recordings to sessions
   - Download transcripts if available

**API Endpoints Needed:**
- `POST /api/integrations/google-drive/connect` - OAuth connection
- `GET /api/integrations/google-drive/search-recordings` - Search for recordings
- `POST /api/sessions/<filename>/auto-link-recording` - Auto-link from Drive

### Phase 2: Email Scanning
**Goal**: Scan emails from igotanoffer to detect upcoming sessions

**Implementation:**
1. Add Gmail API to requirements.txt
2. Create `app/email_integration.py`:
   - Connect to Gmail API
   - Search for emails from "igotanoffer"
   - Parse session details (date, time, client, type)
   - Create session entries automatically
   - Link email threads to sessions

**API Endpoints Needed:**
- `POST /api/integrations/gmail/connect` - OAuth connection
- `GET /api/integrations/gmail/scan-sessions` - Scan for upcoming sessions
- `POST /api/integrations/gmail/auto-create-sessions` - Auto-create from emails

### Phase 3: AI Content Generation
**Goal**: Generate articles, blogs, and shorts from session content

**Implementation:**
1. Add OpenAI/Anthropic API support
2. Create `app/ai_content_generator.py`:
   - Generate articles from session transcripts
   - Create blog posts with key insights
   - Generate multiple shorts scripts
   - Create social media posts
   - Use all linked resources (recordings, transcripts, notes)

**API Endpoints Needed:**
- `POST /api/sessions/<filename>/generate-article` - Generate article
- `POST /api/sessions/<filename>/generate-blog` - Generate blog post
- `POST /api/sessions/<filename>/generate-shorts` - Already exists, enhance it
- `POST /api/sessions/<filename>/generate-social-posts` - Generate social media posts

### Phase 4: Knowledge Base
**Goal**: Unified search and content creation from all sessions

**Implementation:**
1. Create `app/knowledge_base.py`:
   - Vector database for semantic search
   - Search across all sessions, transcripts, notes
   - Find related sessions by topic
   - Generate content from multiple sessions
   - Tag and categorize automatically

**Features:**
- Semantic search: "Find sessions about system design interviews"
- Content aggregation: "Create article from all leadership sessions"
- Topic clustering: Group similar sessions
- Auto-tagging: AI-powered tag generation

## 📋 Quick Start Guide

### Using the Enhanced Session View

1. **Go to Sessions page**: http://localhost:5001/sessions
2. **Click "View"** on any session
3. **View Content**: See full session text in the Content tab
4. **Link Attachments**:
   - Go to Attachments tab
   - Paste Google Drive URL for Meet recording
   - Paste Google Drive URL for Gemini transcript
   - Add email thread ID
5. **Edit Metadata**:
   - Go to Edit Metadata tab
   - Fill in client name, date, role, type
   - **Paste ChatGPT notes** in the textarea
   - Add tags
   - Click "Save Metadata"
6. **Generate Content**:
   - Click "Generate Shorts" for viral shorts scripts
   - Click "Generate Article" (coming soon)
   - Click "Generate Blog" (coming soon)

### Linking Google Drive Files

**Format**: Paste the full Google Drive URL
- Example: `https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing`
- The system automatically extracts the file ID
- You can also paste just the file ID: `1ABC123xyz`

### Adding ChatGPT Notes

1. Copy your ChatGPT conversation or notes
2. Go to Edit Metadata tab
3. Paste in "ChatGPT Notes" textarea
4. Click "Save Metadata"
5. These notes will be used for AI content generation

## 🔧 Configuration Needed

### For Google Drive Integration:
1. Enable Google Drive API in Google Cloud Console
2. Add Drive scope to OAuth: `https://www.googleapis.com/auth/drive.readonly`
3. Update `client_secret.json` with Drive API access

### For Gmail Integration:
1. Enable Gmail API in Google Cloud Console
2. Add Gmail scope: `https://www.googleapis.com/auth/gmail.readonly`
3. Update OAuth scopes

### For AI Content Generation:
1. Add OpenAI API key to settings (or use Anthropic/other)
2. Configure in Settings page
3. Set content generation preferences

## 📊 Database Schema

### sessions_metadata Table
```sql
CREATE TABLE sessions_metadata (
    id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE,
    role TEXT,
    session_type TEXT,
    client_name TEXT,
    session_date TEXT,
    meet_recording_url TEXT,
    meet_recording_drive_id TEXT,
    gemini_transcript_url TEXT,
    gemini_transcript_drive_id TEXT,
    chatgpt_notes TEXT,
    email_thread_id TEXT,
    email_subject TEXT,
    additional_notes TEXT,
    tags TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### session_content Table
```sql
CREATE TABLE session_content (
    id INTEGER PRIMARY KEY,
    session_filename TEXT,
    content_type TEXT,  -- 'article', 'blog', 'shorts', 'social_post'
    content TEXT,
    platform TEXT,
    status TEXT DEFAULT 'draft',
    scheduled_date TEXT,
    published_date TEXT,
    created_at TIMESTAMP
)
```

## 🎯 Current Status

✅ **Working Now:**
- View session content in modal
- Link attachments (recordings, transcripts, emails)
- Edit metadata (including ChatGPT notes)
- Save all metadata to database
- Generate shorts scripts

🚧 **In Progress:**
- Google Drive auto-linking
- Email scanning
- AI content generation (articles, blogs)
- Knowledge base search

## 💡 Usage Tips

1. **Organize Sessions**: Use tags to organize sessions by topic, client type, or interview type
2. **Link Everything**: Link recordings, transcripts, and emails for complete session context
3. **Use ChatGPT Notes**: Paste your analysis/notes from ChatGPT - they'll be used for content generation
4. **Generate Multiple Content Types**: From one session, generate shorts, articles, and blog posts
5. **Search & Filter**: Use the search box to find specific sessions quickly

## 🔗 Next Integration Steps

1. **Google Drive**: Set up OAuth, then auto-link recordings
2. **Gmail**: Set up OAuth, then scan for upcoming sessions
3. **AI APIs**: Add OpenAI/Anthropic for content generation
4. **Vector DB**: Add semantic search with embeddings

---

**Ready to use now**: Session viewing, metadata editing, attachment linking
**Coming soon**: Auto-integrations, AI content generation, knowledge base

