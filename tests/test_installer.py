from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import install_framecrew as installer


class InstallerTests(unittest.TestCase):
    def test_registers_original_skills_and_preserves_existing_setup(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "FrameCrew with spaces"
            home = Path(temporary) / "Hermes profile"
            for directory in ("skills", "templates", "config", "memories"):
                shutil.copytree(installer.ROOT / directory, root / directory)
            (root / "scripts").mkdir()
            shutil.copyfile(installer.ROOT / "scripts/check_windows_job.py",
                            root / "scripts/check_windows_job.py")
            shutil.copyfile(installer.ROOT / ".env.example", root / ".env.example")
            with patch.object(installer, "ROOT", root), patch.object(
                installer, "HERMES_HOME", home
            ), patch.object(installer, "WINDOWS", True), patch.dict(
                installer.os.environ, {"PROJECTS_ROOT": "", "TEMPLATES_ROOT": ""}
            ):
                installer.install_profile()
                skills = list(home.glob("skills/video/*/SKILL.md"))
                self.assertEqual(len(skills), 13)
                watcher = home / "skills/video/watcher-agent"
                self.assertTrue((watcher / "check_windows_job.py").is_file())
                original = (watcher / "SKILL.md").read_text(encoding="utf-8")
                (watcher / "SKILL.md").write_text(original + "\nUser customization\n", encoding="utf-8")
                config = root / "config/framecrew.yaml"
                config.write_text("custom: true", encoding="utf-8")
                installer.install_profile()
                self.assertIn("User customization", (watcher / "SKILL.md").read_text(encoding="utf-8"))
                self.assertEqual(config.read_text(encoding="utf-8"), "custom: true")
                self.assertTrue((root / ".framecrew-work/Projects").is_dir())

    def test_media_rechecks_missing_dependency_after_install(self):
        with patch.object(installer, "usable", side_effect=[
            None, "ffmpeg", "ffprobe", "magick", "magick",
        ]), patch.object(installer, "system_package") as install:
            installer.ensure_media_tools()
        install.assert_called_once_with("Gyan.FFmpeg", "ffmpeg")

    def test_python_packages_are_not_reinstalled_when_present(self):
        with TemporaryDirectory() as temporary:
            python = Path(temporary) / "python"
            python.touch()
            with patch.object(installer, "PYTHON", python), patch.object(
                installer, "module_missing", return_value=False
            ), patch.object(installer, "run") as run:
                installer.ensure_python_packages(installer.CORE)
            run.assert_not_called()
