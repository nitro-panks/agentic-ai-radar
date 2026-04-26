"""One-line "thesis" summarizer for ai-radar tools.

Used by `apply_adds.py` for new entries and by sweep-level refresh scripts to
regenerate summaries for the whole tracked set. Backed by the `instructor`
library + Claude (Anthropic SDK).

Output goes into `state/landscape-meta.json[<repo>].notes` and surfaces in:
  - `landscape.md` (the rightmost "Notes" column)
  - `viz/data.json` (`notes` field; shown at the bottom of the treemap tooltip)

Constraints baked into the prompt + schema:
  - ≤90 characters, one line
  - no star/fork/contributor counts (they're shown elsewhere)
  - no leading repo name ("LangGraph is a..." → bad; "default for stateful flows" → good)
  - no generic praise ("popular", "well-known", "powerful", "robust")
  - sentence fragments fine; opinionated voice preferred
"""
from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import anthropic
import instructor
from pydantic import BaseModel, Field

DEFAULT_MODEL = "claude-sonnet-4-5"
MAX_LEN = 90


class Summary(BaseModel):
    summary: str = Field(
        max_length=MAX_LEN,
        description=(
            "One-line thesis (≤90 chars). Sentence fragment is fine. "
            "Capture what the tool *is for* and what makes it distinctive vs. its category peers. "
            "DO NOT include star/fork counts, the year, or the repo's own name as a prefix. "
            "DO NOT use the words 'popular', 'well-known', 'comprehensive', 'powerful', 'robust', "
            "'cutting-edge', 'state-of-the-art', 'innovative', or 'leading'. "
            "Strong examples: 'default for stateful agent flows', 'when Postgres is already in the stack', "
            "'graph-based RAG; better on multi-hop synthesis', 'visual builder; demos and internal tools', "
            "'durable execution substrate for long-running agents'. "
            "Weak examples to avoid: 'X is a popular Python framework', 'has 30k stars and active development', "
            "'LangGraph is a library that...'"
        ),
    )


SYSTEM_PROMPT = """You write one-line theses for tools in the ai-radar — a curated knowledge base of agentic-AI tooling.

Your output is shown at the bottom of a treemap tooltip and as the rightmost cell in a comparison table. Stars, forks, and the category are already shown elsewhere; do not repeat them.

# What makes a good thesis line
- Captures the *distinctive angle* — what this tool optimizes for, the niche it owns vs. its category peers.
- Sentence-fragment style is fine; opinionated and terse is better than complete-sentence and bland.
- ≤90 characters, one line, no trailing period required.
- Reads as advice to an engineer skimming the radar: "when would I reach for this?"

# Prohibited
- Star/fork/watcher counts, year, "popular", "well-known", "comprehensive", "powerful", "robust", "cutting-edge", "state-of-the-art", "innovative", "leading", "feature-rich".
- Starting with the repo's own name ("LangGraph is...") — the name is shown alongside.
- Restating the category ("an agent framework that..." when the category is already 'agent-frameworks').
- Marketing fluff ("the future of...", "next-generation...").

# Style examples (good)
- LangGraph: default for stateful agent flows; checkpoints + HITL primitives
- pgvector: vectors in Postgres — when transactional consistency with rows matters
- vLLM: GPU-throughput-first serving with PagedAttention
- Aider: terminal pair-programmer; auto-commits each edit
- Garak: pre-deploy LLM red-team scanner; broad probe library
- Temporal: durable execution substrate; agents that survive process crashes
- GraphRAG: graph-based RAG; better on multi-hop synthesis vs. similarity retrieval

# Style examples (bad — do not emit)
- "AnythingLLM is a comprehensive all-in-one platform" (banned word, name prefix)
- "has 50k stars and active community" (number, fluff)
- "an agent framework for building agents" (restates category, tautology)
- "the leading observability tool for LLMs" (banned word, marketing voice)"""


def _user_message(repo: str, name: str, category: str, description: str | None,
                  prior_notes: str | None) -> str:
    parts = [
        f"Repo: {repo}",
        f"Display name: {name}",
        f"Category: {category}",
    ]
    if description:
        parts.append(f"Upstream description: {description}")
    if prior_notes:
        parts.append(f"Prior note (may be redundant or low-quality): {prior_notes}")
    parts.append("\nWrite the thesis line.")
    return "\n".join(parts)


def make_client() -> instructor.Instructor:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return instructor.from_anthropic(anthropic.Anthropic())


def summarize_one(client: instructor.Instructor, repo: str, name: str, category: str,
                  description: str | None, prior_notes: str | None,
                  model: str = DEFAULT_MODEL) -> str:
    """Generate one thesis line. Raises on hard failure; caller decides fallback."""
    out: Summary = client.messages.create(
        model=model,
        max_tokens=200,
        system=[
            {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
        ],
        messages=[{"role": "user", "content": _user_message(repo, name, category, description, prior_notes)}],
        response_model=Summary,
    )
    return out.summary.strip().strip(".").strip()


def summarize_many(items: Iterable[dict], *, workers: int = 8,
                   model: str = DEFAULT_MODEL, log: bool = True) -> dict[str, str]:
    """Each item: {repo, name, category, description, prior_notes}.
    Returns {repo: summary}; errors are surfaced and logged but do not abort the batch."""
    client = make_client()
    items = list(items)
    out: dict[str, str] = {}

    def task(it: dict) -> tuple[str, str | Exception]:
        try:
            s = summarize_one(client, it["repo"], it["name"], it["category"],
                              it.get("description"), it.get("prior_notes"), model=model)
            return it["repo"], s
        except Exception as e:
            return it["repo"], e

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(task, it) for it in items]
        for i, fut in enumerate(as_completed(futures), 1):
            repo, result = fut.result()
            if isinstance(result, Exception):
                if log:
                    print(f"[{i:>3}/{len(items)}] {repo:<55} ERR {type(result).__name__}: {str(result)[:80]}",
                          file=sys.stderr)
                continue
            out[repo] = result
            if log:
                print(f"[{i:>3}/{len(items)}] {repo:<55} → {result}", file=sys.stderr)
    return out
