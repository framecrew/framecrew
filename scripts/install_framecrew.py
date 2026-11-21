"""Install FrameCrew into an existing or new local Hermes profile."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

if __package__:
    from .transcribe import ensure_model, ffmpeg_has_whisper
else:
    from transcribe import ensure_model, ffmpeg_has_whisper

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = sys.platform == "win32"
VENV_BIN = ROOT / ".venv" / ("Scripts" if WINDOWS else "bin")
PYTHON = VENV_BIN / ("python.exe" if WINDOWS else "python")
LOCAL = Path(os.environ.get("LOCALAPPDATA") or Path.home())
HERMES_HOME = Path(os.environ.get("HERMES_HOME") or
                   (LOCAL / "hermes" if WINDOWS else Path.home() / ".hermes")).expanduser()
CORE = {"cv2": "scenedetect[opencv]", "scenedetect": "scenedetect[opencv]",
        "yaml": "PyYAML", "watchdog": "watchdog"}
STILLS = {"rembg": "rembg[cpu]", "realesrgan": "realesrgan"}


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def refresh_path():
    locations = [VENV_BIN, HERMES_HOME / "bin", Path.home() / ".local/bin"]
    if WINDOWS:
        import winreg
        locations.append(LOCAL / "Microsoft/WinGet/Links")
        for root in ("ProgramFiles", "ProgramFiles(x86)"):
            if os.environ.get(root):
                locations.extend(sorted(Path(os.environ[root]).glob("ImageMagick-*"), reverse=True))
        registry_paths = []
        for hive, key in ((winreg.HKEY_CURRENT_USER, "Environment"),
                          (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
            try:
                with winreg.OpenKey(hive, key) as environment:
                    registry_paths.append(os.path.expandvars(winreg.QueryValueEx(environment, "Path")[0]))
            except FileNotFoundError:
                continue
        locations.extend(path for entry in registry_paths for path in entry.split(os.pathsep) if path)
    old_path = os.environ.get("PATH", "").split(os.pathsep)
    os.environ["PATH"] = os.pathsep.join(dict.fromkeys([*map(str, locations), *old_path]))


def usable(command, *flags, match=None):
    for entry in os.environ["PATH"].split(os.pathsep):
        if not entry:
            continue
        binary = shutil.which(command, path=entry)
        if not binary:
            continue
        try:
            result = subprocess.run([binary, *flags], capture_output=True,
                                    errors="replace", timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0 and (match is None or re.search(match, result.stdout)):
            return binary
    return None


def system_package(windows_id, brew_name):
    if WINDOWS:
        if not shutil.which("winget"):
            raise ValueError("WinGet is required to install missing system packages")
        run("winget", "install", "--id", windows_id, "--exact", "--source", "winget")
    else:
        installed = subprocess.run(["brew", "list", "--versions", brew_name],
                                   stdout=subprocess.DEVNULL, check=False)
        run("brew", "upgrade" if installed.returncode == 0 else "install", brew_name)
    refresh_path()


def ensure_media_tools():
    ffmpeg = lambda: usable("ffmpeg", "-version", match=r"^ffmpeg version (?:n)?(?:[89]|[1-9][0-9]+)\.")
    if not ffmpeg() or not usable("ffprobe", "-version"):
        system_package("Gyan.FFmpeg", "ffmpeg")
    if not ffmpeg() or not usable("ffprobe", "-version"):
        raise ValueError("FFmpeg 8+ and FFprobe were not found after installation")
    if not usable("magick", "-version"):
        system_package("ImageMagick.ImageMagick", "imagemagick")
    if not usable("magick", "-version"):
        raise ValueError("ImageMagick was not found after installation")


def ensure_hermes():
    launcher = usable("hermes", "--version")
    if launcher:
        return launcher
    # Use the upstream installer with its usual platform permissions and vendor prompts.
    with TemporaryDirectory() as temporary:
        script = Path(temporary) / ("install.ps1" if WINDOWS else "install.sh")
        urlretrieve(f"https://hermes-agent.nousresearch.com/{script.name}", script)
        if WINDOWS:
            # Follow Nous's documented in-memory installer invocation.
            env = dict(os.environ, FRAMECREW_HERMES_SCRIPT=str(script))
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command",
                 "& ([scriptblock]::Create((Get-Content -Raw -LiteralPath $env:FRAMECREW_HERMES_SCRIPT)))"],
                check=True, env=env,
            )
        else:
            run("bash", script)
    refresh_path()
    launcher = usable("hermes", "--version")
    if not launcher:
        raise ValueError("Hermes did not pass its version check after installation")
    return launcher


def module_missing(module):
    return subprocess.run(
        [str(PYTHON), "-c", f"import {module}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode != 0


def ensure_python_packages(packages):
    if not PYTHON.is_file():
        run(sys.executable, "-m", "venv", ROOT / ".venv")
    missing = sorted({package for module, package in packages.items() if module_missing(module)})
    if missing:
        run(PYTHON, "-m", "pip", "install", *missing)
    failed = [module for module in packages if module_missing(module)]
    if failed:
        raise ValueError("Python modules failed to load: " + ", ".join(failed))


def write_if_missing(target, content):
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as stream:
            stream.write(content)
    except FileExistsError:
        pass


def install_profile():
    skills = sorted((ROOT / "skills/video").glob("*.md"))
    if len(skills) != 13:
        raise ValueError(f"Expected 13 FrameCrew skills, found {len(skills)}")
    for source in skills:
        body = source.read_text(encoding="utf-8")
        role = next(line.removeprefix("**Role:** ") for line in body.splitlines()
                    if line.startswith("**Role:** "))
        target = HERMES_HOME / "skills/video" / source.stem / "SKILL.md"
        header = f"---\nname: {source.stem}\ndescription: >-\n  {role}\n---\n\n"
        write_if_missing(target, (header + body).encode("utf-8"))
        if f"name: {source.stem}" not in target.read_text(encoding="utf-8").splitlines():
            raise ValueError(f"Existing Hermes skill needs review: {target}")

    if WINDOWS:
        write_if_missing(HERMES_HOME / "skills/video/watcher-agent/check_windows_job.py",
                         (ROOT / "scripts/check_windows_job.py").read_bytes())
    workspace = ROOT / ".framecrew-work"
    projects = Path(os.environ.get("PROJECTS_ROOT") or workspace / "Projects").expanduser().resolve()
    templates = Path(os.environ.get("TEMPLATES_ROOT") or workspace / "Templates").expanduser().resolve()
    projects.mkdir(parents=True, exist_ok=True)
    for source in (ROOT / "templates").glob("*.txt"):
        write_if_missing(templates / source.name, source.read_bytes())
    config = (ROOT / "config/framecrew.example.yaml").read_text(encoding="utf-8")
    config = (config.replace('"~/FrameCrew/Projects"', json.dumps(projects.as_posix()))
              .replace('"~/FrameCrew/Templates"', json.dumps(templates.as_posix()))
              .replace("notify_telegram: true", "notify_telegram: false"))
    if WINDOWS:
        config = config.replace('title_font: "Helvetica"', 'title_font: "C:/Windows/Fonts/arial.ttf"')
    write_if_missing(ROOT / "config/framecrew.yaml", config.encode("utf-8"))
    write_if_missing(ROOT / ".env", (ROOT / ".env.example").read_bytes())
    write_if_missing(HERMES_HOME / "memories/user/model-routing.md",
                     (ROOT / "memories/model-routing.md").read_bytes())
    print(f"Installed or verified {len(skills)} FrameCrew skills in {HERMES_HOME}")
    print(f"Project folder: {projects}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--launch", action="store_true", help="Launch Hermes with FrameCrew's media tools")
    modes.add_argument("--with-stills", action="store_true", help="Also install the still-image AI packages")
    modes.add_argument("--skills-only", action="store_true", help="Register skills and bootstrap configuration")
    args = parser.parse_args()
    if not WINDOWS and sys.platform != "darwin":
        parser.error("This installer supports Windows and macOS")
    refresh_path()
    os.environ["HERMES_HOME"] = str(HERMES_HOME)
    try:
        if args.skills_only:
            install_profile()
            return 0
        if args.launch:
            launcher = usable("hermes", "--version")
            if not PYTHON.is_file() or not launcher:
                raise ValueError("Run the FrameCrew installer first")
            run(launcher)
            return 0
        launcher = ensure_hermes()
        ensure_media_tools()
        packages = dict(CORE)
        if WINDOWS and ffmpeg_has_whisper():
            ensure_model()
            print("Using FFmpeg's local Whisper filter for transcription.")
        else:
            packages["whisper"] = "openai-whisper"
        ensure_python_packages(packages | (STILLS if args.with_stills else {}))
        install_profile()
        print(f"Hermes launcher: {launcher}")
        print("Setup checks passed. Hermes model sign-in and optional integrations are configured separately.")
        if not args.with_stills:
            print("AI still-image enhancement is optional. Rerun setup with --with-stills to add it.")
    except (OSError, ValueError, StopIteration, subprocess.SubprocessError) as exc:
        print(f"FrameCrew setup failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
