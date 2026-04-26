---
category: vector-stores
tools:
  - { name: "Qdrant",   repo: "qdrant/qdrant" }
  - { name: "Weaviate", repo: "weaviate/weaviate" }
  - { name: "Chroma",   repo: "chroma-core/chroma" }
  - { name: "pgvector", repo: "pgvector/pgvector" }
  - { name: "Milvus",   repo: "milvus-io/milvus" }
  - { name: "LEANN", repo: "yichuan-w/LEANN" }
  - { name: "orama", repo: "oramasearch/orama" }
  - { name: "lancedb", repo: "lancedb/lancedb" }
  - { name: "zvec", repo: "alibaba/zvec" }
  - { name: "deeplake", repo: "activeloopai/deeplake" }
last_reviewed: 2026-04-26
---

# Vector Stores

## Overview
Storage and ANN retrieval for embeddings. Picking is mostly about scale, hybrid-search needs, and whether Postgres is already in the stack.

## Decision heuristics
- Postgres already runs the show → pgvector. Transactional consistency between rows and embeddings is a meaningful win.
- New project, dedicated store, ≤ tens of millions of vectors → Qdrant.
- Hybrid (BM25 + vector) is central → Weaviate.
- Hundreds of millions to billions of vectors → Milvus.
- Notebook / prototype scale → Chroma.

## Tools

<!-- BEGIN TOOL: qdrant/qdrant -->
### Qdrant
<!-- repo: qdrant/qdrant -->

#### What it is
Vector DB written in Rust. Strong filtering, payload indexing, hybrid search, on-disk + quantization.

#### When to reach for it
- Default dedicated vector store for new projects.
- Heavy filter + vector hybrid queries.

#### When not to
- Postgres already runs the show — use pgvector.

#### Sources
- Repo: https://github.com/qdrant/qdrant
<!-- END TOOL: qdrant/qdrant -->

<!-- BEGIN TOOL: weaviate/weaviate -->
### Weaviate
<!-- repo: weaviate/weaviate -->

#### What it is
Vector DB with first-class hybrid search, modules for embeddings/generation, and a GraphQL API.

#### When to reach for it
- Hybrid (BM25 + vector) is central.
- You like its module system for batteries-included pipelines.

#### When not to
- You want a minimal core — the module system can be more than you need.

#### Sources
- Repo: https://github.com/weaviate/weaviate
<!-- END TOOL: weaviate/weaviate -->

<!-- BEGIN TOOL: chroma-core/chroma -->
### Chroma
<!-- repo: chroma-core/chroma -->

#### What it is
Embedded-first vector DB with a server mode. Friendly Python API; common default for prototypes.

#### When to reach for it
- Local prototypes, notebooks, small apps.

#### When not to
- Large-scale production — graduate to Qdrant/Milvus/pgvector.

#### Sources
- Repo: https://github.com/chroma-core/chroma
<!-- END TOOL: chroma-core/chroma -->

<!-- BEGIN TOOL: pgvector/pgvector -->
### pgvector
<!-- repo: pgvector/pgvector -->

#### What it is
Postgres extension for vector similarity. HNSW + IVFFlat indexes; works with everything that talks Postgres.

#### When to reach for it
- Postgres is already in the stack.
- You want transactional consistency between embeddings and rows.

#### When not to
- Billions of vectors — purpose-built stores scale further with less ops pain.

#### Sources
- Repo: https://github.com/pgvector/pgvector
<!-- END TOOL: pgvector/pgvector -->

<!-- BEGIN TOOL: milvus-io/milvus -->
### Milvus
<!-- repo: milvus-io/milvus -->

#### What it is
Distributed vector DB designed for very large scale. Cloud-native architecture; Zilliz is the commercial backer.

#### When to reach for it
- Hundreds of millions to billions of vectors.

#### When not to
- Small projects — operational complexity exceeds the benefit.

#### Sources
- Repo: https://github.com/milvus-io/milvus
<!-- END TOOL: milvus-io/milvus -->

<!-- BEGIN TOOL: yichuan-w/LEANN -->
### LEANN
<!-- repo: yichuan-w/LEANN -->

#### What it is
[MLsys2026]: RAG on Everything with LEANN. Enjoy 97% storage savings while running a fast, accurate, and 100% private RAG application on your personal device.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `chroma-core/chroma`, `qdrant/qdrant`, `milvus-io/milvus`, `weaviate/weaviate`, `pgvector/pgvector`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): LEANN is a research-backed vector database optimized for on-device RAG with 97% storage savings. Its focus on local, private deployment with extreme compression represents a distinctive niche versus scale-focused vector stores. MLsys2026 citation and MIT license suggest legitimate infrastructure worth tracking.

#### Sources
- Repo: https://github.com/yichuan-w/LEANN
<!-- END TOOL: yichuan-w/LEANN -->

<!-- BEGIN TOOL: oramasearch/orama -->
### orama
<!-- repo: oramasearch/orama -->

#### What it is
🌌  A complete search engine and RAG pipeline in your browser, server or edge network with support for full-text, vector, and hybrid search in less than 2kb.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): Orama is a sub-2kb vector database and search engine for browser, edge, and server with full-text, vector, and hybrid search. Unlike existing tracked vector stores (Chroma, Milvus, Qdrant, Weaviate, pgvector) which are server-side, Orama's tiny footprint and edge/browser-first design fill a clear niche for embedded RAG scenarios.

#### Sources
- Repo: https://github.com/oramasearch/orama
<!-- END TOOL: oramasearch/orama -->

<!-- BEGIN TOOL: lancedb/lancedb -->
### lancedb
<!-- repo: lancedb/lancedb -->

#### What it is
Developer-friendly OSS embedded retrieval library for multimodal AI. Search More; Manage Less.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `chroma-core/chroma`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.92): LanceDB is a distinctive embedded vector database optimized for multimodal AI retrieval. Its embedded architecture differentiates it from server-based options like Milvus/Qdrant, while its multimodal focus and Lance columnar format backing distinguish it from Chroma. At 10K+ stars, it's a real tool engineers evaluate.

#### Sources
- Repo: https://github.com/lancedb/lancedb
<!-- END TOOL: lancedb/lancedb -->

<!-- BEGIN TOOL: alibaba/zvec -->
### zvec
<!-- repo: alibaba/zvec -->

#### What it is
A lightweight, lightning-fast, in-process vector database

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): zvec is an in-process vector database from Alibaba, offering a distinct deployment model from tracked server-based solutions (Chroma, Milvus, Qdrant, Weaviate) and pgvector. Its "lightweight, in-process" positioning fills the SQLite-like niche for embedded vector search without a separate service. 9.5k stars and active development.

#### Sources
- Repo: https://github.com/alibaba/zvec
<!-- END TOOL: alibaba/zvec -->

<!-- BEGIN TOOL: activeloopai/deeplake -->
### deeplake
<!-- repo: activeloopai/deeplake -->

#### What it is
Deeplake is AI Data Runtime for Agents. It provides serverless postgres with a multimodal datalake, enabling scalable retrieval and training.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `chroma-core/chroma`, `qdrant/qdrant`, `weaviate/weaviate`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): Deep Lake is a multimodal vector database for AI agents emphasizing images, video, and text with versioning and streaming for retrieval and training. Unlike tracked pure vector stores, it bridges storage and training pipelines with "AI Data Runtime" positioning. 9.1k stars, actively maintained.

#### Sources
- Repo: https://github.com/activeloopai/deeplake
<!-- END TOOL: activeloopai/deeplake -->
