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

EXPECTED_SKILLS = {"prd", "use-case", "acceptance-criteria"}

# A plain (unquoted) YAML scalar may not contain ": " or " #", nor end with ":".
# Claude Code tolerates these, but GitHub and other strict parsers reject the whole frontmatter.
PLAIN_SCALAR_BREAKERS = re.compile(r": | #|:$")

# Relative paths a SKILL.md points Claude at, such as `references/template.md`.
REFERENCE_PATH = re.compile(r"`(references/[\w./-]+)`")

# The skills hand off to each other through these IDs, so every skill has to spell them the same way.
TRACE_IDS = {"FR-", "UC-", "AC-"}


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
