"""Score a repository on facts GitHub reports, for weekly candidates and for listed projects alike.

Nothing here needs judgement or reading: README language, code, license, topics, ages,
star speed, forks, commit spread, contributors, issues, and for listed projects whether
they are archived or quiet. A person still decides whether a project fits.
"""
from __future__ import annotations

import re
from datetime import datetime

import common

MIN_COMMITS = 10
# Taken from the topics the listed projects actually use, without generic ones like rust or linux.
TOPICS = ["reverse-engineering", "android-reverse-engineering", "decompilation", "decompiler", "decompile",
          "disassembler", "binary-analysis", "ghidra", "frida", "static-recompilation", "recompilation",
          "reimplementation", "source-port", "native-port", "emulator", "debloat", "android-tv", "google-tv",
          "fire-tv", "smart-tv"]
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
YOUNG_REPO_DAYS = 30
SETTLED_REPO_DAYS = 90


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
    if meta.get("isArchived"):
        signals.append((-2, "archived"))
    elif (days_between(meta.get("pushedAt"), now) or 0) > common.MAX_INACTIVE_DAYS:
        signals.append((-1, "inactive"))

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
