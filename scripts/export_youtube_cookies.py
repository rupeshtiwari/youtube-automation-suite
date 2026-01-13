"""
Export YouTube cookies from Chrome browser and save to cookies.txt
This allows yt-dlp to download private/unlisted videos
"""

import os
import subprocess
import sys


def export_cookies():
    print("=" * 80)
    print("YouTube Cookie Exporter for Private Videos")
    print("=" * 80)
    print()

    cookies_file = "cookies.txt"

    print("This script will export your YouTube cookies from Chrome")
    print("to allow downloading private/unlisted videos.")
    print()

    # Check if yt-dlp can extract cookies
    print("Testing cookie extraction from Chrome...")

    cmd = [
        "yt-dlp",
        "--cookies-from-browser",
        "chrome",
        "--cookies",
        cookies_file,
        "--skip-download",
        "https://www.youtube.com/",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and os.path.exists(cookies_file):
            print(f"✅ Cookies exported successfully to {cookies_file}")
            print()
            print("You can now run download_shorts_playlists.py to download")
            print("private/unlisted videos!")
            print()
            print(f"Cookie file location: {os.path.abspath(cookies_file)}")
            return True
        else:
            print("❌ Failed to export cookies")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Timeout - Chrome may be locked or cookies are encrypted")
        print()
        print("Alternative method:")
        print("1. Install 'Get cookies.txt' Chrome extension")
        print("2. Go to youtube.com and click the extension")
        print("3. Download cookies.txt file")
        print(f"4. Save it to: {os.path.abspath(cookies_file)}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    export_cookies()
