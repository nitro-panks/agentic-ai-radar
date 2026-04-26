"""Two-tier triage scorer for ai-radar sweep candidates (RUNBOOK §7.11).

Reads `01-inbox.jsonl`, fetches each candidate's README, and asks Claude (via
instructor) to classify them against the radar's category schema. The first pass
uses Haiku 4.5 across all candidates. A second pass with Sonnet 4.5 re-scores
rows that came back `defer` or with low confidence, where the better model is
worth the extra cost.

Outputs `04-triage-scored.jsonl` with one TriageDecision per candidate, each
annotated with `tier: "haiku"` or `tier: "haiku→sonnet"`.

Single-candidate mode (for promptfoo and ad-hoc spot checks):

    echo '{"repo":"foo/bar","stars":42,...}' | python triage_score.py --single-candidate
    python triage_score.py --single-candidate --repo owner/name --stars 1234

In single-candidate mode the second pass is always run for `defer` / low-conf
results, mirroring the production hybrid behavior.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal

import anthropic
import instructor
from pydantic import BaseModel, Field

# Allow running as a script (no package context) and still import sibling modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from readme_fetch import fetch_readme  # noqa: E402

ROOT = Path("/home/august/code/agentic-ai-radar")
STATE = ROOT / "state"
SWEEP = STATE / "sweep-2026-04-26b"

# Model IDs verified callable 2026-04-26 (see runbooks/2026-04-26-triage-upgrade.md).
FIRST_PASS_MODEL = "claude-haiku-4-5"
SECOND_PASS_MODEL = "claude-sonnet-4-5"
SECOND_PASS_CONFIDENCE_FLOOR = 0.7

MAX_TOKENS = 600
WORKERS = 8

CATEGORIES = [
    "agent-frameworks", "model-hosting", "model-routing", "rag-and-retrieval",
    "vector-stores", "evaluation", "observability", "tool-use-and-mcp",
    "browser-and-computer-use", "code-agents", "security",
    "orchestration-and-runtime", "memory", "voice-and-multimodal",
    "data-and-extraction",
]


class TriageDecision(BaseModel):
    """Structured triage decision for one candidate repo."""

    decision: Literal["add", "defer", "skip"] = Field(
        description=(
            "add: confident this is a real, distinctive tool that belongs on the radar now. "
            "defer: borderline or needs human eye (legitimate but uncertain category, novel sub-shape, "
            "small but high-velocity). "
            "skip: off-topic, course/tutorial/awesome-list, marketing/star-farm smell, archived, "
            "or strictly redundant with an already-tracked tool."
        )
    )
    confidence: float = Field(ge=0.0, le=1.0, description="0.0 to 1.0")
    proposed_category: str | None = Field(
        default=None,
        description=(
            "One of the 15 ai-radar categories, or null if decision is `skip` and the repo doesn't fit. "
            "Choose the closest fit; if the tool spans categories, pick the strongest one and mention "
            "the others in `reason`."
        ),
    )
    proposed_deploy_status: Literal["prod", "beta", "deprecated"] | None = Field(
        default=None,
        description=(
            "Our adoption stance — independent of upstream health. "
            "prod = recommend for new projects without further investigation; "
            "beta = piloting / promising but uncertain; "
            "deprecated = avoid (and `reason` should explain why). "
            "Default to `beta` for new adds unless very high confidence."
        ),
    )
    redundancy_with: list[str] = Field(
        default_factory=list,
        description="Repos already on the radar that this tool overlaps with materially.",
    )
    reason: str = Field(
        max_length=400,
        description="Two or three short sentences. The why behind the decision; cite distinctive features.",
    )


def build_system_prompt(tracked: dict[str, dict]) -> str:
    tracked_block = "\n".join(
        f"- {repo} ({m.get('category','?')}, {m.get('stars',0)} stars): {m.get('name', repo.split('/')[-1])}"
        for repo, m in sorted(tracked.items(), key=lambda kv: kv[0])
    )
    return f"""You triage candidate GitHub repos for the ai-radar — a curated knowledge base of agentic-AI tooling.

