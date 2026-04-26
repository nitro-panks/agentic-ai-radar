---
category: observability
tools:
  - { name: "Langfuse",        repo: "langfuse/langfuse" }
  - { name: "Phoenix (Arize)", repo: "Arize-ai/phoenix" }
  - { name: "mlflow", repo: "mlflow/mlflow" }
  - { name: "opik", repo: "comet-ml/opik" }
  - { name: "RagaAI-Catalyst", repo: "raga-ai-hub/RagaAI-Catalyst" }
  - { name: "evidently", repo: "evidentlyai/evidently" }
  - { name: "openllmetry", repo: "traceloop/openllmetry" }
  - { name: "helicone", repo: "Helicone/helicone" }
  - { name: "logfire", repo: "pydantic/logfire" }
  - { name: "lmnr", repo: "lmnr-ai/lmnr" }
  - { name: "traceroot", repo: "traceroot-ai/traceroot" }
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

<!-- BEGIN TOOL: mlflow/mlflow -->
### mlflow
<!-- repo: mlflow/mlflow -->

#### What it is
Long-running open-source ML platform that has expanded into LLM/agent observability. The combined surface covers experiment tracking, a model registry, LLM tracing, eval/monitor, prompt management, prompt optimization, and an AI gateway — all under one roof.

#### When to reach for it
- Your team already runs MLflow for traditional ML and you want LLM observability inside the same platform rather than introducing a parallel stack.
- The use case spans both ML and LLM systems and the unified registry / experiment surface is doing real work.

#### When not to
- LLM-only shop with no traditional ML — Langfuse is purpose-built, lighter, and cleaner; MLflow's broader scope is overhead.
- You don't want to operate the MLflow tracking server — its operational footprint is real, especially at scale.

#### Sources
- Repo: https://github.com/mlflow/mlflow
<!-- END TOOL: mlflow/mlflow -->

<!-- BEGIN TOOL: comet-ml/opik -->
### opik
<!-- repo: comet-ml/opik -->

#### What it is
Open-source LLM observability + evaluation + automated optimization platform from Comet. Tracing for RAG/agents, LLM-as-judge evaluators, and a closed-loop prompt-and-tool optimizer that takes the trace data and proposes prompt/tool revisions.

#### When to reach for it
- You want trace → eval → automated prompt/tool optimization as one tight loop, not three composed tools.
- Comet is already in your stack and a unified product surface across model dev and LLM observability matters.

#### When not to
- You're satisfied with separate Langfuse (traces+evals) + promptfoo (prompt regression) and don't want a vendor-managed optimization layer.
- You don't trust automated prompt optimization for your editorial constraints — keeping a human in the loop on prompt edits is the goal.

#### Sources
- Repo: https://github.com/comet-ml/opik
<!-- END TOOL: comet-ml/opik -->

<!-- BEGIN TOOL: raga-ai-hub/RagaAI-Catalyst -->
### RagaAI-Catalyst
<!-- repo: raga-ai-hub/RagaAI-Catalyst -->

#### What it is
Bundled Python SDK around the RagaAI platform that combines tracing, dataset/eval management, prompt management, synthetic data generation, guardrails, and red-teaming under a single project surface — with explicit emphasis on multi-agentic system debugging (timeline + execution-graph views).

#### When to reach for it
- You want one batteries-included platform spanning trace + eval + guardrail + synthetic-data + red-team — and you're comfortable with the RagaAI-hosted backend that comes with it.
- Multi-agent execution-graph debugging is the bottleneck and you want a UI built around it rather than retrofitting Langfuse traces.

#### When not to
- Best-of-breed posture — you'd rather compose Langfuse + promptfoo + Garak than commit to one vendor's platform across all those concerns.
- Self-hosted-only shops where the hosted backend dependency isn't acceptable.

#### Sources
- Repo: https://github.com/raga-ai-hub/RagaAI-Catalyst
<!-- END TOOL: raga-ai-hub/RagaAI-Catalyst -->

<!-- BEGIN TOOL: evidentlyai/evidently -->
### evidently
<!-- repo: evidentlyai/evidently -->

#### What it is
ML and LLM observability framework with deep roots in tabular drift / data-quality monitoring, now extended to LLM evals (built-in LLM judges, RAG metrics). Reports become Test Suites with `gt`/`lt` pass/fail conditions — the canonical shape for CI-style data validation.

#### When to reach for it
- You're monitoring both ML systems (drift, data quality) and LLM systems and want one framework covering both — Evidently's tabular heritage means the ML side is first-class, not an afterthought.
- The Test Suite paradigm (regression-test-as-Python with `gt`/`lt` thresholds) fits how your CI is shaped.

#### When not to
- Pure LLM application — Langfuse is the better-shaped tool for trace-first observability; Evidently's tabular-first heritage is overhead you don't need.
- You want live trace tailing with rich UI — Evidently's monitoring is more dashboard-shaped than session-tail-shaped.

#### Sources
- Repo: https://github.com/evidentlyai/evidently
<!-- END TOOL: evidentlyai/evidently -->

<!-- BEGIN TOOL: traceloop/openllmetry -->
### openllmetry
<!-- repo: traceloop/openllmetry -->

