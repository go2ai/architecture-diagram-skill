# Development

This repository is the source project for the `design-architecture` skill.

## Minimum Requirements

- Python 3.12 or compatible Python 3 runtime
- Node.js and npm if you want to run the official Excalidraw runtime probe

Python scripts are the main implementation surface. The Node setup exists only to support the current Excalidraw validation probe.

## What Is Installable

The installable, harness-facing payload is [`skill/`](../skill/).

## What Is Development Support

These directories are support material for working on the source project:

- `docs/`
- `fixtures/`
- `tests/`

## Running Automated Tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Running Smoke Tests

Use the basic fixture as the default local target repository:

```bash
python3 skill/scripts/validate_mermaid.py fixtures/target-repo-basic/docs/architecture
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic --dry-run
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic --changed-only
python3 skill/scripts/detect_architecture_drift.py --root fixtures/target-repo-basic
```

## Using The Fixtures

- `fixtures/target-repo-basic/`
  - small plausible target repository
  - intentionally contains detectable drift
- `fixtures/target-repo-aligned/`
  - similar target repository with no relevant drift under the current heuristics

Use these fixtures to validate behavior changes before trying the scripts on a real repository.

Harness-specific usage notes live alongside this guide:

- Codex: [`README.codex.md`](README.codex.md)
- Claude Code: [`README.claude-code.md`](README.claude-code.md)
- OpenClaw: [`README.openclaw.md`](README.openclaw.md)

## Official Excalidraw Runtime Probe

If Node dependencies are installed:

```bash
node tests/validate_excalidraw_official.mjs
```

This probe attempts to load the official `@excalidraw/excalidraw` runtime and validate the generated fixture. In the current environment, that runtime still fails to load before restore/import can be exercised, so the probe is mainly a status check.

## Working Boundaries For v1

- do not treat `.excalidraw` output as officially import-verified yet
- do not assume broader Mermaid support than what is documented in `skill/references/`
- prefer conservative changes over speculative compatibility claims
