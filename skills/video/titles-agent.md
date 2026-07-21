# Titles Agent

**Role:** Add opening/closing titles and optional lower-thirds, following brand rules.

Brand rules come from `config/framecrew.yaml` (`brand.title_font`, `brand.title_color`, `brand.minimalist`). Default: clean fade in/out, no drop shadow.

## Process

1. Read `Opening_Title`, `Closing_Title`, `Lower_Thirds`, and `subjects` from `job_brief.json`.
2. Opening title: fade in at 1.5s, hold 3s, fade out 0.8s (FFmpeg `drawtext`).
3. If `Lower_Thirds` is enabled: one lower-third per subject at 10% from the bottom, fade in 0.5s, hold 4s, fade out 0.5s.
4. Closing title over the final 4 seconds.
5. Export `titles_applied.mp4` and update the Kanban card to `TITLES`.

## Rules

- Font/color are config-driven. On macOS, use a full font path, e.g. `fontfile=/System/Library/Fonts/Helvetica.ttc`.
