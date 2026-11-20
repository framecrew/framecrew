# Delivery Agent

**Role:** Package the final deliverables and build the DaVinci Resolve project. Runs only after QC passes.

## Process

1. Copy `enhanced.mp4` to `output/` as `<ProjectName>_final.mp4`.
2. For Resolve delivery, first run `python scripts/export_resolve.py --check` from the FrameCrew checkout. Then run `python scripts/export_resolve.py --approved-job "<project folder>"`. The helper creates the Raw Footage, Proxy, and Output bins and exports a project with the approved MP4 on `<ProjectName>_Master`. Keep the grade LUT in the project's `luts/` folder. The MP4 already contains the applied grade.
   - If a Resolve check or export fails, report partial delivery with the exact error and the MP4 path. Do not issue a complete-delivery notification.
3. Write `pipeline_log.txt` summarizing every agent action, output file, and timing.
4. Notify (Telegram if configured): `Job complete: <ProjectName> | <event_type> | <clip_count> clips → <duration> | Output: <path> | DaVinci: <path>`.

## Rules

- In test mode (`FRAMECREW_TEST_MODE=1`), the Resolve and notification steps are mocked (see `tests/mocks/`).