# Goal of the radar
Help engineers pick the right OSS tool when starting a project or evaluating an addition. The radar is GitHub-anchored: every entry has a public repo. Quality bar matters more than coverage; one well-judged "add" beats five lukewarm ones.

# Categories (pick exactly one when adding)
{', '.join(CATEGORIES)}

# Decision criteria
- ADD when the tool is a real, distinctive piece of agentic-AI infrastructure that an engineer would want to know about. Examples of strong "add": canonical projects on the coverage checklist, distinctive sub-shapes that the radar lacks, established tools with a clear when-to-reach-for niche.
- DEFER when the tool seems legitimate but the category fit is unclear, the tool is small but rapidly growing, or it's a novel sub-shape that warrants human framing.
- SKIP when:
  - The repo is a tutorial / course / awesome-list / paper-replication / cheat-sheet (e.g. names like "ai-agents-for-beginners", "prompt-engineering-guide", "best-practices").
  - The repo's description reads as marketing / star-farming / LLM-generated hype with vague claims and no concrete technical contribution.
  - The repo is strictly redundant with an already-tracked tool (then list the overlap in `redundancy_with`).
  - The repo is a model checkpoint, dataset, or research demo rather than tooling.
  - The repo is off-topic (general dev tools that happen to mention AI, OCR, low-code, search engines without LLM relevance).

# Currently tracked tools (do not re-add; flag overlaps in `redundancy_with`)
{tracked_block}

