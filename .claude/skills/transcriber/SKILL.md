# Skill: transcriber

Transcribes a local audio file to text using a local Whisper backend. Outputs `[MM:SS] text` format.

## Script

### transcribe.py
```bash
uv run python .claude/skills/transcriber/scripts/transcribe.py <audio_file_path>
# → output/tmp/<video_id>/transcript.txt
```

## Backend Selection
Automatically selects the available backend:
1. **mlx-whisper** (Apple Silicon) — tried first
2. **faster-whisper** (CUDA / CPU) — fallback

Install the appropriate backend for your hardware:
```bash
uv add mlx-whisper        # Apple Silicon
uv add faster-whisper     # CUDA / CPU
```

## Output Format
```
[00:00] First segment text
[00:15] Second segment text
...
```
Same format as `subtitle.txt` — the agent reads both files identically.

## Notes
- On first run, mlx-whisper downloads the model (~1.6 GB) from Hugging Face automatically
- Logs failures to `output/tmp/<video_id>/issues.log`
