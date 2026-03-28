# Diagram Conventions

This document defines how architecture diagrams should be scoped, named, and split so they remain maintainable as the codebase changes.

The default rule is simple: prefer several small diagrams with clear purpose over one large diagram that tries to explain everything.

## Diagram Categories

Use separate diagrams for separate questions.

### 1. System Context

Use a system context diagram when the goal is to show:

- the main system or product boundary
- primary users or operators
- major external services or platforms
- the top-level ingress and egress of the system

Typical size:

- 5-12 nodes
- little or no internal component detail

Do not use this diagram to document internal jobs, queues, tables, or component wiring.

### 2. Containers And Components

Use a container or component diagram when the goal is to show:

- deployable services
- applications, workers, APIs, or internal modules
- databases, caches, queues, and storage used by those components
- the main runtime relationships inside the system boundary

Typical size:

- 6-20 nodes
- grouped by bounded area or deployment boundary when useful

Do not mix this with a full async event narrative unless the async flow is very small.

### 3. Async Flows

Use an async flow diagram when the goal is to show:

- event producers and consumers
- queue or topic handoff
- retries, dead-letter routing, or scheduled jobs
- cross-service asynchronous movement of work

Typical size:

- 4-15 nodes
- edges are usually more important than node variety

Do not overload a structural component diagram with every async edge if that makes the main layout harder to read.

## Granularity Rules

Choose one level of abstraction per diagram.

Good examples:

- one diagram for external context
- one diagram for internal containers
- one separate diagram for order-processing async flow

Avoid mixing:

- people, high-level systems, and low-level classes in one diagram
- broad platform topology and step-by-step message flow in one diagram
- operational infrastructure detail that is irrelevant to the question the diagram answers

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

## v1 Limitations

v1 does not attempt to standardize every possible diagram type. It standardizes the minimum set needed for repeatable architecture maintenance: context, containers/components, and async flows.
