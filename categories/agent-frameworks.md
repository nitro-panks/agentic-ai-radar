---
category: agent-frameworks
tools:
  - { name: "LangGraph",   repo: "langchain-ai/langgraph" }
  - { name: "LangChain",   repo: "langchain-ai/langchain" }
  - { name: "CrewAI",      repo: "crewAIInc/crewAI" }
  - { name: "AutoGen",     repo: "microsoft/autogen" }
  - { name: "Pydantic AI", repo: "pydantic/pydantic-ai" }
  - { name: "smolagents",  repo: "huggingface/smolagents" }
  - { name: "Agno",        repo: "agno-agi/agno" }
  - { name: "Dify",        repo: "langgenius/dify" }
  - { name: "Flowise",     repo: "FlowiseAI/Flowise" }
  - { name: "deer-flow", repo: "bytedance/deer-flow" }
  - { name: "UI-TARS-desktop", repo: "bytedance/UI-TARS-desktop" }
  - { name: "gpt-researcher", repo: "assafelovic/gpt-researcher" }
  - { name: "agentscope", repo: "agentscope-ai/agentscope" }
  - { name: "openfang", repo: "RightNow-AI/openfang" }
  - { name: "outlines", repo: "dottxt-ai/outlines" }
  - { name: "langchain4j", repo: "langchain4j/langchain4j" }
  - { name: "promptflow", repo: "microsoft/promptflow" }
  - { name: "hive", repo: "aden-hive/hive" }
  - { name: "GenericAgent", repo: "lsdefine/GenericAgent" }
  - { name: "rig", repo: "0xPlaygrounds/rig" }
  - { name: "youtu-agent", repo: "TencentCloudADP/youtu-agent" }
  - { name: "langroid", repo: "langroid/langroid" }
  - { name: "fast-agent", repo: "evalstate/fast-agent" }
last_reviewed: 2026-04-26
---

# Agent Frameworks

## Overview
The orchestration layer above the model SDK: how an LLM call becomes a multi-step, tool-using, possibly multi-agent program.

Sub-shapes worth distinguishing before picking:
- **Graph / control-flow first** — explicit state machines, durable, debuggable. *LangGraph*, Pydantic AI Graph.
- **Role / crew first** — multi-agent collaboration as the primary abstraction. *CrewAI*, *AutoGen*.
- **Code-execution first** — agent emits Python instead of JSON tool calls. *smolagents*.
- **Minimal / typed** — small surface, strict types. *Pydantic AI*.
- **Broad SDK / chains** — composable component libraries with a long tail of integrations. *LangChain*, *Agno*.
- **Visual builder / hosted platform** — drag-and-drop or self-host UI for assembling agents. *Flowise*, *Dify*.

## Decision heuristics
- Stateful workflows with branching/HITL → LangGraph.
- Multi-agent collaboration as the central concern → CrewAI (opinionated) or AutoGen (research-flexible).
- Strict typing, small surface → Pydantic AI.
- Heavy code-execution patterns → smolagents.
- Need durable, resumable, long-running execution? Pair with Temporal/Inngest, or use LangGraph Platform — most "frameworks" are in-process by default.
- Avoid stacking frameworks. If you're using LangGraph, don't also bring CrewAI for "the multi-agent part" — model multi-agent as a graph instead.

## Tools

<!-- BEGIN TOOL: langchain-ai/langgraph -->
### LangGraph
<!-- repo: langchain-ai/langgraph -->

#### What it is
Library for building stateful, multi-step agent workflows as directed graphs. Nodes are functions/LLM calls; edges encode control flow including loops, branches, and human-in-the-loop interrupts. Built by the LangChain team but usable without LangChain.

#### When to reach for it
- Workflows that need explicit state, retries, branching, or interruption/resume.
- Multi-agent setups where you want graph-level introspection over a "swarm" abstraction.
- When you need durable execution via LangGraph Platform / checkpointers.

#### When not to
- Simple single-shot prompt + tool-call — overkill, just use the SDK.
- If you want minimal magic and strict typing, prefer Pydantic AI.
- Heavy lock-in to LangChain ecosystem if you adopt the broader stack.

#### How it fits with other tools
Composes with LiteLLM for model routing, Langfuse/Phoenix for tracing. Competes with CrewAI, AutoGen, Pydantic AI Graph, smolagents at the orchestration layer.

