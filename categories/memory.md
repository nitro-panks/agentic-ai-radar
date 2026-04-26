---
category: memory
tools:
  - { name: "Mem0",  repo: "mem0ai/mem0" }
  - { name: "Letta", repo: "letta-ai/letta" }
  - { name: "SuperLocalMemory", repo: "qualixar/superlocalmemory" }
  - { name: "claude-mem", repo: "thedotmack/claude-mem" }
  - { name: "cognee", repo: "topoteretes/cognee" }
  - { name: "memvid", repo: "memvid/memvid" }
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

<!-- BEGIN TOOL: qualixar/superlocalmemory -->
### SuperLocalMemory
<!-- repo: qualixar/superlocalmemory -->

#### What it is
Local-only AI memory system exposing an MCP server (`mcp__superlocalmemory__*`) plus desktop app, with episodic/semantic/opinion memory types and per-project session context. Benchmarks itself against LoCoMo retrieval; ships a cloud-augmented "mode C" but defaults to fully local.

#### When to reach for it
- Privacy-sensitive workflows where memory must never leave the machine.
- Coding assistants that benefit from persistent per-project session context across runs.

#### When not to
- Multi-user / server-side personalization — Mem0 is the right shape.
- You need a memory hierarchy that the agent itself rewrites — Letta fits better.
- AGPL-3.0 license is incompatible with your distribution model.

#### How it fits with other tools
- Overlap with `mem0ai/mem0` and `letta-ai/letta`, but distinguished by the local-only / MCP-first posture.

#### Sources
- Repo: https://github.com/qualixar/superlocalmemory
<!-- END TOOL: qualixar/superlocalmemory -->

<!-- BEGIN TOOL: thedotmack/claude-mem -->
### claude-mem
<!-- repo: thedotmack/claude-mem -->

#### What it is
Claude Code-specific memory plugin. Captures the session transcript, summarizes it via the Claude agent SDK, and injects the digest into future sessions so context survives compactions and restarts.

#### When to reach for it
- You use Claude Code as your primary coding agent and want continuity across sessions without rebuilding context manually.
- The memory you care about is the *coding session itself* — what was tried, what worked — not user-level facts.

#### When not to
- You're on Cursor / Cline / a different code agent — this is wired specifically to Claude Code's hook surface.
- AGPL-3.0 is incompatible with what your dotfiles or workflows are licensed under.
- You want general per-user personalization that travels across tools — Mem0 is the right shape; this is the IDE-session shape.

#### Sources
- Repo: https://github.com/thedotmack/claude-mem
<!-- END TOOL: thedotmack/claude-mem -->

<!-- BEGIN TOOL: topoteretes/cognee -->
### cognee
<!-- repo: topoteretes/cognee -->

#### What it is
Knowledge-engine memory layer that combines vector search and graph storage. Ingests heterogeneous documents and builds a queryable graph of entities and relationships alongside the embeddings, so memory can be searched both by meaning and by structure.

#### When to reach for it
- The "memory" you need is over a document corpus where entities link to each other — meeting notes that reference projects, projects that reference people — and a flat fact store loses that structure.
- You want the graph layer up front rather than retrofitting one onto Mem0 or a plain vector store.

#### When not to
- Per-user fact personalization with no graph component — Mem0 is lighter and the right shape.
- A self-editing memory hierarchy that the agent itself rewrites — Letta is more aligned.
- Operating a graph DB alongside your vector store is more infrastructure than the use case justifies.

#### Sources
- Repo: https://github.com/topoteretes/cognee
<!-- END TOOL: topoteretes/cognee -->

<!-- BEGIN TOOL: memvid/memvid -->
### memvid
<!-- repo: memvid/memvid -->

#### What it is
Single-file, append-only memory layer in Rust. Packages embeddings, search index, and metadata into one immutable artifact ("Smart Frames") that an agent can load and query without a separate database or service.

#### When to reach for it
- You want portable memory that ships *with* the agent — embedded contexts, edge deployments, distributed agents that each need their own snapshot.
- You explicitly do not want to operate Postgres / Qdrant / Redis just to give an agent persistence.

#### When not to
- Multiple writers updating the same memory concurrently — append-only single-file storage is the wrong shape for that.
- You need queryable graph relationships across memories — Cognee is the right shape.
- Your team is Python-first and the Rust toolchain dependency is friction you don't want.

#### Sources
- Repo: https://github.com/memvid/memvid
<!-- END TOOL: memvid/memvid -->
