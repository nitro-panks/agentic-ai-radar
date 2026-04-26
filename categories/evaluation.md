---
category: evaluation
tools:
  - { name: "Ragas",     repo: "vibrantlabsai/ragas" }
  - { name: "promptfoo", repo: "promptfoo/promptfoo" }
  - { name: "DeepEval",  repo: "confident-ai/deepeval" }
last_reviewed: 2026-04-26
---

# Evaluation

## Overview
Quantifying LLM/RAG behavior change across iterations. The category overlaps with observability — Langfuse and Phoenix both ship eval tooling — but the focus here is "compute scores and assert."

## Decision heuristics
- RAG-shaped quality questions (faithfulness, context precision/recall) → Ragas.
- Eval-as-code in CI, side-by-side prompt/model comparison → promptfoo.
- "Pytest for LLMs" assertion style gating PRs → DeepEval.
- Trace-anchored evals you'll explore visually → Langfuse / Phoenix instead (see observability).

## Tools

<!-- BEGIN TOOL: vibrantlabsai/ragas -->
### Ragas
<!-- repo: vibrantlabsai/ragas -->

#### What it is
RAG-focused eval library: faithfulness, answer relevancy, context precision/recall, etc. Synthetic test set generation.

#### When to reach for it
- Quantifying RAG quality changes across iterations.

#### When not to
- Non-RAG evals — promptfoo or DeepEval fit better.

#### Sources
- Repo: https://github.com/vibrantlabsai/ragas
<!-- END TOOL: vibrantlabsai/ragas -->

<!-- BEGIN TOOL: promptfoo/promptfoo -->
### promptfoo
<!-- repo: promptfoo/promptfoo -->

#### What it is
CLI-first eval + red-team toolkit. YAML configs, side-by-side prompt/model comparisons, CI integration, vulnerability scans.

#### When to reach for it
- Eval-as-code in CI for prompt/model regressions.
- Lightweight red-team probing.

#### When not to
- Heavy research-style evals on giant datasets — lm-evaluation-harness is the right shape.

#### Sources
- Repo: https://github.com/promptfoo/promptfoo
<!-- END TOOL: promptfoo/promptfoo -->

<!-- BEGIN TOOL: confident-ai/deepeval -->
### DeepEval
<!-- repo: confident-ai/deepeval -->

#### What it is
"Pytest for LLMs" — assertion-style metrics (G-Eval, hallucination, toxicity, bias, RAG metrics) usable in test suites.

#### When to reach for it
- You want eval to look like unit tests, gating PRs.

#### When not to
- You don't already use pytest — the abstraction loses its appeal.

#### Sources
- Repo: https://github.com/confident-ai/deepeval
<!-- END TOOL: confident-ai/deepeval -->
