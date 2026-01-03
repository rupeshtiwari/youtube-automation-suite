# Recommended Session Folder Structure

## Overview
To easily parse and display mentoring sessions, we recommend the following folder structure:

## Structure

```
Mentoring Sessions/
├── upcoming/
│   ├── 2026-01-15_john-doe_swe-system-design.txt
│   ├── 2026-01-20_jane-smith_pm-behavioral.md
│   └── 2026-01-25_alex-jones_sa-leadership.md
├── completed/
│   ├── 2025/
│   │   ├── 12/
│   │   │   ├── 2025-12-15_client-name_role-type.txt
│   │   │   └── 2025-12-20_client-name_role-type.md
│   │   └── 11/
│   └── 2024/
├── templates/
│   ├── session-template.txt
│   └── session-template.md
└── archive/
    └── (old sessions moved here)
```

## File Naming Convention

Format: `YYYY-MM-DD_client-name_role-type.extension`

Examples:
- `2026-01-15_john-doe_swe-system-design.txt`
- `2026-01-20_jane-smith_pm-behavioral.md`
- `2026-01-25_alex-jones_sa-leadership.md`

### Fields:
- **Date**: YYYY-MM-DD (ISO format, easy to parse and sort)
- **Client Name**: lowercase, hyphen-separated (e.g., `john-doe`)
- **Role-Type**: format like `role-interview-type`
  - Roles: `swe`, `pm`, `sa`, `tpm`, `em`, `mgr`, `dir`, `vp`
  - Types: `system-design`, `behavioral`, `coding`, `leadership`, `resume`, `salary-negotiation`

## Alternative: Metadata Files

If you prefer keeping existing filenames, use a `sessions.json` metadata file:

```json
{
  "sessions": [
    {
      "filename": "john-doe-interview-prep.txt",
      "date": "2026-01-15",
      "status": "upcoming",
      "client_name": "John Doe",
      "role": "swe",
      "type": "system-design",
      "notes": "Focus on distributed systems"
    }
  ]
}
```

## Current Implementation

The app will support both approaches:
1. **Smart filename parsing** - extracts date, client, role, type from filename
2. **Metadata file** - reads from `sessions.json` if available
3. **Fallback** - shows all files with basic info if structure doesn't match

## Benefits

- ✅ Easy to parse programmatically
- ✅ Chronologically sortable
- ✅ Clear status separation (upcoming vs completed)
- ✅ Organized by year/month for completed sessions
- ✅ Searchable by role, type, client name
- ✅ Can extract metadata automatically from filename

