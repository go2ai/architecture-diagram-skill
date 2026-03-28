import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class OfficialExcalidrawValidationTests(unittest.TestCase):
    def test_official_validation_probe_returns_structured_result(self) -> None:
        result = subprocess.run(
            ["node", "tests/validate_excalidraw_official.mjs"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertIn(payload["status"], {"accepted", "environment_error"})
        if payload["status"] == "accepted":
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(payload["accepted"])
            self.assertGreater(payload["elementCount"], 0)
            self.assertTrue(payload["appStatePresent"])
            self.assertTrue(payload["filesPresent"])
        else:
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse(payload["accepted"])
            self.assertIn("could not be loaded", payload["message"])
