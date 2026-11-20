"""Package a QC-approved FrameCrew MP4 in a DaVinci Resolve project."""
import argparse
from pathlib import Path
import os
import sys
from uuid import uuid4


def connect():
    if sys.platform == "win32":
        support = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
        support /= "Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting"
    elif sys.platform == "darwin":
        support = Path("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
    else:
        support = Path("/opt/resolve/Developer/Scripting")
    sys.path.append(str(Path(os.environ.get("RESOLVE_SCRIPT_API", support)) / "Modules"))
    try:
        import DaVinciResolveScript
    except (ImportError, OSError) as exc:
        raise ValueError(f"Resolve scripting SDK could not load: {exc}") from exc
    resolve = DaVinciResolveScript.scriptapp("Resolve")
    if not resolve:
        raise ValueError(
            "Resolve scripting connection unavailable. Verify Resolve Studio is open, "
            "external scripting is set to Local, and this process can reach Resolve."
        )
    return resolve


def require(value, message):
    if not value:
        raise ValueError(message)
    return value


def import_bin(pool, root, name, files):
    folder = require(pool.AddSubFolder(root, name), f"Could not create bin {name}")
    require(pool.SetCurrentFolder(folder), f"Could not select bin {name}")
    if not files:
        return []
    clips = pool.ImportMedia([{"FilePath": str(path)} for path in files])
    if not clips or len(clips) != len(files):
        raise ValueError(f"Resolve did not import every file into {name}")
    return clips


def export(resolve, folder):
    name = folder.name
    final = folder / "output" / f"{name}_final.mp4"
    if not final.is_file() or not final.stat().st_size:
        raise ValueError(f"Approved MP4 missing: {final}")
    destination = folder / "davinci" / f"{name}.drp"
    if destination.exists():
        raise ValueError(f"Resolve export already exists: {destination}")
    manager = require(resolve.GetProjectManager(), "Resolve project manager unavailable")
    project = require(manager.CreateProject(name), f"Could not create Resolve project {name}")
    pool = require(project.GetMediaPool(), "Resolve media pool unavailable")
    root = require(pool.GetRootFolder(), "Resolve root bin unavailable")
    extensions = {".mp4", ".mov", ".mxf", ".avi", ".mkv"}
    for directory, label in (("raw", "Raw Footage"), ("proxy", "Proxy")):
        files = sorted(path for path in (folder / directory).rglob("*")
                       if path.is_file() and path.suffix.lower() in extensions)
        import_bin(pool, root, label, files)
    output = import_bin(pool, root, "Output", [final])
    timeline = pool.CreateTimelineFromClips(f"{name}_Master",
                                            [{"mediaPoolItem": output[0]}])
    require(timeline, "Could not create timeline from the approved MP4")
    require(manager.SaveProject(), "Could not save Resolve project")
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_name(f"{uuid4().hex}.drp")
    try:
        require(manager.ExportProject(name, str(temporary)), "Resolve project export failed")
        require(temporary.is_file() and temporary.stat().st_size,
                "Resolve did not create a nonempty project archive")
        temporary.rename(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--approved-job", type=Path)
    args = parser.parse_args()
    try:
        resolve = connect()
        if args.check:
            print(f"Resolve connected: {resolve.GetProductName()} {resolve.GetVersionString()}")
        else:
            print(export(resolve, args.approved_job.resolve(strict=True)))
    except (OSError, ValueError) as exc:
        print(f"FrameCrew delivery: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
