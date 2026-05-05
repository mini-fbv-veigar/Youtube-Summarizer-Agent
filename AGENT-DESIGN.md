# YouTube Summarizer Agent — Design Document

> **Purpose**: Reference specification for implementing the YouTube summarizer agent in Claude Code.

---

## 1. Context

### Background & Goals

An agent system that accepts a YouTube video URL, collects audio transcription (via Whisper), subtitles, metadata, and comments, then produces a well-structured Markdown summary document. Designed to run locally on any machine with a compatible GPU.

### Input / Output

| Item | Description |
|------|-------------|
| **Input** | `/input/<video_title>.txt` — one YouTube URL per file |
| **Output** | `/output/<video_title>.md` — structured Markdown summary |
| **Intermediates** | `/output/tmp/<video_id>/` — transcript, metadata JSON, comments JSON |

### Constraints

- If subtitles are unavailable, fall back to Whisper transcription; prefer subtitles when available for speed
- Local Whisper transcription using GPU acceleration (e.g., mlx-whisper on Apple Silicon, faster-whisper on CUDA)
- Runs as a single agent within Claude Code
- Must work without an external YouTube Data API key (yt-dlp based)
- Comments are collected optionally — videos with comments disabled are handled gracefully
- Python package environment managed by `uv`; all scripts invoked via `uv run python`

### Glossary

| Term | Definition |
|------|------------|
| **Transcription** | Audio-to-text output produced by Whisper |
| **Subtitle** | YouTube subtitle track (including auto-generated captions) |
| **Metadata** | Video title, channel name, upload date, view count, like count, description |
| **Issue Log** | Record of errors or anomalies written to `/output/tmp/<id>/issues.log` during processing |

---

## 2. Workflow

### End-to-End Flow

```
[START]
   │
   ▼
① Scan input folder
   │  Script: scan_input.py
   │  → Returns list of files to process
   │
   ▼
② Validate URL
   │  Script: validate_url.py
   │  → On failure: skip + log
   │
   ▼
③ Fetch metadata
   │  Script: fetch_metadata.py (yt-dlp)
   │  → Title, channel, description, view count, duration, etc.
   │
   ▼
④ Check subtitle availability  ◄─── branch point
   │  Based on fetch_metadata.py output
   │
   ├─ Subtitles found ──► ④-A Download subtitles
   │                           Script: download_subtitle.py
   │
   └─ No subtitles   ──► ④-B Download audio + Whisper transcription
                              Scripts: download_audio.py → transcribe.py
   │
   ▼
⑤ Fetch comments (optional)
   │  Script: fetch_comments.py (yt-dlp)
   │  → On failure: skip + log (comments-disabled videos handled normally)
   │  → Up to 50 top-level comments
   │
   ▼
⑥ [LLM] Analyze content & generate summary
   │  Performed directly by the agent
   │  → Synthesizes transcript/subtitles + metadata + comments into a draft summary
   │
   ▼
⑦ [LLM] Self-validate summary quality
   │  Performed directly by the agent
   │  → Checks structural completeness, missing content, section balance
   │  → On failure: rewrite (up to 2 attempts)
   │
   ▼
⑧ Save Markdown file
   │  Script: save_output.py
   │
   ▼
[END] → output/<title>.md created
```

### Branch Conditions

| Branch | Condition | Action |
|--------|-----------|--------|
| Use subtitles | `subtitles` or `automatic_captions` key present in metadata | Subtitle download path |
| Use Whisper | No subtitles available | Audio download → transcription path |
| Skip comments | `comments_disabled` or collection error | Skip + issue log, continue |
| Skip entirely | Invalid URL or private/deleted video | Skip file + issue log |

### LLM vs Script Responsibilities

| Step | Owner | Reason |
|------|-------|--------|
| File scan, URL parsing | Script | Deterministic |
| Metadata / subtitle / comment collection | Script (yt-dlp) | External API calls |
| Audio download | Script (yt-dlp) | File I/O |
| Whisper transcription | Script (Whisper) | Model inference, repeatable |
| Content analysis & summary | **LLM (agent)** | Contextual understanding, insight generation, natural language |
| Summary quality validation | **LLM (agent)** | Qualitative judgment |
| File save | Script | File I/O |

### Success Criteria & Failure Handling

| Step | Success Criteria | Validation | On Failure |
|------|-----------------|------------|------------|
| ② URL validation | youtube.com or youtu.be domain, video ID parseable | Regex | Skip + issue log |
| ③ Metadata fetch | Title, channel name, duration fields present | Schema check | Auto-retry once → agent best-effort + issue log |
| ④-A/B Transcript/subtitle | Text length > 100 characters | Rule-based | Auto-retry once → agent best-effort + issue log |
| ⑤ Comment fetch | Attempt completed (0 results acceptable) | Rule-based | Skip + issue log |
| ⑥ Summary generation | All 4 required sections present, minimum length met | LLM self-check | Rewrite up to 2× → agent best-effort completion + issue log |
| ⑦ Quality validation | No missing content, timestamps correctly formatted | LLM self-check | Rewrite up to 2× |

---

## 3. Output Document Structure

Each generated Markdown file contains four sections:

