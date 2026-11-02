"""Fetch current stats for every listed GitHub project and append today's star snapshot."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import common
import github

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

    today = datetime.now(timezone.utc).date().isoformat()
    common.write_json(common.STATS_FILE, {"fetched": today, "repos": stats})
    common.write_json(common.HISTORY_FILE, update_history(common.load_json(common.HISTORY_FILE, {}), stars, today))
    print(f"Fetched {len(stars)} of {len(repos)} repositories for {today}")


if __name__ == "__main__":
    main()
