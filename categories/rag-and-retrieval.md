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
The all-in-one AI productivity accelerator. On device and privacy first with no annoying setup or configuration.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): AnythingLLM is a distinctive all-in-one RAG platform emphasizing privacy-first, on-device deployment with minimal setup. Unlike LlamaIndex or Haystack (frameworks), this is a complete turnkey application combining document ingestion, vector storage, and chat. Strong adoption (59k stars) and active development fill the "ready-to-run RAG solution" niche.

#### Sources
- Repo: https://github.com/Mintplex-Labs/anything-llm
<!-- END TOOL: Mintplex-Labs/anything-llm -->

<!-- BEGIN TOOL: HKUDS/LightRAG -->
### LightRAG
<!-- repo: HKUDS/LightRAG -->

#### What it is
[EMNLP2025] "LightRAG: Simple and Fast Retrieval-Augmented Generation"

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `run-llama/llama_index`, `deepset-ai/haystack`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): LightRAG is a peer-reviewed (EMNLP 2025) RAG implementation emphasizing simplicity and speed, differentiating it from heavier frameworks like LlamaIndex and Haystack. With 34K stars and active development, it represents a meaningful lightweight option for engineers prioritizing performance.

#### Sources
- Repo: https://github.com/HKUDS/LightRAG
<!-- END TOOL: HKUDS/LightRAG -->

<!-- BEGIN TOOL: khoj-ai/khoj -->
### khoj
<!-- repo: khoj-ai/khoj -->

#### What it is
Your AI second brain. Self-hostable. Get answers from the web or your docs. Build custom agents, schedule automations, do deep research. Turn any online or local LLM into your personal, autonomous AI (gpt, claude, gemini, llama, qwen, mistral). Get started - free.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): Khoj is a self-hostable AI assistant for personal knowledge management with RAG over documents, web search, custom agents, and automation. With 34k stars, it occupies a distinctive "AI second brain" niche combining RAG with personal productivity features, differentiating it from developer-focused frameworks already tracked.

#### Sources
- Repo: https://github.com/khoj-ai/khoj
<!-- END TOOL: khoj-ai/khoj -->

<!-- BEGIN TOOL: VectifyAI/PageIndex -->
### PageIndex
<!-- repo: VectifyAI/PageIndex -->

#### What it is
📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): PageIndex presents a distinctive "vectorless" RAG approach using reasoning-based document indexing rather than traditional embeddings. This differentiates it from embedding-centric tools already tracked. With 25K+ stars and active development, it represents a novel retrieval paradigm worth tracking.

#### Sources
- Repo: https://github.com/VectifyAI/PageIndex
<!-- END TOOL: VectifyAI/PageIndex -->

<!-- BEGIN TOOL: neuml/txtai -->
### txtai
<!-- repo: neuml/txtai -->

#### What it is
💡 All-in-one AI framework for semantic search, LLM orchestration and language model workflows

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `run-llama/llama_index`, `deepset-ai/haystack`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): txtai is an established all-in-one framework for semantic search and RAG workflows with integrated vector database. While it overlaps with LlamaIndex and Haystack, it offers a distinctive single-package approach combining embeddings, search, and LLM orchestration. 12K+ stars and active maintenance suggest real adoption.

#### Sources
- Repo: https://github.com/neuml/txtai
<!-- END TOOL: neuml/txtai -->
