"""Grade prd eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CASES = Path(__file__).resolve().parent / "cases.json"
MOSCOW = {"Must", "Should", "Could", "Won't"}
# the fixture README's stack; a PRD says what and why, so none of it belongs in one
STACK = re.compile(r"\b(react|node|postgres(ql)?|elasticsearch|redis|sql|api endpoint|websocket)\b", re.I)
FR_ROW = re.compile(r"^\|\s*(~~)?(FR-\d+)\b.*$", re.M)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def check(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def changed(repo):
    """Paths changed since the fixture was built: committed, staged, unstaged and untracked."""
    head = git(repo, "config", "fixture.head").strip()
    paths = set(git(repo, "diff", "--name-only", head).split())
    paths |= set(git(repo, "ls-files", "--others", "--exclude-standard").split())
    return sorted(paths)


def section(text, title):
    m = re.search(rf"^## {title}\b.*?\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def rows(text):
    """{FR-n: full table row} for every requirement row."""
    return {m.group(2): m.group(0) for m in FR_ROW.finditer(text)}


def original_rows(repo, path):
    head = git(repo, "config", "fixture.head").strip()
    return rows(git(repo, "show", f"{head}:{path}"))


def grade(case, run):
    repo, notes_path = run / "repo", run / "notes.md"
    notes = notes_path.read_text() if notes_path.exists() else ""
    paths = changed(repo)
    if case.get("print"):
        # --print: the reply (saved by the run as notes.md) is the PRD
        prds, path, text = [], None, notes
    else:
        prds = [p for p in paths if re.search(case["path"], p)]
        path = prds[0] if prds else next((p for p in paths if p.endswith(".md")), None)
        text = (repo / path).read_text() if path and (repo / path).exists() else ""
    reqs = rows(text)
    words = len(text.split())
    # "Word count: 497" first; else "497 words" (a space, so "the 600-word ceiling" is not a count)
    reported = re.search(r"word count\W{0,6}(\d{2,4})", notes, re.I) or re.search(r"(\d{2,4}) words\b", notes)

    checks = {
        "Nothing saved": (not paths, f"changed: {paths}"),
        "Reply is only the PRD (starts at the title, no fence, no report)": (
            notes.startswith("# ") and "```" not in notes, f"starts {notes[:60]!r}"),
        "Close to the 450-word aim (under 500)": (text and words < 500, f"{words} words"),
        "Reported word count matches wc -w": (
            reported and int(reported.group(1)) == words,
            f"reported {reported.group(1) if reported else 'none'}, wc -w {words}"),
        "PRD written at the expected path": (bool(prds), f"changed: {paths}"),
        "Exactly one PRD written, nothing else changed": (len(paths) == 1 and bool(prds), f"changed: {paths}"),
        "Under 600 words": (text and words <= 600, f"{words} words in {path}"),
        "No implementation detail from the README's stack": (
            text and not STACK.search(text), f"found: {sorted({m.group(0) for m in STACK.finditer(text)})}"),
        "Reported the path back to the user (notes.md)": (
            path and path in notes, f"notes.md {'mentions' if path and path in notes else 'does not mention'} {path}"),
        "Not committed": (
            git(repo, "rev-parse", "HEAD").strip() == git(repo, "config", "fixture.head").strip(), "HEAD vs fixture"),
    }

    summary = section(text, "Summary").strip()
    sentences = re.findall(r"[.!?](?:\s|$)", summary)
    checks["Summary is one sentence"] = (len(sentences) == 1, f"{len(sentences)} sentences: {summary[:160]!r}")
    unprioritized = [i for i, row in reqs.items() if not row.startswith("| ~~")
                     and not any(f"| {p}" in row for p in MOSCOW)]
    checks["Every requirement has an FR- ID and a MoSCoW priority"] = (
        reqs and not unprioritized, f"{len(reqs)} FR rows; without priority: {unprioritized}")
    metrics = section(text, "Success metrics")
    checks["Success metrics include a guardrail"] = ("guardrail" in metrics.lower(), metrics.strip()[:200])
    questions = section(text, "Open questions")
    checks["Guesses listed as Assumed: under Open questions"] = (
        "assumed:" in questions.lower(), f"{questions.lower().count('assumed:')} Assumed: entries")

    if case["name"] == "explicit-file-update":
        before = original_rows(repo, path) if prds else {}
        same = [i for i in ("FR-1", "FR-2", "FR-4") if reqs.get(i) == before.get(i)]
        checks["FR-1, FR-2 and FR-4 unchanged"] = (len(same) == 3, f"unchanged: {same}")
        fr3 = reqs.get("FR-3", "")
        checks["FR-3 struck through with a reason, not deleted or reused"] = (
            "~~" in fr3 and re.search(r"removed|replaced|dropped", fr3, re.I), fr3 or "FR-3 row missing")
        fr5 = reqs.get("FR-5", "")
        checks["Genre filter added as FR-5"] = ("genre" in fr5.lower(), fr5 or "FR-5 row missing")
        stamp = re.search(r"\| Last updated \| ([^|]+) \|", text)
        checks["Last updated bumped"] = (
            stamp and stamp.group(1).strip() != "2026-01-01", stamp.group(1) if stamp else "no Last updated row")

    expectations = [check(a, *checks[a]) for a in case["assertions"]]
    passed = sum(e["passed"] for e in expectations)
    return {"expectations": expectations,
            "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations),
                        "pass_rate": round(passed / len(expectations), 2)}}


def main(iteration):
    for case in json.loads(CASES.read_text())["evals"]:
        for run in sorted(iteration.glob(f"eval-{case['id']}-{case['name']}/*/run-*/repo")):
            result = grade(case, run.parent)
            (run.parent / "grading.json").write_text(json.dumps(result, indent=2) + "\n")
            print(f"{case['name']:34} {run.parent.parent.name:11} {result['summary']['passed']}/{result['summary']['total']}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
