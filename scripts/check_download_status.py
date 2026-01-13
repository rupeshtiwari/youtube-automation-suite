"""
Check download status and show what worked vs what failed
"""

import os
from pathlib import Path

DOWNLOAD_DIR = "data/shorts_downloads"


def main():
    print("=" * 80)
    print("YouTube Shorts Download Report")
    print("=" * 80)
    print()

    base_dir = Path(DOWNLOAD_DIR)

    if not base_dir.exists():
        print(f"❌ Download directory not found: {base_dir}")
        return

    # Get all playlist folders
    playlists = sorted([d for d in base_dir.iterdir() if d.is_dir()])

    total_playlists = len(playlists)
    total_videos = 0
    empty_playlists = []
    successful_playlists = []

    print(f"📂 Found {total_playlists} playlist folders\n")

    for playlist_dir in playlists:
        # Count video files
        video_files = list(playlist_dir.glob("*.mp4")) + list(
            playlist_dir.glob("*.webm")
        )
        video_count = len(video_files)
        total_videos += video_count

        if video_count == 0:
            empty_playlists.append(playlist_dir.name)
            status = "❌ EMPTY"
        else:
            successful_playlists.append((playlist_dir.name, video_count))
            status = f"✅ {video_count:2d} videos"

        print(f"{status} - {playlist_dir.name}")

    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"✅ Successful playlists: {len(successful_playlists)}")
    print(f"📹 Total videos downloaded: {total_videos}")
    print(f"❌ Empty playlists: {len(empty_playlists)}")
    print()

    if empty_playlists:
        print("Empty playlists (may contain private/unlisted videos):")
        for name in empty_playlists:
            print(f"   • {name}")
        print()
        print(
            "Note: These playlists likely contain private, unlisted, or deleted videos"
        )
        print(
            "that cannot be downloaded without being logged into your YouTube account."
        )

    print()
    print(f"📂 All videos saved to: {base_dir.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
