"""Fetch current stats for every listed GitHub project and append today's star snapshot."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import common
import github
import scoring

HISTORY_DAYS = 90


def update_history(history: dict, stars: dict[str, int], today: str, keep_days: int = HISTORY_DAYS) -> dict:
    """Add today's snapshot and drop anything older than keep_days."""
    cutoff = (date.fromisoformat(today) - timedelta(days=keep_days)).isoformat()
    updated: dict[str, dict[str, int]] = {}
    for repo in sorted(set(history) | set(stars)):
        snapshots = {day: count for day, count in history.get(repo, {}).items() if day >= cutoff}
        if repo in stars:
            snapshots[today] = stars[repo]
        if snapshots:
            updated[repo] = dict(sorted(snapshots.items()))
    return updated


def health(repos: list[str], now: datetime) -> dict[str, dict]:
    """Score and signals per repository, the same facts the weekly search scores candidates on."""
    meta = github.fetch_repositories(repos, batch_size=10, repo_fields=github.CANDIDATE_FIELDS)
    result = {}
    for repo in repos:
        if meta.get(repo) is not None:
            points, signals = scoring.score(meta[repo], github.contributor_count(repo), now)
            result[repo] = {"health": points, "signals": signals}
    return result


def main() -> None:
    repos = sorted({repo for p in common.load_projects() if (repo := common.github_repo(p["url"]))})
    fetched = github.fetch_repositories(repos)
    previous = common.load_json(common.STATS_FILE, {"repos": {}})["repos"]

    stats, stars = {}, {}
    for repo in repos:
        item = fetched.get(repo)
        if item is None:
            print(f"::warning::{repo} could not be resolved, keeping the last known stats")
            if repo in previous:
                stats[repo] = {**previous[repo], "missing": True}
            continue
        target = (item.get("defaultBranchRef") or {}).get("target") or {}
        stats[repo] = {
            "archived": item["isArchived"],
            "commits": (target.get("history") or {}).get("totalCount", 0),
            "created": item["createdAt"][:10],
            "forks": item["forkCount"],
            "pushed": item["pushedAt"][:10],
            "stars": item["stargazerCount"],
        }
        stars[repo] = item["stargazerCount"]

    now = datetime.now(timezone.utc)
    try:
        scores = health(sorted(stars), now)
    except Exception as error:  # Health is extra. A failure here must not stop the star refresh.
        print(f"::warning::health scores failed, keeping the last ones: {error}")
        scores = {}
    for repo in stats:
        known = scores.get(repo) or {key: previous[repo][key] for key in ("health", "signals")
                                     if key in previous.get(repo, {})}
        stats[repo].update(known)

    today = now.date().isoformat()
    common.write_json(common.STATS_FILE, {"fetched": today, "repos": stats})
    common.write_json(common.HISTORY_FILE, update_history(common.load_json(common.HISTORY_FILE, {}), stars, today))
    print(f"Fetched {len(stars)} of {len(repos)} repositories for {today}")


if __name__ == "__main__":
    main()
