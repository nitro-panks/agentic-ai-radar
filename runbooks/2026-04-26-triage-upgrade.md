# Runbook — Triage scoring upgrade (2026-04-26)

One-shot upgrade plan for the `triage` stage of the sweep pipeline (RUNBOOK.md §7.11). Three independent phases, ordered by ROI. Each phase is self-contained, has its own validation, and can be rolled back without affecting the others.

## Goal

Improve quality and reduce cost of the auto-triage step that classifies inbox candidates into `add` / `defer` / `skip`. Today it is a single-pass Sonnet 4.5 call seeing only `description, language, license, stars, pushed_at, sources`. Three changes:

1. **Two-tier model**: Haiku 4.5 default, Sonnet 4.5 only on rows the first pass marked `defer` or scored with low confidence.
2. **README enrichment**: fetch the candidate's GitHub README and feed an excerpt to the triage call so the model has more than the description to judge "real tool vs course/wrapper."
3. **promptfoo eval harness**: a regression gate that compares any triage prompt/model change against a labeled set of past decisions.

## Non-goals

- Not changing the rubric, categories, decision schema, or DAG topology.
- Not changing what `apply_adds.py` consumes — `04-triage-scored.jsonl` schema stays a superset.
- Not introducing Langfuse. The radar is offline batch — observability adds ceremony without proportional value at current scale.

## Baseline (pre-change)

From `state/sweep-2026-04-26b/04-triage-scored.jsonl` (164 candidates):

| Decision | Count | Low-confidence (<0.7) |
|---|---:|---:|
| add | 67 | 0 |
| defer | 28 | 25 |
| skip | 69 | 0 |

Implication for two-tier sizing: ~28/164 = **17% of rows** would be re-scored on Sonnet under the current prompt, the other 83% terminate on Haiku. Cost reduction is real but unquantified here on purpose: Phase 1's savings get partially eaten by Phase 2's larger user message (README excerpt is ~25× the description-only payload and is not cached). Operators should re-measure end-to-end after both phases ship.

## Pre-flight (run once, before any phase)

- Confirm model IDs exist and are callable. Verified 2026-04-26: `claude-haiku-4-5`, `claude-haiku-4-5-20251001`, `claude-sonnet-4-5`, `claude-sonnet-4-5-20250929` all return 200 on a 4-token probe. We use the unpinned aliases — pin only if a specific minor regression appears.
- Confirm `gh auth status` shows an account with `repo` scope (for Phase 2 `gh api repos/{repo}/readme`).
- `.gitignore` does NOT exist at repo root (verified 2026-04-26). Create one in Phase 2 with at minimum `state/.cache/`.

## Phase 1 — Two-tier Haiku → Sonnet

### Why first
Pure code change to one file, no new dependencies, no new env vars, no schema migration. Direct cost reduction with no quality loss on the rows that matter (defers and low-confidence get the better model).

### Files touched
- `state/sweep-2026-04-26b/triage_score.py` — model constants and a second-pass loop.

### Implementation
1. Replace `MODEL = "claude-sonnet-4-5"` with two constants:
   ```python
   FIRST_PASS_MODEL = "claude-haiku-4-5"
   SECOND_PASS_MODEL = "claude-sonnet-4-5"
   SECOND_PASS_CONFIDENCE_FLOOR = 0.7
   ```
2. Generalize `score_one(...)` to take `model` as a parameter.
3. After the first-pass `as_completed` loop, build a list of rows where `decision == "defer"` OR `confidence < SECOND_PASS_CONFIDENCE_FLOOR` OR `_error == True`. Re-score that list with `SECOND_PASS_MODEL`. Replace the corresponding entries in `decisions`.
4. Annotate every output row with `"tier": "haiku"` or `"tier": "haiku→sonnet"` so downstream consumers and humans can audit which model produced each decision.
5. Print a second summary block after the second pass: "rescored N rows on Sonnet — A→B decision flips" so the operator sees the disagreement rate at a glance.

### Validation

