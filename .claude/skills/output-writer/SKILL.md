# Skill: output-writer

Saves the completed Markdown summary to the output folder.

## Script

### save_output.py
```bash
# From a file
uv run python .claude/skills/output-writer/scripts/save_output.py "<title>" "<markdown_file_path>"

# From stdin
echo "<markdown>" | uv run python .claude/skills/output-writer/scripts/save_output.py "<title>" -
```

Output path: `output/<sanitized_title>.md`

## Notes
- Title is sanitized for use as a filename (special characters replaced with `_`)
- Returns JSON: `{"success": true, "path": "output/<title>.md"}`
