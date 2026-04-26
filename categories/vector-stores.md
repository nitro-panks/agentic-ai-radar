---
category: vector-stores
tools:
  - { name: "Qdrant",   repo: "qdrant/qdrant" }
  - { name: "Weaviate", repo: "weaviate/weaviate" }
  - { name: "Chroma",   repo: "chroma-core/chroma" }
  - { name: "pgvector", repo: "pgvector/pgvector" }
  - { name: "Milvus",   repo: "milvus-io/milvus" }
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
