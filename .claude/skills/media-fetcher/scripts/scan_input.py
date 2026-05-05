import sys
import json
from pathlib import Path


def scan_input(folder: str = "./input") -> dict:
    result = {}
    input_path = Path(folder)
    if not input_path.exists():
        return result
    for f in sorted(input_path.glob("*.txt")):
        url = f.read_text(encoding="utf-8").strip()
        if url:
            result[f.stem] = url
    return result


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./input"
    print(json.dumps(scan_input(folder), ensure_ascii=False, indent=2))
