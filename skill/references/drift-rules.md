# Drift Rules

This document defines how v1 should reason about architecture drift between code and maintained diagrams.

The skill should prefer conservative inference. If the evidence is not strong enough, it should say so explicitly instead of presenting a weak guess as a fact.

## Core Principle

Drift means a meaningful architectural mismatch between the current repository and the maintained diagrams.

In v1, the skill should look for drift using repository evidence such as:

- service and worker directories
- infrastructure-as-code files
- deployment manifests
- queue, bucket, database, or gateway configuration
- code references to external platforms or internal services

## Evidence Tiers

### Strong Signals Of Drift

Treat these as high-confidence candidates for drift:

- a clearly defined infrastructure resource exists in code or IaC but has no corresponding diagram element where it should appear
- a diagram shows a component that no longer exists in code, config, or deployment definitions
- a named integration path changed direction or changed intermediary resources, such as sync to async
- a service was split or merged in code, but the diagram still shows the old topology
- a queue, database, or external API is renamed in the repo and the diagram still uses the previous name

### Weak Or Inferred Signals

Treat these as tentative and explicitly label them as inferred:

- naming conventions strongly suggest a missing component, but no deployment or config evidence confirms it
- code references indicate a dependency, but it is unclear whether the dependency is architecturally significant
- a package or SDK is present, but its usage may be optional, local-only, or experimental
- repository structure implies a boundary that may not correspond to a deployable or documented component

Weak signals should trigger a suggestion for review, not an automatic diagram rewrite.

## Resource Heuristics

v1 should use only durable heuristics that are likely to survive across repositories.

### Queues

Strong indicators:

- queue resources declared in IaC or deployment config
- producer and consumer code paths referencing the same queue name
- explicit dead-letter or retry queue configuration

Likely diagram treatment:

- represent the queue as its own node in container/component or async diagrams
- show producer-to-queue and queue-to-consumer relationships

Weak-only indicators:

- helper classes with queue-like names but no concrete configured resource

### Buckets

Strong indicators:

- named object storage buckets in IaC, env config, or application settings
- code that reads from or writes to those buckets through concrete bucket names or bindings

Likely diagram treatment:

- represent the bucket as a storage node only when it is part of the system's architecture, not just a temporary implementation detail

Weak-only indicators:

- generic storage client libraries without named bucket references

### Databases

Strong indicators:

- database instances declared in infrastructure or service config
- connection strings, named schemas, or clearly owned persistence layers
- migrations or ORM configuration that map to a specific database boundary

Likely diagram treatment:

- represent distinct databases or architecturally important stores
- do not create separate nodes for every table or model in v1

Weak-only indicators:

- incidental test database configuration
- embedded local databases used only for development tooling

### Lambdas, Workers, And Jobs

Strong indicators:

- deployed function definitions
- dedicated worker entry points
- scheduler or cron configuration invoking specific jobs
- message consumer handlers tied to a deployable process

Likely diagram treatment:

- show them as distinct runtime nodes when they execute independently from the main API or app

Weak-only indicators:

- utility modules with `job` or `worker` in the file name but no runtime boundary evidence

### Gateways And APIs

Strong indicators:

- explicit API gateway, ingress, route table, or edge proxy configuration
- public API surfaces exposed independently from internal services
- service-to-service API clients with stable named endpoints

Likely diagram treatment:

- show the gateway or public API as a distinct node if it is a real architecture boundary
- show major internal API relationships, not every internal HTTP call

Weak-only indicators:

- generic HTTP clients without stable target naming

### External Services

Strong indicators:

- concrete third-party service names in config, code, or deployment
- authenticated integrations with clear operational relevance
- inbound or outbound business-critical data flows

Likely diagram treatment:

- include external services that materially affect system behavior, data flow, or dependencies

Weak-only indicators:

- optional SDKs
- dormant integrations
- development-only tooling services

## Reporting Guidance

When drift is detected, the skill should separate:

- confirmed drift based on strong evidence
- probable drift based on multiple weak signals
- unknowns that require human review

The skill should name the evidence source whenever possible, such as:

- infrastructure config
- deployment manifest
- service entry point
- application configuration
- repository path convention

## v1 Limitations

v1 intentionally avoids fragile heuristics such as guessing architecture only from package names, only from directory names, or only from transient code references. It should prefer missing a speculative change over confidently asserting the wrong architecture.
