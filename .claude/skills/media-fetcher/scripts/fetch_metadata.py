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


def fetch_metadata(video_id: str) -> dict:
    out_dir = Path(f"output/tmp/{video_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://www.youtube.com/watch?v={video_id}"
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--skip-download", url],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        msg = f"yt-dlp failed: {result.stderr.strip()[:300]}"
        log_issue(video_id, "fetch_metadata", msg)
        return {"success": False, "error": msg}

    data = json.loads(result.stdout)
    out_path = out_dir / "metadata.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Metadata saved to {out_path}", file=sys.stderr)
    return {"success": True, "path": str(out_path)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_metadata.py <video_id>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch_metadata(sys.argv[1])))
