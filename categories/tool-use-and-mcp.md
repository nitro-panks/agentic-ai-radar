---
category: tool-use-and-mcp
tools:
  - { name: "Model Context Protocol", repo: "modelcontextprotocol/modelcontextprotocol" }
  - { name: "FastMCP",                repo: "PrefectHQ/fastmcp" }
  - { name: "chrome-devtools-mcp", repo: "ChromeDevTools/chrome-devtools-mcp" }
  - { name: "github-mcp-server", repo: "github/github-mcp-server" }
  - { name: "composio", repo: "ComposioHQ/composio" }
  - { name: "serena", repo: "oraios/serena" }
  - { name: "Skill_Seekers", repo: "yusufkaraaslan/Skill_Seekers" }
  - { name: "mcp-use", repo: "mcp-use/mcp-use" }
  - { name: "claude-context", repo: "zilliztech/claude-context" }
  - { name: "cursor-talk-to-figma-mcp", repo: "grab/cursor-talk-to-figma-mcp" }
  - { name: "XcodeBuildMCP", repo: "getsentry/XcodeBuildMCP" }
  - { name: "openagent", repo: "the-open-agent/openagent" }
  - { name: "mcp-context-forge", repo: "IBM/mcp-context-forge" }
  - { name: "arxiv-mcp-server", repo: "blazickjp/arxiv-mcp-server" }
  - { name: "metamcp", repo: "metatool-ai/metamcp" }
  - { name: "google_workspace_mcp", repo: "taylorwilsdon/google_workspace_mcp" }
last_reviewed: 2026-04-26
---

# Tool Use and MCP

## Overview
The Model Context Protocol (MCP) is becoming the de facto standard for connecting LLM apps to tools, resources, and prompts. Adopting MCP decouples your tool surface from any single agent framework or client.

## Decision heuristics
- Building a tool integration that should work across multiple clients (Claude, Cursor, Cline, etc.) → MCP server.
- Standing up an MCP server quickly in Python → FastMCP.
- TS / Node side → official `@modelcontextprotocol/sdk`.
- Don't reinvent: cross-reference `awesome-mcp-servers` before writing one yourself.

## Tools

<!-- BEGIN TOOL: modelcontextprotocol/modelcontextprotocol -->
### Model Context Protocol
<!-- repo: modelcontextprotocol/modelcontextprotocol -->

#### What it is
Open protocol from Anthropic for connecting LLM apps to tools, resources, and prompts via standardized servers/clients. JSON-RPC over stdio or HTTP.

#### When to reach for it
- One tool integration usable across many clients.
- An internal "tool-shelf" decoupled from any one agent framework.

#### When not to
- Single-app, single-client use where the protocol overhead earns nothing.

#### How it fits with other tools
Curated server lists: `punkpeye/awesome-mcp-servers`. FastMCP and the official SDKs are the easiest server entry points.

#### Sources
- Spec: https://modelcontextprotocol.io/
- Repo: https://github.com/modelcontextprotocol/modelcontextprotocol
<!-- END TOOL: modelcontextprotocol/modelcontextprotocol -->

<!-- BEGIN TOOL: PrefectHQ/fastmcp -->
### FastMCP
<!-- repo: PrefectHQ/fastmcp -->

#### What it is
Pythonic MCP server framework — decorate functions to expose tools/resources. Pieces of v2 were upstreamed into the official Python SDK; FastMCP itself remains the higher-level dev experience.

#### When to reach for it
- Standing up an MCP server quickly in Python.

#### When not to
- TS / Node — use the official SDK.

#### Sources
- Repo: https://github.com/PrefectHQ/fastmcp
<!-- END TOOL: PrefectHQ/fastmcp -->

<!-- BEGIN TOOL: ChromeDevTools/chrome-devtools-mcp -->
### chrome-devtools-mcp
<!-- repo: ChromeDevTools/chrome-devtools-mcp -->

#### What it is
Official MCP server from the Chrome DevTools team that exposes the full DevTools surface — performance traces, network requests, console messages with source-mapped stack traces, screenshots — to a coding agent. Uses Puppeteer underneath for reliable automation; CLI also available without MCP.

#### When to reach for it
- A coding agent needs to debug or profile a real Chrome session — repro a bug from a stack trace, capture a perf trace, inspect failing network calls.
- You want first-party DevTools access rather than reinventing the inspection surface on top of raw browser automation.

#### When not to
- Click/type browser automation against the public DOM — Browser-Use or Stagehand are the right shape; chrome-devtools-mcp is for inspection/debugging, not navigation.
- Non-Chromium target — only Google Chrome and Chrome for Testing are officially supported.

#### Sources
- Repo: https://github.com/ChromeDevTools/chrome-devtools-mcp
<!-- END TOOL: ChromeDevTools/chrome-devtools-mcp -->

