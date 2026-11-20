# FrameCrew

FrameCrew turns an ordered list of clips into a single 720p MP4. It runs locally with Python and FFmpeg, records each stage in SQLite, and checks that the video and audio decode before publishing the export.

## Quick start

You need Python 3.11 or newer and FFmpeg 8 or newer with `ffprobe` and `libx264`. On macOS with Homebrew, run `bash install.sh` from the repository root. On Windows, install the tools and put them on your PATH. No API key is needed.

```sh
python3 framecrew.py run --job demo-job "clip one.mov" "clip two.mp4"
python3 framecrew.py status --job demo-job
```

On Windows, use `python` in place of `python3`. The clips play in the order supplied. Open `demo-job/finished.mp4` when delivery completes. Use a new job folder for a different clip list or if the source files have changed.

## Stage contracts

| Stage | Reads | Writes |
| --- | --- | --- |
| Normalize | Ordered, SHA-256-pinned source clips | One 1280×720 H.264 clip per input, with aspect-preserving padding, video normalized to 30 fps and stereo 48 kHz AAC. Silent sources get an audio track. |
| Assemble | Normalized clips | A single stream-copied MP4 in the supplied clip order. |
| QC | Assembled MP4 and normalized clips | A JSON report with the duration and media hash after stream checks, a duration comparison and a full audio/video decode. |
| Deliver | QC-approved MP4 | `finished.mp4`, published through an atomic rename in the job folder. |

The job database and intermediate files live in `<job>/.framecrew/`. A second runner for the same job gets a busy error. Keep the job on a local disk and leave its source paths and contents in place until delivery finishes.

To resume, use the same job folder with no clip arguments:

```sh
python3 framecrew.py run --job demo-job
```

FrameCrew reuses stages whose saved artifact hashes still match. It restarts an interrupted stage, rebuilds from the first missing or changed artifact, and retries assembly after a QC failure. The status command shows the recorded stage and its error. Keep the folder if you need the job records or want to resume.

## Tests and scope

```sh
python3 -m unittest discover -s tests -v
```

The suite generates landscape and portrait fixtures with different frame rates and audio layouts. It runs the workflow with real FFmpeg and checks clip order, duration, output reuse, QC failure recovery, interruption recovery and writer exclusion. The GitHub Actions workflow runs the suite on macOS.

This release scope is a straight cut with audio and MP4 delivery. The Hermes skills, watcher and Telegram confirmation are experimental design material. DaVinci Resolve export, creative editing features, and production-footage acceptance are outside the current MVP. See the [original Hermes audit](docs/TECHNICAL_OVERVIEW.md) and [experimental kickoff instructions](KICKOFF.md).