#### Notable recent developments
- Track LangGraph Platform GA features and Studio updates each sweep.

#### Sources
- Docs: https://langchain-ai.github.io/langgraph/
- Repo: https://github.com/langchain-ai/langgraph
<!-- END TOOL: langchain-ai/langgraph -->

<!-- BEGIN TOOL: crewAIInc/crewAI -->
### CrewAI
<!-- repo: crewAIInc/crewAI -->

#### What it is
Opinionated multi-agent framework built around roles, tasks, and "crews" that collaborate. Independent of LangChain.

#### When to reach for it
- Role-based teams of agents (researcher, writer, reviewer) where the abstraction matches the problem.
- Quick prototypes that benefit from strong defaults.

#### When not to
- Highly custom control flow — prefer LangGraph or hand-rolled.
- When you want first-class graph state and time-travel debugging.

#### How it fits with other tools
Competes with AutoGen and LangGraph on multi-agent patterns. Often paired with LiteLLM for backend flexibility.

#### Sources
- Docs: https://docs.crewai.com/
- Repo: https://github.com/crewAIInc/crewAI
<!-- END TOOL: crewAIInc/crewAI -->

<!-- BEGIN TOOL: microsoft/autogen -->
### AutoGen
<!-- repo: microsoft/autogen -->

#### What it is
Microsoft Research framework for multi-agent conversation patterns. v0.4 split into `autogen-core` (event-driven runtime), `autogen-agentchat` (high-level), and `autogen-ext`.

#### When to reach for it
- Research-style experimentation with conversational agent patterns.
- Distributed/event-driven agents using the v0.4 core.

#### When not to
- Production systems wanting stable, narrow APIs — pace of change has been high.
- If you need a managed/durable platform — pair with Temporal or use LangGraph Platform.

#### Sources
- Docs: https://microsoft.github.io/autogen/
- Repo: https://github.com/microsoft/autogen
<!-- END TOOL: microsoft/autogen -->

<!-- BEGIN TOOL: pydantic/pydantic-ai -->
### Pydantic AI
<!-- repo: pydantic/pydantic-ai -->

#### What it is
Typed, minimalist agent framework from the Pydantic team. Strong structured outputs, dependency injection, and a `Graph` module for stateful flows.

#### When to reach for it
- Python codebases that already lean on Pydantic.
- You want strict types and small surface area.

#### When not to
- Need a sprawling integration ecosystem — LangChain still leads there.

#### Sources
- Docs: https://ai.pydantic.dev/
- Repo: https://github.com/pydantic/pydantic-ai
<!-- END TOOL: pydantic/pydantic-ai -->

<!-- BEGIN TOOL: huggingface/smolagents -->
### smolagents
<!-- repo: huggingface/smolagents -->

#### What it is
Hugging Face's small agent library. Distinguishing idea: code-writing agents that emit Python (executed in a sandbox) instead of JSON tool calls.

#### When to reach for it
- Tasks where the LLM benefits from writing actual code (data manipulation, multi-step math).
- You want tight integration with HF Hub models.

#### When not to
- Conservative environments where executing model-generated code is a non-starter — sandboxing complexity isn't worth it.

#### Sources
- Repo: https://github.com/huggingface/smolagents
<!-- END TOOL: huggingface/smolagents -->

<!-- BEGIN TOOL: langchain-ai/langchain -->
### LangChain
<!-- repo: langchain-ai/langchain -->

#### What it is
The original LangChain framework — a broad SDK for chaining LLM calls, tools, retrievers, and memory. Predates and underpins LangGraph; the wider ecosystem includes integrations for hundreds of providers and stores.

#### When to reach for it
- You want one library that already speaks to most providers and vector stores.
- Quick prototypes that benefit from off-the-shelf chains.

#### When not to
- Non-trivial control flow — graduate to LangGraph (graph-first state) rather than wedging Runnables.
- Strict typing / minimalism — Pydantic AI fits better.
- Long-term maintenance: the framework's API surface has churned; pin versions deliberately.

#### How it fits with other tools
LangGraph builds on LangChain primitives but is independently useful. Pairs with LiteLLM for routing, Langfuse for tracing.

