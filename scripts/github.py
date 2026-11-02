"""Minimal GitHub API client on the standard library, so the list needs no dependencies."""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"


def token() -> str:
    value = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if value:
        return value
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def request(url: str, data: dict | None = None, retries: int = 3) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token()}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "awesome-reverse-engineer-anything",
    })
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (403, 429, 500, 502, 503, 504) or attempt == retries - 1:
                raise
        time.sleep(20 * (attempt + 1))
    raise RuntimeError("unreachable")


def search_repositories(query: str, per_page: int = 50) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": per_page})
    return request(f"{API}/search/repositories?{params}")["items"]


REPO_FIELDS = (
    "nameWithOwner stargazerCount forkCount createdAt pushedAt isArchived isFork "
    "defaultBranchRef { target { ... on Commit { history { totalCount } } } }"
)

# Everything scoring.score looks at. Three README spellings cover nearly every repository,
# the other three catch an English translation next to a README in another language.
CANDIDATE_FIELDS = (
    "nameWithOwner stargazerCount forkCount createdAt pushedAt isArchived isFork "
    "owner { ... on User { createdAt } ... on Organization { createdAt } } "
    "licenseInfo { spdxId } repositoryTopics(first: 30) { nodes { topic { name } } } "
    "languages(first: 10) { nodes { name } } issues { totalCount } "
    'readme1: object(expression: "HEAD:README.md") { ... on Blob { text } } '
    'readme2: object(expression: "HEAD:readme.md") { ... on Blob { text } } '
    'readme3: object(expression: "HEAD:README") { ... on Blob { text } } '
    'readme_en1: object(expression: "HEAD:README.en.md") { ... on Blob { text } } '
    'readme_en2: object(expression: "HEAD:README_EN.md") { ... on Blob { text } } '
    'readme_en3: object(expression: "HEAD:README_en.md") { ... on Blob { text } } '
    "defaultBranchRef { target { ... on Commit { history(first: 100) { totalCount nodes { committedDate } } } } }"
)


def contributor_count(repo: str, cap: int = 3) -> int | None:
    """Number of contributors, counted up to cap. None when GitHub does not tell, e.g. for a huge history."""
    try:
        people = request(f"{API}/repos/{repo}/contributors?per_page={cap}")
    except (urllib.error.HTTPError, json.JSONDecodeError):
        return None
    return len(people) if isinstance(people, list) else None


def fetch_repositories(repos: list[str], batch_size: int = 40,
                       repo_fields: str = REPO_FIELDS) -> dict[str, dict | None]:
    """Metadata per owner/repo. A repository that no longer exists maps to None."""
    result: dict[str, dict | None] = {}
    for start in range(0, len(repos), batch_size):
        batch = repos[start:start + batch_size]
        fields = " ".join(
            'r{}: repository(owner: {}, name: {}) {{ {} }}'.format(
                index, json.dumps(repo.split("/")[0]), json.dumps(repo.split("/")[1]), repo_fields)
            for index, repo in enumerate(batch)
        )
        payload = request(f"{API}/graphql", {"query": f"query {{ {fields} }}"})
        if payload.get("data") is None:
            raise RuntimeError(f"GraphQL request failed: {payload.get('errors')}")
        for index, repo in enumerate(batch):
            result[repo] = payload["data"].get(f"r{index}")
    return result
