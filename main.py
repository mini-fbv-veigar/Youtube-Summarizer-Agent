"""
Convenience CLI entry point for the YouTube Summarizer Agent.

This script is a helper for humans. The actual summarization is performed
by the Claude Code agent following CLAUDE.md.

Usage:
  uv run python main.py                        # Print usage
  uv run python main.py <youtube_url> [title]  # Write URL to input/<title>.txt
  uv run python main.py --list                 # List pending input files
"""

import sys
import re
from pathlib import Path


def write_input(url: str, title: str):
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    target = input_dir / f"{title}.txt"
    target.write_text(url.strip() + "\n", encoding="utf-8")
    print(f"Created: {target}")
    print("Run the agent with: claude")


def list_inputs():
    input_dir = Path("input")
    files = sorted(input_dir.glob("*.txt")) if input_dir.exists() else []
    if not files:
        print("No input files found in input/")
        return
    for f in files:
        url = f.read_text(encoding="utf-8").strip()
        print(f"  {f.name}: {url}")


def title_from_url(url: str) -> str:
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else "video"


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__.strip())
        return

    if args[0] == "--list":
        list_inputs()
        return

    url = args[0]
    if not url.startswith("http"):
        print(f"Error: expected a YouTube URL, got: {url}", file=sys.stderr)
        sys.exit(1)

    title = args[1] if len(args) > 1 else title_from_url(url)
    write_input(url, title)


if __name__ == "__main__":
    main()
