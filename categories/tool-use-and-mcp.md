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
Convert documentation websites, GitHub repositories, and PDFs into Claude AI skills with automatic conflict detection

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `modelcontextprotocol/modelcontextprotocol`, `PrefectHQ/fastmcp`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): Distinctive MCP server builder that converts docs, GitHub repos, and PDFs into Claude skills with automatic conflict detection. Addresses upstream knowledge ingestion for MCP—complementary to FastMCP (authoring SDK) and the spec itself. 13K stars, recently active, solves real integration pain.

#### Sources
- Repo: https://github.com/yusufkaraaslan/Skill_Seekers
<!-- END TOOL: yusufkaraaslan/Skill_Seekers -->

<!-- BEGIN TOOL: mcp-use/mcp-use -->
### mcp-use
<!-- repo: mcp-use/mcp-use -->

#### What it is
The fullstack MCP framework to develop MCP Apps for ChatGPT / Claude & MCP Servers for AI Agents.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `modelcontextprotocol/modelcontextprotocol`, `PrefectHQ/fastmcp`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): Fullstack MCP framework for developing both MCP apps (ChatGPT/Claude integrations) and MCP servers for agents. Goes beyond the protocol spec or simple SDKs to provide higher-level development tooling. Active maintenance, nearly 10k stars, and distinct positioning warrant addition.

#### Sources
- Repo: https://github.com/mcp-use/mcp-use
<!-- END TOOL: mcp-use/mcp-use -->

<!-- BEGIN TOOL: zilliztech/claude-context -->
### claude-context
<!-- repo: zilliztech/claude-context -->

#### What it is
Code search MCP for Claude Code. Make entire codebase the context for any coding agent.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): MCP server providing semantic code search for coding agents, making entire codebases accessible as context. Distinctive implementation focused on code-search use case, complementing the protocol and SDK already tracked. Solid adoption (9.4k stars) with recent activity.

#### Sources
- Repo: https://github.com/zilliztech/claude-context
<!-- END TOOL: zilliztech/claude-context -->

<!-- BEGIN TOOL: grab/cursor-talk-to-figma-mcp -->
### cursor-talk-to-figma-mcp
<!-- repo: grab/cursor-talk-to-figma-mcp -->

#### What it is
TalkToFigma: MCP integration between AI Agent (Cursor, Claude Code) and Figma, allowing Agentic AI to communicate with Figma for reading designs and modifying them programmatically.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `modelcontextprotocol/modelcontextprotocol`, `PrefectHQ/fastmcp`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): TalkToFigma is a concrete MCP server bridging AI agents with Figma's API for programmatic design reading and modification. It provides distinctive vertical integration (design tools ↔ agents) beyond generic MCP implementations, addressing a real workflow need for AI-driven Figma manipulation.

#### Sources
- Repo: https://github.com/grab/cursor-talk-to-figma-mcp
<!-- END TOOL: grab/cursor-talk-to-figma-mcp -->

<!-- BEGIN TOOL: getsentry/XcodeBuildMCP -->
### XcodeBuildMCP
<!-- repo: getsentry/XcodeBuildMCP -->

#### What it is
A Model Context Protocol (MCP) server and CLI that provides tools for agent use when working on iOS and macOS projects.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): XcodeBuildMCP is a concrete MCP server for iOS/macOS development—building, testing, and debugging Xcode projects via agents. Fills a clear mobile-dev niche distinct from general MCP frameworks. From Sentry (credible), MIT-licensed, actively maintained.

#### Sources
- Repo: https://github.com/getsentry/XcodeBuildMCP
<!-- END TOOL: getsentry/XcodeBuildMCP -->

<!-- BEGIN TOOL: the-open-agent/openagent -->
### openagent
<!-- repo: the-open-agent/openagent -->

