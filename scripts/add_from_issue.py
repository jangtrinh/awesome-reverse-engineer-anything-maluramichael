"""Turn an "Add a project" issue form into a project file.

The issue body is untrusted input. It only ever reaches this script through an
environment variable and only leaves it as JSON values that pass check_project.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

import common
import github

LABELS = {category["title"]: key for key, category in common.CATEGORIES.items() if key != "related"}
FIELDS = {"Project URL": "url", "Project name": "name", "Category": "category",
          "What does it rebuild?": "target", "Description": "description"}


def parse_form(body: str) -> dict[str, str]:
    """GitHub renders issue forms as '### Label' followed by the answer."""
    values = {}
    for label, answer in re.findall(r"^### (.+?)\s*\n(.*?)(?=^### |\Z)", body, flags=re.M | re.S):
        key = FIELDS.get(label.strip())
        answer = answer.strip()
        if key and answer and answer != "_No response_":
            values[key] = answer
    return values


def build_project(values: dict[str, str], today: str) -> tuple[dict | None, list[str]]:
    project = dict(values)
    if "category" in project:
        project["category"] = LABELS.get(project["category"], project["category"])
    project["url"] = project.get("url", "").rstrip("/").removesuffix("#readme")
    project["added"] = today
    errors = common.check_project(project)
    return (None, errors) if errors else (project, [])


def existing_problem(project: dict) -> str | None:
    url = project["url"].lower()
    if any(p["url"].lower() == url for p in common.load_projects()):
        return "this project is already on the list"
    if any(link.lower() == url for link in common.load_rejected()):
        return "this project was rejected before, see data/rejected.json"
    repo = common.github_repo(project["url"])
    item = github.fetch_repositories([repo]).get(repo) if repo else None
    return common.repo_bar_problem(project, item, project["added"])


def main() -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    project, errors = build_project(parse_form(os.environ["ISSUE_BODY"]), today)
    if project:
        problem = existing_problem(project)
        errors = [problem] if problem else []
    output = os.environ["GITHUB_OUTPUT"]
    if errors:
        with open(os.environ["ERROR_FILE"], "w", encoding="utf-8") as handle:
            handle.write("This could not be turned into a pull request yet. Edit the issue and it runs again.\n\n")
            handle.writelines(f"- {error}\n" for error in errors)
        with open(output, "a", encoding="utf-8") as handle:
            handle.write("ok=false\n")
        return 0
    slug = common.slug_for(project["url"])
    (common.PROJECTS_DIR / f"{slug}.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False, sort_keys=True) + "\n", "utf-8")
    with open(output, "a", encoding="utf-8") as handle:
        handle.write(f"ok=true\nslug={slug}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