```markdown
# [Video Title]

> Channel | Upload date | View count | Duration

---

## 📖 Overview & Context
<!-- Topic, background, and purpose of the video -->
<!-- Intended audience and assumed prior knowledge -->

## 💡 Key Content Summary
<!-- Section-by-section summary focused on readability -->
<!-- Important concepts, arguments, and explanations in paragraph form -->

## 🔍 Insights & Critical Perspective
<!-- Agent-derived implications and takeaways -->
<!-- Strength of evidence, limitations, potential counterarguments -->
<!-- Comparison with other viewpoints where applicable -->

## ⏱️ Timestamp Index
<!-- Key segments with timestamps -->
<!-- Format: [MM:SS] Description -->

---
*Generated: YYYY-MM-DD HH:MM | Transcription method: Whisper / Subtitle | Issues: <none or brief note>*
```

---

## 4. Implementation Spec

### Folder Structure

```
/youtube-summarizer
  ├── CLAUDE.md                          # Main agent instructions
  ├── main.py                            # Convenience CLI entry point (single URL or batch)
  ├── pyproject.toml                     # uv project config and dependencies
  ├── .venv/                             # Virtual environment managed by uv (git-ignored)
  ├── /.claude
  │   └── /skills
  │       ├── /media-fetcher             # yt-dlp based data collection
  │       │   ├── SKILL.md
  │       │   └── /scripts
  │       │       ├── scan_input.py      # Scan input folder
  │       │       ├── validate_url.py    # Validate URL format
  │       │       ├── fetch_metadata.py  # Fetch metadata + check subtitle availability
  │       │       ├── download_subtitle.py
  │       │       ├── download_audio.py
  │       │       └── fetch_comments.py
  │       ├── /transcriber               # Whisper transcription
  │       │   ├── SKILL.md
  │       │   └── /scripts
  │       │       └── transcribe.py      # Whisper inference
  │       └── /output-writer             # Save result files
  │           ├── SKILL.md
  │           └── /scripts
  │               └── save_output.py
  ├── /input                             # Input .txt files
  ├── /output                            # Generated .md files
  │   └── /tmp                           # Intermediates (transcripts, metadata, etc.)
  └── /docs
      └── setup-guide.md                 # Environment setup guide
```

### CLAUDE.md Key Sections

- Agent role definition and purpose
- Workflow steps and which skill to invoke at each step
- **Script execution rule: all Python scripts called via `uv run python <script>`** (no manual venv activation needed)
- Subtitle language parameter default and how to override (`lang` argument, default `"en,ko"`)
- Output document template
- LLM self-validation checklist
- Error handling policy: agent acts autonomously, records issues to `issues.log`, notes issues in the final document's metadata line
- Retry policy (1 automatic retry)

### Agent Architecture

**Single-agent** design.

- The workflow is linear and each step is not independently complex
- Synthesizing transcript, metadata, and comments within a single context yields better summary quality
- Splitting into sub-agents adds context-passing overhead that outweighs any benefit

### Skills

| Skill | Role | Trigger |
|-------|------|---------|
| `media-fetcher` | Collect metadata, subtitles, audio, and comments via yt-dlp | Steps ②–⑤ |
| `transcriber` | Transcribe audio to text via Whisper | Step ④-B (no subtitles available) |
| `output-writer` | Save completed Markdown to `/output`, clean up temp files | Step ⑧ after summary is finalized |

### Script Specifications

| Script | Input | Output |
|--------|-------|--------|
| `scan_input.py` | `/input` folder path | `{filename: URL}` dict of files to process |
| `validate_url.py` | YouTube URL string | `{valid: bool, video_id: str}` |
| `fetch_metadata.py` | `video_id` | `/output/tmp/<id>/metadata.json` |
| `download_subtitle.py` | `video_id`, `lang` (default: `"en,ko"`) | `/output/tmp/<id>/subtitle.txt` — saved as `[MM:SS] text` format |
| `download_audio.py` | `video_id` | `/output/tmp/<id>/audio.m4a` |
| `transcribe.py` | audio file path | `/output/tmp/<id>/transcript.txt` — Whisper segments saved as `[MM:SS] text` format |
| `fetch_comments.py` | `video_id` | `/output/tmp/<id>/comments.json` |
| `save_output.py` | Markdown text, title | `/output/<title>.md` |

### Error Handling & Issue Log Policy

The agent resolves all errors autonomously using best judgment — it never requests human intervention. When an error or exception occurs:

1. **Log the issue**: Write to `/output/tmp/<video_id>/issues.log` using the format: `[YYYY-MM-DD HH:MM] [step] Error description and action taken`
2. **Continue processing**: Skippable steps (comments, invalid URL, etc.) are bypassed and the workflow continues
3. **Retry**: Network/I/O errors trigger one automatic retry; on repeated failure the agent determines the best alternative
4. **Surface in output**: The final Markdown metadata line briefly notes any significant issues (e.g., `Comments unavailable`, `No subtitles — Whisper transcription used`)

### Data Flow

- Between scripts: file-based (`/output/tmp/<video_id>/`)
- Script → Agent: agent reads files from the path returned by scripts
- Agent → Script: agent passes Markdown text inline to `save_output.py`

### Intermediate File Formats

| File | Format | Notes |
|------|--------|-------|
| `metadata.json` | JSON | yt-dlp standard output format |
| `transcript.txt` | Text | `[MM:SS] utterance` per line |
| `subtitle.txt` | Text | SRT converted to `[MM:SS] text` format (same as transcript.txt) |
| `comments.json` | JSON | `{author, text, likes, timestamp}` array |
| `issues.log` | Text | `[timestamp] [step] message` per line |
| `<title>.md` | Markdown | Final output |

---

*Design document version: v1.0 | Created: 2026-05*
