# Runbook: Source Sweep Pipeline

A durable, resumable pipeline for re-scanning sources and updating the radar. Modeled as a DAG of idempotent stages with persistent state on disk. You (or a future Claude session) can stop after any stage, come back later, and continue.

This file is the spec. Per-sweep work happens in `state/sweep-<YYYY-MM-DD>/`. Human-readable output lives in `landscape.md` and `categories/<category>.md`.

---

## 1. Repo layout (canonical)

```
ai-radar/
├── README.md                    # what the radar is, how to use it
├── CLAUDE.md                    # operating instructions for AI assistants
├── RUNBOOK.md                   # this file — pipeline spec
├── TEMPLATE.md                  # category-page skeleton
├── landscape.md                 # GENERATED — single index table; one row per tool
├── radar.md                     # headline picks + changes log (curated)
├── sources.md                   # external sources to scan (curated)
├── categories/
│   ├── agent-frameworks.md      # human-curated learnings on every tool in this category
│   ├── model-hosting.md
│   └── ... one file per category ...
├── state/
│   ├── ledger.jsonl             # append-only sweep events
│   ├── metrics-history.jsonl    # append-only per-repo metric snapshots
│   ├── metrics-current.json     # GENERATED — latest metric snapshot, all tracked tools
│   ├── landscape-meta.json      # deploy_status + notes per tool (human-curated)
│   ├── sources-cursor.json      # last-scanned timestamp per source
│   └── sweep-<DATE>/            # per-sweep workspace
└── viz/
    ├── treemap.html             # static d3 v7 page (no build step; CDN-loaded)
    ├── data.json                # GENERATED — feeds the treemap (root → category → tool)
    ├── data-<DATE>.json         # GENERATED — per-sweep archive
    └── README.md                # setup, controls, keyboard, data shape
```

There is **no** `tools/` directory and no per-tool markdown file. All learnings about a tool live inside its category page; metrics for every tool live in `state/metrics-current.json` and are surfaced in `landscape.md` and `viz/data.json`.

## 2. Three layers of truth

| Layer | What | Source of truth | Edited by |
|---|---|---|---|
| **Curated prose** | Why a tool exists, when to reach for it, when not, how it fits | `categories/<cat>.md` | Humans (and Claude) |
| **Deploy status** | Our stance on adoption: 🟢 prod / 🟡 beta / 🔴 deprecated | `state/landscape-meta.json` | Humans (and Claude, on request) |
| **Metrics** | Stars, forks, velocity, etc. | `state/metrics-current.json` and `state/metrics-history.jsonl` | Pipeline only — never hand-edited |

`landscape.md` is regenerated from all three; never hand-edit it.

## 3. Deploy status semantics

The `status` we already track on the repo (active/maintenance/dormant/archived) describes the **upstream project's** lifecycle. `deploy_status` is **our adoption stance** — independent.

| Light | Value | Meaning |
|---|---|---|
| 🟢 | `prod` | Recommended. Stable in our use, suitable for new projects without further investigation. |
| 🟡 | `beta` | Piloting / evaluating. Promising but uncertain — try in non-critical paths. |
| 🔴 | `deprecated` | We've moved off, or actively recommend against — note the reason in `landscape-meta.json`. |

