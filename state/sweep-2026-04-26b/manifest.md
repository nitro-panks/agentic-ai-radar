# Sweep 2026-04-26b (continuation — `gh` token + Instructor scoring)

## Instructor-backed triage (RUNBOOK §7.11)

**Run after the manual 6-add round below.** Implemented per user feedback (memory: "Use Instructor for triage scoring"). All 164 candidates from `01-inbox.jsonl` re-scored with `claude-sonnet-4-5` via the `instructor` library, structured output as a Pydantic `TriageDecision` (decision / confidence / proposed_category / proposed_deploy_status / redundancy_with / reason). 8 worker threads, prompt caching on the system prompt + tracked-tools list, ~38s wall time, 0 errors.

| Decision | Count |
|---|---:|
| add | 67 |
| defer | 28 |
| skip | 69 |

Outputs: `04-triage-scored.jsonl` (full structured decisions), `05-actions.jsonl` (apply log).

**Adds applied per category:**

| Category | New blocks |
|---|---:|
| agent-frameworks | 14 |
| tool-use-and-mcp | 14 |
| observability | 9 |
| browser-and-computer-use | 6 |
| rag-and-retrieval | 5 |
| vector-stores | 5 |
| memory | 3 |
| code-agents | 3 |
| model-routing | 3 |
| orchestration-and-runtime | 2 |
| data-and-extraction | 1 |
| model-hosting | 1 |
| security | 1 |

Each add was written as a sentinel-wrapped stub block on the right category page with:
- `What it is` — paraphrase of the upstream description.
- `When to reach for it` / `When not to` — `_TODO — needs human review (auto-triaged stub)._`
- `Triage notes` — model, confidence, and reason — provenance is explicit so a reader can see this is auto-generated.
- Real metrics (stars/forks/watchers/contributors) fetched via `gh api repos/{r}` and `repos/{r}/contributors?per_page=1`.

Defaulted `deploy_status: beta` for new adds unless the model proposed otherwise. Notes shortened to first sentence of the model's reason (≤80 chars) for the `landscape-meta.json` overlay.

**After this stage:**
- Tracked tools: **49 → 116**
- `landscape.md`: 116 rows, 0 untriaged
- `viz/data.json` + `viz/data-2026-04-26b.json` archive regenerated
- `metrics-history.jsonl`: 116 rows under `sweep: 2026-04-26b` (replaced the prior 49-row partial for this sweep id per the same-sweep dedupe rule in RUNBOOK §14)

**Notable adds:**
- Observability: `pydantic/logfire`, `comet-ml/opik`, `mlflow/mlflow`, `lmnr-ai/lmnr` (Laminar)
- Browser/computer-use: `Skyvern-AI/skyvern`, `lightpanda-io/browser`, `bytedance/UI-TARS-desktop`
- Memory: `topoteretes/cognee`, `memvid/memvid`
- Tool-use & MCP: `github/github-mcp-server`, `ChromeDevTools/chrome-devtools-mcp`, `ComposioHQ/composio`, `oraios/serena`, `IBM/mcp-context-forge`, `metatool-ai/metamcp`
- Agent frameworks: `bytedance/deer-flow`, `Mintplex-Labs/anything-llm`, `langroid/langroid`, `assafelovic/gpt-researcher`, `agentscope-ai/agentscope`
- RAG: `HKUDS/LightRAG`, `khoj-ai/khoj`
- Orchestration: `daytonaio/daytona` (sandbox infra — promote sub-shape next sweep)

**Defers (28)** — kept in `04-triage-scored.jsonl`; common patterns: novel sub-shapes (git-native agent protocols, RL bridges), brand-new high-momentum repos, multi-faceted LLMOps platforms.

**Skips (69)** — common patterns from the model's reasons: educational/awesome-list repos, single-purpose MCP wrappers around commercial APIs, marketing-named star-farms, off-topic high-star projects.

---

