#!/usr/bin/env bash
# Adapter for promptfoo's exec provider — argv[1] is the candidate JSON.
# Pipes it to `triage_score.py --single-candidate` via stdin so the script's
# argparse doesn't need to know promptfoo's calling convention. Other args
# promptfoo passes (provider options, context) are ignored.
set -euo pipefail
exec python "$(dirname "$0")/../../state/sweep-2026-04-26b/triage_score.py" --single-candidate <<<"${1:-}"
