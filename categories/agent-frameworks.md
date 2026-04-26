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
