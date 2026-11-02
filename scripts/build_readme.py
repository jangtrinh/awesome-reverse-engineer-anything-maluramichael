"""Generate README.md from data/. Never edit README.md by hand."""
from __future__ import annotations

import sys
from datetime import date, timedelta

import common

LINKS = """<!-- links:start -->
[![Support me on Ko-fi](https://malura.de/assets/badge/kofi.svg)](https://malura.de/go/kofi?ref=awesome-reverse-engineer-anything)
[![Check out my page](https://malura.de/assets/badge/malura.svg)](https://malura.de/go/site?ref=awesome-reverse-engineer-anything)
<!-- links:end -->"""

INTRO = (
    "Reverse engineering turns a closed program, protocol or device into something you can read, "
    "rebuild and run yourself. These are the open projects that did it and the tools they used, "
    f"with star trends refreshed every day. Only what is hot makes it: at least {common.MIN_STARS} stars "
    "and a commit in the last year to get in, and once a project is in, it stays."
)

ISSUE_FORM = "https://github.com/maluramichael/awesome-reverse-engineer-anything/issues/new?template=add-project.yml"

REPO = "maluramichael/awesome-reverse-engineer-anything"
STAR_CHART = f"https://api.star-history.com/chart?repos={REPO}&type=date&legend=top-left"
STAR_PAGE = f"https://www.star-history.com/?repos={REPO.replace('/', '%2F')}&type=date&legend=top-left"

TREND_WINDOW = 7
TREND_LIMIT = 15
GROWTH_BAR_WIDTH = 30


def format_stars(count: int) -> str:
    if count >= 1000:
        return f"{count / 1000:.1f}k".replace(".0k", "k")
    return str(count)


def trend(snapshots: dict[str, int], stars: int, created: str, today: str,
          window: int = TREND_WINDOW) -> tuple[float, bool]:
    """Stars per day and whether the number is measured.

    Measured means it comes from our own snapshots inside the window. Without any
    usable snapshot it falls back to the lifetime average, which is only an estimate.
    """
    today_date = date.fromisoformat(today)
    cutoff = (today_date - timedelta(days=window)).isoformat()
    earlier = sorted(day for day in snapshots if cutoff <= day < today)
    if earlier:
        days = (today_date - date.fromisoformat(earlier[0])).days
        return max(stars - snapshots[earlier[0]], 0) / days, True
    age = max((today_date - date.fromisoformat(created)).days, 1)
    return stars / age, False


def trending(projects: list[dict], stats: dict, history: dict, today: str,
             limit: int = TREND_LIMIT) -> list[tuple[dict, float, bool]]:
    rows = []
    for project in projects:
        repo = common.github_repo(project["url"])
        if project["category"] == "related" or repo not in stats:
            continue
        info = stats[repo]
        if info.get("archived") or info.get("missing"):
            continue
        rate, measured = trend(history.get(repo, {}), info["stars"], info["created"], today)
        rows.append((project, rate, measured))
    rows.sort(key=lambda row: (-row[1], row[0]["name"].lower()))
    return rows[:limit]


def project_link(project: dict) -> str:
    return f"[{project['name']}]({project['url']})"


def trending_section(projects: list[dict], stats: dict, history: dict, today: str) -> list[str]:
    rows = trending(projects, stats, history, today)
    lines = ["## Trending", "",
             f"Most stars gained per day over the last {TREND_WINDOW} days, excluding related lists.", "",
             "| Project | Category | Stars | Stars per day |", "| --- | --- | ---: | ---: |"]
    for project, rate, measured in rows:
        title = common.CATEGORIES[project["category"]]["title"]
        anchor = anchor_for(title)
        repo = common.github_repo(project["url"])
        value = f"{rate:,.0f}" if measured else f"~{rate:,.0f}"
        lines.append(f"| {project_link(project)} | [{title}](#{anchor}) | {format_stars(stats[repo]['stars'])} | {value} |")
    if any(not measured for _, _, measured in rows):
        lines += ["", "`~` is the lifetime average, used until a project has daily snapshots."]
    return lines + [""]


