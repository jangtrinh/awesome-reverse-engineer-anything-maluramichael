# Contributing

## Add a project

The quickest way is the [Add a project](../../issues/new?template=add-project.yml) form. A bot checks your answers and opens the pull request for you.

You can also open a pull request yourself. Add one file to [`data/projects`](data/projects), named `owner--repo.json` in lower case:

```json
{
  "added": "2026-11-02",
  "category": "tools",
  "description": "One sentence that says what it does.",
  "group": "AI Agents and MCP",
  "name": "Example",
  "target": "What it rebuilds, if anything",
  "url": "https://github.com/owner/repo"
}
```

`group` and `target` are optional. The categories and groups are defined in [`scripts/common.py`](scripts/common.py). Stars, last commit and trend are filled in by the daily refresh, and `README.md` is generated, so please do not edit it.

## The bar

This is a list of what is hot right now, not of everything that exists. A project needs **at least 500 stars** and **a commit in the last 365 days**, and it must not be archived. The bot and CI check this. The weekly report flags listed projects that fall below it. The only exception is the Crafting Apps group, which stays complete.

## What belongs here

- A project that exists because someone reverse engineered something closed: an app, a game, a console, a protocol, a file format or a device.
- A clean-room rebuild of a closed product.
- A tool people use for this kind of work.
- Public source code, more than a handful of commits, and a README that explains what it does.

## What does not

- ROMs, ISOs, BIOS files, extracted assets, or anything that ships or links to them.
- Leaked source code.
- Cracks, cheats, license or DRM bypasses, and malware.
- Proxies that expose a closed paid service as a free API.
- Copies of another project with a new name.

Rejected projects go in [`data/rejected.json`](data/rejected.json) with a reason, so the weekly search stops suggesting them.

## Description style

Say what the project does in one plain sentence. Start with a capital letter, end with a period, and stay under 170 characters. Skip adjectives like "blazing fast" or "powerful".

## Run it locally

Everything uses the Python standard library. With [uv](https://docs.astral.sh/uv/) and a logged-in [GitHub CLI](https://cli.github.com/):

```bash
uv run --no-project python tests/test_list.py
uv run --no-project python scripts/validate.py
uv run --no-project python scripts/refresh.py
uv run --no-project python scripts/build_readme.py
```

## Rights holders

If you want an entry removed, open an issue and it will be taken down.
