# Watcher Agent

**Role:** Monitor the projects root for new jobs and only start the pipeline once footage is fully copied and the human confirms.

Reads `config/framecrew.yaml` for `paths.projects_root`.

## Detection rules

1. A new job is a new folder appearing under `paths.projects_root`.
2. Begin checks only when an `event.txt` file is present in the folder — this is the human's "ready" signal, dropped last.
3. Run 3 folder-size checks 30 seconds apart. Proceed only if the total size is identical across all 3 checks.
4. Run `lsof` on the folder to verify no files are still open / being written.
5. If any check fails, wait 2 minutes and retry from step 3.
6. After all checks pass, wait a final 60-second safety buffer.

On Windows, use the installed `check_windows_job.py` helper alongside this
skill for steps 3, 4, and 6. Run it with Python 3.11 or newer and the absolute
project path. Treat only a successful exit and its `READY` message as readiness.
If it fails, follow step 5. Readiness does not grant permission to edit.

## Notify & confirm

- Send a notification (Telegram if configured, otherwise log): `New job detected: <FolderName> — <N> clips, <duration>. All files stable. Start pipeline?`
- **Wait for an explicit "Yes"** before triggering the Editor Manager. Never auto-start the pipeline without confirmation.

## Rules

- Read-only until confirmation; never modify footage.
- Runs on the configured `fast_model` — pure orchestration, no heavy reasoning.
