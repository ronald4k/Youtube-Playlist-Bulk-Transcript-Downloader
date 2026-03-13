"""
YouTube Transcript Downloader
==============================
Downloads plain-text transcripts (no timestamps) from YouTube videos or playlists.
Works with youtube-transcript-api v1.x

Author: Spawzer
GitHub: https://github.com/Spawzer/yt-transcript-downloader

QUICK START:
  1. pip install yt-dlp youtube-transcript-api
  2. Edit the CONFIGURATION section below
  3. python download_transcripts.py
"""

import os
import re
import time
import random
import http.cookiejar
import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)

# ══════════════════════════════════════════════════════════════
#  CONFIGURATION — edit this section before running
# ══════════════════════════════════════════════════════════════

# Folder where transcript .txt files will be saved.
# Examples:
#   Windows : r"C:\Users\YourName\Documents\Transcripts"
#   Mac/Linux: "/home/yourname/Documents/Transcripts"
OUTPUT_DIR = r"C:\Users\YourName\Documents\Transcripts"

# Path to your YouTube cookies file (optional but recommended for large playlists).
# Set to None to skip cookies entirely.
# See README.md for how to export this file.
# Examples:
#   Windows : r"C:\Users\YourName\Documents\youtube_cookies.txt"
#   Mac/Linux: "/home/yourname/Documents/youtube_cookies.txt"
COOKIES_FILE = None

# YouTube URLs to download — paste playlist or individual video URLs here.
# You can mix playlists and single videos freely.
URLS = [
    # "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
    # "https://www.youtube.com/watch?v=VIDEO_ID",
]

# Caption language preferences (tries each in order)
LANGUAGES = ["en", "en-GB", "en-US"]

# Seconds to wait between videos (random value between min and max).
# Increase these if you keep hitting rate limits.
DELAY_MIN = 5
DELAY_MAX = 12

# ══════════════════════════════════════════════════════════════


def load_cookie_jar():
    """Load cookies from a Netscape-format cookies.txt file."""
    if not COOKIES_FILE:
        return None
    if not os.path.isfile(COOKIES_FILE):
        print(f"  WARNING: Cookies file not found at: {COOKIES_FILE}")
        print("  Continuing without cookies (may hit 429 on large playlists).\n")
        return None
    try:
        jar = http.cookiejar.MozillaCookieJar()
        jar.load(COOKIES_FILE, ignore_discard=True, ignore_expires=True)
        print(f"  [cookies] Loaded {COOKIES_FILE}")
        return jar
    except Exception as exc:
        print(f"  WARNING: Could not load cookies file: {exc}")
        return None


def sanitize_filename(name: str) -> str:
    """Remove characters that are illegal in filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()


def get_playlist_entries(url: str) -> list[tuple[str, str]]:
    """Use yt-dlp to expand a URL into a list of (video_id, title) pairs."""
    opts = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "ignoreerrors": True,
    }
    if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        return []
    if "entries" in info:
        return [
            (e["id"], e.get("title", e["id"]))
            for e in info["entries"]
            if e and e.get("id")
        ]
    return [(info["id"], info.get("title", info["id"]))]


def fetch_transcript(api: YouTubeTranscriptApi, video_id: str) -> str | None:
    """
    Fetch a transcript for one video and return it as clean plain text.
    Returns None if no captions are available.
    """
    try:
        transcript_list = api.list(video_id)

        fetched = None

        # 1. Try manually created captions first (higher quality)
        try:
            fetched = transcript_list.find_manually_created_transcript(LANGUAGES).fetch()
        except NoTranscriptFound:
            pass

        # 2. Fall back to auto-generated captions
        if fetched is None:
            try:
                fetched = transcript_list.find_generated_transcript(LANGUAGES).fetch()
            except NoTranscriptFound:
                pass

        # 3. Last resort: translate whatever language is available into English
        if fetched is None:
            try:
                available = list(transcript_list)
                if available:
                    fetched = available[0].translate("en").fetch()
            except Exception:
                pass

        if fetched is None:
            return None

        # Build clean plain text — no timestamps, no duplicate lines
        result_lines = []
        prev = ""
        for snippet in fetched:
            text = getattr(snippet, "text", None)
            if text is None:
                text = snippet.get("text", "") if isinstance(snippet, dict) else ""
            # Remove sound descriptions like [Music] or [Applause]
            text = re.sub(r"\[.*?\]", "", text).strip()
            if text and text != prev:
                result_lines.append(text)
                prev = text

        return "\n".join(result_lines) if result_lines else None

    except TranscriptsDisabled:
        print("    Captions are disabled for this video.")
        return None
    except VideoUnavailable:
        print("    Video is unavailable.")
        return None
    except CouldNotRetrieveTranscript as exc:
        print(f"    Could not retrieve transcript: {exc}")
        return None
    except Exception as exc:
        if "429" in str(exc) or "Too Many Requests" in str(exc):
            raise   # bubble up to retry loop
        print(f"    Unexpected error: {exc}")
        return None


def download_transcripts():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 62)
    print("  YouTube Transcript Downloader")
    print(f"  Output  : {OUTPUT_DIR}")
    print(f"  Delay   : {DELAY_MIN}-{DELAY_MAX}s between videos")
    print("=" * 62 + "\n")

    cookie_jar = load_cookie_jar()

    # Build a requests session with browser-like headers and optional cookies
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })
    if cookie_jar is not None:
        session.cookies.update(cookie_jar)

    api = YouTubeTranscriptApi(http_client=session)

    # Expand all URLs into individual (video_id, title) pairs
    all_videos: list[tuple[str, str]] = []
    for url in URLS:
        print(f"  Fetching info: {url}")
        entries = get_playlist_entries(url)
        print(f"  Found {len(entries)} video(s).")
        all_videos.extend(entries)

    total = len(all_videos)
    print(f"\n  Total videos to process: {total}\n")

    saved = 0
    skipped = 0

    for idx, (video_id, title) in enumerate(all_videos, start=1):
        safe_title = sanitize_filename(title)
        print(f"  [{idx}/{total}] {title}")

        text = None
        for attempt in range(1, 6):
            try:
                text = fetch_transcript(api, video_id)
                break
            except Exception as exc:
                if "429" in str(exc) or "Too Many Requests" in str(exc):
                    wait = min(30 * (2 ** (attempt - 1)), 120) + random.uniform(0, 10)
                    print(f"    429 — waiting {wait:.0f}s then retrying ({attempt}/5)...")
                    time.sleep(wait)
                else:
                    print(f"    Error: {exc}")
                    break

        if text:
            out_path = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"    Saved -> {out_path}")
            saved += 1
        else:
            print("    No transcript available — skipping.")
            skipped += 1

        if idx < total:
            delay = random.uniform(DELAY_MIN, DELAY_MAX)
            print(f"    Waiting {delay:.1f}s...\n")
            time.sleep(delay)

    print("\n" + "=" * 62)
    print(f"  Done!  Saved: {saved}   Skipped (no captions): {skipped}")
    print(f"  Transcripts saved to: {OUTPUT_DIR}")
    print("=" * 62)


if __name__ == "__main__":
    if not URLS:
        print("ERROR: No URLs defined.")
        print("Open this script and add your YouTube URLs to the URLS list.")
    else:
        download_transcripts()
