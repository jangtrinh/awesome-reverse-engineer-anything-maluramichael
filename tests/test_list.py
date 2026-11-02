import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import add_from_issue
import build_readme
import common
import discover
import github
import refresh
import scoring
import validate

VALID = {"name": "Example", "url": "https://github.com/acme/example", "category": "apps",
         "description": "Rebuilds a thing.", "added": "2026-11-02"}


class CheckProject(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(common.check_project(VALID, "acme--example.json"), [])

    def test_wrong_filename(self):
        self.assertTrue(common.check_project(VALID, "other.json"))

    def test_em_dash_and_pipe_are_rejected(self):
        for text in ("Rebuilds \u2014 a thing.", "Rebuilds | a thing."):
            self.assertTrue(common.check_project({**VALID, "description": text}))

    def test_description_needs_period(self):
        self.assertTrue(common.check_project({**VALID, "description": "No period"}))

    def test_unknown_field_and_category_and_group(self):
        self.assertTrue(common.check_project({**VALID, "stars": "5"}))
        self.assertTrue(common.check_project({**VALID, "category": "nope"}))
        self.assertTrue(common.check_project({**VALID, "group": "nope"}))

    def test_url_cannot_smuggle_markdown(self):
        self.assertTrue(common.check_project({**VALID, "url": "https://evil.example/a)[x](y"}))

    def test_non_github_url_is_allowed(self):
        project = {**VALID, "url": "https://codeberg.org/a/b"}
        self.assertEqual(common.check_project(project, "codeberg-org-a-b.json"), [])


class Bar(unittest.TestCase):
    TODAY = "2026-11-02"

    def test_clears_the_bar(self):
        self.assertIsNone(common.below_bar(VALID, 500, "2026-01-01", False, self.TODAY))

    def test_too_few_stars(self):
        self.assertIn("499", common.below_bar(VALID, 499, "2026-11-01", False, self.TODAY))

    def test_stale(self):
        self.assertIn("2024-02-04", common.below_bar(VALID, 9000, "2024-02-04", False, self.TODAY))

    def test_archived(self):
        self.assertIn("archived", common.below_bar(VALID, 9000, "2026-11-01", True, self.TODAY))

    def test_crafting_apps_are_exempt(self):
        project = {**VALID, "group": "Crafting Apps"}
        self.assertIsNone(common.below_bar(project, 1, "2020-01-01", False, self.TODAY))

    def test_missing_repository(self):
        self.assertIn("does not exist", common.repo_bar_problem(VALID, None, self.TODAY))

    def test_outside_github_has_nothing_to_measure(self):
        project = {**VALID, "url": "https://codeberg.org/a/b"}
        self.assertIsNone(common.repo_bar_problem(project, None, self.TODAY))


class Trend(unittest.TestCase):
    def test_measured_uses_oldest_snapshot_in_window(self):
        snapshots = {"2026-10-01": 1, "2026-10-26": 100, "2026-11-01": 150}
        self.assertEqual(build_readme.trend(snapshots, 170, "2020-01-01", "2026-11-02"), (10.0, True))

    def test_falls_back_to_lifetime_average(self):
        self.assertEqual(build_readme.trend({}, 100, "2026-10-23", "2026-11-02"), (10.0, False))

    def test_lost_stars_do_not_go_negative(self):
        self.assertEqual(build_readme.trend({"2026-11-01": 10}, 5, "2020-01-01", "2026-11-02"), (0.0, True))

    def test_today_snapshot_alone_is_not_a_measurement(self):
        self.assertFalse(build_readme.trend({"2026-11-02": 5}, 5, "2026-11-01", "2026-11-02")[1])

    def test_trending_skips_related_and_archived(self):
        projects = [{**VALID, "url": "https://github.com/a/b", "name": "B"},
                    {**VALID, "url": "https://github.com/a/c", "name": "C"},
                    {**VALID, "url": "https://github.com/a/d", "name": "D", "category": "related"}]
        base = {"stars": 10, "created": "2026-11-01"}
        stats = {"a/b": base, "a/c": {**base, "archived": True}, "a/d": base}
        rows = build_readme.trending(projects, stats, {}, "2026-11-02")
        self.assertEqual([row[0]["name"] for row in rows], ["B"])


class History(unittest.TestCase):
    def test_adds_today_and_prunes_old(self):
        history = {"a/b": {"2026-01-01": 1, "2026-11-01": 2}}
        self.assertEqual(refresh.update_history(history, {"a/b": 3}, "2026-11-02"),
                         {"a/b": {"2026-11-01": 2, "2026-11-02": 3}})


class Readme(unittest.TestCase):
    def test_format_stars(self):
        self.assertEqual(build_readme.format_stars(999), "999")
        self.assertEqual(build_readme.format_stars(1000), "1k")
        self.assertEqual(build_readme.format_stars(420602), "420.6k")

    def test_render_is_deterministic_and_has_sections(self):
        projects = [{**VALID, "category": "tools", "group": "AI Agents and MCP"}]
        stats = {"fetched": "2026-11-02", "repos": {"acme/example": {"stars": 5, "created": "2026-11-01", "pushed": "2026-11-01"}}}
        first = build_readme.render(projects, stats, {})
        self.assertEqual(first, build_readme.render(projects, stats, {}))
        self.assertIn("## Tools", first)
        self.assertIn("### AI Agents and MCP", first)
        self.assertIn("- [Tools](#tools)", first)
        self.assertNotIn("## Apps", first)
        self.assertIn("- [Star History](#star-history)", first)
        self.assertIn("api.star-history.com/chart?repos=maluramichael/awesome-reverse-engineer-anything&type=date", first)
        self.assertNotIn("dll-proxy-generator", first)
        self.assertIn("| Last commit | Health |", first)

    def test_health_column(self):
        projects = [{**VALID, "category": "emulators"}]
        stats = {"fetched": "2026-11-02", "repos": {"acme/example": {"stars": 5, "created": "2026-11-01",
                                                                     "pushed": "2026-11-01", "health": 4}}}
        self.assertIn("| 5 | 2026-11-01 | 4 |", build_readme.render(projects, stats, {}))

    def test_growth_counts_per_month_and_cumulates(self):
        projects = [{**VALID, "added": "2026-11-02"}, {**VALID, "added": "2026-11-20"}, {**VALID, "added": "2026-12-01"}]
        lines = build_readme.growth_section(projects)
        self.assertTrue(any(line.startswith("| 2026-11 | 2 | 2 |") for line in lines))
        self.assertTrue(any(line.startswith("| 2026-12 | 1 | 3 |") for line in lines))

    def test_anchor_matches_github(self):
        self.assertEqual(build_readme.anchor_for("Protocols, APIs and Formats"), "protocols-apis-and-formats")


class IssueForm(unittest.TestCase):
    BODY = ("### Project URL\n\nhttps://github.com/acme/example/\n\n### Project name\n\nExample\n\n"
            "### Category\n\nProtocols, APIs and Formats\n\n### What does it rebuild?\n\n_No response_\n\n"
            "### Description\n\nRebuilds a thing.\n\n### Checks\n\n- [X] It is fine\n")

    def test_parses_form(self):
        project, errors = add_from_issue.build_project(add_from_issue.parse_form(self.BODY), "2026-11-02")
        self.assertEqual(errors, [])
        self.assertEqual(project, {"url": "https://github.com/acme/example", "name": "Example",
                                   "category": "protocols", "description": "Rebuilds a thing.", "added": "2026-11-02"})

    def test_hostile_input_is_rejected(self):
        body = self.BODY.replace("https://github.com/acme/example/", "https://github.com/a/b;rm -rf /")
        project, errors = add_from_issue.build_project(add_from_issue.parse_form(body), "2026-11-02")
        self.assertIsNone(project)
        self.assertTrue(errors)

    def test_empty_form(self):
        project, errors = add_from_issue.build_project(add_from_issue.parse_form("nothing"), "2026-11-02")
        self.assertIsNone(project)
        self.assertTrue(errors)


class Discover(unittest.TestCase):
    ITEM = {"html_url": "https://github.com/a/b", "full_name": "a/b", "fork": False, "archived": False,
            "stargazers_count": 500, "created_at": "2026-10-01T00:00:00Z", "description": "Text"}

    def test_filters(self):
        self.assertEqual(len(discover.select([self.ITEM, self.ITEM], set(), set())), 1)
        self.assertEqual(discover.select([self.ITEM], {"https://github.com/a/b"}, set()), [])
        self.assertEqual(discover.select([self.ITEM], set(), {"https://github.com/a/b"}), [])
        self.assertEqual(discover.select([{**self.ITEM, "fork": True}], set(), set()), [])
        self.assertEqual(discover.select([{**self.ITEM, "stargazers_count": 499}], set(), set()), [])

    def test_quiet_projects_are_not_flagged(self):
        stats = {"acme/example": {"stars": 3, "pushed": "2020-01-01", "created": "2019-01-01", "archived": True}}
        self.assertEqual(discover.gone_lines([VALID], stats), [])

    def test_missing_repositories_are_flagged(self):
        stats = {"acme/example": {"stars": 3, "pushed": "2020-01-01", "created": "2019-01-01", "missing": True}}
        lines = discover.gone_lines([VALID], stats)
        self.assertEqual(len(lines), 1)
        self.assertIn("the repository is gone", discover.report([], "2026-11-02", lines))

    def test_queries_cover_terms_and_topics(self):
        queries = discover.queries("2026-07-01")
        self.assertEqual(len(queries), len(set(queries)))
        self.assertTrue(any(q.startswith("topic:reverse-engineering created:>2026-07-01") for q in queries))
        self.assertTrue(any(q.startswith("debloat created:>") for q in queries))

    def test_language(self):
        english = "This tool rebuilds the protocol of the device and you can run it on your own machine. " * 5
        german = "Das Werkzeug ist ein Nachbau des Protokolls und es läuft auch auf dem eigenen Rechner. " * 5
        chinese = "关掉国产安卓手机系统里的广告热搜资讯推荐和营销推送不需要root可还原支持一键执行" * 5
        spanish = "Esta herramienta reconstruye el protocolo del dispositivo y funciona en tu propia máquina. " * 5
        self.assertEqual(scoring.language(english), "en/de")
        self.assertEqual(scoring.language(german), "en/de")
        self.assertEqual(scoring.language(chinese + " Android TV"), "other")
        self.assertEqual(scoring.language(spanish), "other")
        self.assertEqual(scoring.language(english + "中文说明：安卓电视去广告"), "en/de")
        self.assertEqual(scoring.language(None), "none")

    def test_code_blocks_do_not_count_as_english(self):
        readme = "关掉国产安卓手机系统里的广告热搜资讯推荐和营销推送" * 3 + "\n```\nthe and of to is for with this\n```\n" * 20
        self.assertEqual(scoring.language(readme), "other")

    def test_score_good_and_bad(self):
        now = datetime(2026, 11, 2, tzinfo=timezone.utc)
        english = "This tool rebuilds the protocol of the device and you can run it on your own machine. " * 5
        commits = [{"committedDate": f"2026-10-{day:02d}T10:00:00Z"} for day in range(1, 21)]
        good = {"stargazerCount": 1000, "forkCount": 80, "createdAt": "2026-08-01T00:00:00Z", "isFork": False,
                "owner": {"createdAt": "2015-01-01T00:00:00Z"}, "licenseInfo": {"spdxId": "MIT"},
                "repositoryTopics": {"nodes": [{"topic": {"name": "decompilation"}}]},
                "languages": {"nodes": [{"name": "C++"}, {"name": "Markdown"}]}, "issues": {"totalCount": 12},
                "readme1": None, "readme2": {"text": english},
                "defaultBranchRef": {"target": {"history": {"totalCount": 400, "nodes": commits}}}}
        points, signals = scoring.score(good, 3, now)
        self.assertEqual(points, 8)
        self.assertEqual(signals, ["+en/de", "+license", "+topics", "+old owner", "+settled repo", "+20 days",
                                   "+contributors", "+issues"])

        bad = {**good, "stargazerCount": 5000, "forkCount": 10, "createdAt": "2026-10-28T00:00:00Z",
               "owner": {"createdAt": "2026-10-01T00:00:00Z"}, "licenseInfo": None,
               "repositoryTopics": {"nodes": []}, "languages": {"nodes": [{"name": "Markdown"}]},
               "issues": {"totalCount": 0}, "readme2": {"text": "关掉国产安卓手机系统里的广告" * 10},
               "defaultBranchRef": {"target": {"history": {"totalCount": 4, "nodes": [commits[0]] * 4}}}}
        points, signals = scoring.score(bad, 1, now)
        self.assertEqual(signals, ["-language", "-no code", "-new owner", "-young repo", "-fast stars",
                                   "-few forks", "-few commits", "-one day"])
        self.assertEqual(points, -10)
        self.assertEqual(scoring.score(None, None, now), (0, ["no data"]))

    def test_english_translation_counts(self):
        now = datetime(2026, 11, 2, tzinfo=timezone.utc)
        english = "This tool rebuilds the protocol of the device and you can run it on your own machine. " * 5
        meta = {"readme1": {"text": "关掉国产安卓手机系统里的广告" * 10}, "readme_en1": {"text": english}}
        self.assertEqual(scoring.score(meta, None, now)[1][0], "+en readme")
        self.assertEqual(scoring.score({**meta, "readme_en1": None}, None, now)[1][0], "-language")

    def test_archived_and_quiet_projects_lose_points(self):
        now = datetime(2026, 11, 2, tzinfo=timezone.utc)
        self.assertIn("-archived", scoring.score({"isArchived": True, "pushedAt": "2020-01-01T00:00:00Z"}, None, now)[1])
        quiet = scoring.score({"isArchived": False, "pushedAt": "2025-01-01T00:00:00Z"}, None, now)[1]
        self.assertIn("-inactive", quiet)
        self.assertNotIn("-archived", quiet)
        self.assertNotIn("-inactive", scoring.score({"pushedAt": "2026-10-01T00:00:00Z"}, None, now)[1])

    def test_busy_day_in_a_long_history_is_not_one_day(self):
        now = datetime(2026, 11, 2, tzinfo=timezone.utc)
        nodes = [{"committedDate": "2026-10-20T10:00:00Z"}] * 100
        long = {"defaultBranchRef": {"target": {"history": {"totalCount": 1144, "nodes": nodes}}}}
        short = {"defaultBranchRef": {"target": {"history": {"totalCount": 5, "nodes": nodes[:5]}}}}
        self.assertNotIn("-one day", scoring.score(long, None, now)[1])
        self.assertIn("-one day", scoring.score(short, None, now)[1])

    def test_report_shows_score_and_signals(self):
        item = {**self.ITEM, "description": "Text"}
        text = discover.report([{"item": item, "commits": 42, "score": 3, "signals": ["+en/de", "-few forks"]}],
                               "2026-11-02")
        self.assertIn("| 3 | [a/b](https://github.com/a/b) | 500 | 2026-10-01 | 42 | +en/de -few forks | Text |", text)

    def test_clean_strips_markdown_and_mentions(self):
        cleaned = discover.clean("[click](http://x) @someone | <b>#1</b> `code`")
        for char in "[]()@|<>#`":
            self.assertNotIn(char, cleaned)


class GitHubClient(unittest.TestCase):
    def test_every_batch_gets_a_flat_query(self):
        queries = []

        def fake_request(url, data=None):
            queries.append(data["query"])
            return {"data": {"r0": {"nameWithOwner": "x"}, "r1": {"nameWithOwner": "y"}}}

        original = github.request
        github.request = fake_request
        try:
            github.fetch_repositories(["a/b", "c/d", "e/f"], batch_size=2, repo_fields="stargazerCount")
        finally:
            github.request = original
        self.assertEqual(len(queries), 2)
        for query in queries:
            self.assertEqual(query.count("repository("), query.count(": repository("))
            self.assertNotIn("r0: repository(owner: \"a\", name: \"b\") { r0", query)
        self.assertEqual(queries[1].count("repository("), 1)


class RealData(unittest.TestCase):
    def test_repository_data_is_valid(self):
        self.assertEqual(validate.validate_all(), [])


if __name__ == "__main__":
    unittest.main()
