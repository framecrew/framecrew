"""Run the FrameCrew local MP4 workflow."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from uuid import uuid4

STAGES = ("normalize", "assemble", "qc", "deliver")
VIDEO = {"codec_name": "h264", "width": 1280, "height": 720,
         "pix_fmt": "yuv420p"}
AUDIO = {"codec_name": "aac", "sample_rate": "48000", "channels": 2}
PROFILE = 1


def signature(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def command(tool, *args, cwd=None):
    result = subprocess.run(
        [tool, *map(str, args)], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=3600, cwd=cwd,
    )
    if result.returncode:
        detail = result.stderr.strip().splitlines()
        raise ValueError(f"{tool} exited {result.returncode}: {' '.join(detail[-4:])[:1000]}")
    return result.stdout


def probe(path):
    return json.loads(command("ffprobe", "-v", "error", "-show_streams",
                              "-show_format", "-of", "json", path))


def ffmpeg(*args, cwd=None):
    command("ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *args, cwd=cwd)


def normalize(clips, work):
    outputs = []
    for index, clip in enumerate(clips):
        streams = probe(clip)["streams"]
        if not any(s["codec_type"] == "video" and
                   not s.get("disposition", {}).get("attached_pic") for s in streams):
            raise ValueError(f"Clip {index + 1} has no playable video stream")
        has_audio = any(s["codec_type"] == "audio" for s in streams)
        audio_input = [] if has_audio else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        output = work / f"clip-{index:05d}.mp4"
        picture = work / f"picture-{uuid4().hex}.mp4"
        temporary = work / f"render-{uuid4().hex}.mp4"
        ffmpeg("-xerror", "-i", clip, "-map", "0:V:0",
               "-vf", "scale=1280:720:force_original_aspect_ratio=decrease:"
               "force_divisible_by=2:reset_sar=1,pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
               "fps=30,setsar=1", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
               "-pix_fmt", "yuv420p", "-map_metadata", "-1", "-map_chapters", "-1", picture)
        duration = probe(picture)["streams"][0]["duration"]
        ffmpeg("-xerror", "-i", picture, *(["-i", clip] if has_audio else audio_input),
               "-map", "0:v:0", "-map", "1:a:0", "-af", "aresample=48000:async=1:first_pts=0,apad",
               "-t", duration, "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2",
               "-map_metadata", "-1", "-map_chapters", "-1", temporary)
        temporary.replace(output)
        picture.unlink()
        outputs.append(output)
    return outputs


def assemble(clips, work):
    playlist = work / "clips.ffconcat"
    playlist.write_text("ffconcat version 1.0\n" +
                        "".join(f"file {clip.name}\n" for clip in clips), encoding="ascii")
    output = work / "assembled.mp4"
    temporary = work / f"render-{uuid4().hex}.mp4"
    ffmpeg("-f", "concat", "-safe", "1", "-i", playlist.name, "-c", "copy",
           "-movflags", "+faststart", temporary.name, cwd=work)
    temporary.replace(output)
    return [output]


def check_video(video, clips, work):
    metadata = probe(video)
    streams = metadata["streams"]
    if len(streams) != 2:
        raise ValueError("Expected exactly one video stream and one audio stream")
    for stream_type, contract in (("video", VIDEO), ("audio", AUDIO)):
        stream = next((s for s in streams if s["codec_type"] == stream_type), {})
        if any(stream.get(key) != value for key, value in contract.items()):
            raise ValueError(f"Rendered {stream_type} does not match the delivery profile")
    duration = float(metadata["format"]["duration"])
    expected = sum(float(probe(clip)["format"]["duration"]) for clip in clips)
    if not duration > 0 or abs(duration - expected) > max(0.1, 0.05 * len(clips)):
        raise ValueError("Rendered duration does not match the normalized clips")
    ffmpeg("-xerror", "-err_detect", "explode", "-i", video, "-map", "0:v:0",
           "-map", "0:a:0", "-f", "null", "-")
    report = work / "qc.json"
    report.write_text(json.dumps({"duration_seconds": duration,
                                  "media_sha256": signature(video)}, indent=2) + "\n",
                      encoding="utf-8")
    return [report]


def deliver(video, folder):
    output = folder / "finished.mp4"
    temporary = folder / ".framecrew" / "delivery.tmp"
    shutil.copyfile(video, temporary)
    temporary.replace(output)
    return [output]


def record(db, stage, status, artifacts=None, error=None):
    with db:
        db.execute(
            "INSERT OR REPLACE INTO stages VALUES (?, ?, ?, ?)",
            (stage, status, json.dumps(artifacts), error),
        )


def run(folder, clips):
    folder.mkdir(parents=True, exist_ok=True)
    work = folder / ".framecrew"
    work.mkdir(exist_ok=True)
    output = folder / "finished.mp4"
    if any(clip.is_relative_to(work.resolve()) or clip == output.resolve() for clip in clips):
        raise ValueError("Inputs must be outside FrameCrew's job artifacts")

    # A separate SQLite database holds an OS-released lock across stage commits.
    with closing(sqlite3.connect(work / "lock.sqlite", timeout=0)) as lock:
        try:
            lock.execute("BEGIN EXCLUSIVE")
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc):
                raise ValueError("Another process is running this job") from exc
            raise
        with closing(sqlite3.connect(work / "job.sqlite")) as db:
            run_job(db, folder, work, clips)


def run_job(db, folder, work, clips):
    with db:
        db.execute("CREATE TABLE IF NOT EXISTS job (id INTEGER PRIMARY KEY, manifest TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS stages "
                   "(name TEXT PRIMARY KEY, status TEXT, artifacts TEXT, error TEXT)")
    existing = db.execute("SELECT manifest FROM job WHERE id = 1").fetchone()
    if not clips and existing:
        clips = [Path(item["path"]) for item in json.loads(existing[0])["clips"]]
    if not clips:
        raise ValueError("Supply one or more clips for a new job")
    output = folder / "finished.mp4"
    if not existing and output.exists():
        raise ValueError("Choose a new job folder. finished.mp4 already exists here")
    inputs = [{"path": str(clip), "sha256": signature(clip)} for clip in clips]
    manifest = json.dumps({"profile": PROFILE, "clips": inputs})
    if existing and existing[0] != manifest:
        raise ValueError("Input paths, contents, or profile changed. Use a new job folder")
    with db:
        db.execute("INSERT OR IGNORE INTO job VALUES (1, ?)", (manifest,))

    normalized = [work / f"clip-{index:05d}.mp4" for index in range(len(clips))]
    assembled = work / "assembled.mp4"
    steps = (
        lambda: normalize(clips, work),
        lambda: assemble(normalized, work),
        lambda: check_video(assembled, normalized, work),
        lambda: deliver(assembled, folder),
    )
    rebuilding = False
    qc_failed = db.execute(
        "SELECT 1 FROM stages WHERE name = 'qc' AND status = 'failed'"
    ).fetchone()
    for index, (stage, execute) in enumerate(zip(STAGES, steps)):
        saved = db.execute("SELECT status, artifacts FROM stages WHERE name = ?", (stage,)).fetchone()
        if not rebuilding and saved and saved[0] == "complete" and not (
            stage == "assemble" and qc_failed
        ):
            artifacts = json.loads(saved[1])
            if artifacts and all((folder / path).is_file() and
                                 signature(folder / path) == digest
                                 for path, digest in artifacts.items()):
                print(f"{stage}: reused", flush=True)
                continue

        rebuilding = True
        with db:
            db.executemany("DELETE FROM stages WHERE name = ?",
                           [(name,) for name in STAGES[index:]])
        record(db, stage, "running")
        try:
            paths = execute()
            if stage == "normalize" and any(signature(Path(item["path"])) != item["sha256"]
                                             for item in inputs):
                raise ValueError("Input changed during normalization")
            record(db, stage, "complete",
                   {path.relative_to(folder).as_posix(): signature(path) for path in paths})
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
            record(db, stage, "failed", error=str(exc))
            raise ValueError(f"{stage}: {exc}") from exc
        print(f"{stage}: complete", flush=True)
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    start = commands.add_parser("run", help="Start or resume a job")
    start.add_argument("--job", type=Path, required=True)
    start.add_argument("clips", type=Path, nargs="*")
    status = commands.add_parser("status", help="Show persisted stage results")
    status.add_argument("--job", type=Path, required=True)
    args = parser.parse_args()
    folder = args.job.resolve()
    try:
        if args.action == "run":
            run(folder, [path.resolve() for path in args.clips])
        else:
            database = folder / ".framecrew" / "job.sqlite"
            if not database.is_file():
                raise ValueError("No job found")
            with closing(sqlite3.connect(database)) as db:
                rows = db.execute("SELECT name, status, artifacts, error FROM stages")
                stages = {name: {"status": status, "artifacts": json.loads(artifacts),
                                 "error": error} for name, status, artifacts, error in rows}
            print(json.dumps({stage: stages.get(stage, {"status": "pending"})
                              for stage in STAGES}, indent=2))
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"FrameCrew: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
