---
category: rag-and-retrieval
tools:
  - { name: "LlamaIndex", repo: "run-llama/llama_index" }
  - { name: "Haystack",   repo: "deepset-ai/haystack" }
  - { name: "RAGFlow",    repo: "infiniflow/ragflow" }
  - { name: "GraphRAG",   repo: "microsoft/graphrag" }
  - { name: "anything-llm", repo: "Mintplex-Labs/anything-llm" }
  - { name: "LightRAG", repo: "HKUDS/LightRAG" }
  - { name: "khoj", repo: "khoj-ai/khoj" }
  - { name: "PageIndex", repo: "VectifyAI/PageIndex" }
  - { name: "txtai", repo: "neuml/txtai" }
last_reviewed: 2026-04-26
---

# RAG and Retrieval

## Overview
Frameworks that turn a corpus + a query into a grounded LLM response. The category bundles ingestion, indexing, retrieval primitives, and increasingly an agent layer on top.

## Decision heuristics
- Heterogeneous data sources, broad connector ecosystem → LlamaIndex.
- Production-leaning typed pipelines → Haystack.
- High-fidelity PDF parsing + a usable web UI for end users → RAGFlow.
- Need only retrieval primitives over a vector DB → skip the framework; talk to the store directly.

## Tools

<!-- BEGIN TOOL: run-llama/llama_index -->
### LlamaIndex
<!-- repo: run-llama/llama_index -->

#### What it is
Data framework for LLMs: ingestion, indexing, retrieval, query engines, agents. Broad connector ecosystem (LlamaHub).

#### When to reach for it
- RAG over heterogeneous sources where connectors save real time.
- You want retrieval primitives plus an agent layer in one place.

#### When not to
- Pure agent control flow — use LangGraph or Pydantic AI.
- If you want minimal abstractions over a vector DB.

#### Sources
- Docs: https://docs.llamaindex.ai/
- Repo: https://github.com/run-llama/llama_index
<!-- END TOOL: run-llama/llama_index -->

<!-- BEGIN TOOL: deepset-ai/haystack -->
### Haystack
<!-- repo: deepset-ai/haystack -->

#### What it is
Production-oriented RAG/orchestration framework with a "pipelines and components" model. From deepset.

#### When to reach for it
- Enterprise-flavored RAG with strong typing on pipeline components.
- Search-heavy applications.

#### When not to
- Quick prototypes — LlamaIndex's lower setup cost wins.

#### Sources
- Repo: https://github.com/deepset-ai/haystack
<!-- END TOOL: deepset-ai/haystack -->

<!-- BEGIN TOOL: infiniflow/ragflow -->
### RAGFlow
<!-- repo: infiniflow/ragflow -->

#### What it is
Open RAG engine with a strong emphasis on deep document understanding (layout-aware parsing, tables, citations) and a usable web UI.

#### When to reach for it
- RAG over messy PDFs/docs where parsing fidelity matters.
- You want a self-hostable end-user UI, not just a library.

#### When not to
- Embedding RAG into a custom app — the UI-first stance becomes baggage.

#### Sources
- Repo: https://github.com/infiniflow/ragflow
<!-- END TOOL: infiniflow/ragflow -->

<!-- BEGIN TOOL: microsoft/graphrag -->
### GraphRAG
<!-- repo: microsoft/graphrag -->

#### What it is
Microsoft Research's modular graph-based RAG library. Constructs an entity/relation knowledge graph from a corpus, then answers queries by traversing it — usually outperforms vanilla similarity RAG on multi-hop / synthesis questions.

#### When to reach for it
- Question types like "summarize themes across this corpus" where similarity retrieval misses the structure.
- Documents with rich entity relationships (legal, scientific literature, intelligence).

#### When not to
- Cost-sensitive — building the graph is LLM-heavy and re-runs on corpus changes hurt.
- Simple FAQ / chatbot use cases where vanilla RAG is already good enough.

#### How it fits with other tools
Complements rather than competes with LlamaIndex / Haystack — usable as a retrieval backend within them. Also see LightRAG and similar academic descendants.

#### Sources
- Repo: https://github.com/microsoft/graphrag
<!-- END TOOL: microsoft/graphrag -->

<!-- BEGIN TOOL: Mintplex-Labs/anything-llm -->
### anything-llm
<!-- repo: Mintplex-Labs/anything-llm -->

#### What it is
Turnkey all-in-one chat-with-your-docs application: bundles ingestion, vector storage, multi-user workspaces, and an agent builder behind a desktop/Docker UI. Privacy-first defaults, runs locally with pluggable LLM and embedder providers.

