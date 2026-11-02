import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import add_from_issue
import build_readme
import common
import discover
import refresh
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

    def test_report_flags_projects_below_the_bar(self):
        stats = {"acme/example": {"stars": 3, "pushed": "2026-11-01", "created": "2026-01-01"}}
        lines = discover.below_bar_lines([VALID], stats, "2026-11-02")
        self.assertEqual(len(lines), 1)
        self.assertIn("## On the list but below the bar", discover.report([], {}, "2026-11-02", lines))

    def test_clean_strips_markdown_and_mentions(self):
        cleaned = discover.clean("[click](http://x) @someone | <b>#1</b> `code`")
        for char in "[]()@|<>#`":
            self.assertNotIn(char, cleaned)


class RealData(unittest.TestCase):
    def test_repository_data_is_valid(self):
        self.assertEqual(validate.validate_all(), [])


if __name__ == "__main__":
    unittest.main()
