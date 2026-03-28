import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill" / "scripts"))

import mermaid_to_excalidraw_adapter as adapter  # noqa: E402


class AdapterTests(unittest.TestCase):
    def test_parse_and_serialize_minimal_diagram(self) -> None:
        source = "\n".join(
            [
                "flowchart LR",
                "api[Public API] --> worker[Billing Worker]",
                "worker --> db[(Orders DB)]",
            ]
        )

        model = adapter.parse_mermaid(source)
        payload = adapter.diagram_to_excalidraw(model)

        self.assertEqual(model.direction, "LR")
        self.assertEqual(sorted(model.nodes.keys()), ["api", "db", "worker"])
        self.assertEqual(len(model.edges), 2)
        self.assertEqual(payload["type"], "excalidraw")
        self.assertEqual(payload["version"], 2)
        self.assertIn("appState", payload)
        self.assertEqual(payload["files"], {})
        self.assertGreaterEqual(len(payload["elements"]), 5)
        rectangle = next(element for element in payload["elements"] if element["type"] == "rectangle")
        text = next(element for element in payload["elements"] if element["type"] == "text")
        arrow = next(element for element in payload["elements"] if element["type"] == "arrow")
        self.assertIn("boundElements", rectangle)
        self.assertEqual(text["containerId"], rectangle["id"])
        self.assertIn("points", arrow)
        json.dumps(payload)
