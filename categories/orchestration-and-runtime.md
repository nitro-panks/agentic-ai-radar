---
category: orchestration-and-runtime
tools:
  - { name: "Temporal", repo: "temporalio/temporal" }
  - { name: "Inngest",  repo: "inngest/inngest" }
last_reviewed: 2026-04-26
---

# Orchestration and Runtime

## Overview
Durable execution substrates — workflows that survive crashes, retries, timers, and signals. Increasingly relevant as agent runs grow longer than a single request and need exactly-once side effects.

## Decision heuristics
- Long-running agents, exactly-once side effects, polyglot SDKs → Temporal.
- TS / Node-first teams, want durable steps without standing up a Temporal cluster → Inngest.
- Short-lived request/response agents → skip the category.
- Domain-specific (genAI-flavored) abstractions → Dapr Agents / Hatchet (not yet expanded here).

## Tools

<!-- BEGIN TOOL: temporalio/temporal -->
### Temporal
<!-- repo: temporalio/temporal -->

#### What it is
Durable execution engine. Workflows-as-code with automatic state persistence, retries, timers, signals. Increasingly used as a substrate for long-running agents.

#### When to reach for it
- Agent workflows that must survive process crashes, run for hours/days, or need exactly-once side effects.

#### When not to
- Short-lived request/response agents — overkill.

#### Sources
- Repo: https://github.com/temporalio/temporal
<!-- END TOOL: temporalio/temporal -->

<!-- BEGIN TOOL: inngest/inngest -->
### Inngest
<!-- repo: inngest/inngest -->

#### What it is
Event-driven durable functions. Ergonomic SDK in TS/Python with step memoization — popular for background AI jobs and agent step graphs.

#### When to reach for it
- TS/Node-first teams that want durable steps without standing up Temporal.

#### When not to
- Polyglot enterprise stacks where Temporal's broader SDK ecosystem matters.

#### Sources
- Repo: https://github.com/inngest/inngest
<!-- END TOOL: inngest/inngest -->
