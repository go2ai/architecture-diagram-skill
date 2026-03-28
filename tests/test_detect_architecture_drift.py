import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "scripts" / "detect_architecture_drift.py"


class DetectArchitectureDriftCliTests(unittest.TestCase):
    def test_reports_structured_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = pathlib.Path(tmpdir)
            (project_root / "infra").mkdir()
            (project_root / "infra" / "queue.tf").write_text(
                'resource "aws_sqs_queue" "orders" { name = "orders-queue" }\n',
                encoding="utf-8",
            )
            (project_root / "docs" / "architecture").mkdir(parents=True)
            (project_root / "docs" / "architecture" / "containers.mmd").write_text(
                "flowchart TD\napi[API] --> db[(DB)]\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(project_root)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("confirmed", payload)
            self.assertIn("probable", payload)
            self.assertIn("unknown", payload)
            self.assertGreaterEqual(len(payload["probable"]), 1)

    def test_aligned_diagram_reduces_drift_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = pathlib.Path(tmpdir)
            (project_root / "infra").mkdir()
            (project_root / "infra" / "resources.tf").write_text(
                '\n'.join(
                    [
                        'resource "aws_sqs_queue" "orders" { name = "orders-queue" }',
                        'resource "aws_s3_bucket" "artifacts" { bucket = "orders-artifacts" }',
                        'resource "aws_db_instance" "orders" { identifier = "orders-db" }',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (project_root / "docs" / "architecture").mkdir(parents=True)
            (project_root / "docs" / "architecture" / "containers.mmd").write_text(
                "\n".join(
                    [
                        "flowchart TD",
                        "gateway[Public API] --> api[Orders API]",
                        "api --> queue[Orders Queue]",
                        "queue --> worker[Orders Worker]",
                        "worker --> bucket[(Artifacts Bucket)]",
                        "api --> db[(Orders DB)]",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(project_root)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["confirmed"], [])
            self.assertEqual(payload["probable"], [])
