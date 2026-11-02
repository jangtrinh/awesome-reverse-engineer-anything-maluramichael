# Contributing

## Add a project

The quickest way is the [Add a project](https://github.com/maluramichael/awesome-reverse-engineer-anything/issues/new?template=add-project.yml) form. A bot checks your answers and opens the pull request for you.

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

To get on the list, a project needs **at least 500 stars** and **a commit in the last 365 days**, and it must not be archived. The bot and CI check this. The only exception is the Crafting Apps group, which stays complete.

The bar only applies on the way in. Once a project is listed it stays, even when the hype is over, and an archived one is marked as such. Only a repository that no longer exists is removed by hand, or an entry a rights holder asks to take down.

## What belongs here

- A project that exists because someone reverse engineered something closed: an app, a game, a console, a protocol, a file format or a device.
- A clean-room rebuild of a closed product.
- A project that takes a device back from its vendor: ads, telemetry, cloud lock-in.
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
