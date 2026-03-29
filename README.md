# architecture-diagram-sync

`architecture-diagram-sync` is the source repository for a shared skill that helps keep architecture diagrams aligned with the codebase they describe.

The installable, portable core lives in [`skill/`](skill/). The rest of this repository exists to support public documentation, harness-specific onboarding, fixtures, tests, and local development.

## What The Skill Does

In its current v1 form, the project can:

- validate `.mmd` architecture diagrams against a conservative Mermaid subset
- generate a derived `.excalidraw` document from supported Mermaid flowcharts
- detect likely architecture drift with simple, explicit heuristics
- run repeatable local tests and smoke tests against sample target repositories

Default mode is standard Mermaid flowchart. Optional C4 support is available only when explicitly requested, and it is narrower and more conservative than the default path.

Mermaid is the canonical source of truth. `.excalidraw` is a derived artifact.

## Install on Codex

Install the portable skill payload directly from GitHub:

```bash
$skill-installer install https://github.com/go2ai/architecture-diagram-skill/tree/main/skill
```

After installation, restart Codex to pick up the new skill.

For Codex-specific usage notes, see [`docs/README.codex.md`](docs/README.codex.md).

## Current Status

Ready today:

- portable skill instructions under `skill/`
- script entry points for validation, sync, drift detection, and Excalidraw shaping
- fixtures and automated tests for the current v1 behavior
- harness-specific onboarding docs, starting with Codex

Still partial in v1:

- Mermaid support is intentionally narrow
- drift detection is heuristic and conservative
- generated `.excalidraw` output is still experimental
- official Excalidraw runtime validation is not yet passing in this environment

The generated `.excalidraw` document now follows a much closer Excalidraw-shaped JSON structure, including `elements`, `appState`, and `files`. It should still not be described as verified importable until a real Excalidraw restore/import path succeeds.

## Repository Layout

```text
.
├── skill/                  # Portable skill core and installable payload
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
├── .codex/                 # Codex-specific repository-local install notes
├── docs/                   # Public docs and harness overlays
├── fixtures/               # Sample target repositories for smoke testing
├── tests/                  # Automated tests for the current v1 behavior
├── package.json            # Small Node setup for official Excalidraw validation probe
└── README.md
```

## Harness Docs

- Codex: [`docs/README.codex.md`](docs/README.codex.md)
- Claude Code: [`docs/README.claude-code.md`](docs/README.claude-code.md)
- OpenClaw: [`docs/README.openclaw.md`](docs/README.openclaw.md)
- Local development: [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)

For a short Codex-specific note kept under the repository root, see [`.codex/INSTALL.md`](.codex/INSTALL.md).

## Local Testing

Automated tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Smoke tests:

```bash
python3 skill/scripts/validate_mermaid.py fixtures/target-repo-basic/docs/architecture
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic --dry-run
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic
python3 skill/scripts/sync_diagrams.py --root fixtures/target-repo-basic --changed-only
python3 skill/scripts/detect_architecture_drift.py --root fixtures/target-repo-basic
```

Official Excalidraw runtime probe:

```bash
node tests/validate_excalidraw_official.mjs
```

That probe is useful for status-checking, but today it still reports an environment/runtime loading failure rather than a successful official restore.

## Known Limitations

- Only `.mmd` is supported in v1.
- Only a small Mermaid flowchart subset is supported.
- `docs/architecture/` is the expected diagram root when using `--root`.
- `--changed-only` is timestamp-based, not git-aware.
- Drift reporting is intentionally conservative and does not model full topology.
- The `.excalidraw` output is closer to the real format, but still not proven importable by the official runtime here.

## Next Steps

- validate generated `.excalidraw` successfully through an official or equivalent restore path
- refine the conversion output only after import compatibility is demonstrated
- expand harness documentation only where the integration path is actually verified

## Publishing Notes

- publish it as experimental, not as a production-ready skill
- do not promise verified Excalidraw import compatibility yet
- keep Codex usage documented as conservative and environment-dependent
- treat Claude Code and OpenClaw docs as placeholders until those flows are verified
