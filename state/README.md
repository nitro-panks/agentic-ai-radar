# state/

Persistent state for the sweep pipeline (see `../RUNBOOK.md`).

- `ledger.jsonl` — append-only history of every tool-add/update/dormant/archive event. Never rewritten.
- `sources-cursor.json` — `{ "<source-key>": { "last_seen": "ISO-8601" } }`. Updated at the end of each `collect:*` stage.
- `sweep-<YYYY-MM-DD>/` — one directory per sweep run. Contains the stage outputs, `.done` markers, and `manifest.md`.

Rules:
- Files here are operational state, not human documentation. Don't hand-edit unless you know what you're undoing.
- Old `sweep-*` directories are kept as records — do not delete. They double as a changelog.
- If a sweep is aborted, leave the directory in place. The next sweep on a new date starts fresh.
