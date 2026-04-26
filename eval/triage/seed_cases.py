"""Build a seed eval set for the triage scorer from past sweep outputs.

Reads `state/sweep-*/04-triage-scored.jsonl`, joins each row to its inbox
candidate (for the input fields the scorer needs), and emits one JSON-line
per case to `eval/triage/cases.jsonl`.

Cases are auto-seeded — past decisions are *not* ground truth. The
`expected.confidence` field captures the past confidence so the harness can
gate strict assertions on high-confidence past decisions only. Humans curating
real ground truth should override `source: "auto-seed-..."` with `"human"`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state"
OUT_PATH = ROOT / "eval" / "triage" / "cases.jsonl"

# Use the new-system output (Sonnet+README+auto) as the seed when available;
# fall back to the original Sonnet-no-README output otherwise.
PREFERRED_SCORED = "04-triage-scored.sonnet-readme.jsonl"
FALLBACK_SCORED = "04-triage-scored.jsonl"


def collect_sweeps() -> list[Path]:
    return sorted(p for p in STATE.glob("sweep-*") if p.is_dir())


def seed_cases() -> list[dict]:
    cases: list[dict] = []
    seen: set[str] = set()
    for sweep_dir in collect_sweeps():
        inbox_path = sweep_dir / "01-inbox.jsonl"
        scored_path = sweep_dir / PREFERRED_SCORED
        if not scored_path.exists():
            scored_path = sweep_dir / FALLBACK_SCORED
        if not (inbox_path.exists() and scored_path.exists()):
            continue
        inbox = {json.loads(l)["repo"]: json.loads(l) for l in inbox_path.read_text().splitlines() if l.strip()}
        for line in scored_path.read_text().splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            repo = d["repo"]
            if repo in seen:
                continue
            seen.add(repo)
            c = inbox.get(repo)
            if not c:
                continue
            cases.append({
                "input": {
                    "repo": repo,
                    "stars": c.get("stars"),
                    "forks": c.get("forks"),
                    "language": c.get("language"),
                    "license": c.get("license"),
                    "pushed_at": c.get("pushed_at"),
                    "description": c.get("description") or "",
                    "sources": c.get("sources") or [],
                },
                "expected": {
                    "decision": d["decision"],
                    "proposed_category": d.get("proposed_category"),
                    "confidence": d.get("confidence", 0.0),
                },
                "source": f"auto-seed-from-{sweep_dir.name}-via-{scored_path.name.replace('04-triage-scored.', '').replace('.jsonl', '') or 'canonical'}",
            })
    return cases


def main() -> int:
    cases = seed_cases()
    OUT_PATH.write_text("\n".join(json.dumps(c) for c in cases) + "\n")
    n_high = sum(1 for c in cases if c["expected"]["confidence"] >= 0.85)
    print(f"wrote {len(cases)} seed cases ({n_high} high-confidence) to {OUT_PATH.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
