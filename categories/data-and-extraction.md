---
category: data-and-extraction
tools:
  - { name: "Firecrawl",    repo: "firecrawl/firecrawl" }
  - { name: "Crawl4AI",     repo: "unclecode/crawl4ai" }
  - { name: "Docling",      repo: "docling-project/docling" }
  - { name: "Unstructured", repo: "Unstructured-IO/unstructured" }
  - { name: "llm-scraper", repo: "mishushakov/llm-scraper" }
last_reviewed: 2026-04-26
---

# Data and Extraction

## Overview
Turning the web and arbitrary documents into clean, LLM-consumable Markdown / JSON. Quality of parsing dominates downstream RAG quality far more than embedding-model choice.

## Decision heuristics
- Hosted web → markdown crawl → Firecrawl.
- Self-hosted Python crawl at scale → Crawl4AI.
- High-fidelity PDFs (especially with tables) → Docling.
- Heterogeneous file types where you need one library to handle all of them → Unstructured.

## Tools

<!-- BEGIN TOOL: firecrawl/firecrawl -->
### Firecrawl
<!-- repo: firecrawl/firecrawl -->

#### What it is
Web → LLM-ready Markdown. Scrape, crawl, and structured extraction with JS rendering. Hosted + self-host.

#### When to reach for it
- Building RAG corpora or research agents that need clean web content.

#### When not to
- Tightly controlled sites where you want hand-tuned scrapers.

#### Sources
- Repo: https://github.com/firecrawl/firecrawl
<!-- END TOOL: firecrawl/firecrawl -->

<!-- BEGIN TOOL: unclecode/crawl4ai -->
### Crawl4AI
<!-- repo: unclecode/crawl4ai -->

#### What it is
Python crawler tuned for LLM consumption — clean Markdown, async, browser-based, schema-aware extraction.

#### When to reach for it
- Self-hosted, code-first crawling at scale; alternative to hosted Firecrawl.

#### When not to
- You want a hosted service with no infra — Firecrawl.

#### Sources
- Repo: https://github.com/unclecode/crawl4ai
<!-- END TOOL: unclecode/crawl4ai -->

<!-- BEGIN TOOL: docling-project/docling -->
### Docling
<!-- repo: docling-project/docling -->

#### What it is
IBM-originated document parser — PDF/DOCX/PPTX/HTML to structured Markdown/JSON with layout, tables, and figures preserved. Now under LF AI & Data.

#### When to reach for it
- High-fidelity document ingestion for RAG, especially complex PDFs with tables.

#### When not to
- Web content — use Firecrawl/Crawl4AI.

#### Sources
- Repo: https://github.com/docling-project/docling
<!-- END TOOL: docling-project/docling -->

<!-- BEGIN TOOL: Unstructured-IO/unstructured -->
### Unstructured
<!-- repo: Unstructured-IO/unstructured -->

#### What it is
Library for parsing many file types into normalized elements for LLM/RAG pipelines.

#### When to reach for it
- Heterogeneous file types where one normalization layer simplifies ingestion.

#### When not to
- Specialized PDFs — Docling parses them better.

#### Sources
- Repo: https://github.com/Unstructured-IO/unstructured
<!-- END TOOL: Unstructured-IO/unstructured -->

<!-- BEGIN TOOL: mishushakov/llm-scraper -->
### llm-scraper
<!-- repo: mishushakov/llm-scraper -->

#### What it is
TypeScript library that combines Playwright with an LLM to extract Zod-schema-typed structured data from any webpage. Supports HTML / raw HTML / markdown / text / image input modes and works against the major model families via the Vercel AI SDK.

#### When to reach for it
- TypeScript pipeline that needs schema-validated structured extraction from a real, possibly JS-rendered webpage — not just clean markdown.
- You want type-safety on the extracted shape (Zod) and full control over which model performs the extraction step.

#### When not to
- You just need clean markdown of a page for downstream RAG — Firecrawl is the right shape and doesn't bind you to the TS / Playwright stack.
- Self-hosted, scaled crawling — Crawl4AI fits that better; llm-scraper is a per-page extraction tool, not a crawler.

#### Sources
- Repo: https://github.com/mishushakov/llm-scraper
<!-- END TOOL: mishushakov/llm-scraper -->