## Stages
- [x] init-sweep
- [x] collect:topics — 12 topic queries via `gh api search/repositories`; 164 unique candidates after dedupe vs. tracked
- [-] collect:github-trending — DEFERRED (HTML scrape; not blocking)
- [-] collect:awesome-lists / blogs-rss / social-leads / leaderboards — DEFERRED
- [x] merge — n/a (single source per row this round)
- [x] enrich — full `repos/{r}` for the 6 adds
- [x] velocity — n/a (sweep `2026-04-26` baseline barely hours old; deltas would be noise)
- [x] triage — see Decisions below
- [x] apply:category-page — 6 tool blocks added with sentinels
- [x] metrics-refresh — augmentation of tracked tools: `contributors`, `latest_release`, `latest_release_date`, `release_cadence_days` filled for all 43
- [x] stale-check — no new dormant/archived flags beyond `Azure/PyRIT`
- [x] apply:dormant — n/a
- [x] apply:landscape — `landscape.md` regenerated (49 rows, 0 untriaged)
- [x] viz:treemap — `viz/data.json` + `viz/data-2026-04-26b.json` archive written
- [x] radar-diff — no headline-pick changes
- [x] finalize — `metrics-history.jsonl` appended (49 rows under `sweep: 2026-04-26b`)

## Token / budget
- Authed as `nitro-panks`; 5000/hr core, 30/min search.
- Used ~150 calls (43 contributor counts + 43 releases + ~12 searches + ~12 enrich for adds).

## Decisions

### Adds (6, all `deploy_status: beta`)
| Repo | Category | Stars | Forks | Contributors | Reason |
|---|---|---:|---:|---:|---|
| `langchain-ai/langchain` | agent-frameworks | 134,933 | 22,310 | 3,673 | canonical SDK; surprising omission from baseline |
| `langgenius/dify` | agent-frameworks | 139,173 | 21,822 | 1,277 | dominant agentic-platform with self-host UI |
| `agno-agi/agno` | agent-frameworks | 39,678 | 5,299 | 429 | on coverage checklist (formerly Phidata) |
| `FlowiseAI/Flowise` | agent-frameworks | 52,280 | 24,220 | 327 | distinctive sub-shape (visual builder) |
| `microsoft/graphrag` | rag-and-retrieval | 32,505 | 3,428 | 50 | distinctive sub-shape (graph RAG) |
| `google-gemini/gemini-cli` | code-agents | 102,413 | 13,328 | 635 | first-party vendor CLI |

### Defers (~158)
The remaining candidates from topic search were deferred. Top-10 worth a closer look next sweep:
- `bytedance/deer-flow` — ByteDance "long-horizon SuperAgent harness" (~64k★)
- `Mintplex-Labs/anything-llm` — full-stack RAG/UI (~59k★)
- `meilisearch/meilisearch` — search engine with vector support (~57k★, judgment call: borderline vector-stores)
- `khoj-ai/khoj` — self-hostable AI second brain (~34k★)
- `mindsdb/mindsdb` — query engine for AI agents (~39k★)
- `HKUDS/LightRAG` — academic graph-RAG descendant (~34k★)
- `ChromeDevTools/chrome-devtools-mcp` — browser MCP server (~37k★)
- `daytonaio/daytona` — sandbox infra for agents (~72k★, may belong in new "sandbox/runtime" sub-category)

### Skips (smell-test failures)
A few high-star repos in the search results had names + descriptions that read as star-farming or LLM-generated marketing (`affaan-m/everything-claude-code`, `thedotmack/claude-mem`, `NousResearch/hermes-agent`, `code-yeongyu/oh-my-openagent`, `JuliusBrussee/caveman`, `HKUDS/nanobot`, etc.). Skipped without entries; flagged for human pattern-checking only if they recur next sweep.

## Notable findings (from augmentation)
- **vLLM**: 2,566 contributors — by far the broadest contributor base in the radar.
- **llama.cpp**: 1,640 contributors, b8934 release tag (continuous build cadence).
- **LangChain**: 3,673 contributors — even larger than vLLM.
- **AutoGen**: latest release `python-v0.7.5` from 2025-09-30; 8-month gap suggests the v0.4 architectural rework slowed the cadence.
- **Aider**: latest release `v0.86.0` from 2025-08-09 — also long gap; check whether dev moved to nightly / source installs.
- **pgvector / Azure/PyRIT / protectai/llm-guard**: no GitHub releases at all (rolling tags only, or no release process).

## For next sweep
- **Use Instructor for triage scoring** (per user feedback 2026-04-26): rather than the current heuristic rules in §7.11, call an LLM via Instructor with a Pydantic schema (`add | defer | skip`, `confidence`, `reason`, `proposed_category`, `proposed_deploy_status`). Run it over the deferred ~158 candidates from this sweep first as a backfill.
- Investigate `Azure/PyRIT` successor (still pending from morning sweep).
- Re-evaluate the ~10 deferred candidates above with Instructor scoring; aim to convert the canonical ones to `add`.
- Compute first real velocity now that two snapshots exist (today's morning + afternoon).
