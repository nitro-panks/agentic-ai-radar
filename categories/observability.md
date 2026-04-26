---
category: observability
tools:
  - { name: "Langfuse",        repo: "langfuse/langfuse" }
  - { name: "Phoenix (Arize)", repo: "Arize-ai/phoenix" }
last_reviewed: 2026-04-26
---

# Observability

## Overview
Traces, sessions, scores, and prompt management for LLM apps. Overlaps with evaluation — both tools ship eval tooling — but the entry point is "make production behavior visible."

## Decision heuristics
- Single self-hosted plane for tracing + evals + prompt versioning → Langfuse.
- OTel-native, you already standardized on OpenTelemetry → Phoenix.
- Hosted-only, no infra ownership → LangSmith (not yet expanded here).

## Tools

<!-- BEGIN TOOL: langfuse/langfuse -->
### Langfuse
<!-- repo: langfuse/langfuse -->

#### What it is
Self-hostable LLM observability + evals + prompt management. Traces, sessions, scores, datasets.

#### When to reach for it
- A single self-hosted plane for tracing, evals, and prompt versioning.
- Framework-agnostic — SDKs for Python/JS, OTel-compatible.

#### When not to
- You want OTel-first semantics; Phoenix's traces are closer to canonical OTel.

#### How it fits with other tools
Pairs with LangGraph, LlamaIndex, LiteLLM (all have integrations). Phoenix is the closest OSS competitor.

#### Sources
- Repo: https://github.com/langfuse/langfuse
<!-- END TOOL: langfuse/langfuse -->

<!-- BEGIN TOOL: Arize-ai/phoenix -->
### Phoenix (Arize)
<!-- repo: Arize-ai/phoenix -->

#### What it is
OTel-native LLM observability + evaluation from Arize. Strong on tracing semantics for retrieval and agents.

#### When to reach for it
- You're already standardized on OpenTelemetry.
- You want eval primitives close to traces.

#### When not to
- You want a single tool that also owns prompt management + datasets — Langfuse covers that breadth more directly.

#### Sources
- Repo: https://github.com/Arize-ai/phoenix
<!-- END TOOL: Arize-ai/phoenix -->
