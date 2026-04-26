#!/usr/bin/env python3
"""Metrics-refresh stage. Hits GET /repos/{owner}/{repo} for every tracked tool,
writes 03-enriched.jsonl, updates state/metrics-current.json, and appends to
state/metrics-history.jsonl. Designed for unauthenticated GitHub API (60 req/hr).
"""
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state"
SWEEP = Path(__file__).resolve().parent
SWEEP_DATE = SWEEP.name.removeprefix("sweep-")

CURRENT = STATE / "metrics-current.json"
HISTORY = STATE / "metrics-history.jsonl"
ENRICHED = SWEEP / "03-enriched.jsonl"
STALE = SWEEP / "06-stale.jsonl"

UA = "ai-radar-sweep/0.1 (+https://github.com/ai-radar)"


def fetch(repo: str):
    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read()
        remaining = resp.headers.get("X-RateLimit-Remaining")
        return json.loads(body), remaining


def iso_date(s: str | None) -> str | None:
    if not s:
        return None
    # GitHub returns ISO 8601 with Z; keep YYYY-MM-DD for files.
    return s[:10]


def to_metric_row(repo: str, raw: dict, snapshot_ts: str, prior: dict | None):
    license_id = (raw.get("license") or {}).get("spdx_id") or (raw.get("license") or {}).get("key")
    return {
        "repo": repo,
        "name": (prior or {}).get("name") or raw.get("name"),
        "category": (prior or {}).get("category"),
        "stars": raw.get("stargazers_count"),
        "forks": raw.get("forks_count"),
        "watchers": raw.get("subscribers_count"),
        "open_issues": raw.get("open_issues_count"),
        "contributors": (prior or {}).get("contributors"),  # not refreshed this sweep
        "created_at": iso_date(raw.get("created_at")),
        "pushed_at": iso_date(raw.get("pushed_at")),
        "language": raw.get("language") or (prior or {}).get("language"),
        "license": license_id or (prior or {}).get("license"),
        "archived": bool(raw.get("archived")),
        "disabled": bool(raw.get("disabled")),
        "default_branch": raw.get("default_branch"),
        "size_kb": raw.get("size"),
        "stars_30d": None,
        "stars_90d": None,
        "commits_30d": None,
        "release_cadence_days": (prior or {}).get("release_cadence_days"),
        "latest_release": (prior or {}).get("latest_release"),
        "latest_release_date": (prior or {}).get("latest_release_date"),
        "snapshot_ts": snapshot_ts,
    }


def history_row(metric: dict) -> dict:
    return {
        "ts": metric["snapshot_ts"],
        "sweep": SWEEP_DATE,
        "repo": metric["repo"],
        "stars": metric["stars"],
        "forks": metric["forks"],
        "watchers": metric["watchers"],
        "open_issues": metric["open_issues"],
        "contributors": metric.get("contributors"),
        "pushed_at": metric["pushed_at"],
    }


def stale_classify(metric: dict, sweep_date: str) -> dict | None:
    if metric.get("archived"):
        return {"repo": metric["repo"], "classification": "archived", "reason": "archived flag"}
    if metric.get("disabled"):
        return {"repo": metric["repo"], "classification": "disabled", "reason": "disabled flag"}
    pushed = metric.get("pushed_at")
    if pushed:
        # ~6 months
        from datetime import date
        y, m, d = (int(x) for x in pushed.split("-"))
        sweep_y, sweep_m, sweep_d = (int(x) for x in sweep_date.split("-"))
        delta_days = (date(sweep_y, sweep_m, sweep_d) - date(y, m, d)).days
        if delta_days > 180:
            return {"repo": metric["repo"], "classification": "dormant", "reason": f"no push in {delta_days} days"}
    return None


