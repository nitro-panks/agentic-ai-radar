# Runbook — Radar follow-ups (2026-04-26)

Companion to `2026-04-26-triage-upgrade.md`. That runbook shipped the triage upgrade (auto-skip, Haiku→Sonnet, README enrichment, promptfoo eval). This one captures the rest of the work surfaced in the project review — content debt, plumbing, hygiene, and operational cadence — in priority order.

## Goal

Close the gap between "radar that works" and "radar that's useful." The pipeline is operational; the content and operating posture aren't yet. Each phase is independent and can be done in isolation; the order reflects ROI, not dependency.

## Non-goals

- No new categories, tools, or pipeline stages.
- No model swap revisited — that work is done.
- No introduction of Firecrawl / LiteLLM / Langfuse. Those stay future hooks.

## Phase 1 — Fill the `TODO — needs human review` stubs

**Why first.** The radar's value is the curated prose: "What it is / When to reach for it / When not to." Today, 67 tool blocks across 13 category pages have empty prose for recently auto-triaged tools (cognee, memvid, claude-mem, deer-flow, etc.). A reader bouncing off empty sections is the worst failure mode for a curated knowledge base.

**Distribution (2026-04-26 audit, by stub *line* count — each tool block has 2 stub lines, "When to reach for it" + "When not to"):**

| Category | TODO lines | Tools |
|---|---:|---:|
| agent-frameworks | 28 | 14 |
| tool-use-and-mcp | 28 | 14 |
| observability | 18 | 9 |
| browser-and-computer-use | 12 | 6 |
| rag-and-retrieval | 10 | 5 |
| vector-stores | 10 | 5 |
| memory | 6 | 3 |
| model-routing | 6 | 3 |
| code-agents | 6 | 3 |
| orchestration-and-runtime | 4 | 2 |
| data-and-extraction | 2 | 1 |
| security | 2 | 1 |
| model-hosting | 2 | 1 |
| **total** | **134** | **67** |

**Pre-flight (verified 2026-04-26):**
- All 67 stubbed tools have a cached README under `state/.cache/readmes/` — no fetches needed before starting.
- All tool blocks contain the `#### When not to` header — the prose underneath is TODO, but the structure is intact. (Cross-verified with `grep -L "When not to"` across `categories/*.md`.)

**Source material per tool (already captured, not yet curated):**
- The triage `reason` field in `state/sweep-2026-04-26b/04-triage-scored.*.jsonl` — the LLM's rationale, usually 1–2 sentences that name what makes the tool distinctive.
- The README excerpt in `state/.cache/readmes/<owner>__<name>.md` — already fetched, ~8k chars per tool, gives architecture / install / canonical use case.
- `metrics-current.json` — stars/forks/language/license/upstream status.
- Existing tool blocks in the same category — match the established voice ("default for X", "when typing matters", etc.).

**Workflow per tool:**

1. Open the category page. Find the next stub block (`grep -n "TODO — needs human review" categories/<cat>.md`).
2. Read the cached README for that repo and the LLM's `reason`.
3. Write **two sentences max** for "When to reach for it" — name a concrete use case or sub-shape this tool occupies that no already-tracked tool covers.
4. Write **two sentences max** for "When not to" — at least one negative. Either "use [already-tracked alternative] when X" or "this tool's tradeoff is Y; if Y matters to you, skip."
5. Delete the "Triage notes" auto-stub if the prose now stands on its own. Keep the section if there's a real concern the future-you should remember (e.g., "vendor-specific plugin, re-evaluate after MCP standard lands").

**Editorial constraints (enforced repo-wide via `CLAUDE.md`):**
- **No numbers in prose.** Never paraphrase the LLM's "63K-star ByteDance project" verbatim. Stars/forks live in `metrics-current.json`; the prose names mechanisms, not popularity.
- **"When not to" is mandatory.** Already true structurally — the section header is present in every stub. The prose under it cannot stay empty.
- **License field uses SPDX when known**; flag split-licensing.

