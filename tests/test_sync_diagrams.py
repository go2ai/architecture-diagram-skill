import json
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "scripts" / "sync_diagrams.py"


class SyncDiagramsCliTests(unittest.TestCase):
    def test_dry_run_reports_processed_without_writing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = pathlib.Path(tmpdir)
            diagram_dir = project_root / "docs" / "architecture"
            diagram_dir.mkdir(parents=True)
            diagram = diagram_dir / "containers.mmd"
            diagram.write_text(
                textwrap.dedent(
                    """
                    flowchart TD
                    api[API] --> queue[Orders Queue]
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(project_root), "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("processed=1", result.stdout)
            self.assertFalse((diagram_dir / "containers.excalidraw").exists())

    def test_sync_writes_excalidraw_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = pathlib.Path(tmpdir)
            diagram_dir = project_root / "docs" / "architecture"
            diagram_dir.mkdir(parents=True)
            diagram = diagram_dir / "containers.mmd"
            diagram.write_text("flowchart TD\napi[API] --> db[(DB)]\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--diagram", str(diagram)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output_file = diagram_dir / "containers.excalidraw"
            self.assertTrue(output_file.exists())
            payload = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(payload["type"], "excalidraw")

    def test_changed_only_skips_up_to_date_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = pathlib.Path(tmpdir)
            diagram_dir = project_root / "docs" / "architecture"
            diagram_dir.mkdir(parents=True)
            diagram = diagram_dir / "containers.mmd"
            output_file = diagram_dir / "containers.excalidraw"
            diagram.write_text("flowchart TD\napi[API] --> db[(DB)]\n", encoding="utf-8")
            output_file.write_text('{"type":"excalidraw"}\n', encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(project_root), "--changed-only"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("No diagrams matched --changed-only", result.stdout)