#### When to reach for it
- You want a deployable end-user product (multi-user ChatGPT-over-our-docs) without writing a RAG stack from scratch.
- Non-developer teams need a self-hostable UI with document uploads, citations, and an MCP-compatible agent layer.

#### When not to
- Embedding RAG into your own application code — reach for LlamaIndex or Haystack as libraries instead.
- Heavy document parsing (complex PDFs, tables, layouts) — RAGFlow's parsing pipeline is stronger.

#### Sources
- Repo: https://github.com/Mintplex-Labs/anything-llm
<!-- END TOOL: Mintplex-Labs/anything-llm -->

<!-- BEGIN TOOL: HKUDS/LightRAG -->
### LightRAG
<!-- repo: HKUDS/LightRAG -->

#### What it is
EMNLP 2025 paper-and-implementation pairing entity/relation graph extraction with dual-level (local + global) retrieval. Pluggable storage backends (Postgres, Neo4j, MongoDB, OpenSearch) and a web UI for graph inspection.

#### When to reach for it
- You want graph-based RAG with cheaper graph construction and incremental updates than the full GraphRAG pipeline.
- Multi-hop or thematic queries where dual-level (entity-near + community-wide) retrieval beats vanilla similarity.

#### When not to
- The Microsoft GraphRAG community-summary methodology is what you actually want — go straight to GraphRAG.
- Plain similarity RAG over a small corpus — LlamaIndex with a vector store is simpler and cheaper to build.

#### Sources
- Repo: https://github.com/HKUDS/LightRAG
<!-- END TOOL: HKUDS/LightRAG -->

<!-- BEGIN TOOL: khoj-ai/khoj -->
### khoj
<!-- repo: khoj-ai/khoj -->

#### What it is
Self-hostable personal-AI app: semantic search and chat over your notes, PDFs, Org/Markdown, Notion, plus the open web, with scheduled research and agent personas. Surfaces from browser, Obsidian, Emacs, desktop, mobile, or WhatsApp clients.

#### When to reach for it
- An end-user "second brain" over personal docs and the web, with multi-client access (Obsidian/Emacs/mobile) out of the box.
- You want scheduled deep-research and notification automations bundled with retrieval, not just a library.

#### When not to
- Developer-focused RAG embedded in your own product — use LlamaIndex or Haystack instead.
- Team/enterprise document chat with workspace permissions — anything-llm or RAGFlow is closer to that shape.

#### Sources
- Repo: https://github.com/khoj-ai/khoj
<!-- END TOOL: khoj-ai/khoj -->

<!-- BEGIN TOOL: VectifyAI/PageIndex -->
### PageIndex
<!-- repo: VectifyAI/PageIndex -->

#### What it is
Vectorless, reasoning-based RAG: builds a hierarchical table-of-contents tree per document and lets an LLM tree-search it instead of doing similarity over chunks. Aimed at long professional documents (financial filings, regulations, textbooks) where similarity ≠ relevance.

#### When to reach for it
- Long structured documents where section hierarchy matters and chunk-similarity retrieval keeps missing the right passage.
- You want explainable, traceable retrieval (page and section references) rather than opaque vector neighbors.

#### When not to
- Large heterogeneous corpora where TOC trees per document don't compose — LlamaIndex with a vector store fits better.
- Cross-document synthesis driven by entity relationships — GraphRAG (or LightRAG) is the right shape.

#### Sources
- Repo: https://github.com/VectifyAI/PageIndex
<!-- END TOOL: VectifyAI/PageIndex -->

<!-- BEGIN TOOL: neuml/txtai -->
### txtai
<!-- repo: neuml/txtai -->

#### What it is
Single-package framework whose core is an embeddings database unifying sparse + dense vector indexes, graph networks, and a relational store, with pipelines, workflows, and agents layered on top. Apache-2.0, low-footprint, with bindings for JS/Java/Rust/Go and an MCP API.

#### When to reach for it
- You want one batteries-included Python dependency that handles embeddings, semantic search, and LLM workflows without wiring a separate vector store.
- Multimodal indexing (text/audio/image/video) inside a single embeddings index, served via FastAPI or MCP.

#### When not to
- Large RAG systems needing rich connectors, query engines, and a wide ecosystem — LlamaIndex's surface area is bigger.
- Typed production pipelines with explicit component contracts — Haystack's pipeline model fits better.

#### Sources
- Repo: https://github.com/neuml/txtai
<!-- END TOOL: neuml/txtai -->