#### Sources
- Repo: https://github.com/langchain-ai/langchain
<!-- END TOOL: langchain-ai/langchain -->

<!-- BEGIN TOOL: agno-agi/agno -->
### Agno
<!-- repo: agno-agi/agno -->

#### What it is
Multi-modal agent framework (formerly Phidata). Performance-oriented: claims very fast agent instantiation; first-class memory, tools, and reasoning steps.

#### When to reach for it
- Latency-sensitive agent workloads where framework overhead matters.
- You want batteries-included multi-modal (text + image + audio) without stitching libraries.

#### When not to
- LangChain ecosystem already covers your integrations — switching cost may not pay back.
- Project needs the maturity of LangGraph's graph debugging and HITL primitives.

#### Sources
- Repo: https://github.com/agno-agi/agno
<!-- END TOOL: agno-agi/agno -->

<!-- BEGIN TOOL: langgenius/dify -->
### Dify
<!-- repo: langgenius/dify -->

#### What it is
Self-hostable platform for building agentic workflows with a web UI. Combines workflow editor, RAG pipeline, model proxy, and ops in one product.

#### When to reach for it
- Non-engineers (or engineers prototyping fast) need a visual flow builder with auth, datasets, and observability included.
- You want a single self-hosted plane rather than wiring multiple OSS pieces.

#### When not to
- The product is the abstraction — if you need fine-grained control of agent state or want the framework as a library inside your code, this is the wrong shape.
- AGPL/commercial-license complications matter to your distribution model — read the license terms.

#### How it fits with other tools
Overlaps with Flowise on visual building; overlaps with Langfuse on observability (Dify includes its own).

#### Sources
- Repo: https://github.com/langgenius/dify
<!-- END TOOL: langgenius/dify -->

<!-- BEGIN TOOL: FlowiseAI/Flowise -->
### Flowise
<!-- repo: FlowiseAI/Flowise -->

#### What it is
Open-source visual builder for LLM apps and agents. Drag-and-drop graph editor with nodes for LangChain components, vector stores, model providers.

#### When to reach for it
- Quick prototyping of RAG / agent flows with visual feedback.
- Demos and internal tooling where the visual artifact is itself useful.

#### When not to
- Production code-as-source-of-truth — visual builders make code review and version control awkward.
- Heavy custom logic — escape hatches exist but you'll fight the abstraction.

#### Sources
- Repo: https://github.com/FlowiseAI/Flowise
<!-- END TOOL: FlowiseAI/Flowise -->

<!-- BEGIN TOOL: bytedance/deer-flow -->
### deer-flow
<!-- repo: bytedance/deer-flow -->

#### What it is
"Super-agent harness" that orchestrates sub-agents, memory, sandboxes, and skills for long-horizon work — research, coding, multi-step creation tasks that run for tens of minutes to hours rather than seconds. v2.0 is a ground-up rewrite; v1 lives on the `1.x` branch.

#### When to reach for it
- The unit of work is "spend an hour producing a researched deliverable" rather than "answer this prompt" — long-horizon research/coding pipelines where sub-agent + memory + sandbox composition is the design center.
- You want a vertical, opinionated harness rather than wiring sub-agents, memory, and sandbox runtime yourself on top of LangGraph.

#### When not to
- Short-horizon, request-response agents — LangGraph is lighter and the right shape; deer-flow's harness is overhead you don't need.
- You require API stability — v2 ships fast and v1 is a separate branch; pin to a commit if you adopt.

#### Sources
- Repo: https://github.com/bytedance/deer-flow
<!-- END TOOL: bytedance/deer-flow -->

<!-- BEGIN TOOL: bytedance/UI-TARS-desktop -->
### UI-TARS-desktop
<!-- repo: bytedance/UI-TARS-desktop -->

#### What it is
Multimodal agent stack tied to the UI-TARS vision-model family. Ships two surfaces: Agent TARS (CLI + Web UI for general multimodal task completion via MCP and computer-use tools) and UI-TARS Desktop (a native desktop app providing a GUI agent driven by the vision model with local and remote operators).

#### When to reach for it
- You're building computer-use agents that drive real desktop GUIs — not just browsers — and want a stack opinionated around vision-LLM-as-controller, with MCP wiring already in place.
- You're committed to (or evaluating) the UI-TARS model series; this is the canonical reference stack.

