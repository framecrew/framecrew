from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import framecrew


class MediaWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for tool in ("ffmpeg", "ffprobe"):
            if not shutil.which(tool):
                raise RuntimeError(f"{tool} is required for the media integration tests")
        cls.fixtures = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixtures.cleanup)
        folder = Path(cls.fixtures.name)
        cls.first = folder / "first clip.mp4"
        cls.second = folder / "second 'clip'.mov"
        framecrew.ffmpeg("-f", "lavfi", "-i", "color=red:s=320x240:r=24:d=0.5",
                         "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
                         "-c:v", "libx264", "-c:a", "aac", "-shortest", cls.first)
        framecrew.ffmpeg("-f", "lavfi", "-i", "color=blue:s=240x320:r=25:d=0.8",
                         "-c:v", "libx264", cls.second)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.job = Path(temporary.name) / "edit job"

    def cli(self, action, *clips):
        return subprocess.run(
            [sys.executable, framecrew.__file__, action, "--job", self.job, *clips],
            capture_output=True, text=True,
        )

    def test_export_order_and_reuse(self):
        result = self.cli("run", self.second, self.first)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.job / "finished.mp4"
        for time, channel in (("0.2", 2), ("1.0", 0)):
            sample = subprocess.check_output(
                ["ffmpeg", "-v", "error", "-ss", time, "-i", output, "-frames:v", "1",
                 "-vf", "crop=2:2,scale=1:1,format=rgb24", "-f", "rawvideo", "-"],
            )
            self.assertGreater(sample[channel], 200)
        report = json.loads((self.job / ".framecrew" / "qc.json").read_text())
        self.assertAlmostEqual(report["duration_seconds"], 1.3, delta=0.1)
        self.assertEqual(report["media_sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
        resumed = self.cli("run")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(resumed.stdout.count("reused"), 4)
        changed = self.cli("run", self.first, self.second)
        self.assertNotEqual(changed.returncode, 0)
        self.assertIn("changed", changed.stderr)

    def test_qc_failure_and_restart(self):
        def corrupt_assembly(clips, work):
            output = work / "assembled.mp4"
            output.write_bytes(b"broken MP4")
            return [output]

        with patch.object(framecrew, "assemble", side_effect=corrupt_assembly):
            with self.assertRaisesRegex(ValueError, "qc:"):
                framecrew.run(self.job, [self.first])
        stages = json.loads(self.cli("status").stdout)
        self.assertEqual(stages["qc"]["status"], "failed")
        self.assertEqual(stages["deliver"]["status"], "pending")
        self.assertFalse((self.job / "finished.mp4").exists())

        resumed = self.cli("run")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn("normalize: reused", resumed.stdout)
        self.assertIn("assemble: complete", resumed.stdout)
        self.assertIn("qc: complete", resumed.stdout)

        (self.job / "finished.mp4").write_bytes(b"damaged copy")
        repaired = self.cli("run")
        self.assertEqual(repaired.returncode, 0, repaired.stderr)
        self.assertIn("qc: reused", repaired.stdout)
        self.assertIn("deliver: complete", repaired.stdout)

    def test_interrupted_stage_and_exclusive_writer(self):
        with patch.object(framecrew, "deliver", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                framecrew.run(self.job, [self.first])
        self.assertEqual(json.loads(self.cli("status").stdout)["deliver"]["status"], "running")

        with closing(sqlite3.connect(self.job / ".framecrew" / "lock.sqlite")) as lock:
            lock.execute("BEGIN EXCLUSIVE")
            busy = self.cli("run")
            self.assertNotEqual(busy.returncode, 0)
            self.assertIn("Another process", busy.stderr)
        resumed = self.cli("run")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn("qc: reused", resumed.stdout)
        self.assertIn("deliver: complete", resumed.stdout)

    def test_invalid_clip_does_not_deliver(self):
        invalid = self.job.parent / "invalid.mp4"
        invalid.write_bytes(b"not a video")
        result = self.cli("run", invalid)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("normalize:", result.stderr)
        self.assertFalse((self.job / "finished.mp4").exists())
