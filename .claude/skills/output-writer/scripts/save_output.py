import sys
import json
from pathlib import Path


def save_output(markdown: str, title: str) -> dict:
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()
    out_path = out_dir / f"{safe_title}.md"
    out_path.write_text(markdown, encoding="utf-8")

    print(f"Output saved to {out_path}", file=sys.stderr)
    return {"success": True, "path": str(out_path)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: save_output.py <title> <markdown_path_or_->", file=sys.stderr)
        print("  Use '-' as second arg to read from stdin", file=sys.stderr)
        sys.exit(1)

    title = sys.argv[1]
    source = sys.argv[2]
    markdown = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")

    print(json.dumps(save_output(markdown, title)))
