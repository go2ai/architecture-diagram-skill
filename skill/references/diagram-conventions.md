# Diagram Conventions

This document defines how architecture diagrams should be scoped, named, and split so they remain maintainable as the codebase changes.

The default rule is simple: prefer several small diagrams with clear purpose over one large diagram that tries to explain everything.

Default mode is the conservative Mermaid flowchart subset. Only switch to C4 when the user explicitly asks for it and the diagram type benefits from it.

## Diagram Categories

Use separate diagrams for separate questions.

Before writing or updating a diagram, choose the abstraction level first. Do not mix context, deployable containers, and low-level runtime internals in the same file.

### 1. System Context

If C4 mode is explicitly requested, this diagram type should use `C4Context`.

Use a system context diagram when the goal is to show:

- the main system or product boundary
- primary users or operators
- major external services or platforms
- the top-level ingress and egress of the system

Typical size:

- 5-12 nodes
- little or no internal component detail

Do not use this diagram to document internal Lambdas, workers, queues, buckets, tables, or low-level cloud/runtime internals unless one of those is itself a true first-class system boundary.

### 2. Containers And Components

If C4 mode is explicitly requested, container-level diagrams should use `C4Container`.

Use `C4Component` only when component-level detail is explicitly needed.

Use a container or component diagram when the goal is to show:

- deployable services
- applications, workers, APIs, or internal modules
- databases, caches, queues, and storage used by those components
- the main runtime relationships inside the system boundary

Typical size:

- 6-20 nodes
- grouped by bounded area or deployment boundary when useful

Prefer deployable/runtime containers and primary stores.

Avoid routers, validators, packages, provider-specific internal components, and implementation-detail subcomponents unless the diagram is explicitly component-level.

Avoid disconnected external systems in container diagrams. If an external dependency matters in that view, show at least one meaningful relationship to an internal container. Otherwise omit it.

Simplify carefully. Do not compress an indirect runtime path into a direct edge when the middle hop is an important runtime boundary.

Do not mix this with a full async event narrative unless the async flow is very small.

### 3. Async Flows

Keep async flows in regular Mermaid flowchart mode, even when C4 is requested elsewhere.

Use an async flow diagram when the goal is to show:

- event producers and consumers
- queue or topic handoff
- retries, dead-letter routing, or scheduled jobs
- cross-service asynchronous movement of work

Typical size:

- 4-15 nodes
- edges are usually more important than node variety

Focus on one primary async path. Prefer short labels and minimal narration.

Avoid secondary branches unless they materially change understanding.

When reviewing async diagrams, prefer removing secondary branches unless they materially change understanding.

Do not overload a structural component diagram with every async edge if that makes the main layout harder to read.

## Granularity Rules

Choose one level of abstraction per diagram.

Good examples:

- one diagram for external context
- one diagram for internal containers
- one separate diagram for order-processing async flow

Avoid mixing:

- people, high-level systems, and low-level classes in one diagram
- system boundaries, deployable containers, and low-level cloud/runtime internals in one diagram
- broad platform topology and step-by-step message flow in one diagram
- operational infrastructure detail that is irrelevant to the question the diagram answers
- C4 context/container structure with flowchart-style internal runtime narration unless clearly justified

## Naming Conventions

Use names that are stable, direct, and easy to map back to the repository.

Prefer:

- product or system names for top-level boundaries
- deployable names for services and workers
- domain-oriented names for business components
- concrete platform names only when they matter architecturally

Examples:

- `Public API`
- `Billing Worker`
- `Orders Database`
- `Email Delivery Service`

Avoid:

- vague labels such as `Processor`, `Manager`, or `Service Layer`
- labels that contain implementation trivia
- labels that differ from repository terminology without a good reason

## Visual Clarity Rules

- Keep labels short and scannable
- Minimize crossing edges
- Use left-to-right or top-to-bottom flow consistently inside one diagram
- Use subgraphs only when they clarify ownership or deployment boundaries
- Do not rely on styling alone to explain meaning
- If a legend is required to understand the diagram, the diagram is probably too dense

## When To Update An Existing Diagram

Update an existing diagram when:

- the same question is still being answered
- the same abstraction level still fits
- the change adds or removes a small number of nodes or edges
- the diagram remains readable after the change

## When To Create A New Diagram

Create a new diagram when:

- the change introduces a new viewpoint, such as async flow vs system context
- adding the new information would push the diagram beyond the Mermaid v1 limits
- the diagram would otherwise need multiple abstraction levels
- the audience for the new information is different from the existing diagram's audience

If C4 is requested, switch only the diagrams where C4 improves the architecture semantics. Do not force C4 onto async flow diagrams.

## v1 Limitations

v1 does not attempt to standardize every possible diagram type. It standardizes the minimum set needed for repeatable architecture maintenance: context, containers/components, and async flows.

C4 support is optional, explicit, and narrower than the default flowchart mode. If the repository is too operational or implementation-heavy, staying in flowchart mode is usually the safer choice even when C4 is requested.