#### When not to
- Browser-only automation — Browser-Use or Stagehand are more focused; UI-TARS's desktop scope is overkill.
- Model-agnostic agent abstractions — UI-TARS is most coherent when paired with its namesake model; pure framework value falls off without it.

#### Sources
- Repo: https://github.com/bytedance/UI-TARS-desktop
<!-- END TOOL: bytedance/UI-TARS-desktop -->

<!-- BEGIN TOOL: assafelovic/gpt-researcher -->
### gpt-researcher
<!-- repo: assafelovic/gpt-researcher -->

#### What it is
Opinionated deep-research agent that produces cited, factual long-form reports from web and local sources. Architecture is plan-and-solve over parallel sub-agents that search, scrape, and synthesize — purpose-built for the "research-and-write-a-report" task shape.

#### When to reach for it
- You explicitly want the researcher use case — cited multi-source reports — not a general agent framework that you'd hand-roll into one.
- You need an opinionated, ready-to-run baseline rather than primitives; gpt-researcher gets you to a credible report in one command.

#### When not to
- General-purpose agentic flows — too narrow; LangGraph or CrewAI give you the building blocks for arbitrary shapes.
- You require fine-grained control over the search/synthesis loop — gpt-researcher's prescription works against deep customization.

#### Sources
- Repo: https://github.com/assafelovic/gpt-researcher
<!-- END TOOL: assafelovic/gpt-researcher -->

<!-- BEGIN TOOL: agentscope-ai/agentscope -->
### agentscope
<!-- repo: agentscope-ai/agentscope -->

#### What it is
Production-grade agent framework from Alibaba. Built-in ReAct, tools, skills, HITL, memory, planning, realtime voice, evaluation hooks, and model finetuning paths. First-class MCP/A2A, OTel observability, and deployment targets across local / serverless / Kubernetes.

#### When to reach for it
- Production deployment is the design center — you need OTel observability, K8s targets, MCP/A2A wiring, and a finetuning hook all from one framework rather than glued together.
- Multi-agent message-hub orchestration with strong tracing is a hard requirement.

#### When not to
- Quick prototyping or research scripts — overkill; CrewAI or smolagents are lighter.
- You don't want a framework with finetuning baked in — agentscope's "rising model capability" stance pulls toward custom-model territory you may not need.

#### Sources
- Repo: https://github.com/agentscope-ai/agentscope
<!-- END TOOL: agentscope-ai/agentscope -->

<!-- BEGIN TOOL: RightNow-AI/openfang -->
### openfang
<!-- repo: RightNow-AI/openfang -->

#### What it is
Single-binary "Agent OS" in Rust. Pitches autonomous "Hands" — agents that wake on schedules, build knowledge graphs, monitor targets, post to socials — rather than chat-style request/response. Ships its own dashboard; pre-1.0 with breaking changes between minor versions.

#### When to reach for it
- The agent shape is "always-on background worker that produces results to a dashboard," not "LLM call when the user prompts."
- You want a self-contained runtime (one binary, install script, dashboard) rather than orchestrating Python services and a separate scheduler.

#### When not to
- Interactive request/response agents — wrong shape; LangGraph or Pydantic AI are correct.
- Production stability is required — pre-1.0, expect breaking changes; pin to a commit if you adopt before v1.

#### Sources
- Repo: https://github.com/RightNow-AI/openfang
<!-- END TOOL: RightNow-AI/openfang -->

<!-- BEGIN TOOL: dottxt-ai/outlines -->
### outlines
<!-- repo: dottxt-ai/outlines -->

#### What it is
Decoder-level structured generation — constrains LLM output to a JSON Schema, regex, or formal grammar so the model literally cannot emit invalid tokens. Used inside vLLM, NVIDIA, Cohere, and HuggingFace inference paths.

#### When to reach for it
- You need *guaranteed* schema-compliant output (extracting fields from unstructured input, downstream parser is brittle) and your inference backend supports constrained decoding.
- The cost of post-hoc validate-and-retry exceeds the cost of pre-decode constraint — high-throughput pipelines where retry tail-latency matters.

