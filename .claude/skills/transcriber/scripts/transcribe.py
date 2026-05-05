import sys
import json
from pathlib import Path
from datetime import datetime


def log_issue(video_id: str, step: str, message: str):
    log_path = Path(f"output/tmp/{video_id}/issues.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] [{step}] {message}\n")


def segments_to_text(segments) -> str:
    lines = []
    for seg in segments:
        start = seg.get("start", 0) if isinstance(seg, dict) else seg.start
        text = (seg.get("text", "") if isinstance(seg, dict) else seg.text).strip()
        if not text:
            continue
        mm, ss = divmod(int(start), 60)
        lines.append(f"[{mm:02d}:{ss:02d}] {text}")
    return "\n".join(lines)


def transcribe(audio_path: str) -> dict:
    audio = Path(audio_path)
    if not audio.exists():
        return {"success": False, "error": f"Audio file not found: {audio_path}"}

    video_id = audio.parent.name
    out_path = audio.parent / "transcript.txt"
    transcript_text = None
    backend_used = None

    try:
        import mlx_whisper
        result = mlx_whisper.transcribe(
            str(audio),
            path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
            word_timestamps=False,
            language=None,
        )
        transcript_text = segments_to_text(result.get("segments", []))
        backend_used = "mlx-whisper (whisper-large-v3-turbo)"
    except ImportError:
        pass
    except Exception as e:
        log_issue(video_id, "transcribe", f"mlx-whisper failed: {e} — trying faster-whisper")

    if transcript_text is None:
        try:
            from faster_whisper import WhisperModel
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            model = WhisperModel("large-v3", device=device, compute_type=compute_type)
            segments, _ = model.transcribe(str(audio), word_timestamps=False)
            transcript_text = segments_to_text(list(segments))
            backend_used = f"faster-whisper large-v3 ({device})"
        except ImportError:
            return {"success": False, "error": "No Whisper backend available. Install mlx-whisper or faster-whisper."}
        except Exception as e:
            log_issue(video_id, "transcribe", f"faster-whisper failed: {e}")
            return {"success": False, "error": str(e)}

    if len(transcript_text) < 100:
        msg = f"Transcript too short ({len(transcript_text)} chars)"
        log_issue(video_id, "transcribe", msg)
        return {"success": False, "error": msg}

    out_path.write_text(transcript_text, encoding="utf-8")
    print(f"Transcript saved to {out_path} (backend: {backend_used})", file=sys.stderr)
    return {"success": True, "path": str(out_path), "backend": backend_used}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file_path>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(transcribe(sys.argv[1])))
