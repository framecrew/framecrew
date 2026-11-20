# FrameCrew

FrameCrew is designed to take footage and an event brief, ask for approval, and coordinate an edit through Hermes. The original workflow includes creative editing, quality checks, and delivery to MP4 and DaVinci Resolve. To set up the Hermes workflow on macOS, run `bash install.sh` and follow the [Hermes kickoff instructions](KICKOFF.md). The full workflow still needs an end-to-end acceptance run.

## Start a Hermes job without opening chat

On Windows, install the FrameCrew skills and use the Hermes launcher that can reach your gateway. Each project needs an `event.txt` and footage in `raw/`.

```powershell
python hermes_job.py path/to/project prepare
python hermes_job.py path/to/project approve --hermes path/to/hermes.exe
python hermes_job.py path/to/project status
```

`prepare` runs the Windows Watcher checks. `approve` is the operator's explicit approval of that exact footage and brief. The runner invokes the original Hermes Editor Manager and checks for a QC report, a decodable MP4, and a Resolve archive. Use a fresh folder to retry a failed run.

## Standalone MP4 utility

This utility turns an ordered list of clips into a single 720p MP4. It needs Python 3.11 or newer and FFmpeg 8 or newer with `ffprobe` and `libx264`. On macOS with Homebrew, run `bash install.sh --media-only`. On Windows, install the tools and put them on your PATH. No API key is needed.

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
