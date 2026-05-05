import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def log_issue(video_id: str, step: str, message: str):
    log_path = Path(f"output/tmp/{video_id}/issues.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] [{step}] {message}\n")


def download_audio(video_id: str) -> dict:
    out_dir = Path(f"output/tmp/{video_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://www.youtube.com/watch?v={video_id}"
    result = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "m4a",
         "-o", str(out_dir / "audio.%(ext)s"), url],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        msg = f"yt-dlp audio download failed: {result.stderr.strip()[:300]}"
        log_issue(video_id, "download_audio", msg)
        return {"success": False, "error": msg}

    audio_files = list(out_dir.glob("audio.*"))
    if not audio_files:
        msg = "Audio file not found after download"
        log_issue(video_id, "download_audio", msg)
        return {"success": False, "error": msg}

    audio_path = audio_files[0]
    print(f"Audio saved to {audio_path}", file=sys.stderr)
    return {"success": True, "path": str(audio_path)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: download_audio.py <video_id>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(download_audio(sys.argv[1])))
