"""Checks the shipped plugin without running Claude: manifest, skill layout, frontmatter and cross-references.

usage: python3 -m unittest discover -s tests
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"

EXPECTED_SKILLS = {"prd", "nfr", "use-case", "acceptance-criteria"}

# A plain (unquoted) YAML scalar may not contain ": " or " #", nor end with ":".
# Claude Code tolerates these, but GitHub and other strict parsers reject the whole frontmatter.
PLAIN_SCALAR_BREAKERS = re.compile(r": | #|:$")

# Relative paths a SKILL.md points Claude at, such as `references/template.md`.
REFERENCE_PATH = re.compile(r"`(references/[\w./-]+)`")

# The skills hand off to each other through these IDs, so every skill has to spell them the same way.
TRACE_IDS = {"FR-", "NFR-", "UC-", "AC-"}


def frontmatter(path):
    lines = path.read_text().splitlines()
    if lines[0] != "---":
        raise ValueError(f"{path}: no frontmatter")
    return lines[1:lines.index("---", 1)]


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


class Manifest(unittest.TestCase):
    def test_manifest_names_the_plugin_specs(self):
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["name"], "specs")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")


class Layout(unittest.TestCase):
    def test_expected_skills_exist(self):
        self.assertEqual({path.parent.name for path in skill_files()}, EXPECTED_SKILLS)

    def test_frontmatter_name_matches_folder(self):
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                self.assertIn(f"name: {path.parent.name}", frontmatter(path))

    def test_referenced_files_exist(self):
        for path in skill_files():
            for ref in REFERENCE_PATH.findall(path.read_text()):
                with self.subTest(skill=path.parent.name, ref=ref):
                    self.assertTrue((path.parent / ref).is_file(), f"{path.relative_to(ROOT)} points to missing {ref}")

    def test_every_reference_file_is_used(self):
        # An unreferenced file is never read, so it is either dead or a link is missing.
        for path in skill_files():
            used = set(REFERENCE_PATH.findall(path.read_text()))
            for ref in sorted((path.parent / "references").glob("**/*")):
                if ref.is_file():
                    rel = str(ref.relative_to(path.parent))
                    with self.subTest(skill=path.parent.name, ref=rel):
                        self.assertIn(rel, used, f"{path.relative_to(ROOT)} never mentions {rel}")


class Traceability(unittest.TestCase):
    def test_every_skill_uses_the_shared_trace_ids(self):
        for path in skill_files():
            text = path.read_text()
            for prefix in TRACE_IDS:
                with self.subTest(skill=path.parent.name, prefix=prefix):
                    self.assertIn(prefix, text)


class PrdIsOnePage(unittest.TestCase):
    # The PRD promises a 1-2 minute read that prints on one page; the worked example is
    # what Claude imitates, so it has to stay inside that budget itself.
    EXAMPLE = SKILLS / "prd" / "references" / "example.md"
    MAX_WORDS = 600

    def test_example_fits_on_one_page(self):
        words = len(self.EXAMPLE.read_text().split())
        self.assertLessEqual(words, self.MAX_WORDS, f"{self.EXAMPLE.relative_to(ROOT)} has {words} words")

    def test_example_summary_is_one_sentence(self):
        # The summary carries only what is being built; the why lives in Problem, right below it.
        section = re.search(r"^## Summary\n(.*?)^## ", self.EXAMPLE.read_text(), re.M | re.S)
        self.assertIsNotNone(section, "example has no ## Summary section")
        sentences = re.findall(r"[.!?](?:\s|$)", section.group(1))
        self.assertEqual(len(sentences), 1, f"summary has {len(sentences)} sentences")

    def test_example_numbers_requirements_for_downstream_specs(self):
        self.assertIn("FR-1", self.EXAMPLE.read_text())


class UseCaseIsOnePage(unittest.TestCase):
    # A use case promises to fit on one printed page; the worked example is what Claude
    # imitates, so it has to stay inside that budget itself.
    EXAMPLE = SKILLS / "use-case" / "references" / "example.md"
    MAX_WORDS = 400

    def test_example_fits_on_one_page(self):
        words = len(self.EXAMPLE.read_text().split())
        self.assertLessEqual(words, self.MAX_WORDS, f"{self.EXAMPLE.relative_to(ROOT)} has {words} words")

    def test_example_main_scenario_has_three_to_nine_steps(self):
        # Fewer steps is a single action, not a goal; more is two goals or UI detail.
        section = re.search(r"^## Main success scenario\n(.*?)^## ", self.EXAMPLE.read_text(), re.M | re.S)
        self.assertIsNotNone(section, "example has no ## Main success scenario section")
        steps = re.findall(r"^\d+\. ", section.group(1), re.M)
        self.assertTrue(3 <= len(steps) <= 9, f"main success scenario has {len(steps)} steps")

    def test_example_traces_to_requirements(self):
        self.assertIn("FR-1", self.EXAMPLE.read_text())


class AcceptanceCriteriaExample(unittest.TestCase):
    # The worked example is what Claude imitates, and it continues the use-case example,
    # so the three examples read as one traceable chain: FR-n -> UC-01 -> AC-01.n.
    EXAMPLE = SKILLS / "acceptance-criteria" / "references" / "example.feature"
    USE_CASE = SKILLS / "use-case" / "references" / "example.md"

    def scenarios(self):
        """Yield (tags, steps) for each scenario: the tag line above it and its step keywords."""
        lines = [line.strip() for line in self.EXAMPLE.read_text().splitlines()]
        lines = [line for line in lines if line and not line.startswith("#")]
        for i, line in enumerate(lines):
            if line.startswith(("Scenario:", "Scenario Outline:")):
                tags = lines[i - 1].split() if lines[i - 1].startswith("@") else []
                steps = []
                for step in lines[i + 1:]:
                    if step.startswith(("@", "Scenario", "Examples:")):
                        break
                    steps.append(step.split()[0])
                yield tags, steps

    def test_feature_traces_to_the_use_case_example(self):
        self.assertIn("@UC-01", self.EXAMPLE.read_text())

    def test_every_scenario_has_its_own_id_and_a_requirement(self):
        ids = []
        for tags, _ in self.scenarios():
            with self.subTest(tags=tags):
                ac = [tag for tag in tags if re.fullmatch(r"@AC-01\.\d+", tag)]
                self.assertEqual(len(ac), 1, "a scenario needs exactly one @AC-01.n tag")
                self.assertTrue(any(tag.startswith("@FR-") for tag in tags), "a scenario needs an @FR- tag")
                ids += ac
        self.assertTrue(ids, "example has no scenarios")
        self.assertEqual(len(ids), len(set(ids)), f"duplicate AC IDs: {ids}")

    def test_every_scenario_has_one_when(self):
        # Several actions mean several behaviors under test; the example must model the rule.
        for tags, steps in self.scenarios():
            with self.subTest(tags=tags):
                self.assertEqual(steps.count("When"), 1)

    def test_every_use_case_extension_has_a_scenario(self):
        extensions = set(re.findall(r"^- \*\*(\d+[a-z])\.\*\*", self.USE_CASE.read_text(), re.M))
        covered = set(re.findall(r"^\s*# Extension (\d+[a-z])", self.EXAMPLE.read_text(), re.M))
        self.assertTrue(extensions, "use-case example has no extensions")
        self.assertEqual(extensions - covered, set(), "extensions without a scenario")


class HeaderFieldsAreATable(unittest.TestCase):
    # Status, owner, actors and traces sit in a table under the title, so they scan at a glance.
    FILES = [SKILLS / skill / "references" / name
             for skill in ("prd", "nfr", "use-case") for name in ("template.md", "example.md")]
    TITLE_THEN_TABLE = re.compile(r"^# .*\n\n\| Field \| Value \|\n\|-+\|-+\|\n", re.M)

    def test_title_is_followed_by_a_field_table(self):
        for path in self.FILES:
            with self.subTest(file=str(path.relative_to(SKILLS))):
                self.assertRegex(path.read_text(), self.TITLE_THEN_TABLE)


class UseCaseLinksToPrd(unittest.TestCase):
    # One relative link in the header lets a reader in GitHub or a PR diff find the PRD;
    # the FR- IDs stay plain text so a search for FR-1 matches every layer the same way.
    FILES = [SKILLS / "use-case" / "references" / name for name in ("template.md", "example.md")]
    TRACES_ROW = re.compile(r"^\| Traces to \| (.*) \|$", re.M)
    PRD_LINK = "([PRD](../prd.md#requirements))"

    def test_traces_row_ends_with_a_prd_link(self):
        for path in self.FILES:
            with self.subTest(file=str(path.relative_to(SKILLS))):
                row = self.TRACES_ROW.search(path.read_text())
                self.assertIsNotNone(row, "no | Traces to | row")
                self.assertTrue(row.group(1).endswith(self.PRD_LINK), f"row is {row.group(1)!r}")
                self.assertNotRegex(row.group(1), r"\[FR-", "FR- IDs should stay plain text")


class NfrExample(unittest.TestCase):
    # The worked example is what Claude imitates, and it continues the PRD example, so every
    # row has to model the rules: a stable ID, a number someone can measure, and a way to verify it.
    EXAMPLE = SKILLS / "nfr" / "references" / "example.md"
    TEMPLATE = SKILLS / "nfr" / "references" / "template.md"
    MAX_WORDS = 400
    ROW = re.compile(r"^\| (NFR-\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", re.M)
    VERIFIED_BY = {"Scenario", "Load test", "Monitoring", "Review"}

    def rows(self):
        rows = self.ROW.findall(self.EXAMPLE.read_text())
        self.assertTrue(rows, "example has no NFR- rows")
        return [[cell.strip() for cell in row] for row in rows]

    def test_example_fits_on_one_page(self):
        words = len(self.EXAMPLE.read_text().split())
        self.assertLessEqual(words, self.MAX_WORDS, f"{self.EXAMPLE.relative_to(ROOT)} has {words} words")

    def test_every_requirement_has_a_measurable_target(self):
        # "Fast" and "secure" can't fail a check; a number with a unit can.
        for nfr, _, requirement, _, _ in self.rows():
            with self.subTest(nfr=nfr):
                self.assertRegex(requirement, r"\d", "requirement has no number to measure against")

    def test_every_requirement_says_how_it_is_verified(self):
        for nfr, _, _, verified_by, _ in self.rows():
            with self.subTest(nfr=nfr):
                self.assertIn(verified_by, self.VERIFIED_BY)

    def test_ids_are_unique(self):
        ids = [row[0] for row in self.rows()]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate NFR IDs: {ids}")

    def test_scoped_requirements_trace_to_the_prd(self):
        self.assertTrue(any("FR-" in row[2] for row in self.rows()), "no requirement names the FR- it applies to")

    def test_traces_row_links_to_the_prd_next_to_it(self):
        # nfr.md sits beside prd.md in specs/<feature>/, so the link has no ../
        for path in (self.EXAMPLE, self.TEMPLATE):
            with self.subTest(file=path.name):
                self.assertRegex(path.read_text(), r"(?m)^\| Traces to \| .*\(\[PRD\]\(prd\.md#requirements\)\) \|$")


class FrontmatterIsStrictYaml(unittest.TestCase):
    def test_description_is_a_folded_block_scalar(self):
        # Descriptions are long prose that gets edited during trigger tuning; a folded
        # scalar lets them contain ": " and " #" without the author thinking about YAML.
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                self.assertTrue("description: >-" in frontmatter(path),
                                f"{path.relative_to(ROOT)}: write description as 'description: >-' "
                                "with the text indented on the following lines")

    def test_plain_values_have_no_yaml_indicators(self):
        for path in skill_files():
            for number, line in enumerate(frontmatter(path), start=2):
                key, sep, value = line.partition(": ")
                if not sep or line.startswith((" ", "#")):
                    continue
                value = value.strip()
                if value[:1] in ("'", '"', ">", "|"):
                    continue
                with self.subTest(skill=path.parent.name, key=key):
                    match = PLAIN_SCALAR_BREAKERS.search(value)
                    self.assertIsNone(
                        match,
                        f"{path.relative_to(ROOT)}:{number} unquoted {key} contains {match and match.group()!r}; "
                        "use a folded block scalar (>-) or quote it",
                    )


if __name__ == "__main__":
    unittest.main()
