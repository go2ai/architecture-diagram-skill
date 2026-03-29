import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "scripts" / "validate_mermaid.py"
sys.path.insert(0, str(ROOT / "skill" / "scripts"))

import validate_mermaid  # noqa: E402


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


class ValidateMermaidEdgeLabelTests(unittest.TestCase):
    def test_plain_adjacent_edges_on_consecutive_lines_do_not_count_as_labeled(self) -> None:
        report = validate_mermaid.validate_text(
            "\n".join(["flowchart TD"] + [f"a{i} --> b{i}" for i in range(1, 15)]),
            path="<memory>",
        )

        warning_codes = {warning.code for warning in report.warnings}
        self.assertNotIn("edge-label-limit-warning", warning_codes)

    def test_actual_labeled_edges_are_counted(self) -> None:
        report = validate_mermaid.validate_text(
            "\n".join(
                [
                    "flowchart TD",
                    "a -- produces --> b",
                    "b -- stores in --> c",
                    "c -- notifies --> d",
                    "d -- retries via --> e",
                    "e -- emits --> f",
                    "f -- persists to --> g",
                    "g -- alerts --> h",
                ]
            ),
            path="<memory>",
        )

        warning_codes = {warning.code for warning in report.warnings}
        self.assertIn("edge-label-limit-warning", warning_codes)

    def test_mixed_plain_and_labeled_edges_only_count_real_labels(self) -> None:
        report = validate_mermaid.validate_text(
            "\n".join(
                ["flowchart TD"]
                + [f"a{i} --> b{i}" for i in range(1, 13)]
                + ["x -- labeled --> y"]
            ),
            path="<memory>",
        )

        warning_codes = {warning.code for warning in report.warnings}
        self.assertNotIn("edge-label-limit-warning", warning_codes)
