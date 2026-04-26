"""README fetcher for ai-radar triage (sweep upgrade Phase 2).

Pulls a candidate repo's README via `gh api repos/{repo}/readme`, caches it on
disk so re-runs are free, and truncates to keep triage user-message size bounded.
"""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "state" / ".cache" / "readmes"
TRUNCATE_CHARS = 8000  # ~2k tokens of context — enough to read the elevator pitch + first few sections.


def _cache_path(repo: str) -> Path:
    owner, _, name = repo.partition("/")
    safe = f"{owner}__{name}.md"
    return CACHE_DIR / safe


def fetch_readme(repo: str, *, refresh: bool = False) -> str | None:
    """Return README markdown for `owner/repo`, truncated. Returns None on miss.

    Cached under `state/.cache/readmes/<owner>__<name>.md`. The empty string is a
    valid cached value meaning "we tried and there was no README" — distinct from
    a cache miss (file absent), which triggers a fetch.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp = _cache_path(repo)

    if cp.exists() and not refresh:
        text = cp.read_text()
        return text if text else None

    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/readme", "--jq", "{content, encoding}"],
            capture_output=True, text=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        # 404 / archived / no README — write empty sentinel so we don't refetch.
        cp.write_text("")
        return None

    try:
        payload = json.loads(result.stdout)
        if payload.get("encoding") != "base64":
            cp.write_text("")
            return None
        raw = base64.b64decode(payload["content"]).decode("utf-8", errors="replace")
    except Exception:
        cp.write_text("")
        return None

    truncated = raw[:TRUNCATE_CHARS]
    cp.write_text(truncated)
    return truncated if truncated else None


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: readme_fetch.py owner/repo", file=sys.stderr)
        sys.exit(1)
    out = fetch_readme(sys.argv[1])
    if out is None:
        print("(no README)", file=sys.stderr)
        sys.exit(2)
    print(out)