#### When not to
- Anthropic-direct (or other closed-API-only) flows — constrained decoding requires logit access; Pydantic AI's validate-after pattern is the right shape there.
- The schema is loose enough that a Pydantic re-validate works fine — outlines adds complexity to the inference stack you don't need.

#### Sources
- Repo: https://github.com/dottxt-ai/outlines
<!-- END TOOL: dottxt-ai/outlines -->

<!-- BEGIN TOOL: langchain4j/langchain4j -->
### langchain4j
<!-- repo: langchain4j/langchain4j -->

#### What it is
Idiomatic LangChain-style library for the JVM. Unified API across many LLM providers and embedding stores; tool calling (including MCP), agents, RAG primitives, and out-of-the-box wiring for Quarkus and Spring Boot.

#### When to reach for it
- JVM shop (Java / Kotlin / Scala) — you need LangChain-equivalent abstractions inside your existing application stack, especially with Quarkus or Spring Boot conventions.
- You want a unified provider/embedding-store API without adopting a Python sidecar to host your AI logic.

#### When not to
- Polyglot or Python-leaning environments — Python LangGraph is more mature and reaching for langchain4j just to share patterns introduces JVM coupling for no win.
- You want LangGraph-style stateful graph orchestration — that's not langchain4j's core; it's the chains/agents/RAG surface, not graph-runtime.

#### Sources
- Repo: https://github.com/langchain4j/langchain4j
<!-- END TOOL: langchain4j/langchain4j -->

<!-- BEGIN TOOL: microsoft/promptflow -->
### promptflow
<!-- repo: microsoft/promptflow -->

#### What it is
Microsoft's end-to-end LLM-app dev suite. Visual flow authoring (LLMs + prompts + Python + tools as a DAG), tracing for LLM calls, integrated eval, and a deployment path that lands in Azure ML / Azure AI.

#### When to reach for it
- You're standardized on Azure tooling and want flow authoring + eval + deployment as one product, especially for cross-functional teams that benefit from a visual designer.
- Microsoft-backed governance/compliance story matters for your org's procurement.

#### When not to
- Code-first agent teams that prefer LangGraph-style explicit graphs in Python — promptflow's visual paradigm and Azure-leaning deployment surface adds friction for negative payoff.
- Non-Azure deployment targets — promptflow's value drops outside the Azure ecosystem.

#### Sources
- Repo: https://github.com/microsoft/promptflow
<!-- END TOOL: microsoft/promptflow -->

<!-- BEGIN TOOL: aden-hive/hive -->
### hive
<!-- repo: aden-hive/hive -->

#### What it is
Zero-setup multi-agent harness focused on production workloads — failure recovery, persistent role-based memory, observability, and human oversight. Compiles a graph-based execution DAG from a stated objective and runs specialized agents in parallel; ships native browser/computer-use extensions.

#### When to reach for it
- The unit of work is a long-running business workflow that needs explicit failure recovery and human-oversight points, not a chat loop — Hive's harness is built for that operational shape.
- You want multi-agent coordination + browser/computer-use as a single bundle rather than composing them yourself.

#### When not to
- You want fine-grained control over the agent loop — Hive's "zero-setup" abstractions push hard against customization; LangGraph + your own primitives are the right shape.
- Single-agent flows — overkill; the multi-agent runtime is the point.

#### Sources
- Repo: https://github.com/aden-hive/hive
<!-- END TOOL: aden-hive/hive -->

<!-- BEGIN TOOL: lsdefine/GenericAgent -->
### GenericAgent
<!-- repo: lsdefine/GenericAgent -->

#### What it is
Minimal self-evolving agent — small core (atomic browser / terminal / FS / keyboard / mouse / vision / ADB tools) plus an agent loop that crystallizes successful execution paths into named "skills." Skills accumulate across runs into a personal skill tree the agent can recall on similar tasks.

#### When to reach for it
- Single-machine, single-user autonomous agent that should *learn from its own runs* — the longer it operates, the more its skill library grows; explicit goal is reuse over re-derivation.
- You want maximum agent autonomy (full system control) and are comfortable owning the security envelope on your own machine.

#### When not to
- Production / multi-tenant deployments — the skill-evolution paradigm assumes one user's history; it doesn't generalize cleanly across tenants.
- Predictable, audit-friendly behavior is required — a self-modifying skill set is the opposite of what auditors want.

