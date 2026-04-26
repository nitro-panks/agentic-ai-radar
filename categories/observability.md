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
The open source AI engineering platform for agents, LLMs, and ML models. MLflow enables teams of all sizes to debug, evaluate, monitor, and optimize production-quality AI applications while controlling costs and managing access to models and data.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): MLflow is a mature, widely-adopted platform for experiment tracking, evaluation, and monitoring AI/ML deployments. It has expanded into LLMops with prompt engineering, agent monitoring, and evaluation. Distinct from Phoenix/Langfuse by combining experiment tracking, model registry, and production monitoring in one platform.

#### Sources
- Repo: https://github.com/mlflow/mlflow
<!-- END TOOL: mlflow/mlflow -->

<!-- BEGIN TOOL: comet-ml/opik -->
### opik
<!-- repo: comet-ml/opik -->

#### What it is
Debug, evaluate, and monitor your LLM applications, RAG systems, and agentic workflows with comprehensive tracing, automated evaluations, and production-ready dashboards.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.92): Opik is a comprehensive LLM observability platform with tracing, automated evaluations, and production-ready dashboards. At ~19K stars with active development, it competes with Phoenix and Langfuse but offers distinctive features for monitoring agentic workflows and RAG systems.

#### Sources
- Repo: https://github.com/comet-ml/opik
<!-- END TOOL: comet-ml/opik -->

<!-- BEGIN TOOL: raga-ai-hub/RagaAI-Catalyst -->
### RagaAI-Catalyst
<!-- repo: raga-ai-hub/RagaAI-Catalyst -->

#### What it is
Python SDK for Agent AI Observability, Monitoring and Evaluation Framework. Includes features like agent, llm and tools tracing, debugging multi-agentic system, self-hosted dashboard and advanced analytics with timeline and execution graph view

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): Python SDK for agent observability with tracing, multi-agent debugging, and self-hosted dashboards. Combines monitoring with evaluation features. Overlaps with Phoenix and Langfuse but emphasizes multi-agentic system debugging. 16k+ stars and active development suggest real adoption.

#### Sources
- Repo: https://github.com/raga-ai-hub/RagaAI-Catalyst
<!-- END TOOL: raga-ai-hub/RagaAI-Catalyst -->

<!-- BEGIN TOOL: evidentlyai/evidently -->
### evidently
<!-- repo: evidentlyai/evidently -->

#### What it is
Evidently is ​​an open-source ML and LLM observability framework. Evaluate, test, and monitor any AI-powered system or data pipeline. From tabular data to Gen AI. 100+ metrics.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Evidently is an established ML/LLM observability framework with 7400+ stars. It provides 100+ metrics for evaluation, testing, and monitoring of AI systems. While overlapping with Phoenix and Langfuse, Evidently has distinctive focus on data quality monitoring and test suites that complements existing tools.

#### Sources
- Repo: https://github.com/evidentlyai/evidently
<!-- END TOOL: evidentlyai/evidently -->

<!-- BEGIN TOOL: traceloop/openllmetry -->
### openllmetry
<!-- repo: traceloop/openllmetry -->

#### What it is
Open-source observability for your GenAI or LLM application, based on OpenTelemetry

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): OpenLLMetry provides OpenTelemetry-native observability for LLM applications with automatic instrumentation across multiple frameworks. It offers a vendor-neutral, standards-based approach that complements Phoenix and Langfuse, appealing to teams invested in OTel infrastructure. Active development with 7K+ stars.

#### Sources
- Repo: https://github.com/traceloop/openllmetry
<!-- END TOOL: traceloop/openllmetry -->

<!-- BEGIN TOOL: Helicone/helicone -->
### helicone
<!-- repo: Helicone/helicone -->

#### What it is
🧊 Open source LLM observability platform. One line of code to monitor, evaluate, and experiment. YC W23 🍓

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Helicone is a YC-backed LLM observability platform offering monitoring, evaluation, and experimentation. The "one line of code" integration and combined feature set differentiate it from existing tools like Phoenix and Langfuse, which focus more narrowly on tracing or analytics.

#### Sources
- Repo: https://github.com/Helicone/helicone
<!-- END TOOL: Helicone/helicone -->

<!-- BEGIN TOOL: pydantic/logfire -->
### logfire
<!-- repo: pydantic/logfire -->

#### What it is
AI observability platform for production LLM and agent systems.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Pydantic Logfire is a production AI observability platform from the Pydantic team, with OpenTelemetry integration and structured tracing for LLM/agent systems. While overlapping with Phoenix and Langfuse, it brings a distinct type-safety approach and warrants inclusion as a credible alternative.

#### Sources
- Repo: https://github.com/pydantic/logfire
<!-- END TOOL: pydantic/logfire -->

<!-- BEGIN TOOL: lmnr-ai/lmnr -->
### lmnr
<!-- repo: lmnr-ai/lmnr -->

#### What it is
Laminar - open-source observability platform purpose-built for AI agents. YC S24.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Laminar is purpose-built observability for AI agents, not just general LLM tracing. YC S24-backed with 2.8k stars and active development. Offers agent-specific focus that differentiates it from Phoenix and Langfuse's broader LLM monitoring approach.

#### Sources
- Repo: https://github.com/lmnr-ai/lmnr
<!-- END TOOL: lmnr-ai/lmnr -->

<!-- BEGIN TOOL: traceroot-ai/traceroot -->
### traceroot
<!-- repo: traceroot-ai/traceroot -->

#### What it is
TraceRoot - open-source observability and self-healing layer for AI agents. YC S25

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `Arize-ai/phoenix`, `langfuse/langfuse`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): TraceRoot is an observability tool for AI agents with a distinctive "self-healing" layer (likely automated remediation). YC S25 backed and actively maintained. While it overlaps with Phoenix and Langfuse in monitoring, the self-healing angle is a novel differentiator worth tracking.

#### Sources
- Repo: https://github.com/traceroot-ai/traceroot
<!-- END TOOL: traceroot-ai/traceroot -->
