"""Grade nfr eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from grading import STACK, changed, committed, original, reported_words, run, section  # noqa: E402

CASES = Path(__file__).resolve().parent / "cases.json"
VERIFIED_BY = {"Scenario", "Load test", "Monitoring", "Review"}
NUMBER = re.compile(r"\d|\b(zero|none|one|two|three|four|five|six|seven|eight|nine|ten)\b", re.I)
# all-or-nothing wording: who may act, or a state that holds until an event, even through a failure
RULE = re.compile(r"\b(only|never|cannot|can't|no one|nobody|must not|every|always|until|including after)\b", re.I)
NFR_ROW = re.compile(r"^\|\s*(~~)?(NFR-\d+)\b.*$", re.M)


def rows(text):
    """{NFR-n: full table row} for every requirement row."""
    return {m.group(2): m.group(0) for m in NFR_ROW.finditer(text)}


def cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def measurable(row):
    """A number to measure against, or an all-or-nothing rule (who may or may not do what) a check can fail."""
    requirement = re.sub(r"\bN?FR-\d+", "", " ".join(row[1:]))  # any layout: every cell but the ID
    return bool(NUMBER.search(requirement) or RULE.search(requirement))


def live(reqs):
    return {i: r for i, r in reqs.items() if "~~" not in r}


def grade(case, run_dir):
    repo, notes_path = run_dir / "repo", run_dir / "notes.md"
    notes = notes_path.read_text() if notes_path.exists() else ""
    paths = changed(repo)
    hits = [p for p in paths if re.search(case["path"], p)]
    path = hits[0] if hits else None
    text = notes if case.get("print") else ((repo / path).read_text() if path else "")
    reqs, words = rows(text), len(text.split())
    unmeasured = [i for i, r in live(reqs).items() if not measurable(cells(r))]
    unverified = [i for i, r in live(reqs).items() if not VERIFIED_BY & set(cells(r))]
    scoped = [i for i, r in live(reqs).items() if re.search(r"\bFR-\d", r)]
    reported = reported_words(notes)

    checks = {
        "NFR file written beside the PRD": (bool(hits), f"changed: {paths}"),
        "Exactly one file written, nothing else changed": (len(paths) == 1 and bool(hits), f"changed: {paths}"),
        "Nothing saved": (not paths, f"changed: {paths}"),
        "Reply is only the spec (starts at the title, no fence, no report)": (
            notes.startswith("# ") and "```" not in notes, f"starts {notes[:60]!r}"),
        "Under 400 words": (text and words <= 400, f"{words} words"),
        "Every requirement is measurable (a number, or a pass/fail rule)": (reqs and not unmeasured, f"{len(reqs)} rows; no number: {unmeasured}"),
        "Every requirement says how it is verified (Scenario, Load test, Monitoring, Review)": (
            reqs and not unverified, f"not verified with the four values: {unverified}"),
        "Requirements are scoped to FR- IDs": (
            reqs and len(scoped) * 2 >= len(live(reqs)), f"{len(scoped)} of {len(live(reqs))} name an FR-"),
        "Traces to row links the PRD next to it": (
            re.search(r"(?m)^\| Traces to \|.*\]\(prd\.md(#[\w-]+)?\)", text), "Traces to row with a prd.md link"),
        "Guesses listed as Assumed: under Open questions": (
            "assumed:" in section(text, "open questions").lower(), "Assumed: under Open questions"),
        "Reported word count matches wc -w": (reported == words, f"reported {reported}, wc -w {words}"),
        "No implementation detail from the README's stack": (
            text and not STACK.search(text), f"found: {sorted({m.group(0) for m in STACK.finditer(text)})}"),
        "Reported the path back to the user (notes.md)": (path and path in notes, f"{path} in notes.md"),
        "Not committed": (not committed(repo), "HEAD vs fixture"),
    }
    if case["name"] == "update-keeps-ids":
        before = rows(original(repo, path)) if path else {}
        nfr1, nfr2 = reqs.get("NFR-1", ""), reqs.get("NFR-2", "")
        stamp = re.search(r"\| Last updated \| ([^|]+) \|", text)
        checks |= {
            "NFR-1 tightened to 1 minute": (re.search(r"\b1 minute", nfr1) and "5 minutes" not in nfr1, nfr1 or "missing"),
            "NFR-2 struck through with a reason, not deleted or reused": (
                "~~" in nfr2 and re.search(r"removed|covered|dropped|replaced|platform", nfr2, re.I), nfr2 or "missing"),
            "NFR-3 unchanged": (reqs.get("NFR-3") == before.get("NFR-3"), reqs.get("NFR-3", "missing")),
            "Last updated bumped": (stamp and stamp.group(1).strip() != "2026-01-01", stamp.group(1) if stamp else "none"),
        }
    return checks


if __name__ == "__main__":
    run(CASES, grade, sys.argv[1])
