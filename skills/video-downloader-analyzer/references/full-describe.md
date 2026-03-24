---
name: video-downloader-analyzer
description: Download videos from YouTube, Bilibili, and other sites, and analyze them with Gemini. Supports proxy environments with automatic compression and smart video handling.
homepage: https://ai.google.dev/
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["uv", "ffmpeg", "yt-dlp"], "env": ["GEMINI_API_KEY", "GEMINI_BASE_URL"] },
        "primaryEnv": "GEMINI_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
            {
              "id": "ffmpeg-brew",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install FFmpeg (brew)",
            },
            {
              "id": "yt-dlp-uv",
              "kind": "uv",
              "package": "yt-dlp",
              "bins": ["yt-dlp"],
              "label": "Install yt-dlp via uv",
            }
          ],
      },
  }
---

# Video Downloader & Analyzer

This skill combines powerful video downloading (via **yt-dlp**) with intelligent video analysis (via **Gemini**). 

It supports:
- **Downloading** videos from YouTube, Bilibili, Twitter, and thousands of other sites
- **Analyzing** local or downloaded videos using Gemini
- **Multiple analysis modes** for YouTube (prompt-based, file_uri, inline)
- **Proxy environments** with automatic compression to bypass upload restrictions
- **Smart compression** that adapts to file size automatically

## Part 1: Download Videos

### Prerequisites

Before downloading, verify dependencies are installed:

```bash
# Check yt-dlp
which yt-dlp || echo "yt-dlp not installed. Install with: uv tool install yt-dlp"

# Check ffmpeg (required for audio extraction and format merging)
which ffmpeg || echo "ffmpeg not installed. Install with: brew install ffmpeg"
```

If not installed, install them first:
```bash
uv tool install yt-dlp
brew install ffmpeg
```

### Download Examples

#### 1. Basic Download (Best Quality)

```bash
yt-dlp -P "~/Downloads/video" "VIDEO_URL"
```

#### 2. YouTube Download (with cookies - recommended)

YouTube often blocks direct downloads with 403 errors. Always use browser cookies for YouTube:

```bash
yt-dlp -P "~/Downloads/video" --cookies-from-browser chrome "YOUTUBE_URL"
```

Supported browsers: `chrome`, `firefox`, `safari`, `edge`, `brave`, `opera`

#### 3. Download with Custom Output Path

```bash
yt-dlp -P "/path/to/save" -o "%(title)s.%(ext)s" "VIDEO_URL"
```

#### 4. Download Specific Quality

**720p:**
```bash
yt-dlp -P "~/Downloads/video" -f "bestvideo[height<=720]+bestaudio/best[height<=720]" "VIDEO_URL"
```

**360p (for smaller file size):**
```bash
yt-dlp -P "~/Downloads/video" -f "bestvideo[height<=360][vcodec^=hevc]+bestaudio[ext=m4a]/best[height<=360]" "VIDEO_URL"
```

#### 5. Extract Audio Only (MP3)

```bash
yt-dlp -P "~/Downloads/video" -x --audio-format mp3 "VIDEO_URL"
```

#### 6. Download with Subtitles

```bash
yt-dlp -P "~/Downloads/video" --write-subs --sub-langs all "VIDEO_URL"
```

#### 7. List Available Formats

```bash
yt-dlp -F "VIDEO_URL"
```

Then download specific format by ID:
```bash
yt-dlp -P "~/Downloads/video" -f FORMAT_ID "VIDEO_URL"
```

#### 8. Download Playlist

```bash
# Download entire playlist
yt-dlp -P "~/Downloads/video" -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"

# Download specific range (e.g., items 1-5)
yt-dlp -P "~/Downloads/video" -I 1:5 "PLAYLIST_URL"
```

#### 9. Download with Thumbnail

```bash
yt-dlp -P "~/Downloads/video" --write-thumbnail "VIDEO_URL"
```

### Download Workflow

When user provides a video URL:

1. **Identify the platform**:
   - YouTube/YouTube Music → **Always use `--cookies-from-browser chrome`**
   - Other sites → Try without cookies first

2. **Ask what they want** (if not specified):
   - Just download the video?
   - Extract audio only?
   - Need subtitles?
   - Specific quality?

3. **Construct the command** based on requirements

4. **Execute the download**

5. **Handle errors**:
   - 403 Forbidden → Retry with `--cookies-from-browser`
   - Connection issues → yt-dlp auto-resumes, just retry
   - Format unavailable → Use `-F` to list formats, then select

6. **Report the result** - file location and any errors

---

## Part 2: Analyze Videos

### Setup

Ensure you have your environment variables set:
- `GEMINI_API_KEY`: Your Gemini API key (required)
- `GEMINI_BASE_URL`: The proxy endpoint (optional, e.g., `https://api.yourproxy.com`)

### Smart Compression Strategy

The analysis script automatically adjusts compression based on input file size to ensure it stays under Gemini's upload limits:

| File Size | Action | FPS | Reason |
|-----------|--------|-----|--------|
| < 14 MB   | Skip compression | - | Direct Base64 (green path) ✨ |
| 14-32 MB  | Compress | 6 fps | Balanced quality vs size |
| 32-42 MB  | Compress | 1 fps | Extreme compression |
| > 42 MB   | **Trim first** | 1 fps | Reduce to ~42MB, then compress |

After compression, if the result still exceeds 14MB, the script automatically trims the video to the target size.

### Local Video Analysis

