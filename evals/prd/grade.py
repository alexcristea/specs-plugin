"""Grade prd eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from grading import STACK, committed, original, output, reported_words, run, section  # noqa: E402

CASES = Path(__file__).resolve().parent / "cases.json"
MOSCOW = {"Must", "Should", "Could", "Won't"}
FR_ROW = re.compile(r"^\|\s*(~~)?(FR-\d+)\b.*$", re.M)


def rows(text):
    """{FR-n: full table row} for every requirement row."""
    return {m.group(2): m.group(0) for m in FR_ROW.finditer(text)}


def placement(out):
    """Where the PRD went, and what the reply says about it."""
    reported = out.path and out.path in out.notes
    return {
        "Nothing saved": (not out.paths, f"changed: {out.paths}"),
        "Reply is only the PRD (starts at the title, no fence, no report)": (
            out.notes.startswith("# ") and "```" not in out.notes, f"starts {out.notes[:60]!r}"),
        "PRD written at the expected path": (bool(out.hits), f"changed: {out.paths}"),
        "Exactly one PRD written, nothing else changed": (len(out.paths) == 1 and bool(out.hits), f"changed: {out.paths}"),
        "Reported the path back to the user (notes.md)": (
            reported, f"notes.md {'mentions' if reported else 'does not mention'} {out.path}"),
        "Not committed": (not committed(out.repo), "HEAD vs fixture"),
    }


def content(out):
    """The rules every PRD follows, wherever it was written."""
    text, reqs = out.text, rows(out.text)
    words, reported = len(text.split()), reported_words(out.notes)
    sentences = re.findall(r"[.!?](?:\s|$)", section(text, "Summary").strip())
    unprioritized = [i for i, row in reqs.items() if not row.startswith("| ~~")
                     and not any(f"| {p}" in row for p in MOSCOW)]
    metrics, questions = section(text, "Success metrics"), section(text, "Open questions")
    return {
        # The skill aims at 450 because drafts land about 100 words over the number they are given;
        # what matters is where they land, so this checks the 550 target, not the 450 aim.
        "Within the 550-word target": (text and words <= 550, f"{words} words"),
        "Reported word count matches wc -w": (reported == words, f"reported {reported}, wc -w {words}"),
        "No implementation detail from the README's stack": (
            text and not STACK.search(text), f"found: {sorted({m.group(0) for m in STACK.finditer(text)})}"),
        "Summary is one sentence": (len(sentences) == 1, f"{len(sentences)} sentences: {section(text, 'Summary').strip()[:160]!r}"),
        "Every requirement has an FR- ID and a MoSCoW priority": (
            reqs and not unprioritized, f"{len(reqs)} FR rows; without priority: {unprioritized}"),
        "Success metrics include a guardrail": ("guardrail" in metrics.lower(), metrics.strip()[:200]),
        "Guesses listed as Assumed: under Open questions": (
            "assumed:" in questions.lower(), f"{questions.lower().count('assumed:')} Assumed: entries"),
    }


def update(out):
    """explicit-file-update: FR-3 is dropped and a genre filter added, without touching the rest."""
    before, reqs = rows(original(out.repo, out.path)) if out.hits else {}, rows(out.text)
    same = [i for i in ("FR-1", "FR-2", "FR-4") if reqs.get(i) == before.get(i)]
    fr3, fr5 = reqs.get("FR-3", ""), reqs.get("FR-5", "")
    stamp = re.search(r"\| Last updated \| ([^|]+) \|", out.text)
    return {
        "FR-1, FR-2 and FR-4 unchanged": (len(same) == 3, f"unchanged: {same}"),
        "FR-3 struck through with a reason, not deleted or reused": (
            "~~" in fr3 and re.search(r"removed|replaced|dropped", fr3, re.I), fr3 or "FR-3 row missing"),
        "Genre filter added as FR-5": ("genre" in fr5.lower(), fr5 or "FR-5 row missing"),
        "Last updated bumped": (
            stamp and stamp.group(1).strip() != "2026-01-01", stamp.group(1) if stamp else "no Last updated row"),
    }


def grade(case, run_dir):
    # a PRD written somewhere unexpected is still graded on its content
    out = output(case, run_dir, fallback=".md")
    checks = placement(out) | content(out)
    if case["name"] == "explicit-file-update":
        checks |= update(out)
    return checks


if __name__ == "__main__":
    run(CASES, grade, sys.argv[1])
