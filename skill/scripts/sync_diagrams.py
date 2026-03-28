"""Synchronize canonical Mermaid `.mmd` files to derived `.excalidraw` artifacts.

Operational contract in v1:
- `.mmd` is the source of truth
- `.excalidraw` is a derived artifact that may be generated or overwritten
- `--changed-only` is conservative and timestamp-based in this version
- generated `.excalidraw` content follows a much closer Excalidraw-shaped JSON document,
  but import compatibility is still not claimed without direct verification
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import (
    FileResult,
    ScriptError,
    changed_only_filter,
    corresponding_excalidraw_path,
    discover_diagrams,
    ensure_mmd_file,
    read_text,
    resolve_root,
    write_json,
)
from mermaid_to_excalidraw_adapter import diagram_to_excalidraw, parse_mermaid
from validate_mermaid import validate_text


def discover_targets(root: Path | None, diagram: Path | None, changed_only: bool) -> list[Path]:
    if diagram and root:
        raise ScriptError("Use either --root or --diagram, not both.")
    if diagram:
        targets = [ensure_mmd_file(diagram)]
    elif root:
        targets = discover_diagrams(root)
    else:
        raise ScriptError("Either --root or --diagram is required.")
    if changed_only:
        targets = changed_only_filter(targets)
    return targets


def sync_diagram(diagram_path: Path, dry_run: bool) -> FileResult:
    report = validate_text(read_text(diagram_path), str(diagram_path))
    if not report.is_valid:
        return FileResult(path=str(diagram_path), status="failed", message="validation failed")

    output_path = corresponding_excalidraw_path(diagram_path)
    action = "overwrite" if output_path.exists() else "generate"
    action_past = "overwrote" if output_path.exists() else "generated"
    payload = diagram_to_excalidraw(parse_mermaid(read_text(diagram_path)))
    if dry_run:
        return FileResult(
            path=str(diagram_path),
            status="processed",
            message=(
                f"dry-run: would {action} {output_path} "
                "(.mmd remains source of truth; generated payload is closer to Excalidraw format, but not import-verified in v1)"
            ),
        )

    write_json(output_path, payload)
    return FileResult(
        path=str(diagram_path),
        status="processed",
        message=(
            f"{action_past} {output_path} "
            "(.mmd remains source of truth; overwrite is allowed in sync; payload is closer to Excalidraw format, but not import-verified in v1)"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync Mermaid .mmd diagrams to derived .excalidraw JSON documents with conservative compatibility."
    )
    parser.add_argument("--root", help="Target repository root; diagrams are discovered under docs/architecture/.")
    parser.add_argument("--diagram", help="Path to a specific .mmd diagram.")
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Only process diagrams missing a .excalidraw file or newer than the existing derived artifact.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report what would be written without writing files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.root) if args.root else None
        diagram = resolve_root(args.diagram) if args.diagram else None
        targets = discover_targets(root, diagram, args.changed_only)
    except ScriptError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.changed_only and not targets:
        print("No diagrams matched --changed-only. Nothing to do.")
        print("Summary: processed=0 skipped=0 failed=0")
        return 0
    if not targets:
        print("No .mmd diagrams found under the expected layout.")
        print("Summary: processed=0 skipped=0 failed=0")
        return 0

    processed = 0
    skipped = 0
    failed = 0
    for target in targets:
        result = sync_diagram(target, dry_run=args.dry_run)
        print(f"{result.status.upper()} {result.path}: {result.message}")
        if result.status == "processed":
            processed += 1
        elif result.status == "skipped":
            skipped += 1
        else:
            failed += 1

    print(f"Summary: processed={processed} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