<!-- BEGIN TOOL: github/github-mcp-server -->
### github-mcp-server
<!-- repo: github/github-mcp-server -->

#### What it is
GitHub's first-party MCP server. Surfaces repos, issues, PRs, code search, Actions runs, Dependabot alerts, discussions, and team activity as MCP tools. Both self-host (Go binary) and the remote variant at `api.githubcopilot.com/mcp/` are supported.

#### When to reach for it
- Any agent that touches GitHub — PR triage, issue automation, build-failure analysis, repo browsing across the org's permission surface — and you want the official integration over hand-rolled `gh` calls.
- You need the remote MCP endpoint for clients (VS Code, Cursor) without operating a server yourself.

#### When not to
- Your agent only needs `gh` once or twice per task — shelling out is simpler; the MCP layer adds protocol overhead with no compounding win.
- You can't grant the OAuth scopes needed for the agent to act in your repos — wrong tool for that constraint.

#### Sources
- Repo: https://github.com/github/github-mcp-server
<!-- END TOOL: github/github-mcp-server -->

<!-- BEGIN TOOL: ComposioHQ/composio -->
### composio
<!-- repo: ComposioHQ/composio -->

#### What it is
Tool-integration platform delivering a large catalog of pre-built third-party toolkits (Hackernews, Slack, Linear, Notion, etc.) plus auth, tool search, context management, and a sandboxed workbench. Python and TypeScript SDKs with first-class adapters for the major agent frameworks.

#### When to reach for it
- The agent needs broad coverage of third-party SaaS APIs (auth + tool surfaces) and you'd rather pull from a maintained catalog than wire each integration yourself.
- Multi-tenant agent where per-user OAuth state across many providers is the actual hard problem.

#### When not to
- A single-purpose tool surface — FastMCP is more focused; composio's value is the catalog breadth, not protocol authoring.
- You're committed to MCP-only architecture for portability across clients — composio's SDKs are a separate abstraction; the catalog isn't all exposed as native MCP servers.

#### Sources
- Repo: https://github.com/ComposioHQ/composio
<!-- END TOOL: ComposioHQ/composio -->

<!-- BEGIN TOOL: oraios/serena -->
### serena
<!-- repo: oraios/serena -->

#### What it is
"IDE for the agent" — an MCP toolkit that gives coding agents symbol-level semantic operations (find references, rename, extract function, structured edits) instead of line-numbered string patches. Tools are explicitly designed to be agent-friendly rather than mirroring an IDE's human surface.

#### When to reach for it
- Coding agent operating on a non-trivial codebase where line-number patches cause regressions when files move or refactor — symbol-level tools survive that churn.
- The agent already runs at a level where it can plan rename-across-modules / extract-function operations and benefits from structured, refactor-aware primitives.

#### When not to
- Small or single-file codebase — built-in agent file/edit tools are fine; serena's setup overhead doesn't pay back.
- Non-supported language — serena's value compounds with the language servers it can drive; outside that, the symbol-level promise weakens.

#### Sources
- Repo: https://github.com/oraios/serena
<!-- END TOOL: oraios/serena -->

<!-- BEGIN TOOL: yusufkaraaslan/Skill_Seekers -->
### Skill_Seekers
<!-- repo: yusufkaraaslan/Skill_Seekers -->

#### What it is
Knowledge-ingestion layer that turns heterogeneous sources — docs sites, GitHub repos, PDFs, videos, notebooks, wikis — into structured assets ready to be loaded as Claude/Gemini/OpenAI skills, RAG corpora, or coding-assistant context. Includes conflict detection across imports.

#### When to reach for it
- You need to convert a multi-source backlog (docs + repos + PDFs + recordings) into a single Claude-skill or RAG-ready bundle as one ingestion step rather than per-source pipelines.
- You want pre-built configs for common targets (the SkillSeekersWeb registry) instead of authoring extraction logic per source type.

#### When not to
- You already have a custom RAG pipeline and only need raw markdown — Firecrawl or Docling are the right primitives at that lower layer.
- Single-source ingestion (just one repo, just one docs site) — Skill_Seekers's multi-source value isn't earned; lighter tooling is fine.

#### Sources
- Repo: https://github.com/yusufkaraaslan/Skill_Seekers
<!-- END TOOL: yusufkaraaslan/Skill_Seekers -->

<!-- BEGIN TOOL: mcp-use/mcp-use -->
### mcp-use
<!-- repo: mcp-use/mcp-use -->

#### What it is
Fullstack MCP framework — covers both sides of the protocol: MCP servers (the tool surface) AND MCP apps (the client/consumer surface that ships in ChatGPT or Claude). TS and Python SDKs, an MCP Inspector for testing, and a managed deployment target (Manufact MCP Cloud).

