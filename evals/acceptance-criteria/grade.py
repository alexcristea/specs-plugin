"""Grade acceptance-criteria eval runs by inspecting each run's git repo and notes.md.

usage: python3 grade.py <iteration-dir>
Writes grading.json into every eval-<id>-<name>/<config>/run-<n>/ directory.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from grading import UI, changed, committed, original, run  # noqa: E402

CASES = Path(__file__).resolve().parent / "cases.json"
STEP = re.compile(r"^(Given|When|Then|And|But)\b")


def scenarios(text):
    """[(tags, name, steps, block)] for each scenario: the tag line above it, its steps, and its text."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    found = []
    for i, line in enumerate(lines):
        if line.startswith(("Scenario:", "Scenario Outline:")):
            tags = lines[i - 1].split() if i and lines[i - 1].startswith("@") else []
            body = []
            for step in lines[i + 1:]:
                if step.startswith(("@", "Scenario", "Examples:", "Rule:")):
                    break
                body.append(step)
            found.append((tags, line, [s for s in body if STEP.match(s)], "\n".join([" ".join(tags), line, *body])))
    return found


def by_id(text):
    return {t: block for tags, _, _, block in scenarios(text) for t in tags if re.fullmatch(r"@AC-01\.\d+", t)}


def grade(case, run_dir):
    repo, notes = run_dir / "repo", (run_dir / "notes.md").read_text()
    paths = changed(repo)
    hits = [p for p in paths if re.search(case["path"], p)]
    path = hits[0] if hits else None
    text = notes if case.get("print") else ((repo / path).read_text() if path else "")
    found = scenarios(text)
    ac_ids = [t for tags, *_ in found for t in tags if re.fullmatch(r"@AC-01\.\d+", t)]
    tagged = [len([t for t in tags if re.fullmatch(r"@AC-01\.\d+", t)]) == 1 and any(t.startswith("@FR-") for t in tags)
              for tags, *_ in found]
    whens = [[s.split()[0] for s in steps].count("When") for _, _, steps, _ in found]
    step_text = "\n".join(s for _, _, steps, _ in found for s in steps)
    first = next((line for line in notes.splitlines() if line.strip()), "")

    checks = {
        "Feature file written in acceptance/ beside the use cases": (bool(hits), f"changed: {paths}"),
        "Exactly one file written, nothing else changed": (len(paths) == 1 and bool(hits), f"changed: {paths}"),
        "Nothing saved": (not paths, f"changed: {paths}"),
        "Reply is only the feature file (no fence, no report)": (
            re.match(r"(#|@|Feature:)", first) and "Feature:" in notes and "```" not in notes and not re.search(r"(?m)^## ", notes),
            f"starts {first[:60]!r}"),
        "Every scenario has one unique @AC-01.n tag and an @FR- tag": (
            found and all(tagged) and len(ac_ids) == len(set(ac_ids)), f"{len(found)} scenarios; IDs {ac_ids}"),
        "Feature traces to @UC-01": ("@UC-01" in text, "@UC-01 tag"),
        "Every scenario has exactly one When": (found and all(n == 1 for n in whens), f"When counts: {whens}"),
        "Main path and every extension have a scenario": (
            len(found) >= 4 and re.search(r"7 days", text) and re.search(r"declin", text, re.I),
            f"{len(found)} scenarios (main, 1a, 3a, 3b need 4)"),
        "Scenario-verified NFR-3 tagged on a scenario": ("@NFR-3" in text, "@NFR-3 tag"),
        "Steps are declarative, not UI": (step_text and not UI.search(step_text), f"found: {sorted({m.group(0) for m in UI.finditer(step_text)})}"),
        "Reported the path back to the user (notes.md)": (path and path in notes, f"{path} in notes.md"),
        "Not committed": (not committed(repo), "HEAD vs fixture"),
    }
    if case["name"] == "update-keeps-ids":
        before, after = by_id(original(repo, path)) if path else {}, by_id(text)
        kept = [i for i in ("@AC-01.1", "@AC-01.2", "@AC-01.3") if after.get(i) == before.get(i)]
        new = after.get("@AC-01.4", "")
        checks |= {
            "AC-01.1 to AC-01.3 unchanged": (len(kept) == 3, f"unchanged: {kept}"),
            "Extension 3b covered by a new AC-01.4": (re.search(r"7 days|answer|respond", new, re.I), new[:120] or "no @AC-01.4"),
        }
    return checks


if __name__ == "__main__":
    run(CASES, grade, sys.argv[1])
