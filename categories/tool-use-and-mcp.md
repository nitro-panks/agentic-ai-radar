---
category: tool-use-and-mcp
tools:
  - { name: "Model Context Protocol", repo: "modelcontextprotocol/modelcontextprotocol" }
  - { name: "FastMCP",                repo: "PrefectHQ/fastmcp" }
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
