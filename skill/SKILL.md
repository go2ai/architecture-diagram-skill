---
name: design-architecture
description: "Use this skill only for repository architecture diagram tasks: proposing or revising Mermaid diagrams under docs/architecture, checking diagram abstraction level, validating Mermaid against the supported subset, and reviewing diagram drift against code or infrastructure. Do not use this skill for generic planning, brainstorming, visual companion workflows, or broad documentation tasks unrelated to architecture diagrams."
metadata:
  short-description: Maintain Mermaid architecture diagrams and review architecture drift
---

# design-architecture

Use this skill when working on repository architecture diagrams, especially when checking whether diagrams still match the codebase or when updating architecture documentation.

## Do not use this skill for
- generic planning or task decomposition
- brainstorming multiple solution options
- visual companion or browser preview workflows
- broad documentation work not centered on architecture diagrams
- implementation tasks that do not update or assess architecture diagrams

## Rules

- Treat Mermaid as the source of truth for architecture diagrams.
- Use the default Mermaid flowchart subset unless the user explicitly asks for C4.
- Treat `.excalidraw` files as derived artifacts, not primary authored files.
- When a diagram needs changes, update the Mermaid source first.
- Before writing or revising a diagram, choose its abstraction level explicitly and keep one level per file.
- If C4 is explicitly requested, use `C4Context` for `system-context` and `C4Container` for `containers`.
- Use `C4Component` only when component-level detail is explicitly needed.
- Do not use C4 for `async flow`; keep async diagrams in regular Mermaid flowchart mode.
- Do not mix flowchart internals into a C4 context/container file unless clearly justified.
- For `system-context`, show actors, external systems, system boundaries, and top-level ingress or egress.
- For `system-context`, avoid Lambdas, tables, buckets, queues, and low-level cloud or runtime internals unless they are true first-class boundaries.
- For `containers`, show deployable or runtime containers and primary stores.
- For `containers`, avoid routers, validators, packages, provider-internal components, and other implementation-detail subcomponents unless the diagram is intentionally component-level.
- For `containers`, omit disconnected external systems. If an external dependency matters in that view, show at least one meaningful relationship to an internal container.
- Simplify carefully. Do not compress an indirect runtime path into a direct edge when the middle hop is an important runtime boundary.
- For `async flow`, focus on one primary path, keep labels short, and minimize narrative edge text.
- For `async flow`, avoid secondary branches unless they materially change understanding.
- When reviewing `async flow`, remove secondary branches unless they materially change understanding.
- Name async diagrams after the primary flow they explain, such as `async-ingestion-flow.mmd` or `async-email-delivery-flow.mmd`.
- Avoid generic async names like `async-job-flow.mmd` unless the repository truly has only one meaningful async flow and that generic name is the clearest one.
