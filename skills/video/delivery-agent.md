# Delivery Agent

**Role:** Package the final deliverables and build the DaVinci Resolve project. Runs only after QC passes.

## Process

1. Copy `enhanced.mp4` to `output/` as `<ProjectName>_final.mp4`.
2. Build a DaVinci Resolve project via the Resolve scripting API (requires **Resolve Studio** open):
   - create a project named `<ProjectName>`
   - create bins: `Raw Footage`, `Proxy`, `Output`
   - import proxies, the final MP4, and the `.cube` LUT
   - create a timeline `<ProjectName>_Master`, place the final MP4 on it
   - save the project to `davinci/` as `<ProjectName>.drp`
3. Write `pipeline_log.txt` summarizing every agent action, output file, and timing.
4. Notify (Telegram if configured): `Job complete: <ProjectName> | <event_type> | <clip_count> clips → <duration> | Output: <path> | DaVinci: <path>`.

## Rules

- In test mode (`FRAMECREW_TEST_MODE=1`), the Resolve and notification steps are mocked (see `tests/mocks/`).
