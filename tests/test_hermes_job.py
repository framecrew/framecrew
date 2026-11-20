from contextlib import closing
from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import hermes_job


class HermesJobTests(unittest.TestCase):
    def test_approved_run_without_delivery_fails(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "raw").mkdir()
            (project / "raw" / "clip.mp4").write_bytes(b"source")
            (project / "event.txt").write_text("Event_Type: Street")
            config = project / "config.yaml"
            config.touch()

            def action(name):
                args = ["hermes_job", str(project), name, "--config", str(config)]
                with patch.object(sys, "argv", args):
                    return hermes_job.main()

            with patch.object(hermes_job, "orchestrate") as run:
                def readiness(folder):
                    self.assertFalse((folder / ".framecrew-hermes.sqlite").exists())

                with patch.object(sys, "platform", "win32"), patch.object(
                    hermes_job, "check_windows", side_effect=readiness
                ):
                    self.assertEqual(action("prepare"), 0)
                run.assert_not_called()
                self.assertEqual(action("approve"), 1)
                run.assert_called_once()
                self.assertEqual(action("approve"), 1)
                run.assert_called_once()
            with closing(sqlite3.connect(project / ".framecrew-hermes.sqlite")) as db:
                state, error = db.execute("SELECT state, error FROM job").fetchone()
            self.assertEqual(state, "failed")
            self.assertIn("qc_result.json", error)
