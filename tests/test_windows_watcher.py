from pathlib import Path
import sys
import tempfile
import unittest

from scripts.check_windows_job import check


@unittest.skipUnless(sys.platform == "win32", "Windows file-sharing semantics")
class WindowsWatcherTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        (self.folder / "event.txt").write_text("Event_Type: Street")
        self.clip = self.folder / "clip.mp4"
        self.clip.write_bytes(b"test clip")

    def test_stable_files(self):
        delays = []
        check(self.folder, delays.append)
        self.assertEqual(delays, [30, 30, 60])

    def test_open_writer_is_rejected(self):
        with self.clip.open("ab"):
            with self.assertRaisesRegex(OSError, "Windows error 32"):
                check(self.folder, lambda _: None)

    def test_same_size_change_in_safety_buffer_is_rejected(self):
        def pause(seconds):
            if seconds == 60:
                self.clip.write_bytes(b"new bytes")

        with self.assertRaisesRegex(ValueError, "safety buffer"):
            check(self.folder, pause)
