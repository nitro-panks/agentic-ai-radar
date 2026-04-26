"""Three-way validation for the triage two-tier upgrade.

Compares Haiku-only and hybrid (Haiku→Sonnet) outputs against the canonical
Sonnet+README baseline. Asserts:

  1. `add` ⇄ `skip` direct-flip rate (computed against the *novel* candidate
     count — auto-skipped already-tracked rows are excluded since they are
     deterministic and trivially agree). PASS < 5%, WARN 5–15%, FAIL > 15%.
  2. Haiku-only confidence histogram is not collapsed near 0.5 (hedging check).

Soft signals (printed, not asserted): hybrid `add` count within ±15% of
baseline, decision-flip rates, decision-distribution diff.

Usage:
    python validate_tier.py \\
        --baseline 04-triage-scored.sonnet-readme.jsonl \\
        --haiku-only 04-triage-scored.haiku-only.jsonl \\
        --hybrid 04-triage-scored.tier.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def load(path: Path) -> dict[str, dict]:
    rows = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]
    return {r["repo"]: r for r in rows}


def diff(label: str, baseline: dict[str, dict], other: dict[str, dict]) -> dict:
    """Return diff stats. Hard-asserts no add⇄skip direct flips."""
    flips: list[tuple[str, str, str]] = []
    add_skip_direct: list[tuple[str, str, str]] = []
    for repo, b in baseline.items():
        o = other.get(repo)
        if o is None:
            continue
        if b["decision"] != o["decision"]:
            flips.append((repo, b["decision"], o["decision"]))
            pair = {b["decision"], o["decision"]}
            if pair == {"add", "skip"}:
                add_skip_direct.append((repo, b["decision"], o["decision"]))

    pair_counter = Counter((b, o) for _, b, o in flips)
    return {
        "label": label,
        "n": len(baseline),
        "n_compared": sum(1 for r in baseline if r in other),
        "flips": len(flips),
        "flip_pairs": pair_counter,
        "add_skip_direct": add_skip_direct,
    }


def hist(values: list[float], bins: list[tuple[float, float]]) -> list[int]:
    out = [0] * len(bins)
    for v in values:
        for i, (lo, hi) in enumerate(bins):
            if lo <= v < hi or (hi == 1.0 and v == 1.0):
                out[i] += 1
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True, help="Sonnet-only canonical output")
    ap.add_argument("--haiku-only", type=Path, required=True)
    ap.add_argument("--hybrid", type=Path, required=True)
    args = ap.parse_args()

    base = load(args.baseline)
    haiku = load(args.haiku_only)
    hybrid = load(args.hybrid)

    print(f"baseline   {args.baseline.name}: {len(base)} rows")
    print(f"haiku-only {args.haiku_only.name}: {len(haiku)} rows")
    print(f"hybrid     {args.hybrid.name}: {len(hybrid)} rows")
    print()

    failed = False

    # --- Decision distribution ---
    def dist(name: str, rows: dict[str, dict]) -> Counter:
        c = Counter(r["decision"] for r in rows.values())
        print(f"  {name:<12} {dict(c)}")
        return c
    print("decision distribution:")
    bd = dist("baseline", base)
    dist("haiku-only", haiku)
    hd = dist("hybrid", hybrid)
    print()

    # `auto`-tier rows are deterministic skips for already-tracked repos; they
    # trivially agree across runs and would dilute the disagreement rate. The
    # meaningful denominator is the count of rows the LLM actually scored.
    novel_count = sum(1 for r in base.values() if r.get("tier") != "auto")

    WARN_THRESHOLD = 0.05  # 5%
    FAIL_THRESHOLD = 0.15  # 15%

    for label, other in (("haiku-only", haiku), ("hybrid", hybrid)):
        d = diff(label, base, other)
        print(f"vs baseline ({label}):")
        print(f"  compared rows: {d['n_compared']} ({novel_count} novel)")
        print(f"  total flips: {d['flips']}")
        for (b_dec, o_dec), n in sorted(d["flip_pairs"].items()):
            print(f"    {b_dec:<5} → {o_dec:<5}  {n}")

        n_direct = len(d["add_skip_direct"])
        rate = n_direct / max(1, novel_count)
        if rate >= FAIL_THRESHOLD:
            failed = True
            verdict = f"✗ FAIL  ({rate:.1%} ≥ {FAIL_THRESHOLD:.0%})"
        elif rate >= WARN_THRESHOLD:
            verdict = f"⚠ WARN  ({rate:.1%}, threshold {WARN_THRESHOLD:.0%}–{FAIL_THRESHOLD:.0%})"
        else:
            verdict = f"✓ PASS  ({rate:.1%} < {WARN_THRESHOLD:.0%})"
        print(f"  add⇄skip direct flips: {n_direct}/{novel_count}  {verdict}")
        for repo, b_dec, o_dec in d["add_skip_direct"][:10]:
            print(f"      {repo}: {b_dec} → {o_dec}")
        print()

    # --- Haiku confidence histogram (hedging check) ---
    confs = [r.get("confidence", 0.0) for r in haiku.values()]
    bins = [(0.0, 0.45), (0.45, 0.55), (0.55, 0.7), (0.7, 0.85), (0.85, 1.0)]
    counts = hist(confs, bins)
    n = len(confs)
    print("haiku-only confidence histogram:")
    for (lo, hi), c in zip(bins, counts):
        bar = "█" * round(40 * c / max(1, n))
        print(f"  [{lo:.2f},{hi:.2f})  {c:>3}  {bar}")
    near_mid = counts[1]  # [0.45, 0.55)
    if n and near_mid / n > 0.6:
        failed = True
        print(f"  ✗ HARD-ASSERT FAIL: {near_mid}/{n} ({near_mid/n:.0%}) of rows in [0.45,0.55) — model is hedging")
    else:
        print(f"  ✓ hedging check passed ({near_mid}/{n} in mid-band)")
    print()

    # --- Soft: hybrid `add` count within ±15% of baseline ---
    base_adds = bd.get("add", 0)
    hyb_adds = hd.get("add", 0)
    if base_adds:
        delta = abs(hyb_adds - base_adds) / base_adds
        flag = "✓" if delta <= 0.15 else "⚠"
        print(f"hybrid adds: {hyb_adds} vs baseline {base_adds} ({delta:+.0%})  {flag}")
    print()

    if failed:
        print("RESULT: FAIL — see hard-assert failures above")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
