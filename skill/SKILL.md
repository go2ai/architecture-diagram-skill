---
name: architecture-diagram-sync
description: Use this skill when working on repository architecture diagrams, especially to validate Mermaid-based architecture docs, detect likely drift from the codebase, and generate derived Excalidraw-shaped artifacts while keeping Mermaid as the canonical source of truth.
---

# architecture-diagram-sync

Use this skill when working on repository architecture diagrams, especially when checking whether diagrams still match the codebase or when updating architecture documentation.

Rules:

- Treat Mermaid as the source of truth for architecture diagrams.
- Treat `.excalidraw` files as derived artifacts, not primary authored files.
- When a diagram needs changes, update the Mermaid source first.
