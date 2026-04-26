---
category: code-agents
tools:
  - { name: "Aider",      repo: "Aider-AI/aider" }
  - { name: "OpenHands",  repo: "OpenHands/OpenHands" }
  - { name: "Cline",      repo: "cline/cline" }
  - { name: "Gemini CLI", repo: "google-gemini/gemini-cli" }
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