def growth_section(projects: list[dict]) -> list[str]:
    """New and total projects per month, from each project's added date."""
    months: dict[str, int] = {}
    for project in projects:
        month = project["added"][:7]
        months[month] = months.get(month, 0) + 1
    lines = ["## Growth", "", "Projects never leave the list, so it only gets bigger.", "",
             "| Month | New | Total | |", "| --- | ---: | ---: | --- |"]
    total, largest = 0, len(projects) or 1
    for month in sorted(months):
        total += months[month]
        bar = "\u2588" * max(round(total / largest * GROWTH_BAR_WIDTH), 1)
        lines.append(f"| {month} | {months[month]} | {total} | {bar} |")
    return lines + [""]


def star_history_section() -> list[str]:
    """Stars of this list itself, light or dark to match the reader's GitHub theme."""
    dark = STAR_CHART.replace("&legend", "&theme=dark&legend")
    return ["## Star History", "", f'<a href="{STAR_PAGE}">', " <picture>",
            f'   <source media="(prefers-color-scheme: dark)" srcset="{dark}" />',
            f'   <source media="(prefers-color-scheme: light)" srcset="{STAR_CHART}" />',
            f'   <img alt="Star History Chart" src="{STAR_CHART}" />', " </picture>", "</a>", ""]


def anchor_for(title: str) -> str:
    return "".join(c for c in title.lower().replace(" ", "-") if c.isalnum() or c == "-")


def sort_key(project: dict, stats: dict) -> tuple[int, str]:
    repo = common.github_repo(project["url"])
    return (-stats.get(repo, {}).get("stars", -1), project["name"].lower())


def table(projects: list[dict], stats: dict) -> list[str]:
    with_target = any(p.get("target") for p in projects)
    header = "| Project | " + ("Rebuilds | " if with_target else "") + "What it is | Stars | Last commit |"
    divider = "| --- | " + ("--- | " if with_target else "") + "--- | ---: | --- |"
    lines = [header, divider]
    for project in sorted(projects, key=lambda p: sort_key(p, stats)):
        info = stats.get(common.github_repo(project["url"]), {})
        description = project["description"]
        if info.get("archived"):
            description += " Archived."
        stars = format_stars(info["stars"]) if "stars" in info else ""
        target = f"{project.get('target', '')} | " if with_target else ""
        lines.append(f"| {project_link(project)} | {target}{description} | {stars} | {info.get('pushed', '')} |")
    return lines


def category_section(key: str, projects: list[dict], stats: dict) -> list[str]:
    category = common.CATEGORIES[key]
    members = [p for p in projects if p["category"] == key]
    if not members:
        return []
    lines = [f"## {category['title']}", "", category["intro"], ""]
    groups = category["groups"]
    if not groups:
        return lines + table(members, stats) + [""]
    ungrouped = [p for p in members if p.get("group") not in groups]
    for group in groups:
        grouped = [p for p in members if p.get("group") == group]
        if grouped:
            lines += [f"### {group}", ""] + table(grouped, stats) + [""]
    if ungrouped:
        lines += ["### Other", ""] + table(ungrouped, stats) + [""]
    return lines


def render(projects: list[dict], stats_file: dict, history: dict) -> str:
    stats = stats_file.get("repos", {})
    today = stats_file.get("fetched") or date.today().isoformat()
    titles = [c["title"] for key, c in common.CATEGORIES.items() if any(p["category"] == key for p in projects)]
    lines = ["# Awesome Reverse Engineer Anything [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)", "",
             LINKS, "", f"> {INTRO}", "", "## Contents", "", "- [Trending](#trending)"]
    lines += [f"- [{title}](#{anchor_for(title)})" for title in titles] + ["- [Growth](#growth)", "- [Star History](#star-history)", ""]
    lines += trending_section(projects, stats, history, today)
    for key in common.CATEGORIES:
        lines += category_section(key, projects, stats)
    lines += growth_section(projects)
    lines += star_history_section()
    lines += ["## Contributing", "",
              f"New entries are welcome. [Open an issue]({ISSUE_FORM}) and a bot "
              "prepares the pull request, or read the [contribution guidelines](contributing.md).", "",
              "## Footnotes", "",
              f"{len(projects)} projects. Stars last fetched on {today}. This file is generated from "
              "[`data/projects`](data/projects), please do not edit it by hand.", ""]
    return "\n".join(lines)


def main() -> int:
    content = render(common.load_projects(), common.load_json(common.STATS_FILE, {}),
                     common.load_json(common.HISTORY_FILE, {}))
    if "--check" in sys.argv:
        if common.README_FILE.read_text("utf-8") != content:
            print("README.md is out of date, run scripts/build_readme.py")
            return 1
        return 0
    common.README_FILE.write_text(content, "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
