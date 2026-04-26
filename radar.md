# Radar

Top-level snapshot. Re-run scans periodically and update.

Last full sweep: 2026-04-26 (metrics-only; inbox-collect stages deferred — see `state/sweep-2026-04-26/manifest.md`)

## Headline picks by category

| Category | Default pick | Strong alternative | Notes |
|---|---|---|---|
| Agent framework (graph/control flow) | LangGraph | Pydantic AI | LangGraph for stateful multi-step; Pydantic AI when you want typed, minimal |
| Agent framework (multi-agent) | CrewAI | AutoGen | CrewAI more opinionated; AutoGen more research-flexible |
| Local model hosting | vLLM | Ollama | vLLM for throughput on GPUs; Ollama for laptop dev |
| Model routing | LiteLLM | OpenRouter | LiteLLM is OSS proxy; OpenRouter is hosted |
| Vector store (default) | Qdrant | pgvector | Qdrant for dedicated; pgvector when Postgres is already there |
| RAG framework | LlamaIndex | Haystack | LlamaIndex broader ecosystem |
| Eval / observability | Langfuse | Phoenix | Langfuse for traces+evals self-host; Phoenix for OTel-native |
| Code agent (terminal) | Aider | OpenHands | Aider mature; OpenHands more autonomous |
| Browser agent | Browser-Use | Stagehand | Both Playwright-based |
| Memory | Mem0 | Letta | |
| Security / red-team | Garak | promptfoo redteam | NVIDIA Garak is the broadest scanner |

## Trending watchlist (verify each sweep)

- MCP server ecosystem — explosion of community servers; track which are maintained vs. abandoned.
- Computer-use agents — Anthropic + open clones (e.g., OpenInterpreter forks).
- Durable agent runtimes — Temporal/Inngest/Restate patterns for long-running agents.
- Small open models tuned for tool-use — track releases that beat closed models on function-calling benchmarks.

## Recent changes log

<!-- prepend new entries; one line each -->
- 2026-04-26 — sweep #1: 43 repos refreshed via REST; 4 renames propagated (Ragas → vibrantlabsai, FastMCP → PrefectHQ, OpenHands → OpenHands org, Firecrawl → firecrawl org); Azure/PyRIT flagged archived upstream — needs successor investigation.
- 2026-04-26 — radar initialized.
