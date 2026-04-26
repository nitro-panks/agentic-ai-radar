---
category: model-routing
tools:
  - { name: "LiteLLM", repo: "BerriAI/litellm" }
  - { name: "gateway", repo: "Portkey-AI/gateway" }
  - { name: "plano", repo: "katanemo/plano" }
  - { name: "bifrost", repo: "maximhq/bifrost" }
last_reviewed: 2026-04-26
---

# Model Routing

## Overview
A unifying layer above many model providers. Two shapes: SDK (pull provider abstraction into your code) and proxy/gateway (centralize keys, budgeting, fallbacks, observability).

## Decision heuristics
- Single-provider app → use the provider SDK directly; routing is overhead.
- Multi-provider with team-level key/budget control → LiteLLM proxy.
- Hosted with no infra ownership → OpenRouter (commercial; not yet expanded here).
- Need provider-native features the unified surface flattens? Skip routing for that path.

## Tools

<!-- BEGIN TOOL: BerriAI/litellm -->
### LiteLLM
<!-- repo: BerriAI/litellm -->

#### What it is
Unified OpenAI-format SDK + proxy across 100+ model providers. The proxy adds key management, budgeting, fallback routing, caching, and observability hooks.

#### When to reach for it
- One API surface across OpenAI, Anthropic, Bedrock, Vertex, local.
- Centralized key/budget control at the org level.

#### When not to
- A single-provider app — direct SDK is simpler.
- You need provider-native features that the unified surface flattens away.

#### How it fits with other tools
Sits between agent frameworks and providers. Pairs with Langfuse/Helicone for observability.

#### Sources
- Repo: https://github.com/BerriAI/litellm
<!-- END TOOL: BerriAI/litellm -->

<!-- BEGIN TOOL: Portkey-AI/gateway -->
### gateway
<!-- repo: Portkey-AI/gateway -->

#### What it is
Open-source AI gateway that routes across a wide provider matrix and bundles guardrails, retries, fallbacks, load balancing, conditional routing, and an MCP gateway in one process. Vendor's enterprise feature set is being merged into the OSS v2.0 line.

#### When to reach for it
- You want routing *and* guardrails *and* MCP gateway behavior managed as a single, deployable middleware — not three separate tools.
- Vision/audio/image traffic is in the mix; multi-modal routing is a first-class concern, not a future hook.

#### When not to
- Single-provider Anthropic-direct flow with prompt caching working well — Portkey adds a hop and a moving part you don't need; LiteLLM is lighter for simpler multi-provider needs.
- You don't want to operate guardrails in the gateway layer (some teams prefer guardrails alongside the agent, closer to the prompt) — Portkey's bundled posture works against that.

#### Sources
- Repo: https://github.com/Portkey-AI/gateway
<!-- END TOOL: Portkey-AI/gateway -->

<!-- BEGIN TOOL: katanemo/plano -->
### plano
<!-- repo: katanemo/plano -->

#### What it is
Out-of-process data-plane proxy that pulls "rote plumbing" — agent routing, OTEL traces, guardrails, memory hooks, model routing — out of application code into a single sidecar. Language- and framework-agnostic, exposing the same surface to Python / TS / any HTTP client.

#### When to reach for it
- Polyglot stack — agents written across multiple languages or frameworks — and you want orchestration / observability / guardrails enforced once at the data-plane rather than re-implemented per language.
- You explicitly do not want core delivery concerns embedded in framework-specific abstractions; a sidecar that survives framework churn is the goal.

#### When not to
- Single Python codebase where in-process libraries (LangGraph for orchestration + Langfuse for tracing + LiteLLM for routing) cover the same ground with lower operational cost.
- You're early enough in the project that the sidecar's operational overhead outweighs the consistency win.

#### Sources
- Repo: https://github.com/katanemo/plano
<!-- END TOOL: katanemo/plano -->

<!-- BEGIN TOOL: maximhq/bifrost -->
### bifrost
<!-- repo: maximhq/bifrost -->

#### What it is
Single-binary AI gateway in Go, exposing an OpenAI-compatible API across a broad provider matrix. Ships a built-in web UI for ops, semantic caching, automatic failover, and cluster mode for HA deployments.

#### When to reach for it
- Go shop, or a team that prefers a self-hosted gateway with a built-in admin UI for non-engineers to configure providers and routing rules.
- You want HA / clustering at the gateway layer without operating LiteLLM at scale alongside its ecosystem.

#### When not to
- Python or TS team without operations capacity for a separate gateway service — LiteLLM stays in-process and is easier to reason about for a small fleet.
- You need rich guardrails and MCP gateway behavior bundled — Portkey's posture is a closer fit; Bifrost leans toward routing performance over the policy surface.

#### Sources
- Repo: https://github.com/maximhq/bifrost
<!-- END TOOL: maximhq/bifrost -->
