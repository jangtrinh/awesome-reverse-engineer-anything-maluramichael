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

MIN_COMMITS = 10
LIMIT = 80
TERMS = ['"reverse engineered"', '"reverse-engineered"', '"clean-room"', "reimplementation", "decompilation",
         '"static recompilation"', "debloat", '"smart tv"', '"android tv"', "unofficial", '"native port"',
         "rebuilt", '"not an emulator"']
# Taken from the topics the listed projects actually use, without generic ones like rust or linux.
TOPICS = ["reverse-engineering", "android-reverse-engineering", "decompilation", "decompiler", "decompile",
          "disassembler", "binary-analysis", "ghidra", "frida", "static-recompilation", "recompilation",
          "reimplementation", "source-port", "native-port", "emulator", "debloat", "android-tv", "google-tv",
          "fire-tv", "smart-tv"]
SEARCH_PAUSE_SECONDS = 2.5  # The search API allows 30 requests per minute.

# Words that make up a large share of any English or German text and are rare in other languages.
STOPWORDS = {"the", "and", "of", "to", "is", "for", "with", "this", "that", "you", "it", "on", "are", "your",
             "can", "from", "be", "as", "not", "or", "an", "in", "der", "die", "das", "und", "ist", "nicht",
             "mit", "für", "ein", "eine", "zu", "auf", "den", "ich", "sie", "es", "wird", "auch", "sich"}
MIN_STOPWORD_SHARE = 0.08
# One CJK character carries about as much as a short Latin word, so it weighs as three letters.
CJK_WEIGHT = 3
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]")
LATIN = re.compile(r"[A-Za-z\u00c0-\u024f]")
OTHER_SCRIPT = re.compile(r"[\u0370-\u03ff\u0400-\u052f\u0590-\u06ff\u0900-\u0dff\u0e00-\u0eff]")
NOT_PROSE = re.compile(r"```.*?```|`[^`]*`|<[^>]+>|https?://\S+|\]\([^)]*\)", re.S)
DOCS_ONLY = {"Markdown", "HTML", "CSS", "Text", "Roff", "TeX"}
NEW_OWNER_DAYS = 90
OLD_OWNER_DAYS = 730
FAST_STARS_PER_DAY = 300
MIN_FORK_SHARE = 0.01
SPREAD_DAYS = 7
# Candidates are at most CREATED_WITHIN_DAYS old. One that still draws stars after months outlived its first wave.
CREATED_WITHIN_DAYS = 120
YOUNG_REPO_DAYS = 30
SETTLED_REPO_DAYS = 90


def queries(created: str) -> list[str]:
    terms = TERMS + [f"topic:{topic}" for topic in TOPICS]
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


def language(readme: str | None) -> str:
    """"en/de" when the README is mostly English or German, "other" when it is not, "none" without one."""
    if not readme:
        return "none"
    prose = NOT_PROSE.sub(" ", readme)
    cjk = len(CJK.findall(prose))
    latin = len(LATIN.findall(prose))
    other = len(OTHER_SCRIPT.findall(prose))
    if latin == 0 or cjk * CJK_WEIGHT + other > latin:
        return "other"
    words = re.findall(r"[a-zäöüß]+", prose.lower())
    hits = sum(word in STOPWORDS for word in words)
    return "en/de" if words and hits / len(words) >= MIN_STOPWORD_SHARE else "other"


def days_between(earlier: str | None, now: datetime) -> int | None:
    if not earlier:
        return None
    return (now - datetime.fromisoformat(earlier.replace("Z", "+00:00"))).days


def score(meta: dict | None, contributors: int | None, now: datetime) -> tuple[int, list[str]]:
    """Points and the signals behind them. Only facts GitHub reports, nothing that needs reading."""
    if meta is None:
        return 0, ["no data"]
    signals: list[tuple[int, str]] = []
    def text(*keys: str) -> str | None:
        return next((meta[key]["text"] for key in keys if (meta.get(key) or {}).get("text")), None)

    lang = language(text("readme1", "readme2", "readme3"))
    if lang != "en/de" and language(text("readme_en1", "readme_en2", "readme_en3")) == "en/de":
        signals.append((1, "en readme"))
    else:
        signals.append({"en/de": (1, "en/de"), "other": (-2, "language"), "none": (-1, "no readme")}[lang])
    if meta.get("isFork"):
        signals.append((-2, "fork"))

    languages = {node["name"] for node in (meta.get("languages") or {}).get("nodes") or []}
    if not languages - DOCS_ONLY:
        signals.append((-2, "no code"))
    if meta.get("licenseInfo"):
        signals.append((1, "license"))
    topics = {node["topic"]["name"] for node in (meta.get("repositoryTopics") or {}).get("nodes") or []}
    if topics & set(TOPICS):
        signals.append((1, "topics"))

    owner_age = days_between((meta.get("owner") or {}).get("createdAt"), now)
    if owner_age is not None and owner_age < NEW_OWNER_DAYS:
        signals.append((-1, "new owner"))
    elif owner_age is not None and owner_age >= OLD_OWNER_DAYS:
        signals.append((1, "old owner"))

    stars = meta.get("stargazerCount") or 0
    age = max(days_between(meta.get("createdAt"), now) or 0, 1)
    if age < YOUNG_REPO_DAYS:
        signals.append((-1, "young repo"))
    elif age >= SETTLED_REPO_DAYS:
        signals.append((1, "settled repo"))
    if stars / age >= FAST_STARS_PER_DAY:
        signals.append((-1, "fast stars"))
    if stars and (meta.get("forkCount") or 0) / stars < MIN_FORK_SHARE:
        signals.append((-1, "few forks"))

    history = (((meta.get("defaultBranchRef") or {}).get("target") or {}).get("history") or {})
    if history.get("totalCount", 0) < MIN_COMMITS:
        signals.append((-1, "few commits"))
    nodes = history.get("nodes") or []
    days = {node["committedDate"][:10] for node in nodes}
    if len(days) >= SPREAD_DAYS:
        signals.append((1, f"{len(days)} days"))
    elif len(days) <= 1 and history.get("totalCount", 0) <= len(nodes):
        # Only the newest 100 commits are fetched. A busy day says nothing about a longer history.
        signals.append((-1, "one day"))

    if contributors is not None and contributors >= 2:
        signals.append((1, "contributors"))
    if ((meta.get("issues") or {}).get("totalCount") or 0) >= 5:
        signals.append((1, "issues"))
    return sum(points for points, _ in signals), [f"{'+' if points > 0 else '-'}{name}" for points, name in signals]


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
        points, signals = score(data, github.contributor_count(name), now)
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