Analyze a local video file:

```bash
# Basic analysis
uv run {skill}/scripts/analyze_video.py -v "video.mp4" -p "Describe the video"

# With longer timeout
uv run {skill}/scripts/analyze_video.py -v "video.mp4" -p "Summarize the key points" --exec-timeout 300

# Keep temporary files for debugging
uv run {skill}/scripts/analyze_video.py -v "video.mp4" -p "What's happening?" --keep-temp
```

### YouTube Video Analysis (Three Modes)

#### Mode 1: Prompt Mode (Fastest)
URL is appended to the prompt. **YouTube only**.

```bash
uv run {skill}/scripts/analyze_video.py \
  -v "https://www.youtube.com/watch?v=9hE5-98ZeCg" \
  -p "Describe the video" \
  --mode prompt
```

**Pros:** No download needed, very fast
**Cons:** Limited to YouTube

#### Mode 2: File URI Mode (Google Native)
Uses Google's native file_uri API. **YouTube only**.

```bash
uv run {skill}/scripts/analyze_video.py \
  -v "https://www.youtube.com/watch?v=9hE5-98ZeCg" \
  -p "Describe the video" \
  --mode file_uri
```

**Pros:** Native support, bypasses upload size limits
**Cons:** May have access restrictions depending on region/account

#### Mode 3: Inline Mode (Default, Most Reliable)
Downloads the video, compresses it, converts to Base64, and uploads as inline data.

```bash
uv run {skill}/scripts/analyze_video.py \
  -v "https://www.youtube.com/watch?v=9hE5-98ZeCg" \
  -p "Describe the video" \
  --mode inline
```

**Pros:** Works with any URL, most reliable
**Cons:** Requires download and compression (slower)

### Non-YouTube URL Analysis

For videos from other sources, inline mode is used automatically:

```bash
uv run {skill}/scripts/analyze_video.py \
  -v "https://example.com/video.mp4" \
  -p "Analyze this video"
```

### With Proxy Support

If you need to download through a proxy:

```bash
uv run {skill}/scripts/analyze_video.py \
  -v "https://www.youtube.com/watch?v=xxx" \
  -p "Describe the video" \
  --proxy "http://proxy.example.com:8080"
```

### Resolution and Downscaling

The script automatically handles high-resolution videos:
- If video > 360P: automatically downscaled to 360P (preserves original)
- If downsampled video still > 42MB: auto-trim to size
- If compression result > 14MB: auto-trim to 14MB

### Complete Parameter Reference

```bash
uv run {skill}/scripts/analyze_video.py \
  --video/-v        "Path or URL (required)" \
  --prompt/-p       "Prompt for the model (required)" \
  --model/-m        "Model name (default: gemini-2-flash)" \
  --mode            "YouTube mode: prompt/file_uri/inline (default: inline)" \
  --proxy           "HTTP proxy URL (optional)" \
  --cookies-browser "Browser for cookies: chrome/firefox/safari/etc (default: chrome)" \
  --exec-timeout    "Total execution timeout in seconds (default: 300)" \
  --keep-temp       "Keep temporary files for debugging (optional)"
```

### Example Workflow

1. **Download and analyze in two steps:**
   ```bash
   # Step 1: Download
   yt-dlp -P "~/Downloads/video/" --cookies-from-browser chrome "https://www.youtube.com/watch?v=xxx"
   
   # Step 2: Analyze
   uv run {skill}/scripts/analyze_video.py -v "~/Downloads/video/video.mp4" -p "Describe this video"
   ```

2. **Download and analyze in one command (inline mode):**
   ```bash
   uv run {skill}/scripts/analyze_video.py \
     -v "https://www.youtube.com/watch?v=xxx" \
     -p "用中文总结这个视频" \
     --mode inline
   ```

3. **Quick YouTube analysis with prompt mode (no download):**
   ```bash
   uv run {skill}/scripts/analyze_video.py \
     -v "https://www.youtube.com/watch?v=xxx" \
     -p "What are the main topics?" \
     --mode prompt
   ```

4. **Analyze with proxy:**
   ```bash
   uv run {skill}/scripts/analyze_video.py \
     -v "https://example.com/video.mp4" \
     -p "Analyze the content" \
     --proxy "http://proxy:8080"
   ```

### Error Handling

- **yt-dlp 403 errors:** Script automatically detects and outputs instructions to use `--cookies-from-browser`
- **Video too large:** Auto-compression, auto-trimming handles most cases
- **Timeout issues:** Increase `--exec-timeout` for large files
- **Temporary files:** Use `--keep-temp` to debug compression/trimming issues

---

## Troubleshooting

### YouTube 403 Error
When downloading from YouTube, yt-dlp may return 403 Forbidden. Solution:
```bash
# Use cookies from your browser
yt-dlp --cookies-from-browser chrome --write-sub "YOUTUBE_URL"
```

### Video Still Too Large After Compression
Try:
1. Download a lower resolution version
2. Increase the `--exec-timeout` value
3. Use `--keep-temp` to see which step is slow
4. Manually shorten the source video before analysis

### Memory Issues
If the script runs out of memory:
1. Close other applications
2. Increase `--exec-timeout` 
3. Ensure sufficient disk space for temporary files

### Proxy Issues
If downloads fail through proxy:
1. Test the proxy: `curl -x http://proxy:port https://www.example.com`
2. Ensure proxy URL is correct format: `http://host:port`
3. Try without proxy first to verify the source URL works
