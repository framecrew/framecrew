# FrameCrew

FrameCrew uses Hermes to coordinate a video edit from footage and an `event.txt` brief. The workflow covers intake, proxies, rough cut, trim, color, titles, transitions, audio, quality checks, and delivery.

## Install

1. Open the [FrameCrew repository](https://github.com/framecrew/framecrew), choose **Code → Download ZIP**, and extract it to a folder you can keep.
2. On **Windows**, double-click **Install FrameCrew.cmd**. On **macOS**, double-click **Install FrameCrew.command**, or run `bash install.sh` from the extracted folder.
3. Wait for **Setup checks passed**. Complete any Windows, macOS, or vendor prompts that appear during installation.

The installer reuses compatible tools it finds and installs missing ones. It checks Hermes, Python, FFmpeg 8+, FFprobe, ImageMagick, PySceneDetect, Whisper, and Watchdog. Python media packages go in the repository’s `.venv`. Windows uses WinGet when system packages are missing. macOS uses Homebrew. Both use the [official Nous installer](https://hermes-agent.nousresearch.com/docs/getting-started/installation) if Hermes is missing.

Setup registers the 13 FrameCrew skills in Hermes and preserves existing configuration, templates, and local skill edits. If a Windows machine needs WinGet, it must have Microsoft App Installer. Missing packages require internet access.

## Set up a project

1. Open **Run FrameCrew.cmd** on Windows or run `bash scripts/run_hermes.sh` on macOS. Configure your model provider in Hermes if needed.
2. Save the footage in `.framecrew-work/Projects/<project>/raw/`.
3. Copy an appropriate brief from `.framecrew-work/Templates/`, fill it out, and place it in the project folder as `event.txt`. Add the brief after the footage has finished copying.
4. Follow the [Hermes kickoff](KICKOFF.md). Check the project name and clip count before approving the edit.

Change the working folders, title styling, event presets, and audio targets in `config/framecrew.yaml`. The installer leaves this file in place when you rerun setup.

## Optional integrations

- **Resolve Studio** is used for external project export. Install and activate Studio through Blackmagic if you need that delivery path.
- **Telegram** can handle approval messages once you configure it. It is off in a fresh FrameCrew config.
- **AI still-image enhancement** uses rembg and Real-ESRGAN. To add them, run `"Install FrameCrew.cmd" --with-stills` in Command Prompt on Windows or `bash install.sh --with-stills` on macOS.

## Check setup

Rerun the installer if a prerequisite is missing. It stops and reports the step that failed. Run the [kickoff](KICKOFF.md) on one project and verify the output files before relying on unattended jobs. Installation checks cover dependencies and skill registration. The full Hermes editing and delivery workflow still needs a live acceptance run.

For an ordered straight cut without Hermes, run `python framecrew.py run --job output-job clip-one.mp4 clip-two.mp4` on Windows or use `python3` on macOS.
