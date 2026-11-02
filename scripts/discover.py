"""Search GitHub by keyword and topic for projects worth reviewing and write a Markdown report.

Nothing is added to the list automatically. A person reads the report, which is what
keeps star-farmed copycats out. Each candidate gets a score from signals that need no
judgement, so the review can start at the top. Repository descriptions are untrusted,
so they are stripped of anything Markdown could act on.
"""
from __future__ import annotations

import re
import sys
import time
from datetime import datetime, timedelta, timezone

import common
import github
import scoring

LIMIT = 80
TERMS = ['"reverse engineered"', '"reverse-engineered"', '"clean-room"', "reimplementation", "decompilation",
         '"static recompilation"', "debloat", '"smart tv"', '"android tv"', "unofficial", '"native port"',
         "rebuilt", '"not an emulator"']
SEARCH_PAUSE_SECONDS = 2.5  # The search API allows 30 requests per minute.

# Candidates are at most this old. One that still draws stars after months outlived its first wave.
CREATED_WITHIN_DAYS = 120


def queries(created: str) -> list[str]:
    terms = TERMS + [f"topic:{topic}" for topic in scoring.TOPICS]
    return [f"{term} created:>{created} stars:>={common.MIN_STARS} fork:false" for term in terms]


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


def gone_lines(projects: list[dict], stats: dict) -> list[str]:
    """Listed projects whose repository no longer exists. A quiet project is fine, a dead link is not."""
    return [f"- [{project['name']}]({project['url']})" for project in projects
            if stats.get(common.github_repo(project["url"]), {}).get("missing")]


def report(rows: list[dict], today: str, gone: list[str] | None = None) -> str:
    """rows hold the search item plus commits, score and signals, best score first."""
    lines = ["Repositories found by the weekly search that are not on the list yet. Add good ones "
             "through the issue form, and put bad ones in `data/rejected.json` so they stop showing up.", "",
             "The score only adds up facts GitHub reports: README language, code, license, topics, owner and repository age, "
             "star speed, forks, commit spread, contributors and issues. Whether a project fits still needs a person.", "",
             f"Updated {today}.", "",
             "| Score | Repository | Stars | Created | Commits | Signals | Description |",
             "| ---: | --- | ---: | --- | ---: | --- | --- |"]
    for row in rows:
        item = row["item"]
        name = item["full_name"]
        lines.append(f"| {row['score']} | [{name}](https://github.com/{name}) | {item['stargazers_count']} "
                     f"| {item['created_at'][:10]} | {row['commits']} | {' '.join(row['signals'])} "
                     f"| {clean(item.get('description'))} |")
    if gone:
        lines += ["", "## On the list but the repository is gone", ""] + gone
    return "\n".join(lines) + "\n"


def main() -> int:
    now = datetime.now(timezone.utc)
    created = (now - timedelta(days=CREATED_WITHIN_DAYS)).date().isoformat()
    listed = {p["url"].lower() for p in common.load_projects()}
    rejected = {link.lower() for link in common.load_rejected()}
    found = []
    for query in queries(created):
        found += github.search_repositories(query)
        time.sleep(SEARCH_PAUSE_SECONDS)
    items = select(found, listed, rejected)[:LIMIT]
    # README texts make the response large, so fewer repositories go into one request.
    meta = github.fetch_repositories([i["full_name"] for i in items], batch_size=10, repo_fields=github.CANDIDATE_FIELDS)
    rows = []
    for item in items:
        name = item["full_name"]
        data = meta.get(name)
        target = ((data or {}).get("defaultBranchRef") or {}).get("target") or {}
        points, signals = scoring.score(data, github.contributor_count(name), now)
        rows.append({"item": item, "commits": (target.get("history") or {}).get("totalCount", 0),
                     "score": points, "signals": signals})
    rows.sort(key=lambda row: (-row["score"], -row["item"]["stargazers_count"]))
    with open(sys.argv[1], "w", encoding="utf-8") as handle:
        today = now.date().isoformat()
        stats = common.load_json(common.STATS_FILE, {"repos": {}})["repos"]
        handle.write(report(rows, today, gone_lines(common.load_projects(), stats)))
    print(f"{len(items)} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
