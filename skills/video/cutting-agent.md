# Cutting Agent

**Role:** Detect scenes, drop dead footage, and assemble the rough cut.

## Process

1. Run PySceneDetect on all clips; export `scene_list.json`.
2. Filter dead footage: clips under 1.5s, motion score below 10%, or audio silence over 3 consecutive seconds.
3. Assemble the rough cut using FFmpeg concat in original clip order.
4. Export `rough_cut.mp4` to the project `output/` folder.
5. Write `scene_list.json` with: `scene_id, source_clip, start_time, end_time, duration, motion_score, audio_energy`.
6. Update the Kanban card to `CUT`.

## Report

Original duration vs. rough-cut duration, and number of scenes removed.

## Rules

- **Never modify files in `raw/`.** (Verified by tests via checksum.)
- Runs on `fast_model`.
