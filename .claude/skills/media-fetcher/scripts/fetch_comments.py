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


def fetch_comments(video_id: str, max_comments: int = 50) -> dict:
    out_dir = Path(f"output/tmp/{video_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://www.youtube.com/watch?v={video_id}"
    result = subprocess.run(
        ["yt-dlp", "--write-comments",
         "--extractor-args", f"youtube:max_comments={max_comments}",
         "--dump-json", "--skip-download", url],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        msg = f"Comment fetch failed: {result.stderr.strip()[:200]}"
        log_issue(video_id, "fetch_comments", msg)
        return {"success": False, "error": msg, "count": 0}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        msg = f"Failed to parse yt-dlp output: {e}"
        log_issue(video_id, "fetch_comments", msg)
        return {"success": False, "error": msg, "count": 0}

    comments = [
        {
            "author": c.get("author", ""),
            "text": c.get("text", ""),
            "likes": c.get("like_count", 0),
            "timestamp": c.get("timestamp", ""),
        }
        for c in data.get("comments", [])[:max_comments]
    ]

    out_path = out_dir / "comments.json"
    out_path.write_text(json.dumps(comments, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(comments)} comments saved to {out_path}", file=sys.stderr)
    return {"success": True, "path": str(out_path), "count": len(comments)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_comments.py <video_id> [max_comments]", file=sys.stderr)
        sys.exit(1)
    video_id = sys.argv[1]
    max_comments = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    print(json.dumps(fetch_comments(video_id, max_comments)))
