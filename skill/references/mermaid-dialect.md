# Mermaid Dialect

This document defines the Mermaid subset supported by `architecture-diagram-sync` v1.

The goal is predictability and convertibility, especially for future generation of editable `.excalidraw` artifacts. Full Mermaid coverage is explicitly out of scope.

## Supported Diagram Types

v1 supports only these flowchart headers:

- `flowchart TB`
- `flowchart TD`
- `flowchart LR`

All architecture diagrams handled by the skill should use one of those forms.

Optional experimental mode is also allowed when the user explicitly asks for C4:

- `C4Context`
- `C4Container`
- `C4Component`

This C4 mode is narrower and more lightly validated than the default flowchart mode.

## Supported Building Blocks

Supported and preferred:

- plain nodes with stable identifiers
- short text labels
- directed edges using `-->`
- limited edge labels using `-- text -->`
- simple `subgraph` blocks to group closely related nodes

Recommended node style:

- one logical system element per node
- one node identifier reused consistently inside the file
- labels that fit on one line when possible

For optional C4 mode:

- use `C4Context` for system-context diagrams
- use `C4Container` for container diagrams
- use `C4Component` only when explicitly needed
- keep async flow diagrams in standard Mermaid flowchart, not C4

## Practical Limits

These limits are intentionally conservative for v1:

- Nodes: target 6-25 nodes per diagram; hard limit 40
- Label length: target up to 40 characters; hard limit 60
- Edge labels: target 0-6 per diagram; hard limit 10
- Subgraphs: target 0-3 per diagram; hard limit 4
- Nesting: no nested subgraphs

If a diagram exceeds those limits, split it into smaller diagrams instead of making a single larger one.

## Subgraph Rules

Use subgraphs only to show a meaningful boundary such as:

- internal platform area
- deployment boundary
- application ownership boundary

Do not use subgraphs only for visual decoration. A subgraph should communicate a real grouping that would still matter if the diagram were rendered without styling.

## Prohibited In v1

The following are not supported in v1:

- `graph` syntax variants outside `flowchart`
- `flowchart BT` or `flowchart RL`
- sequence, class, state, ER, Gantt, journey, pie, git, or mindmap diagrams
- clickable nodes, callbacks, or `click` directives
- custom Mermaid initialization blocks such as `%%{init: ...}%%`
- embedded HTML, Markdown formatting tricks, or multiline layout hacks
- icons, images, or custom rendering plugins
- nested subgraphs
- parallel edges between the same pair of nodes when only wording differs
- heavy styling as a source of meaning

## Strongly Discouraged

These may parse in Mermaid but should not be used if the diagram is intended to stay convertible:

- asymmetric edge text used as the only way to explain the relationship
- long labels that read like paragraphs
- using shape variation as the only indicator of node type
- one node connected to nearly every other node
- diagrams that depend on exact renderer spacing to remain understandable
- forcing C4 onto operational or implementation-heavy diagrams where flowchart is the clearer fit

## Authoring Guidance

- Prefer stable IDs such as `api_gateway`, `billing_worker`, or `orders_db`
- Keep labels human-readable, but shorter than prose
- Use edges for relationships, not for documentation paragraphs
- If a diagram needs many annotations, create a companion diagram or surrounding prose instead

## v1 Limitations

v1 is optimized for shared portability across harnesses and future `.excalidraw` generation. It does not attempt to preserve every Mermaid feature, every layout nuance, or renderer-specific behavior.

Flowchart mode remains the default and safest path. C4 support is explicit, optional, and lightly validated in v1.
