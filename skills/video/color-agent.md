# Color Agent

**Role:** Convert log footage and apply the brand grade for the job's color mood.

## Process

1. Read `log_profile` and the preset `color_mood` from `job_brief.json`.
2. Log conversion (S-Log3 example): `ffmpeg -i input.mp4 -vf zscale=transfer=linear,tonemap=hable,zscale=transfer=bt709 output.mp4`. For S-Log2 add `primaries=bt2020`.
3. Apply the grade for `color_mood`:
   - `warm_gold` — warm midtones, lifted blacks, desaturated highlights
   - `rich_deep` — deep shadows, saturated golds
   - `high_contrast` — punchy blacks, vivid mids
   - `cinematic_rec709` — clean Rec.709, subtle warmth
4. Generate `<brand>_grade.cube` (brand name from `config/framecrew.yaml`) and save it to `luts/`.
5. Export `color_graded.mp4` and update the Kanban card to `COLOR`.

## Rules

- Color mood names map to `event_presets` in config — do not hardcode a single look.
