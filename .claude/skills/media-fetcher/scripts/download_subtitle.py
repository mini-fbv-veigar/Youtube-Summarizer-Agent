import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime


def log_issue(video_id: str, step: str, message: str):
    log_path = Path(f"output/tmp/{video_id}/issues.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] [{step}] {message}\n")


def srt_to_timestamped(srt_content: str) -> str:
    lines = []
    for block in re.split(r"\n\n+", srt_content.strip()):
        parts = block.strip().split("\n")
        if len(parts) < 3:
            continue
        ts_match = re.match(r"(\d+):(\d+):(\d+)[,.]", parts[1])
        if not ts_match:
            continue
        total_s = int(ts_match.group(1)) * 3600 + int(ts_match.group(2)) * 60 + int(ts_match.group(3))
        mm, ss = divmod(total_s, 60)
        text = re.sub(r"<[^>]+>", "", " ".join(parts[2:])).strip()
        if text:
            lines.append(f"[{mm:02d}:{ss:02d}] {text}")
    return "\n".join(lines)


def download_subtitle(video_id: str, lang: str = "en,ko") -> dict:
    out_dir = Path(f"output/tmp/{video_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://www.youtube.com/watch?v={video_id}"
    subprocess.run(
        ["yt-dlp", "--write-subs", "--write-auto-subs",
         "--sub-lang", lang, "--sub-format", "srt",
         "--skip-download", "-o", str(out_dir / video_id), url],
        capture_output=True, text=True,
    )

    srt_files = sorted(out_dir.glob("*.srt"))
    if not srt_files:
        msg = f"No subtitle file found (lang={lang})"
        log_issue(video_id, "download_subtitle", msg)
        return {"success": False, "error": msg}

    converted = srt_to_timestamped(srt_files[0].read_text(encoding="utf-8"))
    for f in srt_files:
        f.unlink()

    if len(converted) < 100:
        msg = f"Subtitle too short after conversion ({len(converted)} chars)"
        log_issue(video_id, "download_subtitle", msg)
        return {"success": False, "error": msg}

    out_path = out_dir / "subtitle.txt"
    out_path.write_text(converted, encoding="utf-8")
    print(f"Subtitle saved to {out_path}", file=sys.stderr)
    return {"success": True, "path": str(out_path)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: download_subtitle.py <video_id> [lang]", file=sys.stderr)
        sys.exit(1)
    video_id = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "en,ko"
    print(json.dumps(download_subtitle(video_id, lang)))