A tool can be `status: active` (upstream healthy) and `deploy_status: deprecated` (we don't use it) — that's normal and useful information.

A tool with no `deploy_status` set is treated as **untriaged**; it appears in `landscape.md` with a `—` and gets called out in the manifest for human review.

## 4. Why a stateful pipeline

A scan touches dozens of sources, hundreds of repos, and produces many small file edits. Running it as one shot is fragile: rate limits, network blips, mid-session compaction, or a wrong call all force redoing work. So we treat each scan as a **sweep run** with on-disk state, broken into stages that:

- read from the previous stage's output and `state/ledger.jsonl`,
- write their own output file,
- write a `.done` marker on completion,
- can be re-run safely (idempotent) — re-running overwrites the stage's output, never edits earlier stages' outputs.

Resuming a sweep = "find the highest stage with a `.done` marker, start from the next one."

## 5. Persistent state layout

```
state/
├── ledger.jsonl                      # append-only history across all sweeps
├── metrics-history.jsonl             # append-only per-repo metric snapshots
├── metrics-current.json              # latest snapshot, keyed by repo (regenerated each sweep)
├── landscape-meta.json               # human-curated deploy_status + notes per tool
├── sources-cursor.json               # last-scanned timestamp per source
└── sweep-<YYYY-MM-DD>/               # one directory per sweep
    ├── manifest.md                   # human-readable plan + status
    ├── cursor-before.json            # snapshot of sources-cursor.json at init
    ├── 01-inbox.jsonl                # raw candidates from collect-* stages
    ├── 02-merged.jsonl               # deduped, normalized (first_seen added here)
    ├── 03-enriched.jsonl             # full gh repo metrics for inbox candidates (§7.9)
    ├── 03b-velocity.jsonl            # deltas for inbox candidates vs. last snapshot (§7.10)
    ├── 03c-refresh-enriched.jsonl    # full gh repo metrics for tracked tools (§7.13)
    ├── 03d-refresh-velocity.jsonl    # deltas for tracked tools (§7.13)
    ├── 04-triage.jsonl               # decisions: add/update/skip/defer
    ├── 05-actions.jsonl              # actions staged against categories/* and metrics-current.json
    ├── 06-stale.jsonl                # stale-check results across all tracked tools
    ├── 07-radar-diff.md              # proposed radar.md changes
    └── *.done                        # one marker per completed stage
```

### Record schemas (JSONL)

`01-inbox.jsonl` — raw rows appended by each `collect:*` stage (no `first_seen`):
```json
{"repo": "org/name", "category_guess": "agent-frameworks", "sources": ["github-trending-py"]}
```

`02-merged.jsonl` — deduped output of §7.8 (`first_seen` is set here, not earlier):
```json
{"repo": "org/name", "category_guess": "agent-frameworks", "sources": ["github-trending-py", "awesome-ai-agents"], "first_seen": "2026-04-26"}
```

`03-enriched.jsonl` — full GitHub metrics, one row per repo, captured fresh every sweep:
```json
{
  "repo": "org/name",
  "stars": 12345, "forks": 678, "watchers": 234, "open_issues": 89, "contributors": 142,
  "created_at": "2023-06-01", "pushed_at": "2026-04-20",
  "license": "Apache-2.0", "language": "Python",
  "latest_release": "v0.4.1", "latest_release_date": "2026-04-15",
  "first_release": "v0.0.1", "first_release_date": "2023-07-12",
  "release_cadence_days": 21,
  "archived": false, "disabled": false, "default_branch": "main", "size_kb": 45230,
  "category_guess": "agent-frameworks",
  "snapshot_ts": "2026-04-26T10:11:12Z"
}
```

`03b-velocity.jsonl` — deltas vs. the prior snapshot in `metrics-history.jsonl`:
```json
{"repo": "org/name", "stars_30d": 412, "stars_90d": 1180, "forks_30d": 23, "commits_30d": 87, "prior_snapshot_ts": "...", "current_snapshot_ts": "..."}
```

`state/metrics-history.jsonl` — append-only, one row per repo per sweep:
```json
{"ts": "2026-04-26T10:11:12Z", "sweep": "2026-04-26", "repo": "org/name", "stars": 12345, "forks": 678, "watchers": 234, "open_issues": 89, "contributors": 142, "pushed_at": "2026-04-20"}
```

`state/metrics-current.json` — single object, full latest snapshot for every tracked repo, regenerated at finalize:
```json
{
  "generated_at": "2026-04-26T...",
  "tools": {
    "langchain-ai/langgraph": {
      "name": "LangGraph",
      "category": "agent-frameworks",
      "stars": 12345, "forks": 678, "watchers": 234, "open_issues": 89, "contributors": 142,
      "stars_30d": 412, "stars_90d": 1180, "commits_30d": 87,
      "pushed_at": "2026-04-20", "language": "Python", "license": "MIT",
      "status": "active",
      "latest_release": "v0.4.1", "latest_release_date": "2026-04-15"
    }
  }
}
```

`05-actions.jsonl` — append-only within a sweep; written by §7.12 (category-page edits) and §7.15 (status flips). Consumed by §7.18 (`radar-diff`) and §7.19 (`finalize` applies `mark-*` actions to `metrics-current.json`):
```json
{"repo": "org/name", "category": "agent-frameworks", "action": "added-block|flagged-for-prose-revision|frontmatter-only|mark-dormant|mark-archived|mark-moved", "ts": "2026-04-26T...", "evidence": "optional explanatory string", "new_repo": "owner/name (only for mark-moved)"}
```

`06-stale.jsonl` — produced by §7.14:
```json
{"repo": "org/name", "classification": "dormant|archived|moved|gone", "evidence": "pushed_at=2025-09-01", "new_repo": "neworg/name"}
```

`state/landscape-meta.json` — human-curated overlay for the landscape table:
```json
{
  "langchain-ai/langgraph": {
    "deploy_status": "prod",
    "notes": "default for stateful agent flows",
    "last_reviewed": "2026-04-26"
  },
  "microsoft/autogen": {
    "deploy_status": "beta",
    "notes": "v0.4 split — re-evaluate after 0.5",
    "last_reviewed": "2026-04-12"
  }
}
```

## 6. The DAG

```
                     ┌─ collect:github-trending ─┐
                     ├─ collect:topics ──────────┤
init-sweep ─────────►├─ collect:awesome-lists ───┤──► merge ──► enrich ──► velocity ──► triage ──► apply:category-page ─┐
                     ├─ collect:blogs-rss ───────┤                                                                        ├──► apply:landscape ──► viz:treemap ──► radar-diff ──► finalize
                     ├─ collect:social-leads ────┤                                                                        │
                     └─ collect:leaderboards ────┘                                                                        │
                                                                                                                          │
       metrics-refresh (all tracked repos, independent of inbox) ──────► stale-check ──► apply:dormant ───────────────────┘
```

Explicit per-stage dependencies (a stage is runnable iff every dependency below has its `.done` marker):

- `init-sweep` — no deps.
- `collect:github-trending`, `collect:topics`, `collect:awesome-lists`, `collect:blogs-rss`, `collect:social-leads`, `collect:leaderboards` — each depends only on `init-sweep.done`. Run in any order, in parallel if convenient.
- `merge` — depends on all six `collect:*.done` markers.
- `enrich` — depends on `merge.done`. Pulls full GitHub metrics for inbox candidates → `03-enriched.jsonl`.
- `velocity` — depends on `enrich.done`. Computes inbox-side deltas against `metrics-history.jsonl` → `03b-velocity.jsonl`.
- `triage` — depends on `velocity.done`.
- `apply:category-page` — depends on `triage.done`.
- `metrics-refresh` — depends only on `init-sweep.done` (parallel branch). Refreshes every already-tracked repo → `03c-refresh-enriched.jsonl`, `03d-refresh-velocity.jsonl`.
- `stale-check` — depends on `metrics-refresh.done`. Reads its output; no extra API calls.
- `apply:dormant` — depends on `stale-check.done`.
- `apply:landscape` — **DAG join**. Depends on `apply-category-page.done` AND `apply-dormant.done` AND `metrics-refresh.done`. Regenerates `landscape.md` from `metrics-current.json` + `landscape-meta.json` + the inventory in `categories/`, merged with this sweep's enriched/velocity union.
- `viz:treemap` — depends on `apply-landscape.done` (same data shape).
- `radar-diff` — depends on `viz-treemap.done`.
- `finalize` — depends on `radar-diff.done`.

## 7. Stages — contract per node

Each stage has the same shape:

- **Inputs**: explicit file paths it reads.
- **Outputs**: one file (or set of file edits) it writes, plus a `.done` marker.
- **Idempotency**: re-running re-derives the output from inputs.
- **Failure mode**: leaves no `.done` marker; safe to re-run.
- **Resume rule**: if `<stage>.done` exists, skip; otherwise run.

### 7.1 `init-sweep`
- **Inputs**: `state/sources-cursor.json`, `TEMPLATE.md` (none required from prior stages).
- **Outputs**: `state/sweep-<DATE>/manifest.md` from §10 template; `state/sweep-<DATE>/cursor-before.json` (snapshot of `sources-cursor.json`); `init-sweep.done`.
- **Action**: create the sweep dir if missing; snapshot `sources-cursor.json` as `cursor-before.json`.
- **Idempotency**: if `state/sweep-<DATE>/` already exists (same-day re-run), do not overwrite existing files or `.done` markers — resume into it. Re-running this stage when `init-sweep.done` exists is a no-op. If `manifest.md` is missing it is recreated; if present it is left untouched (humans may have annotated it).
- **Resume rule**: if `init-sweep.done` exists, skip; otherwise run.

### 7.2–7.7 `collect:*` stages — common contract

All `collect:*` stages share this shape; only **Action** and the per-row `sources[]` value differ.

- **Inputs**: `sources.md`, `state/sources-cursor.json`, `init-sweep.done`.
- **Outputs**: append-only writes of inbox rows to `state/sweep-<DATE>/01-inbox.jsonl`. Each row matches the `02-merged.jsonl` schema (§5) **without** the `first_seen` field (which is added at `merge`). Each `collect:*` stage also writes its own `.done` marker (e.g., `collect-github-trending.done`).
- **Concurrency note**: because all collectors append to the same `01-inbox.jsonl`, append writes must be line-atomic (one JSON object per `write(2)` call, terminated with `\n`). The `merge` stage dedupes; no ordering guarantee is required.
- **Idempotency**: re-running a `collect:*` stage clears its previously-appended rows from `01-inbox.jsonl` (identified by `sources[]` containing this stage's tag) and re-appends fresh ones. Cursor updates (§7.5) are committed only on success.
- **Resume rule**: if `<stage>.done` exists, skip; otherwise run.
- **Failure mode**: on network/parse failure, leave no `.done`; partial rows already appended are tolerable — the re-run will rewrite this stage's rows.

### 7.2 `collect:github-trending`
- **Action**: for each language (python, typescript, rust, go), fetch trending; filter against the category checklist (§11). Rows tagged `sources: ["github-trending-<lang>"]`.

### 7.3 `collect:topics`
- **Command**: `gh api -X GET search/repositories -f q='topic:ai-agents stars:>1000 pushed:>YYYY-MM-DD' -f sort=stars -f per_page=30`. Topics: `llm`, `ai-agents`, `rag`, `vector-database`, `mcp`, `llmops`. Rows tagged `sources: ["topic-<topic>"]`.

### 7.4 `collect:awesome-lists`
- **Action**: fetch each list's raw README; extract repo links via `github\.com/([\w.-]+/[\w.-]+)`. Rows tagged `sources: ["awesome-<list-slug>"]`.

### 7.5 `collect:blogs-rss`
- **Action**: walk vendor + independent blog feeds since `sources-cursor.json[<feed>].last_seen`. On stage success, update cursor entries to the most recent entry seen per feed. On RSS unreachable / parse error for an individual feed: log to manifest "Rate-limit/source incidents", skip that feed, continue with others; the stage still succeeds if at least one feed was reachable. Rows tagged `sources: ["blog-<feed-slug>"]`.

### 7.6 `collect:social-leads`
- **Action**: best-effort. Anything not corroborated by a non-social source stays a `lead`, not a candidate. Rows tagged `sources: ["social-<handle-or-feed>"]`. Rows whose only source is social are filtered out at `triage` (§7.11 rule 6 / "≥2 distinct sources").

### 7.7 `collect:leaderboards`
- **Action**: extract project names credited on benchmark boards. Rows tagged `sources: ["leaderboard-<board-slug>"]`.

### 7.8 `merge`
- **Inputs**: `state/sweep-<DATE>/01-inbox.jsonl`, all `collect-*.done` markers, the tool inventory derived from `categories/*.md` frontmatter `tools:` lists.
- **Outputs**: `state/sweep-<DATE>/02-merged.jsonl`; `merge.done`.
- **Action**: dedupe by `repo` (lowercased). Merge `sources` arrays. Set `first_seen` to today's `<DATE>` for repos not in the inventory; for repos already in the inventory, copy `first_seen` from the earliest matching `metrics-history.jsonl` row (or set to `<DATE>` if no history exists). Cross-check against the tool inventory derived from `categories/*.md` frontmatter (each category page lists its tools — see §9). `category_guess` is the page that already lists the repo, else a best-effort match against §11.
- **Idempotency**: rewrites `02-merged.jsonl` from inputs each run.
- **Resume rule**: if `merge.done` exists, skip.

### 7.9 `enrich`
- **Inputs**: `state/sweep-<DATE>/02-merged.jsonl`, `merge.done`.
- **Outputs**: `state/sweep-<DATE>/03-enriched.jsonl` (one row per repo, schema in §5); `enrich.done`.
- **Action**: for each repo in `02-merged.jsonl`, capture the full metric set:
  ```
  gh repo view <repo> --json \
    nameWithOwner,stargazerCount,forkCount,watchers,issues,licenseInfo,primaryLanguage,\
isArchived,isDisabled,defaultBranchRef,createdAt,pushedAt,diskUsage,latestRelease,description
  gh api repos/<repo>/contributors?per_page=1 -i      # Link rel="last" → contributor count
  gh api repos/<repo>/releases?per_page=5             # for cadence median
  ```
  Each repo's row is committed independently; rate-limit aborts are resumable.
- **Idempotency**: re-running re-fetches; rows are keyed by `repo` and last write wins. On partial failure, repos already written are skipped on resume (key by `repo` against existing `03-enriched.jsonl` rows). The `.done` marker is written only when every repo in `02-merged.jsonl` has a corresponding row.
- **Failure modes**: GitHub rate limit (HTTP 403/429) → abort with no `.done`; resume picks up missing repos. Repo renamed (HTTP 301 with `Location`) → follow redirect once, write the row under the **new** `nameWithOwner`, and emit a `repo-renamed` event into the manifest noting the old → new mapping (so a human can update sentinels at follow-up). Repo gone (HTTP 404) → write a stub row with `archived: true, disabled: true, snapshot_ts` set; downstream `triage` will `skip`. `gh` CLI not authenticated → abort entire stage with a clear error in the manifest "Rate-limit/source incidents" section.
- **Resume rule**: if `enrich.done` exists, skip.

### 7.10 `velocity`
- **Inputs**: `03-enriched.jsonl`, `state/metrics-history.jsonl`, `enrich.done`.
- **Outputs**: `state/sweep-<DATE>/03b-velocity.jsonl` (schema in §5); `velocity.done`. (Note: `metrics-refresh` produces its own velocity file `03d-refresh-velocity.jsonl` — see §7.13.)
- **Action**: per-repo deltas of stars/forks/commits over 30/90 days vs. the most recent prior row for that repo in `state/metrics-history.jsonl`. Linearly scale if the prior snapshot is not exactly 30 / 90 days old. `null` when no prior snapshot exists.
- **Idempotency**: pure function of inputs; rewrites `03b-velocity.jsonl`.
- **Resume rule**: if `velocity.done` exists, skip.

### 7.11 `triage`
- **Inputs**: `03-enriched.jsonl`, `03b-velocity.jsonl`, the inventory from `categories/*.md`.
- **Outputs**: `04-triage.jsonl` — one row per repo with shape `{"repo": "...", "decision": "add|update|skip|skip-no-op|defer|skip-archived", "reason": "<rule-id>", "category": "..."}`; `triage.done`.
- **Drift baseline (rule 2)**: "drift" is computed against the **most recent prior row for this repo in `state/metrics-history.jsonl`** (i.e., the snapshot from the previous sweep; not the running sweep's just-appended row, which doesn't exist yet at this point in the DAG). If no prior row exists, the repo is `New` for triage purposes regardless of category-page presence.
- **Drift triggers (rule 2, any one is sufficient, all testable)**:
  - `abs(stars_now - stars_prior) / max(stars_prior, 1) >= 0.05` (i.e., ±5% stars vs. the prior `metrics-history.jsonl` row).
  - `pushed_at_now != pushed_at_prior` (new push since prior snapshot).
  - `latest_release_now != latest_release_prior` (new release tag).
  - `license_now != license_prior` (license change).
  - `archived_now != archived_prior` OR `disabled_now != disabled_prior` (lifecycle flip).
- **Decision rules** (evaluated in order; first match wins):
  1. `archived` or `disabled` → `skip-archived`.
  2. Already tracked (repo present in `categories/*.md` frontmatter inventory) AND any drift trigger above fires → `update`.
  3. Already tracked AND no drift trigger fires → `skip-no-op`.
  4. New AND `stars >= 1000` AND `pushed_at` within 60 days AND ≥2 distinct `sources` → `add`.
  5. New AND `stars < 1000` BUT `stars_30d >= 200` AND ≥2 sources → `add` ("promoted on velocity"). If `stars_30d` is `null` (no prior snapshot), this rule does not match — fall through.
  6. New AND borderline (500–1000 stars OR single source) → `defer`; surface in manifest. **Intentionally manual**: deferred rows require human judgment next sweep.
  7. New AND off-topic vs. category checklist (§11) → `skip`.
- **Idempotency**: pure function of inputs; rewrites `04-triage.jsonl`.
- **Resume rule**: if `triage.done` exists, skip.
- **LLM-scored sub-stage** (`triage_score.py` → `04-triage-scored.jsonl`, marker `triage-scored.done`): a complementary Instructor-backed scorer that classifies inbox rows into `add` / `defer` / `skip` with `proposed_category`, `proposed_deploy_status`, `redundancy_with`, and `reason`. Each output row carries a `tier` annotation: `auto` (deterministic skip for already-tracked repos — no LLM call), `haiku` (Haiku 4.5 first pass), or `haiku→sonnet` (rescored on Sonnet 4.5 for `defer` or low-confidence first-pass results). The user message includes a README excerpt fetched via `gh api repos/{repo}/readme` and cached under `state/.cache/readmes/`. See `runbooks/2026-04-26-triage-upgrade.md` for the upgrade plan and validation thresholds.

### 7.11b `apply:summary` (sub-stage of triage application)
- **What it does**: for every tool that ends up in `state/landscape-meta.json` (both newly-added and refresh-touched), write a one-line "thesis" string into the `notes` field. This is what shows in the rightmost cell of `landscape.md` and at the bottom of the treemap tooltip — so it must be useful, not redundant with stars/forks shown elsewhere.
- **Implementation**: `state/lib/summarize.py`. Instructor-backed (`claude-sonnet-4-5` by default) with a Pydantic `Summary` schema constraining output to ≤90 chars, banning star/fork counts, banned words (popular, comprehensive, robust, leading, etc.), and the repo's own name as a leading prefix. System prompt is cached. Voice target: terse opinionated thesis lines like "default for stateful agent flows" or "vectors in Postgres — when transactional consistency matters".
- **When called**:
  - Inline by `apply:category-page` (§7.12) for every new `add` decision — the result becomes the new `notes` value.
  - As a periodic full refresh via a scratch script (e.g. `state/sweep-<DATE>/refresh_summaries.py`) that re-summarizes every tracked tool. Backup the existing `landscape-meta.json` before overwriting (`landscape-meta.before-summary-refresh.json`).
- **Idempotency**: pure function of (repo, name, category, upstream description, prior notes). Re-running produces stable, near-identical output for the same inputs because the system prompt is fixed and the model is the same.
- **Failure mode**: any per-tool exception is caught and the pipeline falls back to a truncated triage reason (`short_note(...)`) so a single failed call never blocks the apply pass.

### 7.12 `apply:category-page`
- **Inputs**: `04-triage.jsonl` rows where `decision="add"` or `"update"`; current `categories/<category>.md` files; `triage.done`.
- **Outputs**: edits to `categories/<category>.md` (new tool blocks appended; frontmatter `tools:` regenerated to mirror headings); rows appended to `state/sweep-<DATE>/05-actions.jsonl` describing each edit (`{"repo": "...", "category": "...", "action": "added-block|flagged-for-prose-revision|frontmatter-only", "ts": "..."}`); `apply-category-page.done`.
- **`add` decisions**: append a new tool block (TEMPLATE.md skeleton, "When not to" mandatory) inside the `## Tools` section of the matching `categories/<category>.md`, wrapped in BEGIN/END sentinels (§9 spec). Block insertion is alphabetical by name within the section. Frontmatter `tools:` list is regenerated.
- **`update` decisions**: no-op at the prose layer (metrics aren't stored in prose). The action row is logged with `action: "flagged-for-prose-revision"` only when the drift trigger was a new release, an archived/disabled flip, or a license change — these warrant a human prose pass and are surfaced in the manifest. Pure star/push drift produces no action row. **Intentionally manual**: prose revisions are never auto-written; the pipeline only flags.
- **Per-tool block shape** (see `TEMPLATE.md`): `### {{Name}}` heading, then `What it is`, `When to reach for it`, `When not to`, `How it fits with other tools`, `Notable recent developments`, `Sources`. **No metric numbers in prose.**
- **Frontmatter scope**: this stage rewrites only the `tools:` array and updates `last_reviewed:` to today's `<DATE>`. All other frontmatter keys (`category`, plus any human-added keys) are preserved verbatim. Nothing outside the YAML frontmatter and BEGIN/END tool blocks is read or modified — the curated overview prose, decision heuristics, and any other category-level sections are untouched.
- **Idempotency**: identify existing tool blocks by the BEGIN/END sentinel pair (§9) keyed on `<repo>`. Re-running an `add` for a repo that already has a sentinel pair is a no-op (no second block, no duplicate frontmatter entry). Frontmatter regeneration is deterministic from headings.
- **Failure modes**: malformed sentinel state in a category page (see §9 parsing rules) → abort the stage, leave no `.done`, surface offending file + line in the manifest. Edits to a given category file are atomic (parse → in-memory transform → write).
- **Resume rule**: if `apply-category-page.done` exists, skip.

### 7.13 `metrics-refresh`
- **Inputs**: tool inventory from `categories/*.md` frontmatter `tools:` lists (or equivalently the keys of `state/metrics-current.json` if present from a prior sweep — the two MUST agree by the §9 contract; on disagreement, the category-page inventory wins and the discrepancy is logged to the manifest).
- **Outputs**: `state/sweep-<DATE>/03c-refresh-enriched.jsonl` (one row per tracked repo, schema identical to `03-enriched.jsonl` per §5) and `state/sweep-<DATE>/03d-refresh-velocity.jsonl` (schema identical to `03b-velocity.jsonl`); `metrics-refresh.done`. **Note**: this stage writes its own files, distinct from the inbox-branch outputs in §7.9 / §7.10. `apply:landscape` (§7.16) and `finalize` (§7.19) consume the **union** of `{03-enriched.jsonl ∪ 03c-refresh-enriched.jsonl}` and `{03b-velocity.jsonl ∪ 03d-refresh-velocity.jsonl}`, deduped by `repo` with the `metrics-refresh` row winning on conflict (it is the authoritative refresh for already-tracked tools; `enrich`'s row for the same repo is the inbox-discovery snapshot).
- **Action**: same `gh` queries as `enrich` (§7.9). Guarantees every tracked tool's numbers refresh every sweep, independent of whether the inbox surfaced it.
- **Idempotency**: re-running re-fetches; rows keyed by `repo`; last write wins. The `.done` marker is written only when every tracked repo has a row.
- **Failure modes**: same as §7.9 (rate limits resumable, repo rename → follow once and emit `repo-renamed` event, 404 → stub row that flows into `stale-check`, gh CLI unauth → abort).
- **Resume rule**: if `metrics-refresh.done` exists, skip.

### 7.14 `stale-check`
- **Inputs**: `03c-refresh-enriched.jsonl` (refreshed metrics for every tracked repo); `metrics-refresh.done`.
- **Outputs**: `state/sweep-<DATE>/06-stale.jsonl` — one row per repo whose status changed or is non-active: `{"repo": "...", "classification": "dormant|archived|moved", "evidence": "<field>=<value>", "new_repo": "<owner/name>"?}`; `stale-check.done`.
- **Classification** (evaluated in order):
  1. HTTP 404 (or stub-row from §7.13 indicating gone) → `moved` (with `new_repo` set if a redirect was captured) or `gone` (no redirect).
  2. `archived == true` → `archived`.
  3. `pushed_at` older than 180 days from `snapshot_ts` → `dormant`.
  4. Otherwise → no row emitted.
- **Idempotency**: pure function of inputs; rewrites `06-stale.jsonl`.
- **Resume rule**: if `stale-check.done` exists, skip.

### 7.15 `apply:dormant`
- **Inputs**: `06-stale.jsonl`; `stale-check.done`.
- **Outputs**: rows appended to `state/sweep-<DATE>/05-actions.jsonl` with `action: "mark-dormant" | "mark-archived" | "mark-moved"` per repo. The status field is **staged** for `finalize` (§7.19) to write into `metrics-current.json`; this stage does NOT mutate `metrics-current.json` directly (that file is only rewritten at finalize). Category page prose may need a "now dormant / archived / moved" bullet under "Notable recent developments" — flagged in manifest for human edit. **Intentionally manual**: prose updates for status flips are never auto-written.
- **Idempotency**: pure function of `06-stale.jsonl`; existing `mark-*` rows for the same repo in `05-actions.jsonl` are overwritten on re-run (dedupe by `(repo, action-prefix="mark-")`).
- **Resume rule**: if `apply-dormant.done` exists, skip.

### 7.16 `apply:landscape`
- **Inputs**: `state/metrics-current.json` (the **prior sweep's** snapshot — the current sweep's snapshot is not yet written; see §7.19) merged in-memory with the union of `03-enriched.jsonl ∪ 03c-refresh-enriched.jsonl` and `03b-velocity.jsonl ∪ 03d-refresh-velocity.jsonl` (current-sweep authoritative); `state/landscape-meta.json`; `categories/*.md` (for tool inventory + ordering); `apply-category-page.done`, `apply-dormant.done`, `metrics-refresh.done` (DAG join — see §6 / §13).
- **Outputs**: rewrites `landscape.md` end-to-end; `apply-landscape.done`.
- **Format**: see §8.
- **Idempotency**: pure function of inputs.
- **Resume rule**: if `apply-landscape.done` exists, skip.

### 7.17 `viz:treemap`
- **Inputs**: `state/metrics-current.json`, `state/landscape-meta.json`, `categories/*.md` (for category membership + ordering).
- **Outputs**:
  - `viz/data.json` — current snapshot consumed by `viz/treemap.html`.
  - `viz/data-<YYYY-MM-DD>.json` — per-sweep archive, identical schema, never overwritten.
- **Page generation**: none. `viz/treemap.html` is a static, hand-maintained file (pure d3 v7 + Tachyons via CDN, no build step). This stage only writes `data.json`; the page picks it up on next reload.
- **Hierarchy**: `root → category → tool`. Root carries `name`, `generated_at` (ISO timestamp, matches the sweep date), and `children`. Each category carries `name` and `children`. Each leaf carries the full metric block plus `deploy_status`:
  - identity: `name`, `repo` (owner/repo)
  - status axes: `deploy_status` (`prod` | `beta` | `deprecated` | `null`), `status` (`active` | `maintenance` | `dormant` | `archived`) — independent per §3
  - metrics: `stars`, `forks`, `watchers`, `open_issues`, `contributors`, `stars_30d`, `stars_90d`, `pushed_at`
  - meta: `language`, `license`, `notes` (notes copied verbatim from `landscape-meta.json`)
- **Default color encoding** in the page is `deploy_status` (🟢 / 🟡 / 🔴 / —, matching §3); `status` is exposed as a secondary "upstream status" mode and shown alongside `deploy_status` in the tooltip.
- **Idempotency**: pure function of inputs. Re-running for the same date overwrites both `data.json` and `data-<DATE>.json`.
- **Viewing**: `python3 -m http.server -d viz 8080` then `http://localhost:8080/treemap.html`. Opening the file via `file://` is intentionally unsupported (the page fetches `data.json`, which browsers block from `file://`).
- **Publish path → oturu**: the public face of this treemap lives at https://oturu.online/agentic-ai-landscape, served from the oturu repo (`~/code/oturu/`). The trigger phrase **"deploy to oturu"** (also "update the treemap on oturu") means: re-run `viz:treemap` here so `viz/data.json` is fresh, then follow `~/code/oturu/runbooks/runbook-agentic-ai-landscape.md` — it copies the JSON into oturu (rewriting the root `name` to `"agentic-ai-radar"` for brand consistency) and runs `python -m app.cli deploy` to ship to the prod droplet. The oturu page (`app/templates/agentic_ai_landscape.html`) is hand-maintained on the oturu side; only `viz/data.json` flows from this repo.

### 7.18 `radar-diff`
- **Inputs**: `05-actions.jsonl`, `06-stale.jsonl`, the union of `03b-velocity.jsonl` and `03d-refresh-velocity.jsonl`, current `radar.md`; `viz-treemap.done`.
- **Outputs**: `state/sweep-<DATE>/07-radar-diff.md` — proposed patch (new headline picks if any, changes-log lines, top-5 movers by `stars_30d`); `radar-diff.done`.
- **Action**: do not edit `radar.md` yet — that happens at `finalize`.
- **Idempotency**: pure function of inputs; rewrites `07-radar-diff.md`.
- **Resume rule**: if `radar-diff.done` exists, skip.

### 7.19 `finalize`
- **Inputs**: `07-radar-diff.md`; the union of `03-enriched.jsonl ∪ 03c-refresh-enriched.jsonl` and `03b-velocity.jsonl ∪ 03d-refresh-velocity.jsonl` (deduped by `repo`, refresh-row wins); `05-actions.jsonl`; `state/sources-cursor.json` (current); `radar-diff.done`.
- **Outputs**:
  - applied changes to `radar.md` (per `07-radar-diff.md`),
  - rows appended to `state/metrics-history.jsonl` — one per repo in the deduped enriched union, tagged with `sweep: <DATE>`,
  - `state/metrics-current.json` rewritten end-to-end from the deduped enriched union plus the `mark-*` actions in `05-actions.jsonl` (which set the per-repo `status` field to `dormant` / `archived` / `moved`),
  - events appended to `state/ledger.jsonl` (one event per non-skip action plus a sweep-summary event),
  - `state/sources-cursor.json` updated to reflect cursors advanced by the `collect:*` stages,
  - final `manifest.md` summary section filled in,
  - git commit: `sweep: <DATE> — +N tools, ~M updates, K dormant`; `finalize.done`.
- **Idempotency / append-only contract**: `state/metrics-history.jsonl` is append-only forever (§14), but re-running `finalize` for the same `<DATE>` MUST NOT double-write. Before appending, the stage filters out any rows in `metrics-history.jsonl` whose `sweep == <DATE>` (read the file once, compute the desired union of "everything not from this sweep" plus "fresh rows from this sweep", rewrite atomically). This preserves append-only semantics across sweeps while making same-sweep re-runs idempotent. `metrics-current.json`, `radar.md`, `sources-cursor.json`, and the `manifest.md` summary are full overwrites — naturally idempotent. `state/ledger.jsonl` events for this sweep are deduped on `(sweep, action, repo)` before appending.
- **Failure modes**: pre-commit hook failure → leave no `.done`; the next re-run picks up where it stopped (state files are already in their target form; the commit is the only remaining step). Working tree dirty with unrelated changes → abort with a clear error in the manifest; do NOT auto-stash.
- **Resume rule**: if `finalize.done` exists, the sweep is complete — do not re-run. To force a re-run (e.g., to re-do the commit), delete `finalize.done` AND verify the dedupe filter above will produce the intended result.

## 8. `landscape.md` format (generated)

`landscape.md` is regenerated by `apply:landscape`. It has two sections: an intro line (timestamp + counts) and the table.

```markdown
# Landscape

_Generated 2026-04-26 from N tools across K categories. Do not hand-edit — see `RUNBOOK.md` §8._

| Tool | Category | Status | Repo | Stars | Forks | Δ30d | Last push | Notes |
|---|---|:---:|---|---:|---:|---:|---|---|
| LangGraph | agent-frameworks | 🟢 | langchain-ai/langgraph | 9,000 | 1,300 | +412 | 2026-04-20 | default for stateful agent flows |
| AutoGen | agent-frameworks | 🟡 | microsoft/autogen | 35,000 | 5,500 | +120 | 2026-04-21 | v0.4 split — re-evaluate |
| OldThing | model-routing | 🔴 | foo/old | 3,200 | 200 | -10 | 2025-09-01 | superseded by LiteLLM |
| Untriaged | memory | — | bar/new | 2,400 | 100 | +180 | 2026-04-25 | seen this sweep — needs review |
```

Rules:
- Sort by category (alphabetical), then by stars desc within category.
- `Status` cell is one of 🟢 / 🟡 / 🔴 / — (untriaged).
- Numbers use thousands separators; deltas show sign.
- `Notes` from `landscape-meta.json`; truncate to ~80 chars.
- Footer line lists untriaged tools so the human triages them next sweep.

## 9. `categories/<category>.md` format

A category page mixes a curated overview with one section per tool. The pipeline edits only the per-tool prose blocks (and only for `add` decisions); humans own everything else.

```markdown
---
category: agent-frameworks
tools:                          # GENERATED — list of tools whose blocks live below; matches headings
  - { name: "LangGraph", repo: "langchain-ai/langgraph" }
  - { name: "CrewAI",    repo: "crewAIInc/crewAI" }
last_reviewed: 2026-04-26
---

# Agent Frameworks

## Overview
Curated framing of the category. Sub-shapes, decision tree, when to reach for tools in this group vs. others.

## Decision heuristics
- ...

## Tools

<!-- BEGIN TOOL: langchain-ai/langgraph -->
### LangGraph
<!-- repo: langchain-ai/langgraph -->

#### What it is
…

#### When to reach for it
…

#### When not to
…

#### How it fits with other tools
…

#### Notable recent developments
- 2026-04-15 — release v0.4.1; added X.

#### Sources
- Docs: …
- Repo: https://github.com/langchain-ai/langgraph
<!-- END TOOL: langchain-ai/langgraph -->

<!-- BEGIN TOOL: crewAIInc/crewAI -->
### CrewAI
…
<!-- END TOOL: crewAIInc/crewAI -->
```

Rules:
- Frontmatter `tools:` list and `last_reviewed:` are regenerated by `apply:category-page` to match the actual `### {{Name}}` headings present. All other frontmatter keys (`category` and any human-added keys) are preserved verbatim.
- Each tool block is wrapped in `<!-- BEGIN TOOL: <repo> -->` / `<!-- END TOOL: <repo> -->` sentinels. The pipeline only edits content between matching sentinels — never touches the surrounding overview prose.
- No metric numbers inside category pages. Numbers belong to `landscape.md`, `metrics-current.json`, `metrics-history.jsonl`.
- "When not to" is mandatory for every tool block.

### Sentinel parsing spec (load-bearing)

The pipeline (§7.12, §7.13's inventory read, §7.16) reads category pages with this exact contract — two implementers should produce compatible code from it:

- **Regex** (anchored to the start of a line, case-sensitive, allowing trailing whitespace before the newline):
  - Begin: `^<!-- BEGIN TOOL: (?P<repo>[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+) -->\s*$`
  - End:   `^<!-- END TOOL: (?P<repo>[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+) -->\s*$`
- **Whitespace tolerance**: leading whitespace before `<!--` is **not** allowed (sentinels must start at column 0). Trailing whitespace before the newline is allowed. The single space after `BEGIN TOOL:` / `END TOOL:` and around the repo and `-->` is required.
- **Pairing rule**: a `BEGIN TOOL: X` must be followed by a matching `END TOOL: X` (same `<repo>`) before any other `BEGIN TOOL: …` or `END TOOL: …`. Nesting is forbidden. Sentinels are matched in document order via a single linear pass.
- **Inner anchor**: the `<!-- repo: <repo> -->` line directly under the heading is **informational only** — the pipeline does NOT verify it. (Humans use it to grep; sentinels are the authoritative key.) `apply:category-page` includes it when generating new blocks.
- **Malformed states (any of the following)**: a `BEGIN` with no matching `END`; an `END` with no preceding `BEGIN`; a `BEGIN` whose repo does not match its closing `END`; a nested `BEGIN` inside an open block; two `BEGIN` blocks with the same `<repo>` in the same file. On any of these, the consuming stage **aborts** with no `.done` marker, logs the offending file + line range to `manifest.md` "Rate-limit/source incidents", and the run waits for human repair. No partial writes.
- **Frontmatter delimiters**: standard `^---$` lines at the very top of the file open and close the YAML block. Anything between is YAML; everything after is markdown body.

## 10. Manifest template

`state/sweep-<DATE>/manifest.md`:

```
# Sweep <DATE>

## Stages
- [ ] init-sweep
- [ ] collect:github-trending
- [ ] collect:topics
- [ ] collect:awesome-lists
- [ ] collect:blogs-rss
- [ ] collect:social-leads
- [ ] collect:leaderboards
- [ ] merge
- [ ] enrich
- [ ] velocity
- [ ] triage
- [ ] apply:category-page
- [ ] metrics-refresh
- [ ] stale-check
- [ ] apply:dormant
- [ ] apply:landscape
- [ ] viz:treemap
- [ ] radar-diff
- [ ] finalize

## Notes
- Rate-limit incidents:
- Borderline (defer) candidates needing human call:
- New categories proposed:
- Untriaged (no deploy_status set):
- Tools the prose still needs human revision for (status flips, scope shifts):

## Outcome
- Tools added:
- Tools updated (prose):
- Tools dormant/archived:
- Radar headline changes:
```

## 11. Category coverage checklist

When triaging, check coverage against this list. If a popular tool is missing from `categories/<cat>.md`, that's a triage hint to `add`.

- **agent-frameworks**: LangGraph, CrewAI, AutoGen, Pydantic AI, smolagents, LlamaIndex Agents, Agno, Mastra, Vercel AI SDK, DSPy, Atomic Agents.
- **model-hosting**: vLLM, Ollama, llama.cpp, SGLang, TGI, LMDeploy, Aphrodite, MLC-LLM, LM Studio.
- **model-routing**: LiteLLM, OpenRouter, Portkey, RouteLLM, Helicone (proxy mode), Cloudflare AI Gateway.
- **rag-and-retrieval**: LlamaIndex, Haystack, RAGFlow, Verba, Cognita, R2R, Korvus, txtai, Vectara.
- **vector-stores**: Qdrant, Weaviate, Chroma, Milvus, pgvector, LanceDB, Vespa, Marqo, Turbopuffer, Redis, Elasticsearch.
- **evaluation**: Ragas, DeepEval, promptfoo, OpenAI Evals, Inspect (UK AISI), Giskard, TruLens, MLflow LLM Evaluate, lm-evaluation-harness.
- **observability**: Langfuse, Phoenix, Helicone, Logfire, OpenLLMetry, Lunary, LangSmith.
- **tool-use-and-mcp**: MCP spec, FastMCP, official SDKs, mcp-agent, awesome-mcp-servers, Smithery.
- **browser-and-computer-use**: Browser-Use, Stagehand, Playwright-MCP, Steel.dev, Skyvern, LaVague, Anthropic Computer Use, OpenInterpreter.
- **code-agents**: Aider, OpenHands, Cline, Continue, Roo Code, Goose, SWE-agent, opencode/crush.
- **security**: Garak, PyRIT, promptfoo redteam, LLM Guard, Rebuff, NeMo Guardrails, Guardrails AI, Vigil.
- **orchestration-and-runtime**: Temporal, Inngest, Restate, Dapr Agents, Hatchet, Trigger.dev, DBOS, Prefect, Windmill.
- **memory**: Mem0, Letta, Zep, Cognee, MemoryScope, Graphiti.
- **voice-and-multimodal**: Pipecat, LiveKit Agents, Vocode, Ultravox, Vapi, TEN Framework.
- **data-and-extraction**: Firecrawl, Crawl4AI, Docling, Unstructured, Markitdown, ScrapeGraphAI, Reader (Jina), Trafilatura, MegaParse.

## 12. GitHub metrics — what we capture and how

Every tool's metric block in `state/metrics-current.json` is refreshed every sweep.

### Canonical fields

| Field | Source | Why we track it |
|---|---|---|
| `stars` | `stargazerCount` | Headline popularity. |
| `forks` | `forkCount` | Adoption / derivation. |
| `watchers` | `subscribers_count` | Engaged-users signal. |
| `open_issues` | `open_issues_count` | Health proxy. |
| `contributors` | `Link` rel="last" on `contributors?per_page=1` | Bus-factor proxy. |
| `created_at` | `createdAt` | Project age. |
| `pushed_at` | `pushedAt` | Liveness — primary input to dormant classification. |
| `language` | `primaryLanguage.name` | Stack fit. |
| `license` | `licenseInfo.spdxId` | Recommendation gating. |
| `archived` / `disabled` | flags | Hard kill switches. |
| `latest_release`, `latest_release_date` | `latestRelease` | Recency of shipping. |
| `release_cadence_days` | median delta over last 5 releases | Shipping rhythm. |

### Velocity (computed at `velocity` stage)
- `stars_30d`, `stars_90d`, `forks_30d` — deltas vs. prior `metrics-history.jsonl` snapshot, linearly scaled if the prior snapshot ≠ exactly the window edge.
- `commits_30d` — `gh api repos/<r>/commits?since=<30d-ago>&per_page=1` → parse `Link rel="last"`.
- `null` until two snapshots exist.

### Refresh guarantee
`enrich` covers inbox candidates; `metrics-refresh` covers **every** tracked tool. Every tracked repo gets a fresh row in `metrics-history.jsonl` every sweep, so velocity stays computable.

### Cost
~3 API calls per repo × ~50 tools = ~150 calls/sweep — well under the 5000/hr authenticated limit.

## 13. Operating the pipeline

### Start a sweep
```
DATE=$(date +%F)
mkdir -p state/sweep-$DATE
# walk stages in §6 order
```

### Resume a sweep
1. `ls state/sweep-<DATE>/*.done`
2. Find any stage whose declared dependencies (§6) are all `.done` AND whose own `<stage>.done` marker does not yet exist. Such a stage is **runnable**. With two parallel branches there may be more than one runnable stage at a time — pick any (or run them concurrently within the §13 "Concurrency" rules).
3. Run it. Write its `.done` marker on success.
4. Repeat until `finalize.done` exists.

### Re-run a stage
Delete its `.done` marker and its output file; re-run. If the output changed, cascade-clear `.done` markers for every transitive downstream stage per the §6 dependency list (e.g., re-running `metrics-refresh` clears `stale-check.done`, `apply-dormant.done`, `apply-landscape.done`, `viz-treemap.done`, `radar-diff.done`, `finalize.done`).

### Abort
Leave the `state/sweep-<DATE>/` directory in place — it's a record. New sweep starts a new dir.

### Concurrency
`collect:*` are parallelizable with each other (they all append to `01-inbox.jsonl` — see §7.2–7.7). The two main branches (`merge → enrich → velocity → triage → apply:category-page` and `metrics-refresh → stale-check → apply:dormant`) are parallelizable with each other. Within each branch, stages are serial. `apply:landscape`, `viz:treemap`, `radar-diff`, `finalize` run serially after the join.

## 14. Conventions (don't drift)

- One markdown file per category. No per-tool markdown files. No `tools/` directory.
- "When not to" is mandatory in every tool block.
- Don't hand-edit `landscape.md` — regenerated each sweep. Edit `landscape-meta.json` for deploy status / notes.
- Don't hand-edit metric numbers anywhere. They flow from `enrich` / `metrics-refresh` → `metrics-current.json` → `landscape.md` and `viz/data.json`.
- Don't add a category to host one tool. Promote a sub-shape inside an existing category instead.
- Hosted-only products → at most a stub block, clearly marked. Radar is GitHub-anchored.
- A single tweet is not signal. Two independent sources OR one curated list + repo verification.
- Edit `radar.md` headline picks only on `radar-diff`-approved changes — not on taste.
- `state/metrics-history.jsonl` is append-only across sweeps. Within a single sweep, `finalize` (§7.19) MUST dedupe before append: drop any rows where `sweep == <DATE>` first, then append the fresh per-repo rows. This makes same-sweep `finalize` re-runs idempotent without compromising the cross-sweep append-only history.
- `<!-- BEGIN TOOL: <repo> -->` / `<!-- END TOOL: <repo> -->` sentinels in category pages are load-bearing. Don't remove or rename.
