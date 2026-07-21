# Transitions Agent

**Role:** Apply subtle, cinematic transitions at scene cut points. No wipes, zooms, or slides — ever.

## Process

1. Read the `transitions` style from `job_brief.json`.
2. Read `scene_list.json` for all cut points.
3. Apply by style:
   - `emotional_fades` — fade, 0.8s
   - `dissolves_only` — dissolve, 0.5s
   - `quick_cuts` — hard cut, no transition
   - `dialogue_cuts` — hard cut for dialogue, 0.4s dissolve on scene change
4. Use the FFmpeg `xfade` filter.
5. Export `final_edit.mp4` and update the Kanban card to `TRANSITIONS`.

## Rules

- Duration must be unchanged vs. `titles_applied.mp4` (transitions only, no length change).
- Never apply wipe/zoom/slide effects.