**Cadence and chunking.** Don't try to do 134 in one sitting. Realistic chunk: **one category per session**. Order:

1. **`memory` (3 tools) or `model-routing` (3 tools)** — start here to find the per-tool rhythm. ~30 minutes gives you a real effort estimate before committing to the 14-tool sessions.
2. `code-agents` (3), `orchestration-and-runtime` (2), `data-and-extraction` (1), `security` (1), `model-hosting` (1) — short-tail categories, one per session.
3. `browser-and-computer-use` (6), `rag-and-retrieval` (5), `vector-stores` (5) — mid-size, established categories with clear winners; stubs likely fast.
4. `observability` (9) — competitive landscape, "when X over Y" is the entire value; needs more thought.
5. `agent-frameworks` (14) and `tool-use-and-mcp` (14) — the heavy categories; do these last, when the rhythm is locked in.

**Validation.** After each session: `grep -rc "TODO — needs human review" categories/` should show the touched category at 0. The category-page tool count in the frontmatter `tools:` list should still match the `<!-- BEGIN TOOL: ... -->` sentinel count. No prose change should remove a sentinel — those are load-bearing for the pipeline.

**Rollback.** Per-tool — revert the specific block.

## Phase 2 — Close the two open eval boundary cases

**Why.** `promptfoo eval` currently reports 36/38 (94.7%). The two failures are `open-webui/open-webui` and `meilisearch/meilisearch` — the same boundary cases that warned in `validate_tier.py`. Five minutes of human judgment turns this into a clean 38/38 regression gate.

**Steps:**

1. For each of the two repos, decide: does it count as agentic-AI infrastructure on this radar? Concretely:
   - `open-webui` — chat UI for self-hosted models. Reader looking for an "agent framework" probably doesn't find their need here. Lean **skip**.
   - `meilisearch` — general-purpose search engine with vector + hybrid retrieval. Reader looking for vector-store options would want to know. Lean **add**, category `vector-stores`.
   - These are calls; both go either way. Make the call.
2. Edit `eval/triage/cases.jsonl`. For each row, set `metadata.source = "human"` and `vars.expected_decision = "<your call>"`. The eval will now strict-gate them regardless of confidence band.
3. Re-run: `cd eval/triage && promptfoo eval`. Verify 38/38.

**Validation.** `cases.jsonl` rebuild via `python eval/triage/curate_cases.py` preserves human cases (the script merges them in). After regen, `metadata.source` should still be `"human"` on those rows.

**Rollback.** Revert the two cases to auto-curated state by deleting them and re-running `curate_cases.py`.

## Phase 3 — Promote `triage_score.py` & friends out of the per-sweep dir

**Why.** `state/sweep-2026-04-26b/{triage_score, readme_fetch, validate_tier, viz_treemap}.py` are sweep-shared infrastructure, not sweep-specific outputs. Per-sweep dirs are for *artifacts* (.done markers, .jsonl drops). Code lives elsewhere. The next sweep would otherwise have to copy these files; that's the kind of drift that ages badly.

**Files touched:**
- New: `pipeline/` directory at repo root.
- Move: `state/sweep-2026-04-26b/triage_score.py` → `pipeline/triage_score.py`.
- Move: `state/sweep-2026-04-26b/readme_fetch.py` → `pipeline/readme_fetch.py`.
- Move: `state/sweep-2026-04-26b/validate_tier.py` → `pipeline/validate_tier.py`.
- Move: `state/sweep-2026-04-26b/viz_treemap.py` → `pipeline/viz_treemap.py`.
- Update: `eval/triage/run_one.sh` — change relative path to `pipeline/triage_score.py`.
- Update: `RUNBOOK.md` §7.11 — change script reference path.
- Update: `runbooks/2026-04-26-triage-upgrade.md` — replace `state/sweep-2026-04-26b/triage_score.py` references with `pipeline/triage_score.py`.

