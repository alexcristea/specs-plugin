"""Checks the eval graders' heuristics without running Claude.

usage: python3 -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(skill):
    spec = importlib.util.spec_from_file_location(f"grade_{skill}", ROOT / "evals" / skill / "grade.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NfrMeasurable(unittest.TestCase):
    # A requirement passes with a number to measure, or an all-or-nothing rule a check can fail;
    # an adjective passes neither.
    grade = load("nfr")

    def row(self, requirement):
        return ["NFR-1", "Quality", requirement, "Scenario", "Must"]

    def test_accepts_a_number(self):
        self.assertTrue(self.grade.measurable(self.row("95% of borrow requests reach the owner within 2 minutes (FR-2).")))

    def test_accepts_an_access_rule(self):
        self.assertTrue(self.grade.measurable(self.row("Only the owner and the borrower can see who has a book (FR-5).")))

    def test_accepts_an_invariant_that_holds_through_a_failure(self):
        self.assertTrue(self.grade.measurable(self.row(
            "Once a request is accepted, the book shows its borrower until the owner marks it returned, "
            "including after a failed request or a server restart (FR-3, FR-4).")))

    def test_rejects_an_adjective(self):
        for requirement in ("Search is fast and reliable (FR-1).", "Lending data is private (FR-5)."):
            with self.subTest(requirement=requirement):
                self.assertFalse(self.grade.measurable(self.row(requirement)))


class TriggerSets(unittest.TestCase):
    # Every skill's description is checked against the same shape of set: 10 queries that should
    # trigger it and 10 near misses, so recall and false triggers weigh the same.
    def test_every_skill_has_a_balanced_trigger_set(self):
        import json
        for skill in sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill):
                queries = json.loads((ROOT / "evals" / skill / "triggers.json").read_text())
                self.assertEqual(len(queries), 20)
                self.assertEqual(sum(q["should_trigger"] for q in queries), 10)
                self.assertEqual(len({q["query"] for q in queries}), 20, "duplicate queries")


if __name__ == "__main__":
    unittest.main()