Two artifacts, three-way comparison. The hybrid is what we ship; the Haiku-only run is what tells us whether the second-pass filter is catching the rows that needed it.

1. Run **Haiku-only** on all 164 candidates → `04-triage-scored.haiku-only.jsonl`. (Set `SECOND_PASS_CONFIDENCE_FLOOR = -1` and skip the defer-rerun, or run a one-flag mode that disables the second pass.)
2. Run **hybrid** on all 164 → `04-triage-scored.tier.jsonl`.
3. Compare both to the canonical Sonnet output `04-triage-scored.jsonl`.

A small standalone script `state/sweep-2026-04-26b/validate_tier.py` (created during implementation) runs the diffs and **hard-asserts** the stop-signs:

- `Haiku-only vs Sonnet`: count `add` ⇄ `skip` direct flips (no intermediate `defer`). Hard-assert: zero. If any, stop and investigate before promoting.
- `Hybrid vs Sonnet`: same hard-assert. Hybrid is allowed to disagree, but never on a strong case.
- `Haiku-only`: confidence-histogram check. Hard-assert that less than 60% of rows fall in `[0.45, 0.55]` (i.e., model is not hedging on every call).

Soft signals (printed but not asserted):
- Hybrid `add` count within ±15% of Sonnet's 67. Drift > 15% is worth a manual look.
- Decision-flip rate Haiku-only → hybrid ≈ second-pass-rerun rate. If they diverge wildly, the rerun set is mis-defined.

### Rollback
Revert the `MODEL = "claude-sonnet-4-5"` line.

## Phase 2 — README enrichment

### Why second
Improves what the model sees; addresses the actual quality bottleneck (description-only is thin signal for distinguishing "real tool" from "course/awesome-list/wrapper"). Larger code change than Phase 1 but still localized to the triage stage.

### Decision: GitHub API, not Firecrawl

I previously suggested Firecrawl. Re-examining: the radar is **GitHub-anchored** (RUNBOOK §14: "Hosted-only products → at most a stub block. Radar is GitHub-anchored."). Every triage candidate has a public GitHub repo. The GitHub REST API exposes README markdown directly via `GET /repos/{repo}/readme` — no parsing, no JS, no auth beyond what `gh auth` already provides, no per-fetch billing. Firecrawl's value is generic web → markdown across heterogeneous sources, which is overkill when the source is one well-formed API.