**Implementation:**
1. `mkdir pipeline && git mv state/sweep-2026-04-26b/{triage_score,readme_fetch,validate_tier,viz_treemap}.py pipeline/` (or plain `mv` if not yet committed).
2. Update the `SWEEP = STATE / "sweep-2026-04-26b"` path inside `triage_score.py` to take the sweep dir as an arg or env var, defaulting to "the latest `state/sweep-*` dir present." Same for `validate_tier.py` defaults.
3. Smoke-test: `python pipeline/triage_score.py --single-candidate --repo foo/bar --description x` should still emit a TriageDecision.
4. Re-run promptfoo: `cd eval/triage && promptfoo eval` — must still pass post-move.

**Validation.** All four scripts run from their new location. promptfoo eval still passes (or fails only on the same two known boundary cases). README cache at `state/.cache/readmes/` is unaffected.

**Rollback.** `git mv` reverse.

## Phase 4 — Fix merge-stage tracked-tool dedup at the root

**Why.** Phase 2 of the triage upgrade added `auto_skip_tracked()` as a defensive triage-layer filter. Root cause is upstream: the `merge` stage doesn't dedup against `metrics-current.json` before writing `02-merged.jsonl`, so 73/164 (45%) of this sweep's "candidates" were already-tracked tools. Fixing it at merge means the auto-skip filter becomes a no-op (still defensive, never fires) and inbox sizes drop ~half.

**Pre-flight (DO THIS FIRST):** Locate the merge-stage script. The runbook can't tell you where it lives because nobody has — `apply_adds.py` is the apply-stage script; merge is upstream and may be inline in a notebook, a shell pipeline, or yet-to-be-written. Run `grep -rn "02-merged\|merge.done" state/sweep-2026-04-26b/ runbooks/ RUNBOOK.md` and read what you find before planning the implementation.

**Files touched (predicted, confirm during pre-flight):**
- The merge-stage script.
- `RUNBOOK.md` §7.8 — note the dedup behavior.

**Implementation:** Read `state/metrics-current.json` once at merge entry; filter out any candidate whose `repo` is already a key in `metrics["tools"]` *before* writing `02-merged.jsonl`. Log the filter count to the manifest.

**Validation:** On the next sweep, `01-inbox.jsonl ∩ tracked_repos == ∅`. Auto-skip count printed by `triage_score.py` should be 0.

**Rollback.** Remove the filter; the triage-layer auto-skip catches anything that slips through.

## Phase 5 — Establish a sweep cadence

**Why.** Manual sweeps drift. Last one ran 2026-04-26b; before that 2026-04-26 (same day). Without a cadence, the radar gets stale, and "fresh" goes from a feature to a memory.

**Options, in order of pragmatism:**

1. **Scheduled remote agent** via the `schedule` skill — a routine that runs the sweep DAG every 2 weeks (configurable) and surfaces a summary. Catches everything `oturu cycle` would; the operator just reviews and merges the `add` decisions.
2. **Manual reminder** — calendar entry, no automation. Works if you're disciplined; doesn't if you aren't.
3. **GitHub Action** — `cron: '0 12 1,15 * *'` on a self-hosted runner with `ANTHROPIC_API_KEY` and `gh auth` set up. Heavier ops to configure but fully autonomous.

**Tradeoffs:** Scheduled runs cost real money — the prior sweep was 164 candidates × Sonnet+README ≈ a few dollars. Two sweeps a month is fine; daily would be wasteful and noisy.

**Recommendation:** Option 1. The schedule skill is already available; one command sets it up. Configure to surface unresolved `defer` rows for human review — the auto-decided `add`s and `skip`s flow through.

**Validation.** First scheduled run produces a sweep dir under `state/sweep-<DATE>/` with all expected `.done` markers. Manifest summarizes the sweep. Operator reviews the manifest, merges any add-side decisions, done.

**Rollback.** `schedule delete <id>`.

## Phase 6 — Wire promptfoo into CI on prompt/model changes

