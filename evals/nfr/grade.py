"""Grade nfr eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from grading import STACK, committed, original, output, reported_words, run, section  # noqa: E402

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


def placement(out):
    """Where the NFR file went, and what the reply says about it."""
    return {
        "NFR file written beside the PRD": (bool(out.hits), f"changed: {out.paths}"),
        "Exactly one file written, nothing else changed": (len(out.paths) == 1 and bool(out.hits), f"changed: {out.paths}"),
        "Nothing saved": (not out.paths, f"changed: {out.paths}"),
        "Reply is only the spec (starts at the title, no fence, no report)": (
            out.notes.startswith("# ") and "```" not in out.notes, f"starts {out.notes[:60]!r}"),
        "Reported the path back to the user (notes.md)": (out.path and out.path in out.notes, f"{out.path} in notes.md"),
        "Not committed": (not committed(out.repo), "HEAD vs fixture"),
    }


def content(out):
    """The rules every NFR file follows: measurable, verified, scoped, traced."""
    text, every = out.text, rows(out.text)
    reqs = live(every)  # struck-through rows are history, not requirements
    words, reported = len(text.split()), reported_words(out.notes)
    unmeasured = [i for i, r in reqs.items() if not measurable(cells(r))]
    unverified = [i for i, r in reqs.items() if not VERIFIED_BY & set(cells(r))]
    scoped = [i for i, r in reqs.items() if re.search(r"\bFR-\d", r)]
    return {
        "Under 400 words": (text and words <= 400, f"{words} words"),
        "Every requirement is measurable (a number, or a pass/fail rule)": (
            every and not unmeasured, f"{len(every)} rows; no number: {unmeasured}"),
        "Every requirement says how it is verified (Scenario, Load test, Monitoring, Review)": (
            every and not unverified, f"not verified with the four values: {unverified}"),
        "Requirements are scoped to FR- IDs": (
            every and len(scoped) * 2 >= len(reqs), f"{len(scoped)} of {len(reqs)} name an FR-"),
        "Traces to row links the PRD next to it": (
            re.search(r"(?m)^\| Traces to \|.*\]\(prd\.md(#[\w-]+)?\)", text), "Traces to row with a prd.md link"),
        "Guesses listed as Assumed: under Open questions": (
            "assumed:" in section(text, "open questions").lower(), "Assumed: under Open questions"),
        "Reported word count matches wc -w": (reported == words, f"reported {reported}, wc -w {words}"),
        "No implementation detail from the README's stack": (
            text and not STACK.search(text), f"found: {sorted({m.group(0) for m in STACK.finditer(text)})}"),
    }


def update(out):
    """update-keeps-ids: NFR-1 is tightened, NFR-2 dropped and a reminder target added, without touching NFR-3."""
    before, reqs = rows(original(out.repo, out.path)) if out.path else {}, rows(out.text)
    nfr1, nfr2, nfr4 = reqs.get("NFR-1", ""), reqs.get("NFR-2", ""), reqs.get("NFR-4", "")
    stamp = re.search(r"\| Last updated \| ([^|]+) \|", out.text)
    return {
        "NFR-1 tightened to 1 minute": (re.search(r"\b1 minute", nfr1) and "5 minutes" not in nfr1, nfr1 or "missing"),
        "NFR-2 struck through with a reason, not deleted or reused": (
            "~~" in nfr2 and re.search(r"removed|covered|dropped|replaced|platform", nfr2, re.I), nfr2 or "missing"),
        "NFR-3 unchanged": (reqs.get("NFR-3") == before.get("NFR-3"), reqs.get("NFR-3", "missing")),
        "Reminder requirement added as NFR-4, scoped to FR-6": (
            "~~" not in nfr4 and re.search(r"\bFR-6\b", nfr4), nfr4 or "missing"),
        "Last updated bumped": (stamp and stamp.group(1).strip() != "2026-01-01", stamp.group(1) if stamp else "none"),
        # the ADR batches notifications every 5 minutes, which a 1-minute target rules out
        "Warned that ADR 0004 cites the tightened NFR-1": (
            re.search(r"0004|batch-borrow-notifications", out.notes), "ADR 0004 named in notes.md"),
    }


def grade(case, run_dir):
    out = output(case, run_dir)
    checks = placement(out) | content(out)
    if case["name"] == "update-keeps-ids":
        checks |= update(out)
    return checks


if __name__ == "__main__":
    run(CASES, grade, sys.argv[1])
