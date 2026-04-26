# Sweep 2026-04-26

## Stages
- [x] init-sweep
- [-] collect:github-trending — SKIPPED (no `gh` CLI; HTML scraping out-of-scope this pass)
- [-] collect:topics — SKIPPED (search API budget reserved for metrics-refresh)
- [-] collect:awesome-lists — DEFERRED (next sweep, fetch from raw.githubusercontent.com)
- [-] collect:blogs-rss — DEFERRED
- [-] collect:social-leads — DEFERRED
- [-] collect:leaderboards — DEFERRED
- [x] merge — n/a (empty inbox)
- [x] enrich — n/a (empty inbox; metrics-refresh covered all tracked repos)
- [x] velocity — n/a (no prior history; baseline established this sweep)
- [x] triage — n/a (empty inbox)
- [x] apply:category-page — n/a (no add/update)
- [x] metrics-refresh — 43 repos refreshed via REST `/repos/{owner}/{repo}`
- [x] stale-check — 1 archived flagged (Azure/PyRIT)
- [x] apply:dormant — landscape note updated; deploy_status preserved
- [x] apply:landscape — `landscape.md` regenerated
- [x] viz:treemap — `viz/data.json` regenerated; archive `viz/data-2026-04-26.json` written
- [x] radar-diff — no headline-pick changes; movers section deferred (no velocity yet)
- [x] finalize — `metrics-history.jsonl` appended (43 rows); `metrics-current.json` rewritten

## Constraints this run
- Unauthenticated GitHub REST: 60 req/hr ceiling; 43 calls used + ~5 follow-ups for renames.
- `gh` CLI not installed; used `urllib`.
- Per-repo extras (contributors / release cadence / commits_30d) skipped to fit budget — fields preserved as `null` or carried over from prior values.

## Findings

### Renames (4)
| Old repo | New repo |
|---|---|
| `explodinggradients/ragas` | `vibrantlabsai/ragas` |
| `jlowin/fastmcp` | `PrefectHQ/fastmcp` |
| `All-Hands-AI/OpenHands` | `OpenHands/OpenHands` |
| `mendableai/firecrawl` | `firecrawl/firecrawl` |

Propagated to: category-page sentinels (4 files), `landscape-meta.json` keys, `metrics-current.json` keys.

### Archived upstream
- **Azure/PyRIT** — `archived: true`, 18 stars, 1 fork. The repo at this name is no longer canonical; PyRIT proper has presumably moved (perhaps `Azure/airt-pyrit` or similar). Deploy status preserved as `beta`; note rewritten to "upstream archived; investigate successor (red-team toolkit)" — needs human follow-up next sweep to repoint the canonical entry.

### Numbers worth flagging
- Several tools much bigger than the seed estimates: Ollama 170k stars, Firecrawl 112k, llama.cpp 106k, Browser-Use 90k.
- LiteLLM license shows `NOASSERTION` from the API — split licensing. Investigate whether the OSS surface is still permissive enough for `prod` recommendation.
- `Azure/PyRIT` is the only entry with `archived: true`. No dormant tools (oldest active push is `vibrantlabsai/ragas` at 2026-02-24, ~61 days; well under the 180-day dormant threshold).

### Velocity
- No prior `metrics-history.jsonl` rows existed before this sweep. All velocity fields (`stars_30d`, `stars_90d`, `commits_30d`) are `null` for this run. Next sweep will produce a 30-day delta against this baseline.

## Notes for next sweep
- Acquire a GitHub token to lift the 60/hr ceiling. Then enable `collect:topics`, `collect:awesome-lists`, and per-repo `contributors` / `releases` queries.
- Investigate Azure/PyRIT successor and update `landscape-meta.json` + the category page sentinel.
- Compute velocity once a second snapshot exists.