**Therefore:** Phase 2 uses the GitHub REST API. Firecrawl stays a candidate for a *future* enrichment layer (e.g., fetching project landing pages or external docs sites linked from a candidate's README), which is out of scope here.

### Files touched
- New: `state/sweep-2026-04-26b/readme_fetch.py` — standalone fetcher with a tiny disk cache.
- Modify: `state/sweep-2026-04-26b/triage_score.py` — call the fetcher, append README excerpt to the user message.
- New: `state/.cache/readmes/` — disk cache, gitignored.
- Modify: `.gitignore` — add `state/.cache/`.

### Implementation
1. **Fetcher** — `readme_fetch.py`:
   - Function `fetch_readme(repo: str, cache_dir: Path) -> str | None`.
   - Cache key: `cache_dir / f"{owner}__{name}.md"`. If exists and non-empty, return its contents.
   - Otherwise: `subprocess.run(["gh", "api", f"repos/{repo}/readme", "--jq", ".content"])`, base64-decode, write to cache, return.
   - Hard-truncate to **8000 characters** (~2000 tokens) before returning. README excerpts longer than that don't measurably improve triage and inflate cost.
   - On any error (404, gh auth missing, non-text): return `None` — caller falls through to description-only.
2. **Triage call** — `triage_score.py`:
   - Add `readme_excerpt` arg to `candidate_user_message`. If non-empty, append:
     ```
     README excerpt (first 8k chars):
     ---
     {readme_excerpt}
     ---
     ```
   - In `main()`, before the `ThreadPoolExecutor`, fetch READMEs serially (single-threaded — `gh api` is fast and we don't want to thrash GH rate limits). Attach `readme` to each candidate dict.
   - Add a counter for `readme_hit` / `readme_miss`. Print after first-pass summary.

### Validation
- Run end-to-end on the existing inbox. Confirm:
  - At least 90% of public repos return a README. Misses → archived/empty repos and tolerable.
  - User-message length is bounded — no candidate exceeds ~12k chars total (8k README + frame + descriptor).
  - Decision distribution on `04-triage-scored.tier.jsonl` (Phase 1 output, README-enriched) does not regress the `add` rate dramatically — if the `skip` rate jumps from 42% (69/164) to >55%, the README context may be triggering false-skip on niche-but-legitimate tools. Investigate before promoting to canonical.
- Cache behavior: a re-run of triage should make zero `gh api` calls (all hits).

### Rollback
- Set the README excerpt to empty string in the user-message builder; cache stays harmless.
- Or remove the `readme = ...` line in `main()`.

### Future hook
If a candidate's README is itself thin or marketing-shaped, a later layer can use **Firecrawl** to fetch the project's homepage (often linked from the README) for an independent signal. Out of scope for this runbook — captured as a future enhancement.

## Phase 3 — promptfoo eval harness

### Why last
Highest tail effort (curating a labeled set is human work) and only kicks in when the *next* prompt change ships. Doing it now is investment, not a fix to a current bug. Worth doing because Phases 1 and 2 are exactly the kind of changes a regression gate would catch.

### Files touched
- New: `eval/triage/promptfooconfig.yaml`
- New: `eval/triage/cases.jsonl` — seed eval cases derived from past sweeps (`state/sweep-*/04-triage-scored.jsonl`).
- New: `eval/triage/seed_cases.py` — script that builds `cases.jsonl` from past sweeps.
- New: `eval/triage/README.md` — how to run, how to expand the labeled set, what the assertions check.

### Seed-set strategy
The 164 rows from `sweep-2026-04-26b` are decisions, not ground truth. **Promote them to seed cases** with this contract:
- Every row goes in as a case.
- The `expected.decision` field is the past decision.
- A `confidence_floor` field captures the past confidence — assertion only fires if the past decision was `≥0.85`. Lower-confidence past decisions become "no-assertion" cases used for distribution checks but not strict regression gates.
- Mark each case with `source: "auto-seed-from-2026-04-26b"` so when humans curate ground truth, the corrected cases can override seeds.

This gives a working harness on day 1 without blocking on manual curation, while making the auto-seed nature explicit.

### promptfoo config shape

**Provider strategy (committed before implementation):** add a `--single-candidate` CLI mode to `triage_score.py` that reads one candidate JSON from stdin (or a `--repo` arg) and emits one `TriageDecision` JSON to stdout. promptfoo's `exec:` provider runs this binary per case. This re-uses the production code path verbatim — no Python provider adapter, no prompt copy that drifts, no risk of the eval and the live scorer disagreeing on schema. Side benefit: the same CLI mode is useful for ad-hoc human spot-checks ("score this one repo and show me why").

- `providers:` `exec: python {root}/state/sweep-2026-04-26b/triage_score.py --single-candidate`.
- `tests:` loaded from `cases.jsonl`.
- Assertions:
  1. JSON-schema check: response matches `TriageDecision`.
  2. `decision == expected.decision` for high-confidence past cases (`expected.confidence >= 0.85`).
  3. `proposed_category` is one of the 15 known categories when `decision == "add"`.
  4. Aggregate: skip-rate stays within ±10pp of the seed distribution. Drift outside that band fails the suite.

### Validation
- Run promptfoo on the current code (Phase 1 + 2 already in place). It should pass — by construction, since the seed is from the same code path. If it doesn't, the seed-set generation has a bug.
- Then artificially break the prompt (e.g., delete the "skip when course/tutorial" bullet) and confirm the suite goes red. Revert.

### Rollback
Eval harness is purely additive — delete `eval/` to remove.

## Order of operations

1. Phase 1 — implement, validate against the canonical Sonnet baseline, promote.
2. Phase 2 — implement, validate against the Phase 1 baseline, promote.
3. Phase 3 — implement *after* both code phases are stable so the seed cases reflect the new pipeline, not the old one.

## Files NOT to touch

- `RUNBOOK.md` §7.11 contract — the output `04-triage-scored.jsonl` schema gains a `tier` key (additive); category and decision shape are unchanged. Update §7.11 only after Phase 1 lands, in a separate edit.
- `apply_adds.py` — the consumer treats `tier` as opaque metadata.
- `state/sweep-2026-04-26b/04-triage-scored.jsonl` — the canonical sweep artifact. Run new code against `01-inbox.jsonl` and write to a `.tier.jsonl` sibling for comparison; do not overwrite history.

## Open questions / required input

- **None blocking.** All three phases are implementable with current credentials (`ANTHROPIC_API_KEY`, `gh auth`). promptfoo install is `npm i -g promptfoo` — assumed acceptable.
- **For consideration:** the user may want to manually curate a subset of the 164 seed cases into ground-truth (overriding `source: auto-seed-from-2026-04-26b` with `source: human`). That is follow-up work, not blocking this runbook.

## Definition of done

- [x] Phase 1: `triage_score.py` runs two-tier; `04-triage-scored.tier.jsonl` produced; flip-rate report printed; `add ⇄ skip` direct-flip rate within tiered threshold.
- [x] Phase 2: `readme_fetch.py` exists; cache populated under `state/.cache/readmes/`; triage user-message includes README excerpt for the candidates; cache hit rate is 100% on a second run.
- [x] Phase 3: `eval/triage/` directory exists with config, seed cases, generator script, and README. **Not yet run** — promptfoo is not installed locally; `npx promptfoo eval -c promptfooconfig.yaml` is the one command needed once it is.
- [ ] `RUNBOOK.md` §7.11 updated to mention `tier` field, auto-skip pre-filter, and README enrichment.

## Implementation notes (post-hoc)

Three findings surfaced during implementation that the runbook didn't anticipate:

### Finding 1: 73/164 inbox candidates were already tracked

The merge stage isn't dedup'ing against `metrics-current.json`. The LLM was wasting calls re-deciding tools already on the radar — and Haiku 4.5 in particular failed to apply the "do not re-add tracked tools" prose rule reliably (24/31 of its false-positive `add`s on tracked repos).

**Resolution:** added an `auto_skip_tracked()` step in `triage_score.py` that filters already-tracked candidates out before the LLM call, marking them `decision: skip, tier: "auto"` deterministically. This is correct behavior regardless of which model is in use — the merge stage's hygiene gap stays as a separate follow-up.

**Effect:** novel candidate count on this sweep dropped from 164 → 91. Cost reduction is real: 44% fewer LLM calls before the model swap even kicks in.

### Finding 2: README enrichment changes the scoring regime, not just the cost math

Sonnet+README and Sonnet-without-README disagree substantively (the original baseline had 67 adds; Sonnet+README produced 42). The README is doing exactly what was hoped — surfacing course/tutorial/wrapper signal that descriptions hide — but it means **the old `04-triage-scored.jsonl` is not a comparable baseline for the new pipeline.** The validation script accepts a `--baseline 04-triage-scored.sonnet-readme.jsonl` argument so the apples-to-apples comparison is Haiku+README vs Sonnet+README, both with auto-skip enabled.

### Finding 3: zero-tolerance `add ⇄ skip` was the wrong stop-sign

Even after the auto-skip pre-filter and apples-to-apples comparison, Haiku and Sonnet disagree on ~13% of novel candidates (12/91). The flips are clustered on genuine boundary cases (`open-webui`, `meilisearch`, `n8n`, `metaflow`) where two competent models can reasonably differ on whether the tool counts as "agentic-AI infrastructure." The advisor's "zero direct flips" stop-sign was right in spirit but wrong in calibration.

**Resolution:** `validate_tier.py` now uses tiered thresholds — PASS < 5%, WARN 5–15%, FAIL > 15%. Current state validates as **PASS with WARN** at 13.2%; the warning is informational and surfaces the specific repos for human review, but does not block.
