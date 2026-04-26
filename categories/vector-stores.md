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
Research-backed embedded index for on-device RAG. Uses graph-based selective recomputation and high-degree preserving pruning to skip storing per-vector embeddings, trading compute for radically smaller indexes.

#### When to reach for it
- Personal/private RAG over messy local data (files, mail, browser history, chat logs) on a single laptop where storage is the binding constraint.
- You want a semantic search MCP that drops into Claude Code or similar agent runtimes without shipping data to the cloud.

#### When not to
- Multi-tenant or server-side workloads with concurrent writers — reach for `qdrant/qdrant` instead.
- Hundreds of millions of vectors across a cluster — `milvus-io/milvus` is the right shape.

#### Sources
- Repo: https://github.com/yichuan-w/LEANN
<!-- END TOOL: yichuan-w/LEANN -->

<!-- BEGIN TOOL: oramasearch/orama -->
### orama
<!-- repo: oramasearch/orama -->

#### What it is
Tiny TypeScript search engine that ships full-text, vector, and hybrid (BM25 + vector) search in a footprint small enough to run inside the browser, a Worker, or an edge function.

#### When to reach for it
- Client-side or edge RAG where the index ships with the bundle and queries never leave the device — docs sites, in-app help, edge personalization.
- JS/TS-native stacks that want one library covering BM25, typo tolerance, facets, and vector search without standing up a service.

#### When not to
- Server-side workloads holding more than a single machine's worth of vectors — use `qdrant/qdrant` for a dedicated engine, or `weaviate/weaviate` if hybrid search at scale is the centerpiece.

#### Sources
- Repo: https://github.com/oramasearch/orama
<!-- END TOOL: oramasearch/orama -->

<!-- BEGIN TOOL: lancedb/lancedb -->
### lancedb
<!-- repo: lancedb/lancedb -->

#### What it is
Embedded multimodal "lakehouse" for AI: vector + full-text + SQL over the Lance columnar format, with zero-copy versioning and object-store-native storage so the same files back search, training, and analytics.

#### When to reach for it
- Multimodal corpora (images, video, point clouds, text) where you want vector search, SQL filters, and dataloader access against the same underlying files.
- Embedded retrieval in Python/TS/Rust apps that need to outgrow a notebook prototype without standing up a cluster — replaces a `chroma-core/chroma` default once data lives on S3/GCS.

#### When not to
- A live, multi-writer transactional service where embeddings must stay consistent with relational rows — use `pgvector/pgvector`.
- A pure dedicated-server vector engine with rich filtering primitives — `qdrant/qdrant` is more focused.

#### Sources
- Repo: https://github.com/lancedb/lancedb
<!-- END TOOL: lancedb/lancedb -->

<!-- BEGIN TOOL: alibaba/zvec -->
### zvec
<!-- repo: alibaba/zvec -->

#### What it is
SQLite-shaped in-process vector database from Alibaba: dense + sparse vectors, hybrid filters, WAL-backed durability, and multi-reader / single-writer concurrency, with Python/Node/C bindings.

#### When to reach for it
- Embedding an ANN index inside a CLI, agent, or service that wants durability and hybrid filtering without running a separate database process.
- Battle-tested production constraints (WAL, crash safety) in an embedded form — a step up from `chroma-core/chroma` when prototype-grade persistence isn't enough but you still don't want a server.

#### When not to
- Multi-tenant or distributed serving where many writers and replicas matter — use `qdrant/qdrant`, or `milvus-io/milvus` once you push past a single node.

#### Sources
- Repo: https://github.com/alibaba/zvec
<!-- END TOOL: alibaba/zvec -->

<!-- BEGIN TOOL: activeloopai/deeplake -->
### deeplake
<!-- repo: activeloopai/deeplake -->

#### What it is
Serverless multimodal data lake from Activeloop that doubles as a vector store: tensors, embeddings, images, video, and DICOM live in the same versioned format on object storage, with PyTorch/TF dataloaders and LangChain/LlamaIndex hooks.

#### When to reach for it
- Teams that want one substrate for both training datasets and RAG retrieval over heavy multimodal data, with versioning and lineage instead of a separate vector service.
- Cloud-resident corpora (S3/GCS/Azure) where streaming to trainers and serving similarity search from the same files is the win.

#### When not to
- Pure low-latency text RAG with rich payload filters — `qdrant/qdrant` is leaner.
- Hybrid BM25 + vector retrieval as the central pattern — `weaviate/weaviate` ships that out of the box.

#### Sources
- Repo: https://github.com/activeloopai/deeplake
<!-- END TOOL: activeloopai/deeplake -->
