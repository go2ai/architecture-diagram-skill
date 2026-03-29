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
- Before writing or revising a diagram, choose its abstraction level explicitly and keep one level per file.
- For `system-context`, show actors, external systems, system boundaries, and top-level ingress or egress.
- For `system-context`, avoid Lambdas, tables, buckets, queues, and low-level cloud or runtime internals unless they are true first-class system boundaries.
- For `containers`, show deployable or runtime containers and primary stores.
- For `containers`, avoid routers, validators, packages, provider-internal components, and other implementation-detail subcomponents unless the diagram is explicitly component-level.
- For `async flow`, focus on one primary path, keep labels short, and minimize narrative edge text.
- For `async flow`, avoid secondary branches unless they materially change understanding.
