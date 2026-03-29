# Repository Layout

This document describes the expected layout of the target repository that consumes the skill. It does not describe the layout of this skill's own source repository.

## Default Location

The default location for architecture diagrams in the target project is:

- `docs/architecture/`

This directory should be treated as the primary home for canonical Mermaid diagrams and their derived artifacts.

## Canonical And Derived Files

For each maintained architecture diagram:

- `.mmd` is the canonical source
- `.excalidraw` is the derived editable artifact

The pair should live side by side in the same directory whenever possible.

Example:

```text
docs/architecture/
├── system-context.mmd
├── system-context.excalidraw
├── containers.mmd
├── containers.excalidraw
└── async-order-flow.mmd
```

If the derived `.excalidraw` file is not present yet, the Mermaid file still remains the source of truth.

## File Naming Strategy

Use stable, lowercase, hyphenated file names.

Recommended patterns:

- `system-context.mmd`
- `containers.mmd`
- `components-billing.mmd`
- `async-ingestion-flow.mmd`
- `async-video-processing-flow.mmd`
- `async-email-delivery.mmd`

Rules:

- use names that describe viewpoint, not ticket numbers
- keep names short enough to scan in directory listings
- prefer one diagram per file
- for async diagrams, name the file after the primary flow it explains
- avoid generic names like `async-job-flow.mmd` unless there is only one meaningful async flow and that generic name is truly the clearest one
- avoid date-stamped file names for current diagrams
- avoid `final`, `new`, `v2`, or similar temporary suffixes

## Optional Subdirectories

If the architecture area grows, the target repository may split `docs/architecture/` into stable subdirectories such as:

- `docs/architecture/context/`
- `docs/architecture/containers/`
- `docs/architecture/async/`

Use subdirectories only when the number of diagrams makes a single folder hard to navigate. Do not introduce deep nesting in v1.

## Relationship To Code

Diagram files should be committed near the documentation surface of the target repository, not embedded in service folders by default.

The main reason is maintainability:

- architecture diagrams usually describe multiple parts of the system
- reviewers can discover them in one predictable place
- generated `.excalidraw` artifacts stay paired with their Mermaid source

Exceptions may exist for very large monorepos, but v1 assumes `docs/architecture/` first.

## Minimum Expected Layout In A Target Repository

```text
<target-repo>/
├── docs/
│   └── architecture/
│       ├── system-context.mmd
│       ├── system-context.excalidraw
│       ├── containers.mmd
│       └── async-order-flow.mmd
└── ...
```

## v1 Limitations

v1 assumes a documentation-first layout centered on `docs/architecture/`. It does not yet define how to reconcile multiple diagram roots, generated output directories, or organization-wide documentation conventions across many repositories.
