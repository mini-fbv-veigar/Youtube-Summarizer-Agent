# Skill: media-fetcher

Collects all external data for a YouTube video using yt-dlp: metadata, subtitles, audio, and comments.

## Scripts

### scan_input.py
Scans the input folder and returns a dict of `{title: url}` for all `.txt` files.
```bash
uv run python .claude/skills/media-fetcher/scripts/scan_input.py [folder_path]
```

### validate_url.py
Validates a YouTube URL and extracts the video ID.
```bash
uv run python .claude/skills/media-fetcher/scripts/validate_url.py "<url>"
# → {"valid": true, "video_id": "abc123"}
```

### fetch_metadata.py
Fetches full video metadata via yt-dlp and saves to `output/tmp/<id>/metadata.json`.
```bash
uv run python .claude/skills/media-fetcher/scripts/fetch_metadata.py <video_id>
```

### download_subtitle.py
Downloads subtitles (preferred over audio for speed). Converts SRT to `[MM:SS] text` format.
```bash
uv run python .claude/skills/media-fetcher/scripts/download_subtitle.py <video_id> [lang]
# lang default: "en,ko"
# → output/tmp/<id>/subtitle.txt
```

### download_audio.py
Downloads audio as m4a. Use only when subtitles are unavailable.
```bash
uv run python .claude/skills/media-fetcher/scripts/download_audio.py <video_id>
# → output/tmp/<id>/audio.m4a
```

### fetch_comments.py
Fetches up to 50 top-level comments.
```bash
uv run python .claude/skills/media-fetcher/scripts/fetch_comments.py <video_id> [max_comments]
# → output/tmp/<id>/comments.json
```

## Notes
- All scripts write errors to `output/tmp/<video_id>/issues.log`
- Comment fetch failure is non-fatal — skip and continue
