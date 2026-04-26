# Triage scorer eval suite

A promptfoo-driven regression gate for the triage stage of the sweep pipeline (RUNBOOK §7.11). Run it before bumping the model, editing the system prompt, or changing the rubric.

## Files

| File | Purpose |
|---|---|
| `promptfooconfig.yaml` | Provider, prompt template, and shared assertions. |
| `run_one.sh` | Shim — adapts promptfoo's argv-based `exec:` provider to `triage_score.py --single-candidate` (which reads stdin). |
| `cases.jsonl` | Curated test cases in promptfoo's `{description, vars, metadata}` shape. |
| `curate_cases.py` | Rebuilds `cases.jsonl` from past sweep outputs + synthetic edge cases. Idempotent. |
| `seed_cases.py` | Original raw auto-seed generator (every row from `04-triage-scored.*.jsonl`). Kept for reference; `curate_cases.py` is the canonical builder. |

## Running

```bash
cd eval/triage
promptfoo eval                # full suite
promptfoo eval --filter-first-n 5  # first 5 cases (smoke check)
promptfoo view                # browse last results in browser
```

Install once: `npm i -g promptfoo`. `ANTHROPIC_API_KEY` and `gh auth` must be configured — the shim runs the actual production scorer, which makes the same calls it would in a sweep.

## What it asserts

Per case (see `defaultTest` in `promptfooconfig.yaml`):

1. **Schema** — output is valid `TriageDecision` JSON, with `tier ∈ {auto, haiku, haiku→sonnet}`, `decision ∈ {add, defer, skip}`, and `confidence ∈ [0, 1]`.
2. **Decision regression** — strict gate when `expected_confidence ≥ 0.85`. Lower-confidence cases are exempt (they're boundary cases by definition; flips are expected).
3. **Category validity** — when `decision == "add"`, `proposed_category` is one of the 15 known categories.

## Case set composition (current)

`curate_cases.py` builds 38 cases from `state/sweep-2026-04-26b/04-triage-scored.sonnet-readme.jsonl`:

| Tag | Count | Purpose |
|---|---:|---|
| `auto-skip` | 4 | Already-tracked tools — exercise the deterministic pre-filter (no LLM call). |
| `add` (per category) | 15 | Diverse categories, conf ≥ 0.85. Capped at 3 per category. |
| `llm-skip` | 14 | High-confidence rubric-based skips: courses, awesome-lists, redundancies. Conf ≥ 0.92. |
| `defer` | 2 | Boundary cases. Soft-gated (no strict decision assertion). |
| `synthetic` (`source: "human"`) | 3 | Hand-crafted: course, awesome-list, thin-wrapper. Always strict-gated. |

`source: "human"` cases survive future `curate_cases.py` regenerations (the script merges them in). Auto-curated cases (`source: "curated-..."`) get rebuilt each time.

## Current eval result

**36/38 passing (94.7%).** The two failures are known boundary cases — `open-webui/open-webui` and `meilisearch/meilisearch` — where Haiku-with-README and Sonnet-with-README legitimately disagree on whether the tool counts as agentic-AI infrastructure. Documented as accepted disagreement in `runbooks/2026-04-26-triage-upgrade.md` (Finding 3).

To "promote" a boundary case to ground truth, hand-edit `cases.jsonl`: change `metadata.source` to `"human"` and `vars.expected_decision` to whichever call you want to lock in. The change persists across `curate_cases.py` runs.

## Adding a new ground-truth case

Two paths:

1. **Inline edit `cases.jsonl`** — append a row in promptfoo's `{description, vars, metadata}` shape with `metadata.source: "human"`. Survives regeneration.
2. **Add a synthetic case to `curate_cases.py`** — extend the `synthetic_inputs` list. Useful when the case represents a *class* of repo (e.g., "obvious wrapper") rather than a specific real one.

## Regenerating the case set

```bash
python eval/triage/curate_cases.py
# wrote 38 curated cases to eval/triage/cases.jsonl
#   by decision: {'skip': 21, 'add': 15, 'defer': 2}
#   by source:   {'curated-sweep-2026-04-26b-2026-04-26': 35, 'human': 3}
```

When a new sweep lands, edit the `SWEEP` and `SCORED_FILE` constants at the top of `curate_cases.py` to point at the freshest scored output, then rerun.
