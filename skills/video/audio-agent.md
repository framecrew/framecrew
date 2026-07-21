# Audio Agent

**Role:** Transcribe, clean, and normalize audio to the delivery spec.

Loudness targets come from `config/framecrew.yaml` (`audio.loudness`).

## Process

1. Run Whisper locally on `final_edit.mp4` — export `transcript.txt` and `subtitles.srt` to `transcripts/`.
2. Run FFmpeg `afftdn` for noise reduction.
3. Normalize to the `Audio_Spec`:
   - `web_delivery` → -14 LUFS
   - `broadcast` → -23 LUFS
   - e.g. `ffmpeg -i input.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 output.mp4`
4. If music is specified in `job_brief.json`, mix at -18 dB under the main audio.
5. Export `audio_processed.mp4` and update the Kanban card to `AUDIO`.

## Report

Transcript word count, original vs. normalized loudness, and noise reduction applied.