def main():
    current = json.loads(CURRENT.read_text())
    snapshot_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    repos = list(current["tools"].keys())
    print(f"refreshing {len(repos)} repos", file=sys.stderr)

    enriched_rows = []
    stale_rows = []
    history_rows = []
    moved = []
    errors = []

    for i, repo in enumerate(repos, 1):
        prior = current["tools"][repo]
        try:
            raw, remaining = fetch(repo)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # repo moved or deleted — try to follow redirect later; for now mark.
                moved.append({"repo": repo, "code": 404})
                errors.append({"repo": repo, "error": "404"})
                print(f"[{i:>2}/{len(repos)}] {repo}: 404", file=sys.stderr)
                continue
            errors.append({"repo": repo, "error": f"HTTP {e.code}"})
            print(f"[{i:>2}/{len(repos)}] {repo}: HTTP {e.code}", file=sys.stderr)
            if e.code == 403:
                # rate-limited — bail without .done
                print("rate-limited; aborting without .done marker", file=sys.stderr)
                break
            continue
        except Exception as e:
            errors.append({"repo": repo, "error": str(e)})
            print(f"[{i:>2}/{len(repos)}] {repo}: {e}", file=sys.stderr)
            continue

        # Detect rename via full_name mismatch (GitHub redirects on /repos/<old>).
        full = raw.get("full_name", "")
        if full and full.lower() != repo.lower():
            moved.append({"repo": repo, "new_repo": full})
            # Use the new name going forward.
            metric = to_metric_row(full, raw, snapshot_ts, prior)
            metric["category"] = prior.get("category")
            metric["name"] = prior.get("name") or raw.get("name")
        else:
            metric = to_metric_row(repo, raw, snapshot_ts, prior)

        enriched_rows.append(metric)
        history_rows.append(history_row(metric))
        stale = stale_classify(metric, SWEEP_DATE)
        if stale:
            stale_rows.append(stale)

        print(
            f"[{i:>2}/{len(repos)}] {metric['repo']:<48} stars={metric['stars']:>6} forks={metric['forks']:>5} push={metric['pushed_at']} rl={remaining}",
            file=sys.stderr,
        )
        # Be polite even though unauthenticated allows hammering.
        time.sleep(0.4)

    # Write outputs.
    with ENRICHED.open("w") as f:
        for r in enriched_rows:
            f.write(json.dumps(r) + "\n")

    with STALE.open("w") as f:
        for r in stale_rows:
            f.write(json.dumps(r) + "\n")

    with HISTORY.open("a") as f:
        for r in history_rows:
            f.write(json.dumps(r) + "\n")

    # Update metrics-current.json: keep prior keys, replace the refreshed tools.
    new_current = {
        "generated_at": snapshot_ts,
        "_comment": current.get("_comment", ""),
        "tools": {},
    }
    refreshed_by_repo = {r["repo"]: r for r in enriched_rows}
    for repo, prior in current["tools"].items():
        # Repo may have been renamed; if so, keep entry under new name and drop old.
        renamed = next((m for m in moved if m.get("repo") == repo and m.get("new_repo")), None)
        if renamed:
            new_repo = renamed["new_repo"]
            metric = refreshed_by_repo.get(new_repo)
            if metric:
                merged = {**prior, **metric}
                merged["category"] = prior.get("category")
                merged["name"] = prior.get("name") or metric.get("name")
                new_current["tools"][new_repo] = merged
            continue
        metric = refreshed_by_repo.get(repo)
        if metric:
            merged = {**prior, **metric}
            merged["category"] = prior.get("category")
            merged["name"] = prior.get("name") or metric.get("name")
            new_current["tools"][repo] = merged
        else:
            # Refresh failed for this repo — keep prior metric, mark stale freshness.
            new_current["tools"][repo] = prior

    CURRENT.write_text(json.dumps(new_current, indent=2) + "\n")

    # Summary block for manifest.
    summary = {
        "snapshot_ts": snapshot_ts,
        "refreshed": len(enriched_rows),
        "errors": len(errors),
        "stale_flagged": len(stale_rows),
        "moved": moved,
        "errors_detail": errors,
    }
    (SWEEP / "refresh-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
