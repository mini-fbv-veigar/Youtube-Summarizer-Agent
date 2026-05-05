## Appendix: Environment Setup Guide

### Prerequisites

yt-dlp and ffmpeg must be installed. If not:

```bash
# macOS
brew install yt-dlp ffmpeg

# Linux (Debian/Ubuntu)
sudo apt install ffmpeg
pip install yt-dlp
```

### uv Installation & Project Init

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Init project
uv init
uv python pin 3.11   # Pin Python 3.11 for Whisper compatibility

# Install dependencies
uv add yt-dlp
```

Install a Whisper backend appropriate for your hardware (see Whisper section below).

`uv add` auto-creates `.venv/` and records dependencies in `pyproject.toml`.

### pyproject.toml Example

```toml
[project]
name = "youtube-summarizer"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "yt-dlp",
    "mlx-whisper",      # Apple Silicon
    # "faster-whisper", # CUDA / CPU alternative
]
```

### Running Scripts

```bash
# No manual venv activation needed — uv resolves the project .venv automatically
uv run python .claude/skills/media-fetcher/scripts/fetch_metadata.py <video_id>
uv run python .claude/skills/transcriber/scripts/transcribe.py <audio_path>
```

### Whisper Backend Selection

Choose the backend that matches your hardware:

#### Apple Silicon (mlx-whisper)

```bash
uv add mlx-whisper
```

```python
import mlx_whisper

result = mlx_whisper.transcribe(
    "audio.m4a",
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
    word_timestamps=True,
    language=None   # None = auto-detect
)
```

**Recommended models (Apple Silicon):**

| Model | Speed | Accuracy | Size |
|-------|-------|----------|------|
| `whisper-large-v3-turbo` | ★★★★ | ★★★★★ | ~1.6 GB |
| `whisper-medium` | ★★★★★ | ★★★★ | ~0.8 GB |
| `whisper-small` | ★★★★★ | ★★★ | ~0.5 GB |

On first run, the model is downloaded automatically from Hugging Face.

#### CUDA / CPU (faster-whisper)

```bash
uv add faster-whisper
```

```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, _ = model.transcribe("audio.m4a", word_timestamps=True)
```

`transcribe.py` should detect available hardware and select the appropriate backend at runtime.

### yt-dlp Key Options

```bash
# Fetch metadata only (no download)
yt-dlp --dump-json --skip-download <URL>

# Download audio only
yt-dlp -x --audio-format m4a -o "output/tmp/%(id)s/audio.%(ext)s" <URL>

# Download subtitles (language priority: en then ko, falls back to auto-generated)
yt-dlp --write-subs --write-auto-subs --sub-lang en,ko --skip-download -o "output/tmp/%(id)s/%(id)s" <URL>

# Fetch comments (top 50, JSON dump)
yt-dlp --write-comments --max-comments 50 --dump-json --skip-download <URL>
```

The `--sub-lang` value mirrors the `lang` argument passed to `download_subtitle.py` (default: `"en,ko"`).

### Recommended .gitignore

```
.venv/
output/tmp/
__pycache__/
*.pyc
```
