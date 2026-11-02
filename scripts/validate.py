"""Check every project file. Used by CI on each pull request."""
from __future__ import annotations

import json
import sys
from datetime import date

import common
import github


def validate_all() -> list[str]:
    errors, seen = [], {}
    rejected = common.load_rejected()
    for path in sorted(common.PROJECTS_DIR.glob("*.json")):
        try:
            project = json.loads(path.read_text("utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{path.name}: invalid JSON ({error})")
            continue
        errors += [f"{path.name}: {problem}" for problem in common.check_project(project, path.name)]
        if not isinstance(project, dict):
            continue
        url = project.get("url", "").lower()
        if url in seen:
            errors.append(f"{path.name}: same url as {seen[url]}")
        seen[url] = path.name
        reason = next((why for link, why in rejected.items() if link.lower() == url), None)
        if reason:
            errors.append(f"{path.name}: this project was rejected before: {reason}")
    return errors


def new_project_errors() -> list[str]:
    """Hold projects that have no stats yet, so new ones, to the bar.

    The bar only applies on the way in. Projects already on the list stay, however
    quiet they get.
    """
    known = common.load_json(common.STATS_FILE, {"repos": {}})["repos"]
    new = {}
    for project in common.load_projects():
        repo = common.github_repo(project["url"])
        if repo and repo not in known:
            new[repo] = project
    if not new:
        return []
    today = date.today().isoformat()
    fetched = github.fetch_repositories(sorted(new))
    errors = []
    for repo, project in new.items():
        problem = common.repo_bar_problem(project, fetched.get(repo), today)
        if problem:
            errors.append(f"{common.slug_for(project['url'])}.json: {problem}")
    return errors


def main() -> int:
    errors = validate_all()
    if not errors:
        errors = new_project_errors()
    for error in errors:
        print(f"::error::{error}")
    if errors:
        return 1
    print(f"{len(common.load_projects())} projects are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
