---
category: code-agents
tools:
  - { name: "Aider",      repo: "Aider-AI/aider" }
  - { name: "OpenHands",  repo: "OpenHands/OpenHands" }
  - { name: "Cline",      repo: "cline/cline" }
  - { name: "Gemini CLI", repo: "google-gemini/gemini-cli" }
  - { name: "goose", repo: "aaif-goose/goose" }
  - { name: "DeepCode", repo: "HKUDS/DeepCode" }
  - { name: "gptme", repo: "gptme/gptme" }
last_reviewed: 2026-04-26
---

# Code Agents

## Overview
Tools that edit code with LLM assistance. The interesting axis is "supervision tightness": tight (Aider, Cline) vs. autonomous (OpenHands).

## Decision heuristics
- Terminal pair-programmer with git-aware edits → Aider.
- VS Code extension with explicit Plan/Act and approval gates → Cline.
- Longer-horizon autonomous coding tasks in a sandbox → OpenHands.
- Highly customized per-team agent → use Claude Code or build on the SDK rather than these.

## Tools

<!-- BEGIN TOOL: Aider-AI/aider -->
### Aider
<!-- repo: Aider-AI/aider -->

#### What it is
Terminal-based pair programmer that edits code in your local git repo, auto-commits each change.

#### When to reach for it
- Repo-aware edits with tight git integration.
- Works with any model via LiteLLM/OpenAI-compatible endpoints.

#### When not to
- You want an IDE-native experience — Cline / Continue.

#### Sources
- Repo: https://github.com/Aider-AI/aider
<!-- END TOOL: Aider-AI/aider -->

<!-- BEGIN TOOL: OpenHands/OpenHands -->
### OpenHands
<!-- repo: OpenHands/OpenHands -->

#### What it is
Autonomous software-engineering agent (formerly OpenDevin). Sandboxed runtime, browser + shell + editor tools, multi-agent capabilities.

#### When to reach for it
- Longer-horizon autonomous coding tasks.

#### When not to
- Tight, supervised inline edits — Aider/Cline are better fits.

#### Sources
- Repo: https://github.com/OpenHands/OpenHands
<!-- END TOOL: OpenHands/OpenHands -->

<!-- BEGIN TOOL: cline/cline -->
### Cline
<!-- repo: cline/cline -->

#### What it is
VS Code agent extension. Plan/Act modes, MCP tool integration, human-approval gates on file/command actions.

#### When to reach for it
- VS Code-native autonomous coding with explicit approval steps.

#### When not to
- Terminal-only workflow — Aider.

#### Sources
- Repo: https://github.com/cline/cline
<!-- END TOOL: cline/cline -->

<!-- BEGIN TOOL: google-gemini/gemini-cli -->
### Gemini CLI
<!-- repo: google-gemini/gemini-cli -->

#### What it is
Google's official open-source CLI agent for the Gemini family of models. Brings tool-use, file editing, and shell execution to the terminal.

#### When to reach for it
- You're already on Gemini and want a vendor-supported CLI.
- Want to compare tool-use behavior across vendors (Claude Code / Aider / Gemini CLI).

#### When not to
- Vendor-locked-in semantics matter — Aider's any-model stance via LiteLLM travels better.

#### Sources
- Repo: https://github.com/google-gemini/gemini-cli
<!-- END TOOL: google-gemini/gemini-cli -->

<!-- BEGIN TOOL: aaif-goose/goose -->
### goose
<!-- repo: aaif-goose/goose -->

#### What it is
Native, multi-provider AI agent — desktop app, CLI, and embeddable API — written in Rust. Connects to Anthropic / OpenAI / Google / Ollama / Bedrock / Azure and to MCP-compatible extensions; can run on existing Claude / ChatGPT / Gemini subscriptions via ACP. Recently moved to the Linux Foundation's Agentic AI Foundation (formerly `block/goose`).

#### When to reach for it
- You want an agent that runs as both a desktop app and a CLI on the same machine, sharing config — and you want easy switching between providers (Anthropic for hard tasks, local Ollama for cheap ones) inside one workflow.
- You're standing up a custom agent distribution with preconfigured providers and extensions for a team, where the foundation governance matters.

#### When not to
- You want an IDE-integrated assistant — Cline (VS Code) is the right shape; Goose's desktop app is a separate surface from your editor.
- You want a minimal terminal pair-programmer — Aider does that with less ceremony; Goose's broader scope is overkill.

#### Sources
- Repo: https://github.com/aaif-goose/goose
<!-- END TOOL: aaif-goose/goose -->

<!-- BEGIN TOOL: HKUDS/DeepCode -->
### DeepCode
<!-- repo: HKUDS/DeepCode -->

#### What it is
Multi-agent system focused on greenfield code generation from a high-level intent: paper-to-implementation, text-to-web, text-to-backend. Ships both a CLI and a web dashboard for the generation workflow.

#### When to reach for it
- You have a research paper or a written spec and you want an end-to-end first pass at a working implementation, not iterative edits to existing code.
- You want a multi-agent decomposition of the generation problem (planner / coder / verifier) without wiring the orchestration yourself.

#### When not to
- Day-to-day pair-programming on an existing codebase — Aider, Cline, and OpenHands target that surface; DeepCode is paper-to-code, not code-to-better-code.
- You need the agent to operate inside your editor with approval gates — DeepCode's loop is more autonomous and less interactive.

#### Sources
- Repo: https://github.com/HKUDS/DeepCode
<!-- END TOOL: HKUDS/DeepCode -->

<!-- BEGIN TOOL: gptme/gptme -->
### gptme
<!-- repo: gptme/gptme -->

#### What it is
Personal terminal agent with unconstrained local tool access — shell, code, files, web, vision — explicitly positioned as a self-hosted alternative to Claude Code / Codex / Cursor. Plugin and skill systems support persistent autonomous agents on top of the base CLI; one of the earliest agent CLIs and still actively maintained.

#### When to reach for it
- You want full local control of an autonomous loop, comfortable owning the security envelope (no vendor sandbox between the agent and your shell).
- You want a hackable base for a custom agent — plugins, skills, autonomous run loops, lessons — rather than a managed product.

#### When not to
- Production teams that benefit from vendor-managed safety policies and tool-use guardrails — Cline and Aider with default Anthropic policies are saner.
- Tight pair-programming flow with explicit Plan/Act gates — Cline's UX is built for that; gptme leans more toward autonomous execution.

#### Sources
- Repo: https://github.com/gptme/gptme
<!-- END TOOL: gptme/gptme -->
