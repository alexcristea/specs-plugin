"""Grade use-case eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from grading import STACK, UI, committed, output, run, section  # noqa: E402

CASES = Path(__file__).resolve().parent / "cases.json"
MARKER = re.compile(r"^<!-- file: (.+?) -->\s*$", re.M)
TRACED = ["FR-1", "FR-2", "FR-3", "FR-4", "FR-5"]  # the fixture PRD's Must and Should requirements


def documents(case, out):
    """{path: text} for every use case the run produced, from the repo or, with --print, from the reply."""
    if case.get("print"):
        parts = MARKER.split(out.notes)[1:]
        return dict(zip(parts[::2], parts[1::2]))
    return {p: (out.repo / p).read_text() for p in out.paths if p.endswith(".md")}


def steps(text):
    return re.findall(r"^\d+\. ", section(text, r"main (success )?(scenario|flow)"), re.M)


def placement(out, docs):
    """Where the use cases went, and what the reply says about them."""
    hits, paths, notes = out.hits, out.paths, out.notes
    return {
        "Use cases written in use-cases/ beside the PRD": (len(hits) >= 2, f"matching: {hits}"),
        "Use cases written at specs/ in the repo root": (bool(hits), f"changed: {paths}"),
        "Nothing else changed": (hits and len(hits) == len(paths), f"changed: {paths}"),
        "Nothing saved": (not paths, f"changed: {paths}"),
        "Reply is only the use cases, each after a file marker": (
            notes.startswith("<!-- file:") and len(docs) >= 2 and "```" not in notes,
            f"{len(docs)} marked documents; starts {notes[:50]!r}"),
        # a list of five files can name the folder once, so each file name is enough
        "Reported the path back to the user (notes.md)": (
            hits and all(Path(p).name in notes for p in hits) and str(Path(hits[0]).parent) in notes,
            f"{[Path(p).name for p in hits]} and their folder in notes.md"),
        "Not committed": (not committed(out.repo), "HEAD vs fixture"),
    }


def traced(m):
    """A Traces to row with plain FR- IDs (not links) and a link to the PRD."""
    return m and re.search(r"FR-\d", m.group(1)) and "](../prd.md" in m.group(1) and "[FR-" not in m.group(1)


def content(docs):
    """The rules every use case follows: size, shape, traces, and no UI or stack."""
    every = lambda pred: bool(docs) and all(pred(t) for t in docs.values())  # noqa: E731
    words = {p: len(t.split()) for p, t in docs.items()}
    flows = "".join(section(t, r"main (success )?(scenario|flow)") + section(t, "extension|alternat") for t in docs.values())
    traces = [re.search(r"(?m)^\| Traces to \| (.*) \|$", t) for t in docs.values()]
    untraced = [fr for fr in TRACED if not any(re.search(rf"\b{fr}\b", t) for t in docs.values())]
    return {
        "Every use case under 400 words": (every(lambda t: len(t.split()) <= 400), f"words: {words}"),
        "Every main success scenario has 3 to 9 steps": (
            every(lambda t: 3 <= len(steps(t)) <= 9), f"steps: {[len(steps(t)) for t in docs.values()]}"),
        "Every use case has extensions": (
            every(lambda t: section(t, "extension|alternat").strip()), "an Extensions section with content in each"),
        "Traces to row has plain FR- IDs and a PRD link": (
            traces and all(traced(m) for m in traces), f"{[m.group(1) if m else None for m in traces]}"),
        "Every Must and Should requirement is traced": (docs and not untraced, f"untraced: {untraced}"),
        "No FR- IDs invented without a PRD": (docs and not any(re.search(r"\bFR-\d", t) for t in docs.values()), "no FR- IDs"),
        "Steps are intentions, not UI": (flows and not UI.search(flows), f"found: {sorted({m.group(0) for m in UI.finditer(flows)})}"),
        "No implementation detail from the README's stack": (
            docs and not any(STACK.search(t) for t in docs.values()), "no stack names"),
    }


def grade(case, run_dir):
    out = output(case, run_dir)
    docs = documents(case, out)
    return placement(out, docs) | content(docs)


if __name__ == "__main__":
    run(CASES, grade, sys.argv[1])
