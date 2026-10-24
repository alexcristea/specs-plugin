"""Grade acceptance-criteria eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from grading import UI, committed, original, output, run  # noqa: E402

CASES = Path(__file__).resolve().parent / "cases.json"
STEP = re.compile(r"^(Given|When|Then|And|But)\b")


AC_ID = re.compile(r"@AC-01\.\d+")


def body(lines):
    """The lines of one scenario, up to the next tag line, scenario, Examples or Rule."""
    for line in lines:
        if line.startswith(("@", "Scenario", "Examples:", "Rule:")):
            return
        yield line


def scenarios(text):
    """[(tags, name, steps, block)] for each scenario: the tag line above it, its steps, and its text."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    found = []
    for i, line in enumerate(lines):
        if line.startswith(("Scenario:", "Scenario Outline:")):
            tags = lines[i - 1].split() if i and lines[i - 1].startswith("@") else []
            rest = list(body(lines[i + 1:]))
            found.append((tags, line, [s for s in rest if STEP.match(s)], "\n".join([" ".join(tags), line, *rest])))
    return found


def ids(tags):
    return [t for t in tags if AC_ID.fullmatch(t)]


def by_id(text):
    return {t: block for tags, _, _, block in scenarios(text) for t in ids(tags)}


def placement(out):
    """Where the feature file went, and what the reply says about it."""
    first = next((line for line in out.notes.splitlines() if line.strip()), "")
    return {
        "Feature file written in acceptance/ beside the use cases": (bool(out.hits), f"changed: {out.paths}"),
        "Exactly one file written, nothing else changed": (len(out.paths) == 1 and bool(out.hits), f"changed: {out.paths}"),
        "Nothing saved": (not out.paths, f"changed: {out.paths}"),
        "Reply is only the feature file (no fence, no report)": (
            re.match(r"(#|@|Feature:)", first) and "Feature:" in out.notes and "```" not in out.notes
            and not re.search(r"(?m)^## ", out.notes), f"starts {first[:60]!r}"),
        "Reported the path back to the user (notes.md)": (out.path and out.path in out.notes, f"{out.path} in notes.md"),
        "Not committed": (not committed(out.repo), "HEAD vs fixture"),
    }


def content(text):
    """The rules every feature file follows: tags, one When per scenario, coverage, declarative steps."""
    found = scenarios(text)
    ac_ids = [t for tags, *_ in found for t in ids(tags)]
    tagged = [len(ids(tags)) == 1 and any(t.startswith("@FR-") for t in tags) for tags, *_ in found]
    whens = [[s.split()[0] for s in steps].count("When") for _, _, steps, _ in found]
    step_text = "\n".join(s for _, _, steps, _ in found for s in steps)
    return {
        "Every scenario has one unique @AC-01.n tag and an @FR- tag": (
            found and all(tagged) and len(ac_ids) == len(set(ac_ids)), f"{len(found)} scenarios; IDs {ac_ids}"),
        "Feature traces to @UC-01": ("@UC-01" in text, "@UC-01 tag"),
        "Every scenario has exactly one When": (found and all(n == 1 for n in whens), f"When counts: {whens}"),
        "Main path and every extension have a scenario": (
            len(found) >= 4 and re.search(r"7 days", text) and re.search(r"declin", text, re.I),
            f"{len(found)} scenarios (main, 1a, 3a, 3b need 4)"),
        "Scenario-verified NFR-3 tagged on a scenario": ("@NFR-3" in text, "@NFR-3 tag"),
        "Steps are declarative, not UI": (step_text and not UI.search(step_text), f"found: {sorted({m.group(0) for m in UI.finditer(step_text)})}"),
    }


def update(out):
    """update-keeps-ids: extension 3b gets a new scenario, and the existing three stay as they were."""
    before, after = by_id(original(out.repo, out.path)) if out.path else {}, by_id(out.text)
    kept = [i for i in ("@AC-01.1", "@AC-01.2", "@AC-01.3") if after.get(i) == before.get(i)]
    new = after.get("@AC-01.4", "")
    return {
        "AC-01.1 to AC-01.3 unchanged": (len(kept) == 3, f"unchanged: {kept}"),
        "Extension 3b covered by a new AC-01.4": (re.search(r"7 days|answer|respond", new, re.I), new[:120] or "no @AC-01.4"),
    }


def grade(case, run_dir):
    out = output(case, run_dir)
    checks = placement(out) | content(out.text)
    if case["name"] == "update-keeps-ids":
        checks |= update(out)
    return checks


if __name__ == "__main__":
    run(CASES, grade, sys.argv[1])
