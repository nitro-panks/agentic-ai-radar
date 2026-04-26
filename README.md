# ai-radar

A curated, markdown-based knowledge base of tools in the agentic AI landscape. One page per category contains the learnings; a single `landscape.md` table indexes every tool with a deploy status (🟢 prod / 🟡 beta / 🔴 deprecated) and current GitHub metrics.

## Use cases

- Picking the right tools when starting a new project.
- Evaluating additions to an existing stack.
- Tracking what's gaining traction on GitHub.

## Layout

- `landscape.md` — generated index table; one row per tool. Don't hand-edit.
- `categories/<category>.md` — human-curated learnings for every tool in the category. One section per tool, wrapped in `<!-- BEGIN TOOL: <repo> --> / <!-- END TOOL: <repo> -->` sentinels.
- `radar.md` — headline picks + changes log.
- `sources.md` — external sources scanned by the sweep pipeline.
- `RUNBOOK.md` — pipeline spec (the sweep DAG, state model, metrics).
- `TEMPLATE.md` — skeleton for new category pages.
- `viz/treemap.html` — d3 treemap of the radar.
- `state/` — pipeline state (append-only ledger, metrics history, current snapshot, deploy-status overlay).

## Categories

agent-frameworks · model-hosting · model-routing · rag-and-retrieval · vector-stores · evaluation · observability · tool-use-and-mcp · browser-and-computer-use · code-agents · security · orchestration-and-runtime · memory · voice-and-multimodal · data-and-extraction

## Workflow

1. Run a sweep — see `RUNBOOK.md`. The pipeline reads `sources.md`, refreshes GitHub metrics, and updates category prose, `landscape.md`, and `viz/data.json`.
2. Curate deploy status in `state/landscape-meta.json` (the only place humans set 🟢 / 🟡 / 🔴).
3. Edit `categories/<category>.md` directly when adding learnings — keep numbers out of prose.