**Why.** The eval gate exists but only runs when invoked manually. A pre-commit hook or GH Action that runs `promptfoo eval` automatically when `pipeline/triage_score.py` (or its system prompt) changes would catch the regressions the gate is designed for — without relying on operator memory.

**Files touched:**
- New: `.github/workflows/triage-eval.yml` (if going GH Action route) **or** `.git/hooks/pre-push` (if local).
- Possibly: `package.json` to install promptfoo as a dev dependency (so CI doesn't depend on global install).

**Implementation (GH Action sketch):**
- Trigger on push or PR touching `pipeline/triage_score.py` or `eval/triage/**`.
- Step: install deps, install promptfoo (`npm i -g promptfoo`), run `promptfoo eval`.
- Fail the build on >1 failure (allow the 2 known boundary cases until Phase 2 lands; then tighten to 0).
- Secret: `ANTHROPIC_API_KEY` — repo-level secret, not committed.

**Validation.** Push a deliberate prompt-break commit (delete the "skip when course/tutorial" bullet) and confirm CI goes red. Revert.

**Tradeoff.** Each CI run costs the same as one full eval (~50s, ~$0.05 in API). Low enough to enable on every relevant change.

**Rollback.** Disable the workflow file (or `--ignore-failures` flag) if false-positives appear during prompt iteration.

## Phase 7 — Audit `radar.md`

**Why.** It's the documented "headline picks" file in the `radar-diff` → `finalize` flow (RUNBOOK §7.18 / 7.19), but I haven't looked at it in any of the recent sweeps and don't know if it reflects current state. Could be stale.

**Steps:**
1. Read `radar.md`. Compare claims against current `landscape.md` + `landscape-meta.json`.
2. Cross-check any "default for X" claims against deploy_status — if `radar.md` calls something the default and `landscape-meta.json` says `beta`, one of them is wrong.
3. If stale: hand-edit to reflect current state, OR delete and let the next `radar-diff` rebuild it from scratch.

**Validation.** No claim in `radar.md` contradicts `landscape-meta.json`'s notes. The "headline picks" still describe tools that exist on the radar.

**Rollback.** Trivial — git revert.

## Definition of done

- [ ] **Phase 1 (134 stubs):** `grep -rc "TODO — needs human review" categories/` returns 0 across all 15 categories. *Realistic over 4–6 work sessions, not one.*
- [ ] **Phase 2 (boundary cases):** `eval/triage/cases.jsonl` has `metadata.source: "human"` on `open-webui` and `meilisearch`; promptfoo eval reports 38/38 pass.
- [ ] **Phase 3 (script promotion):** `pipeline/{triage_score,readme_fetch,validate_tier,viz_treemap}.py` exist; per-sweep dir contains only artifacts; promptfoo eval still passes.
- [ ] **Phase 4 (merge dedup):** Next sweep's `01-inbox.jsonl` has zero overlap with `metrics-current.json` keys.
- [ ] **Phase 5 (cadence):** A scheduled routine exists and has produced at least one autonomous sweep dir.
- [ ] **Phase 6 (CI):** A workflow / hook exists that runs `promptfoo eval` on triage-related changes; an artificially broken prompt fails the gate.
- [ ] **Phase 7 (radar.md):** Claims in `radar.md` are consistent with `landscape-meta.json` as of the latest sweep.

## Lower-priority / future hooks

Captured here so they don't get lost; not in scope for this runbook.

- **Firecrawl as a second-tier README enricher** — for projects whose GitHub README is thin or marketing-shaped, fetch the project landing page (often linked from the README) for an independent signal. Hook documented in `runbooks/2026-04-26-triage-upgrade.md` Phase 2 "Future hook."
- **LiteLLM as a routing layer** — only if you want provider flexibility on the scorer (Anthropic + Bedrock + Anthropic-via-Vertex). Not justified by current usage.
- **Langfuse for sweep observability** — only if Phase 5 cadence ends up producing many sweeps and per-call cost/cache visibility becomes load-bearing. Skip for now; offline batch doesn't justify it.