#### What it is
OpenTelemetry-native instrumentation library for LLM apps and vector DBs. Standard OTel instrumentations for the major LLM providers and vector stores plus a Traceloop SDK; emits standard OTel data so it lands in Datadog / Honeycomb / Grafana / any OTel backend.

#### When to reach for it
- You already run OpenTelemetry through an existing observability stack and want LLM traces in the same pipe — no parallel UI, no duplicate traces.
- The team prefers vendor-neutral instrumentation (semantic conventions feeding back into OTel itself) over a single-vendor LLM observability product.

#### When not to
- You want a turnkey LLM-specific UI (timeline view, eval annotations, prompt diffs) — Langfuse and Phoenix are the right shape; OpenLLMetry is the instrumentation pipe, not a UI.
- No existing OTel infrastructure — the value is "feeds your existing OTel stack"; without one, you're building observability from scratch anyway.

#### Sources
- Repo: https://github.com/traceloop/openllmetry
<!-- END TOOL: traceloop/openllmetry -->

<!-- BEGIN TOOL: Helicone/helicone -->
### helicone
<!-- repo: Helicone/helicone -->

#### What it is
LLM observability + AI gateway in one product. Sits as an OpenAI-shaped proxy for many providers with intelligent routing, automatic fallbacks, cost/latency tracking, sessions for agents, prompt playground, and dataset/fine-tune workflows.

#### When to reach for it
- You'd rather buy gateway routing and observability as one product (proxy + dashboards) than compose LiteLLM + Langfuse separately.
- Quick integration matters — a single proxy URL gets you both routing and traces with minimal code change.

#### When not to
- You want gateway and observability cleanly decoupled (LiteLLM does routing; Langfuse owns observability) — Helicone bundles them, and that bundling is the friction for some teams.
- You don't want a proxy in the request path — direct Anthropic with prompt caching is faster and cheaper for single-provider flows.

#### Sources
- Repo: https://github.com/Helicone/helicone
<!-- END TOOL: Helicone/helicone -->

<!-- BEGIN TOOL: pydantic/logfire -->
### logfire
<!-- repo: pydantic/logfire -->

#### What it is
Observability platform from the Pydantic team. Opinionated wrapper over OpenTelemetry with Python-centric depth (rich Python-object display, event-loop telemetry, code/db-query profiling), SQL access to traces, and built-in analytics on Pydantic Validation models.

#### When to reach for it
- Heavy Python / Pydantic shop, especially Pydantic AI — Logfire's Python-centric framing and validation-model integration are the value prop and pair tightly with Pydantic AI agents.
- You want SQL over your traces (BI-tool-shaped query access) instead of a custom query DSL.

#### When not to
- Polyglot or non-Python primary stack — Logfire's Python-centric depth doesn't translate; Phoenix or Langfuse are language-agnostic.
- Self-hosted-only requirement — Logfire is SaaS-default; the OSS components don't yet replace the hosted platform end-to-end.

#### Sources
- Repo: https://github.com/pydantic/logfire
<!-- END TOOL: pydantic/logfire -->

<!-- BEGIN TOOL: lmnr-ai/lmnr -->
### lmnr
<!-- repo: lmnr-ai/lmnr -->

#### What it is
Laminar — agent-specific observability platform with OTel-native tracing (one-line auto-instrumentation for Vercel AI SDK, Browser Use, Stagehand, LangChain, the major model providers), evals SDK + CI runner, custom dashboards, SQL editor over traces, dataset annotation, and a Rust-backed real-time view engine.

#### When to reach for it
- Agent-shaped concerns are the bottleneck — browser-agent traces, multi-step tool-call sessions, custom dashboards built on SQL over your trace store.
- You want broad auto-instrumentation across the agentic-AI ecosystem (Vercel AI SDK, Browser Use, Stagehand) without writing instrumentation per framework.

#### When not to
- Plain prompt observability with broad community adoption mattering most — Langfuse is the safer choice; Laminar is younger and more agent-shaped.
- You don't need SQL access or custom dashboards — Laminar's value compounds with that depth; without it, you're paying for unused capability.

#### Sources
- Repo: https://github.com/lmnr-ai/lmnr
<!-- END TOOL: lmnr-ai/lmnr -->

<!-- BEGIN TOOL: traceroot-ai/traceroot -->
### traceroot
<!-- repo: traceroot-ai/traceroot -->

#### What it is
Observability + AI-debugging platform for agents. OpenTelemetry-compatible tracing SDK that captures LLM calls / agent actions / tool usage, plus an AI debugger that connects traces to a sandbox of your production source code and correlates failures with GitHub commits, PRs, and issues.

#### When to reach for it
- Production agents where root-causing failures across hallucinations, tool-call instabilities, and recent code changes is the actual bottleneck — TraceRoot's debugger surfaces "the failing line correlated with the PR that introduced it."
- Trace volume is high enough that manual inspection doesn't scale — the noise-filtering / signal-prioritization step earns its keep.

#### When not to
- Early-stage projects where manual trace inspection is fine and the team isn't shipping fast enough for code-correlation to compound — TraceRoot's value scales with both trace volume and code-change frequency.
- You don't want an AI agent reading your source code in a sandbox — the debugger pattern is core to the product, not optional.

#### Sources
- Repo: https://github.com/traceroot-ai/traceroot
<!-- END TOOL: traceroot-ai/traceroot -->
