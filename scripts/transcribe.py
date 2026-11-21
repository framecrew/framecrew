"""Transcribe FrameCrew audio locally and write text and SRT files."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / ".framecrew-work"
MODEL = WORKSPACE / "ggml-tiny-q5_1.bin"
MODEL_URL = ("https://huggingface.co/ggerganov/whisper.cpp/resolve/"
             "f281eb45af861ab5e5297d23694b7d46e090c02c/ggml-tiny-q5_1.bin")
MODEL_SHA256 = "818710568da3ca15689e31a743197b520007872ff9576237bda97bd1b469c3d7"


def ffmpeg_has_whisper():
    result = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                            capture_output=True, text=True, timeout=30, check=True)
    return bool(re.search(r"^\s*\S+\s+whisper\s+A->A\b", result.stdout, re.MULTILINE))


def model_valid(path):
    if not path.is_file():
        return False
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() == MODEL_SHA256


def ensure_model():
    if model_valid(MODEL):
        return
    WORKSPACE.mkdir(exist_ok=True)
    print("Downloading the local Whisper model (32 MB).", flush=True)
    with TemporaryDirectory(dir=WORKSPACE) as temporary:
        staged = Path(temporary) / MODEL.name
        with urlopen(MODEL_URL, timeout=60) as response, staged.open("wb") as output:
            shutil.copyfileobj(response, output)
        if not model_valid(staged):
            raise ValueError("The downloaded Whisper model failed its checksum")
        staged.replace(MODEL)


def whisper_srt(source, temporary):
    if model_valid(MODEL):
        subtitle = temporary / "speech.srt"
        model = MODEL.relative_to(ROOT).as_posix()
        output = subtitle.relative_to(ROOT).as_posix()
        filters = f"whisper=model={model}:language=auto:queue=5:use_gpu=false:destination={output}:format=srt"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-i", str(source),
             "-map", "0:a:0", "-af", filters, "-f", "null", "-"],
            cwd=ROOT, check=True, timeout=7200,
        )
        return subtitle.read_text(encoding="utf-8")
    subprocess.run(
        [sys.executable, "-m", "whisper", str(source), "--model", "tiny",
         "--output_format", "srt", "--output_dir", str(temporary), "--fp16", "False"],
        check=True, timeout=7200,
    )
    return (temporary / (source.stem + ".srt")).read_text(encoding="utf-8")


def normalize_srt(srt):
    cues = []
    words = []
    for block in re.split(r"\n\s*\n", srt.strip()):
        lines = block.splitlines()
        if not lines:
            continue
        if len(lines) < 3 or "-->" not in lines[1]:
            raise ValueError("Transcription produced an invalid subtitle cue")
        cues.append("\n".join([str(len(cues) + 1), *lines[1:]]))
        words.append(" ".join(lines[2:]))
    return "\n\n".join(cues) + ("\n" if cues else ""), "\n".join(words) + ("\n" if words else "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        source = args.source.resolve(strict=True)
        destination = args.output.resolve()
        WORKSPACE.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=WORKSPACE) as temporary:
            subtitles, transcript = normalize_srt(whisper_srt(source, Path(temporary)))
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "subtitles.srt").write_text(subtitles, encoding="utf-8")
        (destination / "transcript.txt").write_text(transcript, encoding="utf-8")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FrameCrew transcription failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
