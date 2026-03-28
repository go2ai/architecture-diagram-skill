# architecture-diagram-sync

Use this skill when working on repository architecture diagrams, especially when checking whether diagrams still match the codebase or when updating architecture documentation.

Rules:

- Treat Mermaid as the source of truth for architecture diagrams.
- Treat `.excalidraw` files as derived artifacts, not primary authored files.
- When a diagram needs changes, update the Mermaid source first.
- Only regenerate or refresh `.excalidraw` after the Mermaid source is updated.
- Prefer shared references in `references/` and shared scripts in `scripts/` when this skill evolves across harnesses.
