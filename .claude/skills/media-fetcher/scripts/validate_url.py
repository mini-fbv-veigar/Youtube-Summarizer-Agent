import sys
import json
import re

YOUTUBE_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?(?:.*&)?v=|youtu\.be/)([A-Za-z0-9_-]{11})"
)


def validate_url(url: str) -> dict:
    m = YOUTUBE_RE.search(url)
    if m:
        return {"valid": True, "video_id": m.group(1)}
    return {"valid": False, "video_id": ""}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"valid": False, "video_id": ""}))
        sys.exit(1)
    print(json.dumps(validate_url(sys.argv[1])))