#### When to reach for it
- You're authoring both ends — an MCP app and the servers it talks to — and want a unified SDK + inspector + deploy story instead of stitching tools per side.
- You want a managed deployment path (Manufact) where pushing to GitHub gives you a hosted MCP server with observability and branch deploys.

#### When not to
- You're only writing one MCP server in Python — FastMCP is more focused; mcp-use's value compounds when you're shipping a client app too.
- You want self-host-only with no SaaS dependency in the loop — mcp-use's Manufact integration is opt-in but the framing leans toward it.

#### Sources
- Repo: https://github.com/mcp-use/mcp-use
<!-- END TOOL: mcp-use/mcp-use -->

<!-- BEGIN TOOL: zilliztech/claude-context -->
### claude-context
<!-- repo: zilliztech/claude-context -->

#### What it is
MCP server that indexes a codebase into a vector database (Zilliz Cloud) and exposes semantic code search to coding agents. Instead of loading entire directories per turn, the agent issues a query and gets back only the relevant code spans.

#### When to reach for it
- Large codebase where loading directories per turn balloons context cost — vector-indexed search compresses cost dramatically and keeps the agent on the relevant surface.
- You're already on Zilliz Cloud / Milvus, or you're comfortable operating a managed vector DB just for code retrieval.

#### When not to
- Small or medium codebase that fits in context — full-tree loading is simpler and you skip the vector-DB dependency entirely.
- Symbol-level structural operations (rename, refactor) are the goal — Serena is the right shape; claude-context is search/retrieval, not editing.

#### Sources
- Repo: https://github.com/zilliztech/claude-context
<!-- END TOOL: zilliztech/claude-context -->

<!-- BEGIN TOOL: grab/cursor-talk-to-figma-mcp -->
### cursor-talk-to-figma-mcp
<!-- repo: grab/cursor-talk-to-figma-mcp -->

#### What it is
MCP bridge between coding agents (Cursor, Claude Code) and Figma. Ships an MCP server, a Figma plugin, and a WebSocket relay so the agent can read design files and apply programmatic changes — bulk text replacement, instance-override propagation across components, etc.

#### When to reach for it
- Design-engineering loop where the agent should both read design state and apply structured changes back — repetitive Figma operations (rename instances, propagate overrides) are exactly the shape this tool addresses.
- You want an MCP-shaped Figma surface usable across Cursor/Claude Code instead of writing per-client integrations.

#### When not to
- Read-only inspection of Figma — the official Figma REST API plus a thin tool wrapper is simpler.
- Agent doesn't touch Figma at all — too narrow.

#### Sources
- Repo: https://github.com/grab/cursor-talk-to-figma-mcp
<!-- END TOOL: grab/cursor-talk-to-figma-mcp -->

<!-- BEGIN TOOL: getsentry/XcodeBuildMCP -->
### XcodeBuildMCP
<!-- repo: getsentry/XcodeBuildMCP -->

#### What it is
MCP server (and CLI) from Sentry that wraps `xcodebuild`, simulator control, and the surrounding iOS/macOS toolchain into agent-friendly tools. Drop-in client configs for Cursor, Claude Code, and Codex; install via Homebrew or npm.

#### When to reach for it
- Coding agent on an iOS or macOS project — XcodeBuildMCP turns build/test/simulator operations into structured tool calls instead of brittle shelling-out to `xcodebuild`.
- You want an installed agent skill that primes the model with how to use the surface, not raw command help.

#### When not to
- Cross-platform or non-Apple work — irrelevant; the value is fully Xcode-bound.
- Single one-off `xcodebuild` invocation — shelling out is simpler than installing the MCP.

#### Sources
- Repo: https://github.com/getsentry/XcodeBuildMCP
<!-- END TOOL: getsentry/XcodeBuildMCP -->

<!-- BEGIN TOOL: the-open-agent/openagent -->
### openagent
<!-- repo: the-open-agent/openagent -->

#### What it is
Self-hosted enterprise platform combining an AI knowledge base with MCP/A2A server management, admin UI, multi-user accounts, and SSO. React frontend, Go + Python backend, MySQL state. Supports many model providers (ChatGPT, Claude, Llama, Ollama, HuggingFace).

#### When to reach for it
- You need a multi-tenant MCP/A2A platform with SSO and an admin UI for an organization — a finished product to deploy, not a library to compose.
- Knowledge-base + tool-management as one system makes sense for the deployment shape (e.g., an internal IT-managed AI portal).

#### When not to
- Single-developer or small-team setup — openagent's scope (admin UI, SSO, MySQL) is overkill; FastMCP plus a couple of MCP servers is the right size.
- You prefer a library you control over a product-shaped platform — openagent imposes its own UX and deployment posture.

