"""apply:category-page + apply:landscape + viz:treemap for the Instructor-scored adds.

For each `decision=add` from `04-triage-scored.jsonl`:
  - fetch real metrics via `gh api`
  - update `state/metrics-current.json` and `state/landscape-meta.json`
  - append a sentinel-wrapped stub block to the right category page

Stub blocks are honestly marked as triage-generated; humans flesh out prose later.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/august/code/agentic-ai-radar")
STATE = ROOT / "state"
SWEEP = STATE / "sweep-2026-04-26b"
CATEGORIES_DIR = ROOT / "categories"

sys.path.insert(0, str(STATE / "lib"))
from summarize import make_client, summarize_one  # type: ignore  # noqa: E402

VALID_CATEGORIES = {
    "agent-frameworks", "model-hosting", "model-routing", "rag-and-retrieval",
    "vector-stores", "evaluation", "observability", "tool-use-and-mcp",
    "browser-and-computer-use", "code-agents", "security",
    "orchestration-and-runtime", "memory", "voice-and-multimodal",
    "data-and-extraction",
}


def gh_repo(repo: str) -> dict | None:
    r = subprocess.run(
        ["gh", "api", f"repos/{repo}", "--jq",
         "{full_name, name, stargazers_count, forks_count, subscribers_count, open_issues_count, "
         "language, license: .license.spdx_id, archived, disabled, default_branch, "
         "size, created_at, pushed_at, description, html_url}"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def gh_contributors(repo: str) -> int | None:
    r = subprocess.run(
        ["gh", "api", f"repos/{repo}/contributors?per_page=1&anon=1", "--include"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        if line.lower().startswith("link:") and 'rel="last"' in line:
            for chunk in line.split(","):
                if 'rel="last"' in chunk:
                    url = chunk.split(";")[0].strip().strip("<>")
                    if "page=" in url:
                        try:
                            return int(url.split("page=")[-1].split("&")[0].split(">")[0])
                        except Exception:
                            pass
    # Single page; count rows in body.
    body = r.stdout.split("\n\n", 1)[-1]
    try:
        return len(json.loads(body))
    except Exception:
        return None


def display_name(decision: dict, raw: dict) -> str:
    # Prefer the repo's own `name` field; fall back to the segment after slash, trimmed nicely.
    n = raw.get("name") or decision["repo"].split("/")[-1]
    return n


def short_note(reason: str, max_len: int = 80) -> str:
    """Fallback only — when the LLM summarizer is unavailable. Strips the first
    sentence of the triage reason; not great because triage reasons often mention
    star counts or start with the repo name. Prefer `thesis_for(...)` instead."""
    sent = re.split(r"(?<=[.!?])\s", (reason or "").strip())[0]
    return sent[:max_len].strip()


def thesis_for(client, repo: str, name: str, category: str,
               description: str | None, fallback_reason: str | None) -> str:
    """One-line thesis via the Instructor-backed summarizer. Falls back to the
    truncated triage reason on any error so the pipeline never blocks."""
    try:
        return summarize_one(client, repo, name, category, description, fallback_reason)
    except Exception as e:
        print(f"!! summarizer failed for {repo}: {type(e).__name__}: {e}", file=sys.stderr)
        return short_note(fallback_reason or "")


def stub_block(repo: str, name: str, raw: dict, decision: dict) -> str:
    desc = (raw.get("description") or "").strip()
    reason = (decision.get("reason") or "").strip()
    proposed_cat = decision.get("proposed_category", "")
    redundancy = decision.get("redundancy_with") or []
    confidence = decision.get("confidence", 0.0)
    repo_url = raw.get("html_url") or f"https://github.com/{repo}"

    lines = [
        f"<!-- BEGIN TOOL: {repo} -->",
        f"### {name}",
        f"<!-- repo: {repo} -->",
        "",
        "#### What it is",
        desc or f"_(no description from upstream — see repo for details)_",
        "",
        "#### When to reach for it",
        "- _TODO — needs human review (auto-triaged stub)._",
        "",
        "#### When not to",
        "- _TODO — needs human review (auto-triaged stub)._",
    ]
    if redundancy:
        lines += [
            "",
            "#### How it fits with other tools",
            "- Possible overlap with: " + ", ".join(f"`{r}`" for r in redundancy),
        ]
    lines += [
        "",
        "#### Triage notes",
        f"- Auto-triaged 2026-04-26 (Instructor-scored, confidence {confidence:.2f}): {reason}",
        "",
        "#### Sources",
        f"- Repo: {repo_url}",
        f"<!-- END TOOL: {repo} -->",
        "",
    ]
    return "\n".join(lines)


def update_category_page(cat: str, blocks: list[tuple[str, str, str]]) -> int:
    """blocks = list of (repo, name, block_text). Returns count appended."""
    path = CATEGORIES_DIR / f"{cat}.md"
    if not path.exists():
        print(f"!! category page missing: {path}", file=sys.stderr)
        return 0
    text = path.read_text()
    appended = 0
    new_tools_lines: list[str] = []
    for repo, name, block in blocks:
        if f"<!-- BEGIN TOOL: {repo} -->" in text:
            continue
        text += "\n" + block
        new_tools_lines.append(f'  - {{ name: "{name}", repo: "{repo}" }}')
        appended += 1
    # Update frontmatter `tools:` block.
    if new_tools_lines:
        m = re.search(r"^---\n.*?^last_reviewed:\s*\S+\n---", text, re.MULTILINE | re.DOTALL)
        if m:
            fm = m.group(0)
            tools_match = re.search(r"^tools:\n((?:  - .*\n)+)", fm, re.MULTILINE)
            if tools_match:
                new_tools = tools_match.group(1).rstrip("\n") + "\n" + "\n".join(new_tools_lines) + "\n"
                new_fm = fm.replace(tools_match.group(0), f"tools:\n{new_tools}")
                # Bump last_reviewed.
                new_fm = re.sub(r"last_reviewed:\s*\S+", "last_reviewed: 2026-04-26", new_fm)
                text = text.replace(fm, new_fm, 1)
    path.write_text(text)
    return appended


def main() -> int:
    decisions = [json.loads(ln) for ln in (SWEEP / "04-triage-scored.jsonl").read_text().splitlines() if ln.strip()]
    adds = [d for d in decisions if d["decision"] == "add"]
    defers = [d for d in decisions if d["decision"] == "defer"]
    print(f"applying {len(adds)} adds (deferring {len(defers)} for human review)", file=sys.stderr)

    current = json.loads((STATE / "metrics-current.json").read_text())
    meta = json.loads((STATE / "landscape-meta.json").read_text())
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Filter adds: must propose a valid category and not already be tracked.
    skipped_invalid_cat: list[dict] = []
    skipped_already_tracked: list[dict] = []
    todo: list[dict] = []
    for d in adds:
        cat = d.get("proposed_category")
        if cat not in VALID_CATEGORIES:
            d["_skip_reason"] = f"invalid proposed_category: {cat!r}"
            skipped_invalid_cat.append(d)
            continue
        if d["repo"] in current["tools"]:
            skipped_already_tracked.append(d)
            continue
        todo.append(d)
    print(f"  → fetching metrics for {len(todo)} candidates", file=sys.stderr)

    fetched: dict[str, tuple[dict, int | None]] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        future_to_repo = {pool.submit(gh_repo, d["repo"]): d for d in todo}
        for fut in as_completed(future_to_repo):
            d = future_to_repo[fut]
            raw = fut.result()
            if raw is None:
                print(f"!! repo fetch failed for {d['repo']}", file=sys.stderr)
                continue
            fetched[d["repo"]] = (raw, None)

    # Contributors in a second pass (cheap parallelizable).
    with ThreadPoolExecutor(max_workers=8) as pool:
        future_to_repo = {pool.submit(gh_contributors, repo): repo for repo in fetched}
        for fut in as_completed(future_to_repo):
            repo = future_to_repo[fut]
            raw, _ = fetched[repo]
            fetched[repo] = (raw, fut.result())

    # Apply.
    summarizer = make_client()
    by_cat: dict[str, list[tuple[str, str, str]]] = {}
    applied = 0
    for d in todo:
        if d["repo"] not in fetched:
            continue
        raw, contrib = fetched[d["repo"]]
        if raw.get("archived") or raw.get("disabled"):
            print(f"  - skip {d['repo']}: archived/disabled at fetch time", file=sys.stderr)
            continue
        repo = d["repo"]
        cat = d["proposed_category"]
        name = display_name(d, raw)

        current["tools"][repo] = {
            "name": name, "category": cat, "repo": repo,
            "stars": raw["stargazers_count"], "forks": raw["forks_count"],
            "watchers": raw["subscribers_count"], "open_issues": raw["open_issues_count"],
            "contributors": contrib,
            "language": raw["language"], "license": raw["license"],
            "archived": raw["archived"], "disabled": raw["disabled"],
            "default_branch": raw["default_branch"], "size_kb": raw["size"],
            "created_at": (raw["created_at"] or "")[:10],
            "pushed_at": (raw["pushed_at"] or "")[:10],
            "stars_30d": None, "stars_90d": None, "commits_30d": None,
            "release_cadence_days": None, "latest_release": None, "latest_release_date": None,
            "status": "active", "snapshot_ts": ts,
        }
        thesis = thesis_for(summarizer, repo, name, cat,
                             raw.get("description"), d.get("reason"))
        meta[repo] = {
            "deploy_status": d.get("proposed_deploy_status") or "beta",
            "notes": thesis,
            "last_reviewed": "2026-04-26",
            "triage": {
                "auto": True, "model": "claude-sonnet-4-5",
                "confidence": d.get("confidence"),
                "redundancy_with": d.get("redundancy_with") or [],
            },
        }
        block = stub_block(repo, name, raw, d)
        by_cat.setdefault(cat, []).append((repo, name, block))
        applied += 1

    # Write category-page edits.
    written_per_cat = {cat: update_category_page(cat, blocks) for cat, blocks in by_cat.items()}

    current["generated_at"] = ts
    (STATE / "metrics-current.json").write_text(json.dumps(current, indent=2) + "\n")
    (STATE / "landscape-meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    # 05-actions.jsonl
    actions = [
        {"repo": d["repo"], "action": "create-stub",
         "path": f"categories/{d['proposed_category']}.md",
         "category": d["proposed_category"], "ts": ts}
        for d in todo if d["repo"] in fetched
    ]
    with (SWEEP / "05-actions.jsonl").open("w") as f:
        for a in actions:
            f.write(json.dumps(a) + "\n")

    # Summary.
    print(json.dumps({
        "adds_applied": applied,
        "by_category": {c: len(b) for c, b in by_cat.items()},
        "appended_per_category": written_per_cat,
        "skipped_invalid_cat": [d["repo"] for d in skipped_invalid_cat],
        "skipped_already_tracked": [d["repo"] for d in skipped_already_tracked],
        "deferred_count": len(defers),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
