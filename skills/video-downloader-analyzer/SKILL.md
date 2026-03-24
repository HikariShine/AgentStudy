---
name: video-downloader-analyzer
description: Video Downloader + Gemini Analyzer — yt-dlp powered downloading for YouTube, Bilibili, and 1000+ sites; Gemini-powered analysis with zero-download mode for YouTube. Proxy support and intelligent compression included.
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

Combined skill for downloading videos (yt-dlp) and analyzing them with Gemini. Supports YouTube, Bilibili, Twitter, and thousands of other sites with proxy support and automatic compression.

## Download Videos

Verify dependencies:
```bash
which yt-dlp || uv tool install yt-dlp[default]
which ffmpeg || brew install ffmpeg
```

### Common Commands

```bash
# YouTube (with cookies)
yt-dlp -P "~/Downloads/video" --cookies-from-browser chrome "YOUTUBE_URL"

# Basic (any site)
yt-dlp -P "~/Downloads/video" "VIDEO_URL"

# 360p (smaller file)
yt-dlp -P "~/Downloads/video" -f "bestvideo[height<=360][vcodec^=hevc]+bestaudio/best[height<=360]" "URL"

# MP3 audio only
yt-dlp -P "~/Downloads/video" -x --audio-format mp3 "URL"

# With subtitles
yt-dlp -P "~/Downloads/video" --write-subs "URL"

# List available formats
yt-dlp -F "URL"
```

---

## Analyze Videos

Set environment: `GEMINI_API_KEY` (required), optionally `GEMINI_BASE_URL` (proxy)

### Smart File Management

The script **preserves all processed files by default** in the temp directory:

- **Downloaded videos**: Original file automatically saved in temp directory
- **final_<filename>**: Processed file optimized for Gemini (compressed/resized if needed)
- Temp directory shown in output for easy reference

**Follow-up analysis workflow:**
```bash
# First analysis
uv run {skill}/scripts/analyze_video.py -v "https://youtube.com/watch?v=xxx" -p "Summarize"
# Output: 📂 临时工作目录: /tmp/video_analysis_abc123

# Reuse the processed file for follow-up questions
uv run {skill}/scripts/analyze_video.py -v "/tmp/video_analysis_abc123/final_video.mp4" -p "Tell me more about..."
```

### Compression Strategy

Auto-adjusts based on file size:

| Size | Action | FPS |
|------|--------|-----|
| < 14 MB | Skip | - |
| 14-32 MB | Compress | 6 |
| 32-42 MB | Compress | 1 |
| > 42 MB | Trim + Compress | 1 |

### Analysis Examples

**Local video:**
```bash
uv run {skill}/scripts/analyze_video.py -v "video.mp4" -p "Describe the video"
```

**YouTube - URL mode (Google native，Preferred):**
```bash
uv run {skill}/scripts/analyze_video.py -v "https://www.youtube.com/watch?v=xxx" -p "Describe" --mode url
```

**YouTube - Inline mode (download + analyze, most reliable):**
```bash
uv run {skill}/scripts/analyze_video.py -v "https://www.youtube.com/watch?v=xxx" -p "Describe" --mode inline
```

**Mode Selection Strategy for YouTube:**
- **Preferred (url mode)**: Faster, doesn't require download. Use as first choice with `--mode url`
- **Fallback (inline mode)**: If url mode fails, fall back to `--mode inline` which downloads and analyzes locally
- **Recommendation**: url mode is highly preferred to minimize bandwidth and processing time

**Non-YouTube URL (auto inline mode):**
```bash
uv run {skill}/scripts/analyze_video.py -v "https://example.com/video.mp4" -p "Analyze this"
```

**With proxy:**
```bash
uv run {skill}/scripts/analyze_video.py -v "URL" -p "Describe" --proxy "http://proxy:8080"
```

### Parameters

```
--video/-v          Path or URL (required)
--prompt/-p         Prompt for model (default: Summarize the video.)
--model/-m          Model name (default: gemini-3-flash-preview)
--mode              YouTube mode: url/inline (default: url)
--proxy             HTTP proxy URL (optional)
--cookies-browser   Browser for cookies: chrome/firefox/safari/etc (default: chrome)
--exec-timeout      Total execution timeout in seconds (default: 300)
--no-keep-temp      Delete temp files after analysis (optional)
```

### Quick Examples

```bash
# Download and analyze
yt-dlp -P "~/Downloads" --cookies-from-browser chrome "YOUTUBE_URL"
uv run {skill}/scripts/analyze_video.py -v "~/Downloads/video.mp4" -p "Summary"

# One-command YouTube analysis
uv run {skill}/scripts/analyze_video.py -v "YOUTUBE_URL" -p "Analyze this video" --mode inline

# Analysis video and delete file when complete
uv run {skill}/scripts/analyze_video.py -v "/tmp/video_analysis_xxx/final_video.mp4" -p "Focus on..." --no-keep-temp
```
---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| YouTube 403 Error | Use `--cookies-from-browser chrome` |
| Video still > 14MB after compression | Trim/cut the file proportionally by time to fit the target size |
| Memory issues | Close other apps, check disk space |
| Proxy connection fails | Test proxy: `curl -x http://proxy:port https://example.com` |
