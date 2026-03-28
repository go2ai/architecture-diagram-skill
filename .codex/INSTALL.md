# Codex Installation

This repository is the source project for the `architecture-diagram-sync` skill.

For Codex, the consumable unit is the [`skill/`](../skill/) directory. Everything else in the repository exists to support documentation, local testing, fixtures, and development.

## What To Install

Install, copy, or link the `skill/` directory into whatever skill location your Codex environment already uses.

This repository does not provide a universal Codex installer. Skill loading varies by environment, so this documentation stays conservative on purpose.

## What The Codex Payload Contains

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`

## Conservative Local Check

Before wiring the skill into Codex, you can verify the current repository state locally:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skill/scripts/validate_mermaid.py fixtures/target-repo-basic/docs/architecture
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic --dry-run
python3 skill/scripts/detect_architecture_drift.py --root fixtures/target-repo-basic
```

These checks validate the current v1 behavior of the source repository. They do not prove that your Codex environment loads skills in the same way.

For broader local development and fixture usage, see [`docs/DEVELOPMENT.md`](../docs/DEVELOPMENT.md).

## What To Expect In v1

- Mermaid is the canonical source of truth
- `.excalidraw` is derived
- validation, sync, and drift detection work in a conservative local workflow
- generated `.excalidraw` output is still experimental and not yet advertised as officially import-verified

## What Still Depends On Your Environment

- where Codex expects shared skills to live
- how skills are registered or exposed to the harness
- whether your Codex build supports the surrounding workflow exactly as documented here
- whether your environment-specific installation path matches the assumptions in this repository