#### Sources
- Repo: https://github.com/lsdefine/GenericAgent
<!-- END TOOL: lsdefine/GenericAgent -->

<!-- BEGIN TOOL: 0xPlaygrounds/rig -->
### rig
<!-- repo: 0xPlaygrounds/rig -->

#### What it is
Rust-native library for LLM agents. Unified interface across many model providers and vector stores, GenAI semantic-convention OTel compatibility, multi-turn streaming, and full WASM compatibility for the core library.

#### When to reach for it
- Rust-first team — you want LangGraph-class abstractions but in your existing toolchain, with the compile-time guarantees Rust gives you.
- Edge / browser deployment is in scope and you need to compile your agent core to WASM; rig's WASM compatibility is a hard differentiator here.

#### When not to
- Python or TypeScript shop — rig's value is the Rust ergonomics; Pydantic AI / LangGraph cover the same ground without the toolchain shift.
- API stability is a hard requirement — the maintainers explicitly warn that future updates *will* contain breaking changes.

#### Sources
- Repo: https://github.com/0xPlaygrounds/rig
<!-- END TOOL: 0xPlaygrounds/rig -->

<!-- BEGIN TOOL: TencentCloudADP/youtu-agent -->
### youtu-agent
<!-- repo: TencentCloudADP/youtu-agent -->

#### What it is
Tencent agent framework optimized for open-weight models (DeepSeek-V3 et al.). Two paradigms: a Workflow mode for standard tasks and a Meta-Agent mode that auto-generates tool code, prompts, and configs. Includes a continuous-learning module (Training-Free GRPO) and an end-to-end Agent RL training pipeline.

#### When to reach for it
- You're committed to open-weight inference and want a framework whose benchmarks demonstrate they can compete with closed models without rewriting prompts for each model swap.
- Agent RL training or experience-based learning is in scope — youtu-agent's RL pipeline and GRPO module are first-class.

#### When not to
- Closed-API-only flow (Anthropic / OpenAI) — youtu-agent's open-model optimizations and RL infrastructure become irrelevant overhead.
- You want a small ReAct loop, not a meta-agent generation paradigm with auto-synthesized tools.

#### Sources
- Repo: https://github.com/TencentCloudADP/youtu-agent
<!-- END TOOL: TencentCloudADP/youtu-agent -->

<!-- BEGIN TOOL: langroid/langroid -->
### langroid
<!-- repo: langroid/langroid -->

#### What it is
Lightweight Python multi-agent framework built on the actor model — agents exchange messages to collaboratively solve a task, equipped optionally with LLM, vector store, and tools. From CMU / UW-Madison researchers; deliberately not built on LangChain or any other LLM framework.

#### When to reach for it
- The actor / message-passing model fits your problem naturally — specialized agents handing off via messages, not a single graph of stateful nodes.
- You want a clean, hackable Python library independent of the LangChain ecosystem.

#### When not to
- Single-agent flows — langroid's value is the actor abstraction; one actor is just a more complicated function call.
- Role/crew abstractions (manager, researcher, writer) fit your design better than bare actors — CrewAI is the closer shape.

#### Sources
- Repo: https://github.com/langroid/langroid
<!-- END TOOL: langroid/langroid -->

<!-- BEGIN TOOL: evalstate/fast-agent -->
### fast-agent
<!-- repo: evalstate/fast-agent -->

#### What it is
Interactive agent shell with first-class MCP and ACP integration — `/connect` to stdio or streamable-HTTP MCP servers (with OAuth), `/skills` to manage a skill registry, model packs for HF Inference / OpenAI Codex / local llama.cpp. Doubles as coding agent, dev toolkit, eval, and workflow platform.

#### When to reach for it
- MCP is central to your agent architecture — fast-agent's connect/skill commands are built around the protocol rather than retrofitted.
- You want an interactive shell experience for development and ad-hoc agent runs, with provider-pack switching baked in (Codex, HF, local).

#### When not to
- You don't want to live inside an interactive shell — your agent is a long-running service, not a development companion.
- Anthropic-direct only, no MCP usage in scope — fast-agent's value compounds with MCP; without it the value drops.

#### Sources
- Repo: https://github.com/evalstate/fast-agent
<!-- END TOOL: evalstate/fast-agent -->
