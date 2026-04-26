---
category: model-routing
tools:
  - { name: "LiteLLM", repo: "BerriAI/litellm" }
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
