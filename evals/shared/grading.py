"""Helpers shared by the evals/<skill>/grade.py scripts: git state, sections, the run loop."""
import json
import re
import subprocess
from pathlib import Path

# the fixture README's stack; a spec says what and how well, so none of it belongs in one
STACK = re.compile(r"\b(react|node|postgres(ql)?|elasticsearch|redis|sql|api endpoint|websocket)\b", re.I)
# a step that names the UI breaks on every redesign
UI = re.compile(r"\b(clicks?|taps?|press(es)?|button|dropdown|text ?field|screen|modal|navigates?)\b", re.I)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def check(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def head(repo):
    return git(repo, "config", "fixture.head").strip()


def changed(repo):
    """Paths changed since the fixture was built: committed, staged, unstaged and untracked."""
    paths = set(git(repo, "diff", "--name-only", head(repo)).split())
    paths |= set(git(repo, "ls-files", "--others", "--exclude-standard").split())
    return sorted(paths)


def original(repo, path):
    return git(repo, "show", f"{head(repo)}:{path}")


def committed(repo):
    return git(repo, "rev-parse", "HEAD").strip() != head(repo)


def section(text, title):
    """Body of the first markdown heading (any level) matching the title regex, up to the next heading."""
    m = re.search(rf"^#+ [^\n]*(?:{title})[^\n]*\n(?P<body>.*?)(?=^#+ |\Z)", text, re.M | re.S | re.I)
    return m.group("body") if m else ""


def reported_words(notes):
    m = re.search(r"(\d{2,4})[ -]words?", notes)
    return int(m.group(1)) if m else None


def summarize(expectations):
    passed = sum(e["passed"] for e in expectations)
    return {"expectations": expectations,
            "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations),
                        "pass_rate": round(passed / len(expectations), 2)}}


def run(cases_path, grade, iteration):
    """Grade every run of every case: grade(case, run_dir) returns {assertion text: (passed, evidence)}."""
    for case in json.loads(Path(cases_path).read_text())["evals"]:
        for repo in sorted(Path(iteration).glob(f"eval-{case['id']}-{case['name']}/*/run-*/repo")):
            checks = grade(case, repo.parent)
            result = summarize([check(a, *checks[a]) for a in case["assertions"]])
            (repo.parent / "grading.json").write_text(json.dumps(result, indent=2) + "\n")
            s = result["summary"]
            print(f"{case['name']:28} {repo.parent.parent.name:14} {s['passed']}/{s['total']}")
