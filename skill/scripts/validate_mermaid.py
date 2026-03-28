"""Validate Mermaid `.mmd` files against the v1 project rules.

v1 is intentionally conservative:
- only `.mmd` is supported
- only `flowchart TB`, `flowchart TD`, and `flowchart LR` are accepted
- validation focuses on predictable conversion rather than full Mermaid support
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from _common import CANONICAL_EXTENSION, ScriptError, print_json, read_text, resolve_root


SUPPORTED_HEADERS = {"flowchart TB", "flowchart TD", "flowchart LR"}
PROHIBITED_PATTERNS: dict[str, re.Pattern[str]] = {
    "init directive": re.compile(r"^\s*%%\{init:", re.IGNORECASE | re.MULTILINE),
    "click directive": re.compile(r"^\s*click\s+", re.IGNORECASE | re.MULTILINE),
    "sequence diagram": re.compile(r"^\s*sequenceDiagram\b", re.IGNORECASE | re.MULTILINE),
    "class diagram": re.compile(r"^\s*classDiagram\b", re.IGNORECASE | re.MULTILINE),
    "state diagram": re.compile(r"^\s*stateDiagram", re.IGNORECASE | re.MULTILINE),
    "er diagram": re.compile(r"^\s*erDiagram\b", re.IGNORECASE | re.MULTILINE),
    "journey diagram": re.compile(r"^\s*journey\b", re.IGNORECASE | re.MULTILINE),
    "pie diagram": re.compile(r"^\s*pie\b", re.IGNORECASE | re.MULTILINE),
    "mindmap": re.compile(r"^\s*mindmap\b", re.IGNORECASE | re.MULTILINE),
    "unsupported flowchart direction": re.compile(r"^\s*flowchart\s+(BT|RL)\b", re.MULTILINE),
}
NODE_PATTERN = re.compile(
    r"(?P<id>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<shape>\[\[.*?\]\]|\[.*?\]|\(\(.*?\)\)|\(.*?\)|\{.*?\})"
)
SUBGRAPH_PATTERN = re.compile(r"^\s*subgraph\b", re.IGNORECASE)
LABELED_EDGE_LINE_PATTERN = re.compile(r"--\s+[^-\n][^\n]*?\s+-->")


@dataclass(slots=True)
class Diagnostic:
    level: str
    code: str
    message: str
    line: int | None = None


@dataclass(slots=True)
class ValidationReport:
    path: str
    errors: list[Diagnostic]
    warnings: list[Diagnostic]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        return f"{self.path}: errors={len(self.errors)} warnings={len(self.warnings)}"


def first_non_empty_line(text: str) -> tuple[int | None, str | None]:
    for index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped:
            return index, stripped
    return None, None


def count_labeled_edges(text: str) -> int:
    return sum(1 for line in text.splitlines() if LABELED_EDGE_LINE_PATTERN.search(line))


def validate_text(text: str, path: str) -> ValidationReport:
    errors: list[Diagnostic] = []
    warnings: list[Diagnostic] = []
    line_number, header = first_non_empty_line(text)
    if header not in SUPPORTED_HEADERS:
        errors.append(
            Diagnostic(
                level="error",
                code="unsupported-header",
                message="Unsupported header. Expected one of: flowchart TB, flowchart TD, flowchart LR.",
                line=line_number,
            )
        )

    for name, pattern in PROHIBITED_PATTERNS.items():
        if pattern.search(text):
            errors.append(
                Diagnostic(
                    level="error",
                    code="prohibited-construct",
                    message=f"Prohibited construct detected: {name}.",
                )
            )

    nodes = {match.group("id"): match.group(0) for match in NODE_PATTERN.finditer(text)}
    node_count = len(nodes)
    if node_count > 40:
        errors.append(Diagnostic("error", "node-limit", f"Diagram defines {node_count} nodes; hard limit is 40."))
    elif node_count > 25:
        warnings.append(
            Diagnostic("warning", "node-limit-warning", f"Diagram defines {node_count} nodes; recommended limit is 25.")
        )

    labels = []
    for raw_node in nodes.values():
        label = re.sub(r"^[A-Za-z_][A-Za-z0-9_]*\s*", "", raw_node)
        label = label.strip("[](){}\" ")
        labels.append(label)
    for label in labels:
        if len(label) > 60:
            errors.append(
                Diagnostic("error", "label-limit", f"Node label exceeds hard limit of 60 characters: {label[:40]}...")
            )
        elif len(label) > 40:
            warnings.append(
                Diagnostic(
                    "warning",
                    "label-limit-warning",
                    f"Node label exceeds recommended limit of 40 characters: {label[:40]}...",
                )
            )

    edge_label_count = count_labeled_edges(text)
    if edge_label_count > 10:
        errors.append(
            Diagnostic("error", "edge-label-limit", f"Diagram uses {edge_label_count} edge labels; hard limit is 10.")
        )
    elif edge_label_count > 6:
        warnings.append(
            Diagnostic(
                "warning",
                "edge-label-limit-warning",
                f"Diagram uses {edge_label_count} edge labels; recommended limit is 6.",
            )
        )

    subgraph_depth = 0
    subgraph_count = 0
    for line_index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if SUBGRAPH_PATTERN.match(line):
            subgraph_count += 1
            subgraph_depth += 1
            if subgraph_depth > 1:
                errors.append(
                    Diagnostic("error", "nested-subgraph", "Nested subgraphs are not supported in v1.", line_index)
                )
        elif stripped == "end" and subgraph_depth > 0:
            subgraph_depth -= 1

    if subgraph_count > 4:
        errors.append(Diagnostic("error", "subgraph-limit", f"Diagram uses {subgraph_count} subgraphs; hard limit is 4."))
    elif subgraph_count > 3:
        warnings.append(
            Diagnostic(
                "warning",
                "subgraph-limit-warning",
                f"Diagram uses {subgraph_count} subgraphs; recommended limit is 3.",
            )
        )

    return ValidationReport(path=path, errors=errors, warnings=warnings)


def validate_path(path: Path) -> list[ValidationReport]:
    if path.is_file():
        if path.suffix != CANONICAL_EXTENSION:
            raise ScriptError(
                f"Unsupported extension for {path}. v1 validates {CANONICAL_EXTENSION} files only."
            )
        return [validate_text(read_text(path), str(path))]
    reports: list[ValidationReport] = []
    for file_path in sorted(path.rglob(f"*{CANONICAL_EXTENSION}")):
        reports.append(validate_text(read_text(file_path), str(file_path)))
    return reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Mermaid .mmd files for architecture-diagram-sync v1.")
    parser.add_argument("path", help="Path to a .mmd file or a directory containing .mmd files.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON in addition to exit status.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        path = resolve_root(args.path)
        reports = validate_path(path)
    except ScriptError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    error_count = 0
    warning_count = 0
    for report in reports:
        print(report.summary())
        for diagnostic in report.errors:
            error_count += 1
            prefix = f"line {diagnostic.line}: " if diagnostic.line else ""
            print(f"  ERROR {diagnostic.code}: {prefix}{diagnostic.message}")
        for diagnostic in report.warnings:
            warning_count += 1
            prefix = f"line {diagnostic.line}: " if diagnostic.line else ""
            print(f"  WARNING {diagnostic.code}: {prefix}{diagnostic.message}")

    print(
        f"Summary: files={len(reports)} errors={error_count} warnings={warning_count} valid={sum(r.is_valid for r in reports)}"
    )

    if args.json:
        payload = {
            "files": [asdict(report) for report in reports],
            "summary": {
                "files": len(reports),
                "errors": error_count,
                "warnings": warning_count,
                "valid": sum(report.is_valid for report in reports),
            },
        }
        print_json(payload)

    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
