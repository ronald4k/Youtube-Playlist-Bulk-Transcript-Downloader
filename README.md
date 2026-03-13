# YouTube Transcript Downloader

Downloads plain-text transcripts (no timestamps) from YouTube videos or playlists.
Saves each video as a clean `.txt` file. Works with playlists of any size.

---

## Features

- Downloads transcripts from any YouTube video or playlist
- Saves clean plain text — no timestamps, no VTT markup, no duplicate lines
- Removes `[Music]`, `[Applause]` and other sound labels
- Prefers manually created captions, falls back to auto-generated ones
- Smart rate-limit handling with automatic retries and delays
- Skips videos with no captions instead of crashing

---

## Requirements

- Python 3.10 or newer
- Internet connection

---

## Installation

**Step 1 — Install Python** (if you don't have it)

Download from https://www.python.org/downloads/ and install.
On Windows, tick "Add Python to PATH" during setup.

**Step 2 — Install the required libraries**

Open a terminal (Command Prompt on Windows) and run:

```
pip install yt-dlp youtube-transcript-api
```

---

## Setup

### 1. Download the script

Click the green **Code** button on this page → **Download ZIP** → extract it anywhere you like.

Or if you have Git installed:
```
git clone https://github.com/ronald4k/Youtube-Playlist-Bulk-Transcript-Downloader
cd Youtube-Playlist-Bulk-Transcript-Downloader
```

### 2. Export your YouTube cookies (recommended)

This prevents YouTube from rate-limiting you on large playlists.

1. Open **Chrome** and make sure you are **logged in** to YouTube
2. Install the Chrome extension **"Get cookies.txt LOCALLY"**
   → https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
3. Go to **https://www.youtube.com**
4. Click the extension icon (puzzle piece top-right of Chrome) → click the extension name → click **Export**
5. A file will download — rename it to `youtube_cookies.txt`
6. Move it somewhere easy to find, e.g. your Documents folder

> **Note:** You can skip this step for small downloads (a few videos). It is strongly recommended for full playlists.

---

## Usage

### 1. Open `download_transcripts.py` in any text editor

### 2. Edit the CONFIGURATION section at the top of the file

```python
# Where to save the transcript .txt files
OUTPUT_DIR = r"C:\Users\YourName\Documents\Transcripts"

# Path to your cookies file (or set to None to skip)
COOKIES_FILE = r"C:\Users\YourName\Documents\youtube_cookies.txt"

# YouTube URLs — paste playlist or video URLs here
URLS = [
    "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
    "https://www.youtube.com/watch?v=VIDEO_ID",
]
```

**Mac/Linux paths** look like this:
```python
OUTPUT_DIR   = "/home/yourname/Documents/Transcripts"
COOKIES_FILE = "/home/yourname/Documents/youtube_cookies.txt"
```

### 3. Run the script

**Windows:**
```
py download_transcripts.py
```

**Mac / Linux:**
```
python3 download_transcripts.py
```

---

## Output

Each video gets its own `.txt` file in your output folder named after the video title:

```
Transcripts/
  What Has YouTube Become_.txt
  Apple_ This Is Only the Beginning....txt
  It_s Time..txt
  ...
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install yt-dlp youtube-transcript-api` |
| `No transcript available` | The video has no captions — YouTube doesn't provide them for every video |
| `429 Too Many Requests` | Export your `youtube_cookies.txt` (see Setup above) and add its path to `COOKIES_FILE` |
| Script crashes immediately | Make sure you are using Python 3.10 or newer: run `python --version` |
| Wrong Python version used | On Windows use `py` instead of `python` |

---

## Notes

- This tool only downloads **captions/subtitles** — it does not download video files
- Auto-generated captions are used when manual ones are not available
- Videos without any captions are skipped and reported at the end
- Delays between requests are randomized to avoid triggering rate limits

---

## License

MIT License — free to use, modify, and share.
