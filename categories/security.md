---
category: security
tools:
  - { name: "Garak",     repo: "NVIDIA/garak" }
  - { name: "PyRIT",     repo: "Azure/PyRIT" }
  - { name: "LLM Guard", repo: "protectai/llm-guard" }
last_reviewed: 2026-04-26
---

# Security

## Overview
Two distinct concerns, often confused:
1. **Pre-deploy testing** — find weaknesses before shipping. *Garak*, *PyRIT*, *promptfoo redteam*.
2. **Runtime guardrails** — block bad input/output in production. *LLM Guard*, *Rebuff*, *NeMo Guardrails*.

A single tool rarely covers both well. Pick one from each row.

## Decision heuristics
- Broad first-pass vulnerability scan → Garak.
- Orchestrated, scenario-driven red-team campaign → PyRIT.
- CI-friendly, OWASP LLM Top 10 → promptfoo redteam (see evaluation).
- Production input/output gating → LLM Guard.
- Programmable rails (Colang) → NeMo Guardrails (not yet expanded here).
- For agents with tool access, the threat model is "bad action," not "bad output." Sandboxing the tool runtime matters more than output filters.

## Tools

<!-- BEGIN TOOL: NVIDIA/garak -->
### Garak
<!-- repo: NVIDIA/garak -->

#### What it is
LLM vulnerability scanner from NVIDIA. Probes for prompt injection, jailbreaks, data leakage, toxicity, hallucination patterns.

#### When to reach for it
- Pre-deploy red-team scan against an LLM endpoint.

#### When not to
- Runtime gating — Garak is offline; pair with LLM Guard.

#### Sources
- Repo: https://github.com/NVIDIA/garak
<!-- END TOOL: NVIDIA/garak -->

<!-- BEGIN TOOL: Azure/PyRIT -->
### PyRIT
<!-- repo: Azure/PyRIT -->

#### What it is
Microsoft's Python Risk Identification Toolkit for generative AI. Orchestrators, attack strategies, scorers — geared toward security teams probing apps.

#### When to reach for it
- Structured red-teaming campaigns by an AI security team.

#### When not to
- Lightweight one-shot scans — Garak is faster to set up.

#### Sources
- Repo: https://github.com/Azure/PyRIT
<!-- END TOOL: Azure/PyRIT -->

<!-- BEGIN TOOL: protectai/llm-guard -->
### LLM Guard
<!-- repo: protectai/llm-guard -->

#### What it is
Input/output scanners for LLM apps: PII, prompt injection, toxicity, secrets, code, regex patterns. Pluggable per-direction.

#### When to reach for it
- Production runtime guardrails on user input and model output.

#### When not to
- Pre-deploy testing — pair with Garak.

#### Sources
- Repo: https://github.com/protectai/llm-guard
<!-- END TOOL: protectai/llm-guard -->
