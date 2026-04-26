"""Curate a balanced eval set for the triage scorer.

Reads the auto-seed (`cases.jsonl` produced by `seed_cases.py`), filters and
balances by decision class / confidence / category, and emits a curated
`cases.jsonl` suitable for use as a regression gate.

Selection rules:
  - Auto-tracked skips (`tier == "auto"`, conf 1.0): include 4 representatives.
    They exercise the deterministic pre-filter path.
  - LLM-decided high-confidence cases (conf ≥ 0.90): include with category
    diversity caps so one category doesn't dominate.
  - Defer cases: include all (there are typically very few — they are the
    boundary cases the scorer flagged for human review).
  - Synthetic edge cases: hand-crafted "obvious skip" examples (course-named
    repo, awesome-list, thin wrapper) added so the rubric's skip criteria are
    exercised even when no real candidate of that shape appears in the inbox.

Each curated case is annotated `source: "curated-<sweep>-<date>"`. Future
regenerations preserve `source: "human"` cases (any case where source equals
the literal "human") by reading the existing `cases.jsonl` first and merging.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state"
OUT = ROOT / "eval" / "triage" / "cases.jsonl"

# Sweep we curate from.
SWEEP = "sweep-2026-04-26b"
SCORED_FILE = "04-triage-scored.sonnet-readme.jsonl"
INBOX_FILE = "01-inbox.jsonl"

# Selection knobs.
ADDS_PER_CATEGORY = 3
TARGET_AUTO_SKIPS = 4
LLM_SKIP_CONF_FLOOR = 0.92
ADD_CONF_FLOOR = 0.85
TARGET_LLM_SKIPS = 14


def _input_from(c: dict) -> dict:
    return {
        "repo": c["repo"],
        "stars": c.get("stars"),
        "forks": c.get("forks"),
        "language": c.get("language"),
        "license": c.get("license"),
        "pushed_at": c.get("pushed_at"),
        "description": c.get("description") or "",
        "sources": c.get("sources") or [],
    }


def _src_tag() -> str:
    return f"curated-{SWEEP}-{date.today().isoformat()}"


def _row(input_: dict, decision: str, confidence: float, *, tags: list[str], source: str, proposed_category: str | None = None) -> dict:
    """Build a promptfoo-shaped test row: `vars` + `description` + `metadata`."""
    return {
        "description": f"[{','.join(tags)}] {input_['repo']} → expect {decision}",
        "vars": {
            "candidate": input_,
            "expected_decision": decision,
            "expected_confidence": confidence,
            "expected_proposed_category": proposed_category,
        },
        "metadata": {"tags": tags, "source": source},
    }


def curate() -> list[dict]:
    sweep_dir = STATE / SWEEP
    inbox = {json.loads(l)["repo"]: json.loads(l) for l in (sweep_dir / INBOX_FILE).read_text().splitlines() if l.strip()}
    scored = [json.loads(l) for l in (sweep_dir / SCORED_FILE).read_text().splitlines() if l.strip()]
    tracked = set(json.loads((STATE / "metrics-current.json").read_text())["tools"].keys())
    src = _src_tag()

    cases: list[dict] = []

    # 1. Auto-tracked skips — pick 4 representatives with diverse stars to
    #    exercise the path that bypasses the LLM.
    auto = [r for r in scored if r["decision"] == "skip" and r["repo"] in tracked]
    auto.sort(key=lambda r: -(r.get("stars") or 0))
    spaced = [auto[0], auto[len(auto) // 3], auto[2 * len(auto) // 3], auto[-1]] if len(auto) >= 4 else auto
    for r in spaced[:TARGET_AUTO_SKIPS]:
        c = inbox.get(r["repo"])
        if not c:
            continue
        cases.append(_row(_input_from(c), "skip", 1.0, tags=["auto-skip"], source=src))

    # 2. Adds — diverse categories, high confidence.
    adds = [r for r in scored if r["decision"] == "add" and (r.get("confidence") or 0) >= ADD_CONF_FLOOR]
    adds.sort(key=lambda r: -(r.get("confidence") or 0))
    by_cat: dict[str, int] = defaultdict(int)
    for r in adds:
        cat = r.get("proposed_category") or "other"
        if by_cat[cat] >= ADDS_PER_CATEGORY:
            continue
        c = inbox.get(r["repo"])
        if not c:
            continue
        cases.append(_row(
            _input_from(c), "add", r.get("confidence", 0.0),
            tags=["add", cat], source=src, proposed_category=cat,
        ))
        by_cat[cat] += 1

    # 3. LLM-decided skips — high confidence, novel (not auto-tracked).
    llm_skips = [
        r for r in scored
        if r["decision"] == "skip"
        and r["repo"] not in tracked
        and (r.get("confidence") or 0) >= LLM_SKIP_CONF_FLOOR
    ]
    llm_skips.sort(key=lambda r: -(r.get("confidence") or 0))
    for r in llm_skips[:TARGET_LLM_SKIPS]:
        c = inbox.get(r["repo"])
        if not c:
            continue
        cases.append(_row(_input_from(c), "skip", r.get("confidence", 0.0), tags=["llm-skip"], source=src))

    # 4. Defers — keep all; they're the boundary cases by construction.
    defers = [r for r in scored if r["decision"] == "defer"]
    for r in defers:
        c = inbox.get(r["repo"])
        if not c:
            continue
        cases.append(_row(_input_from(c), "defer", r.get("confidence", 0.0), tags=["defer"], source=src))

    # 5. Synthetic edge cases — hand-crafted, source=human so they survive
    #    future regeneration AND trigger strict assertions regardless of conf.
    synthetic_inputs = [
        ({
            "repo": "synthetic-eval/llm-agents-365-day-bootcamp",
            "stars": 1200, "forks": 80, "language": "Jupyter Notebook", "license": "MIT",
            "pushed_at": "2026-04-15",
            "description": "365-day curriculum to learn LLM agents from scratch — daily exercises, guided notebooks, and a final capstone. For beginners.",
            "sources": ["topic:llm"],
        }, ["synthetic", "course"]),
        ({
            "repo": "synthetic-eval/awesome-mcp-servers-curated",
            "stars": 4200, "forks": 350, "language": None, "license": "CC0-1.0",
            "pushed_at": "2026-04-22",
            "description": "A curated list of awesome MCP servers, clients, and resources. Pull requests welcome.",
            "sources": ["topic:awesome-list"],
        }, ["synthetic", "awesome-list"]),
        ({
            "repo": "synthetic-eval/langgraph-quickstart-templates",
            "stars": 320, "forks": 40, "language": "Python", "license": "MIT",
            "pushed_at": "2026-04-20",
            "description": "Five-minute starter templates for LangGraph agents. Just clone and customize the prompt.",
            "sources": ["topic:agents"],
        }, ["synthetic", "wrapper"]),
    ]
    for inp, tags in synthetic_inputs:
        cases.append(_row(inp, "skip", 1.0, tags=tags, source="human"))

    return cases


def merge_with_existing(curated: list[dict]) -> list[dict]:
    """Keep pre-existing rows whose metadata.source == "human"; drop the rest."""
    if not OUT.exists():
        return curated
    existing = []
    for line in OUT.read_text().splitlines():
        if not line.strip():
            continue
        try:
            existing.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    human = [c for c in existing if (c.get("metadata") or {}).get("source") == "human"]
    seen_repos = {c["vars"]["candidate"]["repo"] for c in curated}
    out = list(curated)
    for h in human:
        repo = (h.get("vars") or {}).get("candidate", {}).get("repo")
        if not repo or repo in seen_repos:
            continue
        out.append(h)
        seen_repos.add(repo)
    return out


def main() -> int:
    curated = curate()
    final = merge_with_existing(curated)
    OUT.write_text("\n".join(json.dumps(c) for c in final) + "\n")
    by_decision: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    for c in final:
        by_decision[c["vars"]["expected_decision"]] += 1
        by_source[(c.get("metadata") or {}).get("source", "?")] += 1
    print(f"wrote {len(final)} curated cases to {OUT.relative_to(ROOT)}")
    print(f"  by decision: {dict(by_decision)}")
    print(f"  by source:   {dict(by_source)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
