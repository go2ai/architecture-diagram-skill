"""Shared helpers for the design-architecture script entry points."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


CANONICAL_EXTENSION = ".mmd"
DERIVED_EXTENSION = ".excalidraw"
DEFAULT_DIAGRAMS_DIR = Path("docs/architecture")
TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rb",
    ".rs",
    ".tf",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".env",
    ".md",
    ".sh",
}
MAX_TEXT_FILE_BYTES = 256_000


@dataclass(slots=True)
class ScriptError(Exception):
    """Raised when CLI arguments or file-level operations are invalid."""

    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(slots=True)
class FileResult:
    """Small structured summary for work performed on a single file."""

    path: str
    status: str
    message: str


def resolve_root(root: str | os.PathLike[str]) -> Path:
    path = Path(root).expanduser().resolve()
    if not path.exists():
        raise ScriptError(f"Path does not exist: {path}")
    return path


def diagrams_root(root: Path) -> Path:
    return root / DEFAULT_DIAGRAMS_DIR


def discover_diagrams(root: Path) -> list[Path]:
    expected = diagrams_root(root)
    if not expected.exists():
        return []
    return sorted(path for path in expected.rglob(f"*{CANONICAL_EXTENSION}") if path.is_file())


def ensure_mmd_file(path: Path) -> Path:
    if not path.is_file():
        raise ScriptError(f"Diagram file not found: {path}")
    if path.suffix != CANONICAL_EXTENSION:
        raise ScriptError(
            f"Unsupported diagram extension for {path}. v1 operates on {CANONICAL_EXTENSION} only."
        )
    return path


def corresponding_excalidraw_path(diagram_path: Path) -> Path:
    return diagram_path.with_suffix(DERIVED_EXTENSION)


def changed_only_filter(diagram_paths: Iterable[Path]) -> list[Path]:
    selected: list[Path] = []
    for diagram_path in diagram_paths:
        target_path = corresponding_excalidraw_path(diagram_path)
        if not target_path.exists():
            selected.append(diagram_path)
            continue
        if diagram_path.stat().st_mtime > target_path.stat().st_mtime:
            selected.append(diagram_path)
    return selected


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def to_serializable(items: Iterable[Any]) -> list[Any]:
    serialized: list[Any] = []
    for item in items:
        if hasattr(item, "__dataclass_fields__"):
            serialized.append(asdict(item))
        else:
            serialized.append(item)
    return serialized


def iter_text_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if DEFAULT_DIAGRAMS_DIR.parts == path.parts[-len(DEFAULT_DIAGRAMS_DIR.parts) :]:
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS and path.stat().st_size <= MAX_TEXT_FILE_BYTES:
            yield path
