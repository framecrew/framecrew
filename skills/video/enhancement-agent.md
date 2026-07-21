# Enhancement Agent

**Role:** Denoise low-light video and upscale/clean any still images.

## Process

1. Run FFmpeg `hqdn3d` noise reduction on `audio_processed.mp4` for low-light footage (detect by average luminance).
2. Scan the project folder for still images (`.jpg`, `.jpeg`, `.png`, `.cr3`, `.arw`).
3. For each still below 4K: upscale with Real-ESRGAN.
4. For stills flagged for background removal in `job_brief.json`: run `rembg`.
5. Save enhanced stills to `stills/`.
6. Export `enhanced.mp4` and update the Kanban card to `ENHANCE`.

## Report

Stills processed, resolution before/after, and video noise reduction applied.

## Rules

- Scan for image extensions case-insensitively.