#### Sources
- Repo: https://github.com/the-open-agent/openagent
<!-- END TOOL: the-open-agent/openagent -->

<!-- BEGIN TOOL: IBM/mcp-context-forge -->
### mcp-context-forge
<!-- repo: IBM/mcp-context-forge -->

#### What it is
IBM's open-source registry and proxy that federates MCP, A2A, and REST/gRPC tool surfaces behind one MCP endpoint. Tools/Agents/API gateways with centralized auth, rate limiting, retries, plugin extensibility, and OpenTelemetry tracing into Phoenix/Jaeger/Zipkin. Scales to multi-cluster Kubernetes with Redis-backed federation.

#### When to reach for it
- Enterprise environment with many tool servers across protocols (MCP + REST + gRPC + A2A) and you need governance, discovery, and observability over the whole fleet — a control plane, not just a server.
- You explicitly need OTel tracing across the tool layer and reverse-proxy concerns (auth, rate limiting) to live in one place.

#### When not to
- Single MCP server with a handful of tools — a federated registry is overkill; FastMCP alone is the right size.
- You don't run on Kubernetes or want centralized federation — context-forge's design center pulls toward that posture.

#### Sources
- Repo: https://github.com/IBM/mcp-context-forge
<!-- END TOOL: IBM/mcp-context-forge -->

<!-- BEGIN TOOL: blazickjp/arxiv-mcp-server -->
### arxiv-mcp-server
<!-- repo: blazickjp/arxiv-mcp-server -->

#### What it is
Narrow MCP server bridging AI assistants to arXiv — paper search with date/category filters, paper download, a local library of fetched papers. Distributed via PyPI / `uvx` and integrated with VS Code, Cursor, Kiro, and Smithery.

#### When to reach for it
- Research-drafting or literature-review agent that needs first-class paper retrieval — the agent should search arXiv directly rather than scrape it via a generic web tool.
- You want a working example of a focused, single-domain MCP server you can install in a minute.

#### When not to
- Industry research / non-arXiv source mix — too narrow; a general web fetch via Firecrawl plus a search API covers the broader case.
- One-shot paper fetch — `arxiv` Python lib or `curl` against the export API is simpler than running an MCP server.

#### Sources
- Repo: https://github.com/blazickjp/arxiv-mcp-server
<!-- END TOOL: blazickjp/arxiv-mcp-server -->

<!-- BEGIN TOOL: metatool-ai/metamcp -->
### metamcp
<!-- repo: metatool-ai/metamcp -->

#### What it is
MCP-to-MCP proxy that dynamically aggregates multiple upstream MCP servers into a single unified MCP endpoint. Adds namespacing, middleware (auth, transformations), an inspector, and tool overrides. Itself an MCP server, so any client (Cursor, Claude Desktop, etc.) can plug into it transparently.

#### When to reach for it
- You operate several MCP servers and want clients to see one aggregated surface — namespaces collide cleanly, middleware applies centrally, and you can rename or rewrite tool annotations without forking the upstream server.
- You want a Docker-deployable proxy with an inspector for debugging the merged surface.

#### When not to
- Single MCP server in scope — a proxy adds a hop and a moving part with no compounding win.
- You need the broader enterprise control-plane (registry, OTel, multi-cluster) — ContextForge is the right shape; metamcp is lighter-weight middleware.

#### Sources
- Repo: https://github.com/metatool-ai/metamcp
<!-- END TOOL: metatool-ai/metamcp -->

<!-- BEGIN TOOL: taylorwilsdon/google_workspace_mcp -->
### google_workspace_mcp
<!-- repo: taylorwilsdon/google_workspace_mcp -->

#### What it is
Comprehensive single MCP server covering the breadth of Google Workspace — Calendar, Drive, Gmail, Docs, Sheets, Slides, Forms, Tasks, Contacts, Chat — with native OAuth 2.1, multi-user support, stateless mode, and external-auth-server integration. Also ships a CLI for use with Claude Code / Codex.

#### When to reach for it
- Agent needs broad Google Workspace coverage and you want one MCP server with multi-user OAuth, not per-service stitching — especially for hosted assistants acting on behalf of org users.
- You need self-hostable infrastructure with org-wide central auth (OAuth 2.1, external auth server) rather than a SaaS Workspace integration.

#### When not to
- Calendar-only or Gmail-only flow — a narrower MCP (or direct Google API call) is simpler than the full server's surface.
- You can't grant the broad Workspace OAuth scopes the server needs — wrong tool for that constraint.

#### Sources
- Repo: https://github.com/taylorwilsdon/google_workspace_mcp
<!-- END TOOL: taylorwilsdon/google_workspace_mcp -->
