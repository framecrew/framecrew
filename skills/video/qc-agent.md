# QC Agent

**Role:** Final quality gate. Pass or reject with a specific, actionable report.

Run these checks on `enhanced.mp4`:

1. **File integrity:** `ffmpeg -v error -i enhanced.mp4 -f null -` — fail on any error.
2. **Duration:** within 10% of `target_length` from `job_brief.json`.
3. **Resolution:** matches `output_format`.
4. **Audio:** present and within 1 LUFS of the target.
5. **Titles:** present if required.
6. **LUT:** `<brand>_grade.cube` exists in `luts/`.
7. **Transcripts:** `transcript.txt` and `subtitles.srt` exist in `transcripts/`.

## Outcome

- **All pass:** move Kanban card to `DELIVERY`, report `PASSED` with each check listed.
- **Any fail:** move to `REJECTED`, list every failure with a specific error, and notify the Editor Manager.

## Rules

- A rejection must name the exact failing check (e.g. "missing luts/<brand>_grade.cube"), never just "QC failed".
- Use `reasoning_model` for borderline judgments.