# How to think
- Read the candidate's full_name, description, language, license, stars, pushed_at, and the README excerpt when present.
- The README is the strongest signal: a course/tutorial reads like a syllabus; a wrapper reads "thin wrapper around X"; a real tool documents an API surface, install command, or architecture.
- Ask: "Would a senior engineer evaluating their stack be surprised this exists?" Strong yes → likely add. Strong no (it's a course / wrapper / vibe-named project) → skip.
- High stars alone do not justify add. New repos often get inflated by trends.
- A tool that only adds a thin wrapper over an already-tracked one → skip with redundancy_with.
- When in doubt, prefer DEFER over ADD."""


def candidate_user_message(c: dict) -> str:
    base = (
        f"Candidate repo: {c['repo']}\n"
        f"Stars: {c.get('stars')} · Forks: {c.get('forks')} · Language: {c.get('language')} · "
        f"License: {c.get('license')} · Last push: {c.get('pushed_at')}\n"
        f"Topic source(s): {', '.join(c.get('sources', []))}\n"
        f"Description: {c.get('description') or '(none)'}\n"
    )
    readme = c.get("readme") or ""
    if readme.strip():
        base += (
            f"\nREADME excerpt (first {len(readme)} chars):\n"
            f"---\n{readme}\n---\n"
        )
    base += "\nTriage this candidate."
    return base


def score_one(
    client: instructor.Instructor,
    system_prompt: str,
    candidate: dict,
    *,
    model: str,
) -> dict:
    try:
        decision = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    # Cache the long system prompt so subsequent calls bill ~10% of the tokens.
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": candidate_user_message(candidate)}],
            response_model=TriageDecision,
        )
        out = decision.model_dump()
        out["repo"] = candidate["repo"]
        out["stars"] = candidate.get("stars")
        out["category_guess"] = candidate.get("category_guess")
        return out
    except Exception as e:
        return {
            "repo": candidate["repo"],
            "decision": "defer",
            "confidence": 0.0,
            "reason": f"scorer error: {type(e).__name__}: {str(e)[:200]}",
            "stars": candidate.get("stars"),
            "category_guess": candidate.get("category_guess"),
            "_error": True,
        }


def needs_rerun(d: dict) -> bool:
    return (
        d.get("_error")
        or d.get("decision") == "defer"
        or (d.get("confidence") or 0.0) < SECOND_PASS_CONFIDENCE_FLOOR
    )


def auto_skip_tracked(candidate: dict) -> dict:
    """Deterministic skip for repos already on the radar — no LLM call needed.

    The LLM is unreliable at applying "do not re-add tracked tools" from prose.
    Filtering here is correct behavior regardless of model: an already-tracked
    repo should never be re-decided as `add` at triage time.
    """
    return {
        "repo": candidate["repo"],
        "decision": "skip",
        "confidence": 1.0,
        "proposed_category": None,
        "proposed_deploy_status": None,
        "redundancy_with": [candidate["repo"]],
        "reason": "Already tracked on the radar (auto-skip; no LLM call).",
        "stars": candidate.get("stars"),
        "category_guess": candidate.get("category_guess"),
        "tier": "auto",
    }


def run_triage(
    candidates: list[dict],
    *,
    second_pass: bool = True,
    progress: bool = True,
) -> list[dict]:
    """Score every candidate. Returns a list of decision dicts in input order.

    Each decision is annotated with a `tier` field reflecting which model(s)
    actually produced it: "auto" (deterministic pre-filter), "haiku" (first
    pass only), or "haiku→sonnet" (rescored).
    """
    tracked = json.loads((STATE / "metrics-current.json").read_text())["tools"]
    tracked_repos = {r for r in tracked if "/" in r}
    system_prompt = build_system_prompt(tracked)
    client = instructor.from_anthropic(anthropic.Anthropic())

    decisions_by_repo: dict[str, dict] = {}
    novel: list[dict] = []
    for c in candidates:
        if c["repo"] in tracked_repos:
            decisions_by_repo[c["repo"]] = auto_skip_tracked(c)
        else:
            novel.append(c)

    n_auto = len(candidates) - len(novel)
    if progress:
        print(
            f"auto-skip: {n_auto} already-tracked candidates filtered (no LLM call)",
            file=sys.stderr,
        )
        print(
            f"first pass: {len(novel)} candidates · {FIRST_PASS_MODEL} · {WORKERS} workers",
            file=sys.stderr,
        )

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {
            pool.submit(score_one, client, system_prompt, c, model=FIRST_PASS_MODEL): c
            for c in novel
        }
        for i, fut in enumerate(as_completed(futures), 1):
            d = fut.result()
            d["tier"] = "haiku"
            decisions_by_repo[d["repo"]] = d
            if progress:
                print(
                    f"[{i:>3}/{len(novel)}] {d['repo']:<55} "
                    f"→ {d['decision']:<5} ({d.get('confidence', 0):.2f}) "
                    f"{d.get('proposed_category') or '-':<28} "
                    f"{(d.get('reason') or '')[:60]}",
                    file=sys.stderr,
                )

    # Only the novel set is eligible for the second pass — auto-skipped tracked
    # repos already have a deterministic decision and a `tier == "auto"` annotation.
    rerun_set = [decisions_by_repo[c["repo"]] for c in novel if needs_rerun(decisions_by_repo[c["repo"]])]

    if second_pass and rerun_set:
        if progress:
            print(
                f"\nsecond pass: {len(rerun_set)} candidates · {SECOND_PASS_MODEL}",
                file=sys.stderr,
            )
        flips = 0
        cand_by_repo = {c["repo"]: c for c in novel}
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {
                pool.submit(
                    score_one, client, system_prompt, cand_by_repo[d["repo"]],
                    model=SECOND_PASS_MODEL,
                ): d for d in rerun_set
            }
            for i, fut in enumerate(as_completed(futures), 1):
                new_d = fut.result()
                new_d["tier"] = "haiku→sonnet"
                old_d = decisions_by_repo[new_d["repo"]]
                if new_d["decision"] != old_d["decision"]:
                    flips += 1
                decisions_by_repo[new_d["repo"]] = new_d
                if progress:
                    arrow = "→" if new_d["decision"] == old_d["decision"] else "⇒"
                    print(
                        f"[{i:>3}/{len(rerun_set)}] {new_d['repo']:<55} "
                        f"{old_d['decision']:<5} {arrow} {new_d['decision']:<5} "
                        f"({new_d.get('confidence', 0):.2f}) "
                        f"{(new_d.get('reason') or '')[:60]}",
                        file=sys.stderr,
                    )
        if progress:
            print(
                f"\nsecond-pass flips: {flips}/{len(rerun_set)} re-scored rows changed decision",
                file=sys.stderr,
            )

    return [decisions_by_repo[c["repo"]] for c in candidates]


def attach_readmes(candidates: list[dict], *, progress: bool = True) -> tuple[int, int]:
    hit = miss = 0
    for c in candidates:
        text = fetch_readme(c["repo"])
        if text:
            c["readme"] = text
            hit += 1
        else:
            c["readme"] = ""
            miss += 1
    if progress:
        print(f"README fetch: {hit} hit, {miss} miss", file=sys.stderr)
    return hit, miss


def main_batch(
    inbox_path: Path,
    out_path: Path,
    *,
    second_pass: bool,
) -> int:
    candidates = [json.loads(ln) for ln in inbox_path.read_text().splitlines() if ln.strip()]
    attach_readmes(candidates)
    decisions = run_triage(candidates, second_pass=second_pass)

    rank = {"add": 0, "defer": 1, "skip": 2}
    decisions.sort(key=lambda d: (rank.get(d["decision"], 9), -(d.get("stars") or 0)))

    with out_path.open("w") as f:
        for d in decisions:
            f.write(json.dumps(d) + "\n")

    counts = {"add": 0, "defer": 0, "skip": 0, "errors": 0}
    for d in decisions:
        if d.get("_error"):
            counts["errors"] += 1
        else:
            counts[d["decision"]] = counts.get(d["decision"], 0) + 1

    print("\n=== SUMMARY ===", file=sys.stderr)
    print(json.dumps(counts, indent=2))
    print(f"\nwrote {out_path}", file=sys.stderr)
    return 0


def main_single(args: argparse.Namespace) -> int:
    """Score one candidate from stdin or CLI flags. Emit one JSON line on stdout."""
    if args.repo:
        candidate = {
            "repo": args.repo,
            "stars": args.stars,
            "forks": args.forks,
            "language": args.language,
            "license": args.license,
            "pushed_at": args.pushed_at,
            "description": args.description or "",
            "sources": [],
        }
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("usage: --single-candidate with stdin JSON or --repo flag", file=sys.stderr)
            return 1
        candidate = json.loads(raw)

    attach_readmes([candidate], progress=False)
    [decision] = run_triage([candidate], second_pass=not args.no_second_pass, progress=False)
    sys.stdout.write(json.dumps(decision) + "\n")
    return 0


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Two-tier triage scorer.")
    p.add_argument("--inbox", type=Path, default=SWEEP / "01-inbox.jsonl")
    p.add_argument("--out", type=Path, default=SWEEP / "04-triage-scored.jsonl")
    p.add_argument(
        "--no-second-pass",
        action="store_true",
        help="Skip the Sonnet rerun. Useful for Haiku-only baselines.",
    )
    p.add_argument(
        "--single-candidate",
        action="store_true",
        help="Score one candidate from stdin or --repo args; write one JSON line to stdout.",
    )
    p.add_argument("--repo")
    p.add_argument("--stars", type=int)
    p.add_argument("--forks", type=int)
    p.add_argument("--language")
    p.add_argument("--license")
    p.add_argument("--pushed-at")
    p.add_argument("--description")
    return p


def main() -> int:
    args = build_argparser().parse_args()
    if args.single_candidate:
        return main_single(args)
    return main_batch(args.inbox, args.out, second_pass=not args.no_second_pass)


if __name__ == "__main__":
    sys.exit(main())
