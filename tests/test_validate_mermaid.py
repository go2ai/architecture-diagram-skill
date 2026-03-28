import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "scripts" / "validate_mermaid.py"


class ValidateMermaidCliTests(unittest.TestCase):
    def test_valid_file_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            diagram = pathlib.Path(tmpdir) / "system-context.mmd"
            diagram.write_text(
                textwrap.dedent(
                    """
                    flowchart TD
                    api[Public API] --> db[(Orders DB)]
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(diagram)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("errors=0", result.stdout)

    def test_invalid_header_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            diagram = pathlib.Path(tmpdir) / "invalid.mmd"
            diagram.write_text(
                textwrap.dedent(
                    """
                    sequenceDiagram
                    A->>B: nope
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(diagram)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsupported header", result.stdout)