#### What it is
⚡️AI Cloud OS: Open-source enterprise-level AI knowledge base and MCP (model-context-protocol)/A2A (agent-to-agent) management platform with admin UI, user management and Single-Sign-On⚡️, supports ChatGPT, Claude, Llama, Ollama, HuggingFace, etc., chat bot demo: https://ai.casibase.com, admin UI demo: https://ai-admin.casibase.com

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `modelcontextprotocol/modelcontextprotocol`, `PrefectHQ/fastmcp`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): Enterprise MCP management platform with admin UI, SSO, and user management. Fills a distinct operational/deployment niche versus the MCP spec itself and FastMCP's SDK. Go-based with 4.5k stars and active maintenance.

#### Sources
- Repo: https://github.com/the-open-agent/openagent
<!-- END TOOL: the-open-agent/openagent -->

<!-- BEGIN TOOL: IBM/mcp-context-forge -->
### mcp-context-forge
<!-- repo: IBM/mcp-context-forge -->

#### What it is
An AI Gateway, registry, and proxy that sits in front of any MCP, A2A, or REST/gRPC APIs, exposing a unified endpoint with centralized discovery, guardrails and management. Optimizes Agent & Tool calling, and supports plugins.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `modelcontextprotocol/modelcontextprotocol`, `PrefectHQ/fastmcp`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): An AI gateway/proxy that unifies MCP, A2A, and REST/gRPC APIs behind a single endpoint with discovery, guardrails, and management. Addresses enterprise tool orchestration concerns (registry, governance, multi-protocol) that neither the MCP protocol spec nor FastMCP SDK handle. IBM-backed, Apache-2.0, actively maintained.

#### Sources
- Repo: https://github.com/IBM/mcp-context-forge
<!-- END TOOL: IBM/mcp-context-forge -->

<!-- BEGIN TOOL: blazickjp/arxiv-mcp-server -->
### arxiv-mcp-server
<!-- repo: blazickjp/arxiv-mcp-server -->

#### What it is
A Model Context Protocol server for searching and analyzing arXiv papers

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.80): A concrete MCP server for arXiv paper search and analysis. Fills a practical niche (academic research retrieval) in the MCP ecosystem, complementing the protocol spec already tracked. Demonstrates real-world MCP server implementation engineers would deploy for research-oriented agents.

#### Sources
- Repo: https://github.com/blazickjp/arxiv-mcp-server
<!-- END TOOL: blazickjp/arxiv-mcp-server -->

<!-- BEGIN TOOL: metatool-ai/metamcp -->
### metamcp
<!-- repo: metatool-ai/metamcp -->

#### What it is
MCP Aggregator, Orchestrator, Middleware, Gateway in one docker

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `modelcontextprotocol/modelcontextprotocol`, `PrefectHQ/fastmcp`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): MetaMCP provides MCP aggregation, orchestration, and gateway infrastructure in a single Docker deployment. While the MCP protocol spec and FastMCP SDK are tracked, this fills a different niche as middleware for managing multiple MCP servers—useful for production deployments that need centralized routing.

#### Sources
- Repo: https://github.com/metatool-ai/metamcp
<!-- END TOOL: metatool-ai/metamcp -->

<!-- BEGIN TOOL: taylorwilsdon/google_workspace_mcp -->
### google_workspace_mcp
<!-- repo: taylorwilsdon/google_workspace_mcp -->

#### What it is
Control Gmail, Google Calendar, Docs, Sheets, Slides, Chat, Forms, Tasks, Search & Drive with AI - Comprehensive Google Workspace / G Suite MCP Server & CLI Tool

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Comprehensive MCP server exposing Google Workspace APIs (Gmail, Calendar, Docs, Sheets, Drive, etc.) to AI agents. Distinctive, batteries-included integration for a major productivity suite. Complements the MCP spec and FastMCP framework with concrete tooling engineers need for Google service interaction.

#### Sources
- Repo: https://github.com/taylorwilsdon/google_workspace_mcp
<!-- END TOOL: taylorwilsdon/google_workspace_mcp -->
