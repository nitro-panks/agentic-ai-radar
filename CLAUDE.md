# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A markdown-based knowledge base of agentic AI tooling. No code, no build, no tests. Three layers:

1. **Curated prose** in `categories/<category>.md` — learnings about each tool. One section per tool, wrapped in `<!-- BEGIN TOOL: <repo> --> / <!-- END TOOL: <repo> -->` sentinels.
2. **Deploy status** in `state/landscape-meta.json` — `prod` / `beta` / `deprecated` per tool, plus a short note. Human-curated.
3. **Metrics** in `state/metrics-current.json` and `state/metrics-history.jsonl` — populated only by the sweep pipeline (`RUNBOOK.md`). Never hand-edit.

`landscape.md` and `viz/data.json` are generated artifacts that combine all three layers.

## Layout invariants

- One markdown file per category in `categories/`. There is no `tools/` directory.
- Each tool block in a category page MUST be wrapped in the `<!-- BEGIN TOOL: <repo> --> / <!-- END TOOL: <repo> -->` sentinels — load-bearing for the pipeline.
- "When not to" is mandatory for every tool block.
- Frontmatter `tools:` list on a category page mirrors the `### {{Name}}` headings inside; the pipeline regenerates it.

## Common tasks

### Add a new tool
1. Confirm category fits.
2. Open `categories/<category>.md` and append a new tool block using `TEMPLATE.md`.
3. Wrap it in `<!-- BEGIN TOOL: <repo> --> / <!-- END TOOL: <repo> -->` sentinels.
4. Add an entry to `state/landscape-meta.json` with `deploy_status` and a one-line note. Use `prod` only after real adoption; use `beta` for piloting; leave the key absent for "untriaged."
5. Add an entry to `state/metrics-current.json` (numbers may be approximate until the next sweep refreshes them).
6. Don't manually rewrite `landscape.md` or `viz/data.json` — they regenerate from the above.

### Update a tool's prose
Edit between the matching sentinels. Don't put numbers in prose.

### Change a deploy status
Edit `state/landscape-meta.json` only. Bump `last_reviewed`.

### Run a sweep
Follow `RUNBOOK.md`. Each stage writes a `.done` marker so a session can stop and resume.

## Editorial conventions

- "When not to" is honest. If a tool only has upsides, you haven't thought about it hard enough.
- License field uses the SPDX identifier when known. Note when a project is split-licensed.
- Status values in metrics: `active` (commits in last ~60d), `maintenance`, `dormant` (>6mo quiet), `archived`. Reflect upstream reality, not adoption stance.
- Deploy status (in `landscape-meta.json`) is OUR adoption stance. Independent of upstream `status`.

## What NOT to do

- Don't recreate a `tools/` directory.
- Don't add tools without a public repo.
- Don't put star counts, fork counts, or any metric in prose.
- Don't hand-edit `landscape.md` or `viz/data.json`.
- Don't add a category to host a single tool; promote a sub-shape inside an existing category instead.
