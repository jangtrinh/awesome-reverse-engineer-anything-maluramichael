"""Shared data model for the list: categories, project files, validation."""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "data" / "projects"
STATS_FILE = ROOT / "data" / "stats.json"
HISTORY_FILE = ROOT / "data" / "history.json"
REJECTED_FILE = ROOT / "data" / "rejected.json"
README_FILE = ROOT / "README.md"

CATEGORIES = {
    "apps": {
        "title": "Apps",
        "intro": "Desktop software and operating systems rebuilt without the original source code.",
        "groups": ["Crafting Apps", "Clean-Room Rebuilds", "Compatibility Layers"],
    },
    "games": {
        "title": "Games",
        "intro": "Commercial games turned back into source code or native ports. None of these should ship game data.",
        "groups": ["Decompilations", "Static Recompilations", "Source Ports and Engine Rebuilds"],
    },
    "emulators": {
        "title": "Emulators",
        "intro": "Consoles reimplemented in software.",
        "groups": [],
    },
    "protocols": {
        "title": "Protocols, APIs and Formats",
        "intro": "Open clients and libraries for closed protocols, private APIs and undocumented file formats.",
        "groups": [],
    },
    "hardware": {
        "title": "Hardware and Firmware",
        "intro": "Devices, chips and cloud-locked gadgets opened up for local use.",
        "groups": [],
    },
    "tools": {
        "title": "Tools",
        "intro": "What people use to take things apart.",
        "groups": [
            "AI Agents and MCP",
            "Decompilers and Disassemblers",
            "Debuggers and Dynamic Analysis",
            "Binary and Firmware Inspection",
            "Network and API Capture",
            "Recompilers and Decomp Toolchains",
        ],
    },
    "related": {
        "title": "Related Lists",
        "intro": "Other lists and directories on the same subject.",
        "groups": [],
    },
}

REQUIRED = {"name", "url", "category", "description", "added"}
OPTIONAL = {"group", "target"}
GITHUB_URL = re.compile(r"^https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)$")
HTTPS_URL = re.compile(r"^https://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/[A-Za-z0-9_.~/-]*)?$")
MAX_DESCRIPTION = 170

# The bar for being on the list. This is a list of what is hot, not of everything that exists.
MIN_STARS = 500
MAX_INACTIVE_DAYS = 365
# Groups kept complete on purpose, even when a single member is still below the bar.
EXEMPT_GROUPS = {"Crafting Apps"}
FORBIDDEN_CHARS = {"\u2014": "em dash", "|": "pipe", "\n": "line break"}


def github_repo(url: str) -> str | None:
    """Return owner/repo for a GitHub URL, otherwise None."""
    match = GITHUB_URL.match(url)
    return f"{match.group(1)}/{match.group(2)}" if match else None


def slug_for(url: str) -> str:
    """File name for a project URL. One file per project keeps PRs free of merge conflicts."""
    repo = github_repo(url)
    if repo:
        return repo.lower().replace("/", "--")
    stripped = url.removeprefix("https://").rstrip("/")
    return re.sub(r"[^a-z0-9]+", "-", stripped.lower()).strip("-")


def check_project(project: object, filename: str | None = None) -> list[str]:
    """Return every rule this project breaks. An empty list means it is valid."""
    if not isinstance(project, dict):
        return ["must be a JSON object"]
    errors = []
    missing = REQUIRED - project.keys()
    unknown = project.keys() - REQUIRED - OPTIONAL
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
    if unknown:
        errors.append(f"unknown fields: {', '.join(sorted(unknown))}")
    if missing:
        return errors
    for key in project:
        if not isinstance(project[key], str) or not project[key].strip():
            errors.append(f"{key} must be a non-empty string")
    if errors:
        return errors

    url = project["url"]
    if not (GITHUB_URL.match(url) or HTTPS_URL.match(url)):
        errors.append("url must be a plain https URL")
    if url.endswith((".git", "/")):
        errors.append("url must not end with .git or /")
    if filename is not None and filename != f"{slug_for(url)}.json":
        errors.append(f"file must be named {slug_for(url)}.json")

    category = CATEGORIES.get(project["category"])
    if category is None:
        errors.append(f"category must be one of: {', '.join(CATEGORIES)}")
    elif "group" in project and project["group"] not in category["groups"]:
        errors.append(f"group must be one of: {', '.join(category['groups']) or 'none for this category'}")

    description = project["description"]
    if not description[0].isupper() and not description[0].isdigit():
        errors.append("description must start with a capital letter or digit")
    if not description.endswith("."):
        errors.append("description must end with a period")
    if len(description) > MAX_DESCRIPTION:
        errors.append(f"description must be at most {MAX_DESCRIPTION} characters")
    for key in ("name", "description", "target"):
        for char, label in FORBIDDEN_CHARS.items():
            if char in project.get(key, ""):
                errors.append(f"{key} must not contain a {label}")
    if len(project["name"]) > 60:
        errors.append("name must be at most 60 characters")
    try:
        date.fromisoformat(project["added"])
    except ValueError:
        errors.append("added must be a date like 2026-11-02")
    return errors


def below_bar(project: dict, stars: int, pushed: str, archived: bool, today: str) -> str | None:
    """Why a project does not clear the bar, or None if it does."""
    if project.get("group") in EXEMPT_GROUPS:
        return None
    if archived:
        return "it is archived"
    if stars < MIN_STARS:
        return f"it has {stars} stars, the list needs at least {MIN_STARS}"
    cutoff = (date.fromisoformat(today) - timedelta(days=MAX_INACTIVE_DAYS)).isoformat()
    if pushed < cutoff:
        return f"its last commit is from {pushed}, the list needs one from the last {MAX_INACTIVE_DAYS} days"
    return None


def repo_bar_problem(project: dict, item: dict | None, today: str) -> str | None:
    """below_bar for a raw GitHub API result. A project outside GitHub has no stars to measure."""
    if repo_missing(project, item):
        return "this GitHub repository does not exist or is private"
    if item is None:
        return None
    return below_bar(project, item["stargazerCount"], item["pushedAt"][:10], item["isArchived"], today)


def repo_missing(project: dict, item: dict | None) -> bool:
    return github_repo(project["url"]) is not None and item is None


def load_projects() -> list[dict]:
    return [json.loads(path.read_text("utf-8")) for path in sorted(PROJECTS_DIR.glob("*.json"))]


def load_rejected() -> dict[str, str]:
    """URL to reason. Keeps rejected projects out of discovery and out of the list."""
    if not REJECTED_FILE.exists():
        return {}
    return json.loads(REJECTED_FILE.read_text("utf-8"))


def load_json(path: Path, default):
    return json.loads(path.read_text("utf-8")) if path.exists() else default


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", "utf-8")
