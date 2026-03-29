# Codex

`architecture-diagram-sync` is intended to be consumed in Codex as a shared skill whose portable core lives in [`skill/`](../skill/).

## Install

Install the skill directly from GitHub:

```bash
$skill-installer install https://github.com/go2ai/architecture-diagram-skill/tree/main/skill
```

Restart Codex to pick up the new skill.

## Installable Unit

Codex should consume `skill/` as the installable payload. Repository-level files such as `README.md`, `docs/`, `fixtures/`, and `tests/` are support material for humans and for local development of the source project.

If your environment uses a different registration mechanism, follow that environment's documented flow instead of inventing a new one here.

## What The Skill Does In Codex

Use it when you want Codex to:

- propose or revise Mermaid architecture diagrams
- keep Mermaid as the canonical source of truth
- validate diagrams against the supported subset
- generate derived `.excalidraw` output conservatively
- review likely architecture drift against repository structure and infrastructure clues

## What You Can Test Locally First

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skill/scripts/validate_mermaid.py fixtures/target-repo-basic/docs/architecture
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic --dry-run
python3 skill/scripts/detect_architecture_drift.py --root fixtures/target-repo-basic
```

These commands confirm the current repository behavior. They are useful before installing the skill into Codex, but they are not a substitute for your environment's own skill-loading semantics.

For a broader local development guide, see [`DEVELOPMENT.md`](DEVELOPMENT.md).

## Current v1 Scope

Available now:

- portable skill instructions
- shared references for diagram rules and repository layout
- Python entry points for validation, sync, and drift detection
- fixtures, smoke tests, and a small Excalidraw runtime probe

Not promised in v1:

- universal harness compatibility
- full Mermaid support
- verified Excalidraw import compatibility

For a shorter repository-local install note, see [`.codex/INSTALL.md`](../.codex/INSTALL.md).
