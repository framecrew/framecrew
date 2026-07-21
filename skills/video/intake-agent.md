# Intake Agent

**Role:** Analyze the raw footage and build the job brief that every downstream agent reads.

## Process

1. Parse `event.txt` into a structured object.
2. Scan the folder for all video files — count clips and compute total duration with FFmpeg (`ffprobe`).
3. Detect the log/color profile from footage metadata (e.g. S-Log2/S-Log3); flag as `unknown` if not detectable.
4. Record resolution, frame rate, and codec per clip.
5. Create 1/4-resolution proxies: `ffmpeg -i input.mp4 -vf scale=iw/4:ih/4 proxy/input_proxy.mp4`.
6. Build `job_brief.json` with: `job_id, project_name, event_type, event_date, location, subjects, footage_path, clip_count, total_duration, log_profile, resolution, fps, codec, style_params, target_length, output_format, proxy_path`.
7. Save `job_brief.json` to the project root and set the Kanban card to `INTAKE`.

## Rules

- Never modify files in `raw/`.
- `style_params` come from the preset the Editor Manager passed in (from `config/framecrew.yaml`).
