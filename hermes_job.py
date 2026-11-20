"""Start an approved FrameCrew job through the Hermes orchestration layer."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from zipfile import BadZipFile, ZipFile

from scripts.check_windows_job import check as check_windows

ROOT = Path(__file__).resolve().parent


def fingerprint(folder):
    sources = sorted(path for path in (folder / "raw").rglob("*") if path.is_file())
    if not sources:
        raise ValueError("No files found in raw/")
    inputs = {}
    for path in [folder / "event.txt", *sources]:
        with path.open("rb") as stream:
            inputs[path.relative_to(folder).as_posix()] = hashlib.file_digest(stream, "sha256").hexdigest()
    return json.dumps(inputs, sort_keys=True)


def verify_delivery(folder):
    name = folder.name
    video = folder / "output" / f"{name}_final.mp4"
    project = folder / "davinci" / f"{name}.drp"
    result = folder / "qc_result.json"
    if not result.is_file():
        raise ValueError("Hermes did not leave qc_result.json")
    report = json.loads(result.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or not isinstance(report.get("checks"), dict):
        raise ValueError("Invalid QC report")
    checks = {"integrity", "duration", "resolution", "audio", "titles", "lut", "transcripts"}
    if report.get("status") != "PASSED" or any(
        report.get("checks", {}).get(key) != "PASS" for key in checks
    ):
        raise ValueError("Hermes did not record all seven original QC checks as passed")
    if not video.is_file() or not project.is_file():
        raise ValueError("Delivery is incomplete. A final MP4 and a Resolve project are required")
    with video.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != report.get("final_sha256"):
            raise ValueError("The final MP4 does not match the QC report")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-map", "0:v:0",
         "-map", "0:a:0", "-f", "null", "-"],
        check=True, timeout=1800,
    )
    with ZipFile(project) as archive:
        if archive.testzip() or "project.xml" not in archive.namelist() or not any(
            path.startswith("SeqContainer/") for path in archive.namelist()
        ):
            raise ValueError("The Resolve archive is missing project or timeline data")


def orchestrate(folder, launcher, config, timeout):
    prompt = (
        f"Process only the FrameCrew project {folder}. The original Watcher readiness "
        "check passed and the project operator has approved this exact input set. "
        f"Read the FrameCrew config at {config}. "
        "Use the installed editor-manager skill and its original downstream skills and "
        "handoffs in order. Keep all generated files inside this project. Never change "
        "raw footage or send external notifications. Do not invoke the standalone "
        "FrameCrew clip joiner. Stop and report any blocked stage. After QC and Delivery, "
        "write qc_result.json in the project folder with status PASSED only when all "
        "seven original QC checks passed, checks mapping integrity, duration, resolution, "
        "audio, titles, lut, transcripts to PASS, and final_sha256 equal to the "
        "SHA-256 of the approved final MP4. Never invent a result or create placeholder artifacts."
    )
    subprocess.run(
        [launcher, "chat", "--oneshot", "--format", "stream-json", "--in", str(ROOT),
         "--query-file", "-"],
        input=prompt, text=True, encoding="utf-8", check=True, timeout=timeout,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("action", choices=("prepare", "approve", "status"))
    parser.add_argument("--hermes", default="hermes")
    parser.add_argument("--config", type=Path, default=ROOT / "config/framecrew.yaml")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    db = None
    try:
        folder = args.project.resolve(strict=True)
        if not folder.is_dir():
            raise ValueError("Project must be a directory")
        db = sqlite3.connect(folder / ".framecrew-hermes.sqlite", timeout=0)
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS job (id INTEGER PRIMARY KEY, state TEXT, "
                       "fingerprint TEXT, error TEXT)")
        row = db.execute("SELECT state, fingerprint, error FROM job WHERE id=1").fetchone()
        if args.action == "status":
            print(json.dumps(dict(zip(("state", "fingerprint", "error"), row))
                             if row else {"state": "new"}))
            return 0
        if args.action == "prepare":
            if sys.platform != "win32":
                raise ValueError("This job entry point currently supports the Windows Watcher")
            inputs = fingerprint(folder)
            check_windows(folder)
            if fingerprint(folder) != inputs:
                raise ValueError("Inputs changed during the Watcher check")
            with db:
                if db.execute("SELECT 1 FROM job WHERE id=1").fetchone():
                    raise ValueError("This project already has a job. Use status")
                db.execute("INSERT INTO job VALUES (1, 'awaiting_approval', ?, NULL)", (inputs,))
            print("Awaiting approval. Run the approve action to start Hermes.")
            return 0
        if not row or row[0] != "awaiting_approval":
            raise ValueError("A prepared job awaiting approval is required")
        if fingerprint(folder) != row[1]:
            raise ValueError("The brief or footage changed after readiness checks")
        if (folder / "qc_result.json").exists():
            raise ValueError("This job already contains a QC report. Use a fresh test project")
        config = args.config.resolve(strict=True)
        with db:
            updated = db.execute("UPDATE job SET state='running' "
                                 "WHERE id=1 AND state='awaiting_approval'")
            if updated.rowcount != 1:
                raise ValueError("Another process already accepted this approval")
        try:
            orchestrate(folder, args.hermes, config, args.timeout)
            if fingerprint(folder) != row[1]:
                raise ValueError("Hermes changed the source brief or footage")
            verify_delivery(folder)
        except (Exception, KeyboardInterrupt) as exc:
            with db:
                db.execute("UPDATE job SET state='failed', error=? WHERE id=1",
                           (str(exc) or type(exc).__name__,))
            raise
        with db:
            db.execute("UPDATE job SET state='complete' WHERE id=1")
        print("FrameCrew delivery verified")
        return 0
    except (OSError, ValueError, sqlite3.Error, subprocess.SubprocessError, BadZipFile) as exc:
        print(f"FrameCrew: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    sys.exit(main())
