---
category: memory
tools:
  - { name: "Mem0",  repo: "mem0ai/mem0" }
  - { name: "Letta", repo: "letta-ai/letta" }
last_reviewed: 2026-04-26
---

# Memory

## Overview
Long-term, per-user, or self-editing memory for LLM apps. Distinct from RAG over a document corpus — the "documents" here are facts and preferences extracted from prior agent interactions.

## Decision heuristics
- Per-user personalization across sessions → Mem0.
- Stateful agents whose memory hierarchy is the central concern → Letta.
- Knowledge-graph flavored memory → Graphiti (not yet expanded here).
- Plain conversation history fits in context → don't add a memory tool.

## Tools

<!-- BEGIN TOOL: mem0ai/mem0 -->
### Mem0
<!-- repo: mem0ai/mem0 -->

#### What it is
Memory layer for LLM apps: extracts, stores, and retrieves personalized memories per user/agent. Pluggable vector + graph backends.

#### When to reach for it
- Apps that need stable per-user personalization across sessions.

#### When not to
- Single-session apps — context window is enough.

#### Sources
- Repo: https://github.com/mem0ai/mem0
<!-- END TOOL: mem0ai/mem0 -->

<!-- BEGIN TOOL: letta-ai/letta -->
### Letta
<!-- repo: letta-ai/letta -->

#### What it is
Stateful agents server (formerly MemGPT). Self-editing memory hierarchy (core/archival), agent-as-a-service runtime.

#### When to reach for it
- Long-lived agents whose memory evolves and is the central concern.

#### When not to
- You only need a memory *library* inside your own runtime — Mem0 is lighter.

#### Sources
- Repo: https://github.com/letta-ai/letta
<!-- END TOOL: letta-ai/letta -->
