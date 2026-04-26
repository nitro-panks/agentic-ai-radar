---
category: rag-and-retrieval
tools:
  - { name: "LlamaIndex", repo: "run-llama/llama_index" }
  - { name: "Haystack",   repo: "deepset-ai/haystack" }
  - { name: "RAGFlow",    repo: "infiniflow/ragflow" }
  - { name: "GraphRAG",   repo: "microsoft/graphrag" }
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
