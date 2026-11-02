"""Search GitHub for projects worth reviewing and write them to a Markdown report.

Nothing is added to the list automatically. A person reads the report, which is what
keeps star-farmed copycats out. Repository descriptions are untrusted, so they are
stripped of anything Markdown could act on.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone

import common
import github

MIN_COMMITS = 10
LIMIT = 40
TERMS = ['"reverse engineered"', '"reverse-engineered"', '"clean-room"', "reimplementation", "decompilation",
         '"static recompilation"', "topic:reverse-engineering", "topic:decompilation"]


def clean(text: str | None, limit: int = 120) -> str:
    text = re.sub(r"[^\w\s.,:;'/+&%-]", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()[:limit]


def select(items: list[dict], listed: set[str], rejected: set[str]) -> list[dict]:
    unique = {}
    for item in items:
        url = item["html_url"].lower()
        if url in listed or url in rejected or item["fork"] or item["archived"]:
            continue
        if item["stargazers_count"] >= common.MIN_STARS:
            unique[url] = item
    return sorted(unique.values(), key=lambda i: -i["stargazers_count"])


def below_bar_lines(projects: list[dict], stats: dict, today: str) -> list[str]:
    """Listed projects that have fallen below the bar and should be reviewed for removal."""
    lines = []
    for project in projects:
        info = stats.get(common.github_repo(project["url"]))
        if info is None:
            continue
        problem = common.below_bar(project, info["stars"], info["pushed"], info.get("archived", False), today)
        if info.get("missing"):
            problem = "the repository could not be resolved"
        if problem:
            lines.append(f"- [{project['name']}]({project['url']}): {problem}")
    return lines


def report(items: list[dict], commits: dict[str, int], today: str, below: list[str] | None = None) -> str:
    lines = ["Repositories found by the weekly search that are not on the list yet. Add good ones "
             "through the issue form, and put bad ones in `data/rejected.json` so they stop showing up.", "",
             f"Updated {today}.", "",
             "| Repository | Stars | Created | Commits | Description |", "| --- | ---: | --- | ---: | --- |"]
    for item in items:
        name = item["full_name"]
        count = commits.get(name, 0)
        flag = " (few)" if count < MIN_COMMITS else ""
        lines.append(f"| [{name}](https://github.com/{name}) | {item['stargazers_count']} | {item['created_at'][:10]} "
                     f"| {count}{flag} | {clean(item.get('description'))} |")
    if below:
        lines += ["", "## On the list but below the bar", ""] + below
    return "\n".join(lines) + "\n"


def main() -> int:
    now = datetime.now(timezone.utc)
    created = (now - timedelta(days=120)).date().isoformat()
    listed = {p["url"].lower() for p in common.load_projects()}
    rejected = {link.lower() for link in common.load_rejected()}
    found = []
    for term in TERMS:
        found += github.search_repositories(f"{term} created:>{created} stars:>={common.MIN_STARS} fork:false")
    items = select(found, listed, rejected)[:LIMIT]
    meta = github.fetch_repositories([i["full_name"] for i in items])
    commits = {}
    for name, item in meta.items():
        target = ((item or {}).get("defaultBranchRef") or {}).get("target") or {}
        commits[name] = (target.get("history") or {}).get("totalCount", 0)
    with open(sys.argv[1], "w", encoding="utf-8") as handle:
        today = now.date().isoformat()
        stats = common.load_json(common.STATS_FILE, {"repos": {}})["repos"]
        handle.write(report(items, commits, today, below_bar_lines(common.load_projects(), stats, today)))
    print(f"{len(items)} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
