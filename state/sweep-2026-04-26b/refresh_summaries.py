"""Refresh the `notes` field in `state/landscape-meta.json` for every tracked tool
using the Instructor-backed thesis summarizer in `state/lib/summarize.py`.

After running, regenerates `landscape.md` and `viz/data.json` so the new tooltips
take effect immediately.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/august/code/agentic-ai-radar")
STATE = ROOT / "state"

sys.path.insert(0, str(STATE / "lib"))
from summarize import summarize_many  # type: ignore  # noqa: E402


def gh_description(repo: str) -> str | None:
    r = subprocess.run(["gh", "api", f"repos/{repo}", "--jq", ".description"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        return None
    desc = r.stdout.strip()
    return desc if desc and desc != "null" else None


def main() -> int:
    current = json.loads((STATE / "metrics-current.json").read_text())
    meta = json.loads((STATE / "landscape-meta.json").read_text())

    items = []
    for repo, m in current["tools"].items():
        prior = (meta.get(repo) or {}).get("notes")
        items.append({
            "repo": repo,
            "name": m.get("name") or repo.split("/")[-1],
            "category": m.get("category") or "uncategorized",
            "description": gh_description(repo),
            "prior_notes": prior,
        })

    print(f"summarizing {len(items)} tools", file=sys.stderr)
    summaries = summarize_many(items, workers=8)
    print(f"\n{len(summaries)}/{len(items)} succeeded", file=sys.stderr)

    # Write through to landscape-meta.json. Preserve existing keys; bump last_reviewed.
    today = "2026-04-26"
    for repo, summary in summaries.items():
        entry = meta.setdefault(repo, {"deploy_status": None})
        entry["notes"] = summary
        entry["last_reviewed"] = today

    # Backup before overwriting.
    bak = STATE / "landscape-meta.before-summary-refresh.json"
    if not bak.exists():
        bak.write_text(json.dumps(json.loads((STATE / "landscape-meta.json").read_text()), indent=2) + "\n")
    (STATE / "landscape-meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"\nwrote {STATE/'landscape-meta.json'} (backup at {bak.name})", file=sys.stderr)

    # Regenerate landscape.md + viz/data.json (same logic as the apply:landscape stage).
    LIGHT = {"prod": "🟢", "beta": "🟡", "deprecated": "🔴", None: "—"}
    rows, untriaged = [], []
    for repo, m in current["tools"].items():
        deploy = (meta.get(repo) or {}).get("deploy_status")
        if deploy is None:
            untriaged.append(repo)
        rows.append({
            "name": m.get("name") or repo.split("/")[-1],
            "category": m.get("category") or "uncategorized",
            "light": LIGHT.get(deploy, "—"), "repo": repo,
            "stars": m.get("stars") or 0, "forks": m.get("forks") or 0,
            "stars_30d": m.get("stars_30d"), "pushed_at": m.get("pushed_at") or "—",
            "notes": (meta.get(repo) or {}).get("notes", ""),
            "archived": m.get("archived"),
        })
    rows.sort(key=lambda r: (r["category"], -r["stars"]))
    fn = lambda n: "—" if n is None else f"{n:,}"

    def fd(n):
        if n is None:
            return "—"
        return f"{'+' if n >= 0 else ''}{n:,}"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n_t, n_c = len(rows), len({r["category"] for r in rows})
    lines = [
        "# Landscape", "",
        f"_Generated {ts[:10]} from {n_t} tools across {n_c} categories. Do not hand-edit — see `RUNBOOK.md` §8._", "",
        "| Tool | Category | Status | Repo | Stars | Forks | Δ30d | Last push | Notes |",
        "|---|---|:---:|---|---:|---:|---:|---|---|",
    ]
    for r in rows:
        notes = r["notes"]
        if r["archived"] and "archived" not in (notes or "").lower():
            notes = ("⚠ archived. " + notes).strip()
        lines.append(
            f"| {r['name']} | {r['category']} | {r['light']} | {r['repo']} | "
            f"{fn(r['stars'])} | {fn(r['forks'])} | {fd(r['stars_30d'])} | {r['pushed_at']} | {(notes or '')[:90]} |"
        )
    lines += [
        "", "**Status legend**: 🟢 prod · 🟡 beta · 🔴 deprecated · — untriaged", "",
        "**Untriaged**: " + (", ".join(untriaged) if untriaged else "_none this sweep_"),
    ]
    (ROOT / "landscape.md").write_text("\n".join(lines) + "\n")

    by_cat: dict[str, list[dict]] = {}
    for repo, m in current["tools"].items():
        cat = m.get("category") or "uncategorized"
        by_cat.setdefault(cat, []).append({
            "name": m.get("name") or repo.split("/")[-1], "repo": repo,
            "deploy_status": (meta.get(repo) or {}).get("deploy_status"),
            "status": "archived" if m.get("archived") else (m.get("status") or "active"),
            "stars": m.get("stars") or 0, "forks": m.get("forks") or 0,
            "watchers": m.get("watchers") or 0, "open_issues": m.get("open_issues") or 0,
            "contributors": m.get("contributors") or 0,
            "stars_30d": m.get("stars_30d"), "stars_90d": m.get("stars_90d"),
            "pushed_at": m.get("pushed_at"), "license": m.get("license"),
            "language": m.get("language"), "notes": (meta.get(repo) or {}).get("notes", ""),
        })
    children = [{"name": cat, "children": sorted(by_cat[cat], key=lambda x: -x["stars"])} for cat in sorted(by_cat)]
    viz = {"name": "ai-radar", "generated_at": ts, "children": children}
    (ROOT / "viz" / "data.json").write_text(json.dumps(viz, indent=2) + "\n")
    print(f"\nlandscape.md: {n_t} rows · viz/data.json: {sum(len(c['children']) for c in children)} leaves", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
