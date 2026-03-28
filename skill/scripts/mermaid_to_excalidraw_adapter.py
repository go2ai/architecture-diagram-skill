"""Convert a conservative Mermaid subset into a serializable Excalidraw-shaped payload.

This adapter intentionally targets a narrow subset of Mermaid flowcharts so `sync_diagrams.py`
can rely on a predictable intermediate model in v1.

The generated document now follows the official top-level shape used by Excalidraw exports:
`type`, `version`, `source`, `elements`, `appState`, and `files`.

Important: that makes the payload much closer to a real `.excalidraw` file, but this project
still does not claim proven import compatibility without validating the generated output against
the real Excalidraw importer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from time import time

from _common import ScriptError, ensure_mmd_file, read_text, resolve_root


NODE_DECLARATION_PATTERN = re.compile(
    r"(?P<id>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<shape>\[\[.*?\]\]|\[.*?\]|\(\(.*?\)\)|\(\[.*?\]\)|\(.*?\)|\{.*?\})"
)
LABELED_EDGE_PATTERN = re.compile(
    r"(?P<source>[A-Za-z_][A-Za-z0-9_]*)\s*--\s*(?P<label>[^-][^-]*?)\s*-->\s*(?P<target>[A-Za-z_][A-Za-z0-9_]*)"
)
PLAIN_EDGE_PATTERN = re.compile(r"(?P<source>[A-Za-z_][A-Za-z0-9_]*)\s*-->\s*(?P<target>[A-Za-z_][A-Za-z0-9_]*)")


@dataclass(slots=True)
class Node:
    id: str
    label: str
    shape: str = "rectangle"


@dataclass(slots=True)
class Edge:
    source: str
    target: str
    label: str | None = None


@dataclass(slots=True)
class DiagramModel:
    direction: str
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    subgraphs: list[str] = field(default_factory=list)


def _seeded_rng(model: DiagramModel) -> Random:
    basis = f"{model.direction}|{'|'.join(model.nodes)}|{len(model.edges)}"
    return Random(basis)


def _next_int(rng: Random) -> int:
    return rng.randint(1, 2_147_483_647)


def _text_metrics(text: str, font_size: int = 20) -> tuple[int, int, int]:
    width = max(40, int(len(text) * font_size * 0.62))
    height = max(28, int(font_size * 1.5))
    baseline = int(font_size * 0.8)
    return width, height, baseline


def _label_from_shape(shape: str) -> str:
    return shape.strip("[](){}\" ")


def parse_mermaid(text: str) -> DiagramModel:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("flowchart "):
        raise ScriptError("Cannot parse Mermaid diagram without a supported flowchart header.")
    direction = lines[0].split()[1]
    model = DiagramModel(direction=direction)

    for line in lines[1:]:
        if line.startswith("subgraph "):
            model.subgraphs.append(line[len("subgraph ") :].strip())
            continue
        if line == "end":
            continue
        for match in NODE_DECLARATION_PATTERN.finditer(line):
            node_id = match.group("id")
            if node_id not in model.nodes:
                model.nodes[node_id] = Node(id=node_id, label=_label_from_shape(match.group("shape")))
        edge_line = NODE_DECLARATION_PATTERN.sub(lambda match: match.group("id"), line)
        edge_match = LABELED_EDGE_PATTERN.search(edge_line) or PLAIN_EDGE_PATTERN.search(edge_line)
        if edge_match:
            source = edge_match.group("source")
            target = edge_match.group("target")
            if source not in model.nodes:
                model.nodes[source] = Node(id=source, label=source.replace("_", " "))
            if target not in model.nodes:
                model.nodes[target] = Node(id=target, label=target.replace("_", " "))
            label = edge_match.groupdict().get("label")
            model.edges.append(Edge(source=source, target=target, label=label.strip() if label else None))

    return model


def diagram_to_excalidraw(model: DiagramModel) -> dict[str, object]:
    rng = _seeded_rng(model)
    updated = int(time() * 1000)
    elements: list[dict[str, object]] = []
    node_ids = list(model.nodes.keys())
    spacing_x = 280 if model.direction == "LR" else 0
    spacing_y = 180 if model.direction in {"TD", "TB"} else 0
    fallback_y = 140 if model.direction == "LR" else 0
    node_positions: dict[str, tuple[int, int, int, int, str]] = {}

    for index, node_id in enumerate(node_ids):
        node = model.nodes[node_id]
        x = index * spacing_x
        y = index * spacing_y if spacing_y else index * fallback_y
        text_id = f"{node.id}__text"
        node_positions[node.id] = (x, y, 220, 80, text_id)
        elements.append(
            {
                "id": node.id,
                "type": "rectangle",
                "x": x,
                "y": y,
                "width": 220,
                "height": 80,
                "angle": 0,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "hachure",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "frameId": None,
                "roundness": None,
                "seed": _next_int(rng),
                "version": 1,
                "versionNonce": _next_int(rng),
                "isDeleted": False,
                "boundElements": [{"id": text_id, "type": "text"}],
                "updated": updated,
                "link": None,
                "locked": False,
            }
        )
        text_width, text_height, baseline = _text_metrics(node.label)
        elements.append(
            {
                "id": text_id,
                "type": "text",
                "x": x + (220 - text_width) / 2,
                "y": y + (80 - text_height) / 2,
                "width": text_width,
                "height": text_height,
                "angle": 0,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "groupIds": [],
                "frameId": None,
                "roundness": None,
                "seed": _next_int(rng),
                "version": 1,
                "versionNonce": _next_int(rng),
                "isDeleted": False,
                "boundElements": [],
                "updated": updated,
                "link": None,
                "locked": False,
                "text": node.label,
                "fontSize": 20,
                "fontFamily": 1,
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": node.id,
                "originalText": node.label,
                "lineHeight": 1.25,
                "baseline": baseline,
            }
        )

    for index, edge in enumerate(model.edges):
        source_x, source_y, source_width, source_height, _ = node_positions[edge.source]
        target_x, target_y, target_width, target_height, _ = node_positions[edge.target]
        start_x = source_x + source_width / 2
        start_y = source_y + source_height / 2
        end_x = target_x + target_width / 2
        end_y = target_y + target_height / 2
        elements.append(
            {
                "id": f"edge-{index}",
                "type": "arrow",
                "x": start_x,
                "y": start_y,
                "width": end_x - start_x,
                "height": end_y - start_y,
                "angle": 0,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "hachure",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "frameId": None,
                "roundness": None,
                "seed": _next_int(rng),
                "version": 1,
                "versionNonce": _next_int(rng),
                "isDeleted": False,
                "boundElements": [],
                "updated": updated,
                "link": None,
                "locked": False,
                "points": [[0, 0], [end_x - start_x, end_y - start_y]],
                "lastCommittedPoint": None,
                "startBinding": None,
                "endBinding": None,
                "startArrowhead": None,
                "endArrowhead": "arrow",
                "elbowed": False,
            }
        )

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "architecture-diagram-sync",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adapt a Mermaid .mmd file into a partial Excalidraw-like JSON payload."
    )
    parser.add_argument("diagram", help="Path to a Mermaid .mmd file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        diagram_path = ensure_mmd_file(resolve_root(args.diagram))
        payload = diagram_to_excalidraw(parse_mermaid(read_text(diagram_path)))
    except ScriptError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
