#!/usr/bin/env python3
"""viz:treemap stage — regenerate viz/data.json from metrics-current.json + landscape-meta.json.

Hierarchy: root → category → tool. Schema per RUNBOOK §7.17.
"""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "state" / "metrics-current.json"
META = ROOT / "state" / "landscape-meta.json"
OUT_CURRENT = ROOT / "viz" / "data.json"
SWEEP_DATE = "2026-04-26"
OUT_ARCHIVE = ROOT / "viz" / f"data-{SWEEP_DATE}c.json"

LEAF_FIELDS = (
    "stars", "forks", "watchers", "open_issues", "contributors",
    "stars_30d", "stars_90d", "pushed_at", "license", "language",
)

def main() -> None:
    metrics = json.loads(METRICS.read_text())["tools"]
    meta = json.loads(META.read_text())

    by_category: dict[str, list[dict]] = defaultdict(list)
    for repo, m in metrics.items():
        cat = m.get("category")
        if not cat:
            continue
        meta_entry = meta.get(repo, {}) if isinstance(meta.get(repo), dict) else {}
        leaf = {
            "name": m.get("name", repo.split("/")[-1]),
            "repo": repo,
            "deploy_status": meta_entry.get("deploy_status"),
            "status": m.get("status"),
        }
        for f in LEAF_FIELDS:
            leaf[f] = m.get(f)
        leaf["notes"] = meta_entry.get("notes", "")
        by_category[cat].append(leaf)

    for cat in by_category:
        by_category[cat].sort(key=lambda t: (-(t.get("stars") or 0), t["name"].lower()))

    children = [
        {"name": cat, "children": tools}
        for cat, tools in sorted(by_category.items())
    ]

    payload = {
        "name": "agentic-ai-radar",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "children": children,
    }

    text = json.dumps(payload, indent=2) + "\n"
    OUT_CURRENT.write_text(text)
    OUT_ARCHIVE.write_text(text)

    n_tools = sum(len(c["children"]) for c in children)
    print(f"viz:treemap → {n_tools} tools across {len(children)} categories")
    print(f"  wrote {OUT_CURRENT.relative_to(ROOT)}")
    print(f"  wrote {OUT_ARCHIVE.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
