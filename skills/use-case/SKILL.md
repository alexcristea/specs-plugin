---
name: use-case
description: >-
  Write one-page fully dressed use cases (Cockburn style) for a feature: primary actor, goal, preconditions, guarantees, a numbered main success scenario and extensions for every step that can fail, each traced to the PRD requirements (FR-1) it covers, saved as specs/<feature>/use-cases/UC-01-<slug>.md. Use this skill whenever the user wants use cases, user flows written as steps, actor goals, or says things like "write the use cases for X", "what are the scenarios for this feature", "walk through how a user does Y", "break the PRD into use cases", or "what can go wrong when a user does Z". Also use it to update use cases after the PRD changes. Not for user stories in a backlog tool, UML diagrams, PRDs or Gherkin acceptance criteria. Takes an optional path, and --print to return the use cases without saving them.
argument-hint: "[path] [--print]"
---

# Use cases

Your job is to describe, step by step, how each actor reaches a goal with the system, and every way that can go wrong. A use case is where vague requirements meet concrete behavior: "admins can invite people" becomes what happens when the email is already a member, when the invite expires, when the admin loses permission halfway through.

The extensions are where the value is. A main success scenario alone is the demo path; the extensions are the bugs that would otherwise be found in production. Each one later becomes a scenario in `acceptance-criteria`.

Arguments: `$ARGUMENTS`

- **A path**: the first word, if it contains a `/`, ends in `.md`, or exists. It says where the use cases go (§1).
- **`--print`**, anywhere: return the use cases instead of saving them, for a tool or script that only needs the text (§7).
- Anything else describes the feature or the goals to cover.

## 1. Find the PRD and the existing use cases

Use cases go in a `use-cases/` folder beside the feature's `prd.md`. Take the first match, in this order:

1. **A path in the arguments.** A `prd.md` is the PRD to read, and the use cases go in `use-cases/` next to it. Any other `.md` file is a use case to write or update, and the PRD is `../prd.md` from it. A `use-cases/` folder is where the files go. A folder that holds a `prd.md` or `use-cases/` is that feature's folder. Any other folder is where feature folders go: `<folder>/<feature-slug>/use-cases/`. Create what doesn't exist yet: the user named the place on purpose.
2. **The feature's PRD in the repo.** Look for it (`git ls-files | grep -iE '(^|/)prd\.md$|/use-cases/'`) and write beside it. With no PRD for this feature, follow where the repo keeps other specs.
3. **`specs/` at the project root**: `$(git rev-parse --show-toplevel)/specs/<feature-slug>/use-cases/`, or the working directory outside a git repo. The root, not the folder you were started in, because the other specs skills look there.

Read the PRD. Use cases trace to its `FR-` IDs, so you need them.

If there is no PRD, say so and offer `prd` first. If the user wants use cases anyway, write them and leave the **Traces to** row as `none (no PRD yet)`, with no link, rather than inventing requirement IDs that don't exist.

Read existing files in the feature's `use-cases/` too: you may be adding to them or updating them, and numbering continues from the highest existing `UC-` number.

## 2. Find the actors and their goals

List the actors (people and external systems that interact with the feature) and the goal each one has. One use case per **user goal**: something the actor would be satisfied to have done in one sitting ("invite a teammate"), not a single click ("press the invite button") and not a whole job ("manage the team").

Show this list to the user before writing the use cases in full: it is cheap to fix a missing actor here and expensive after five files are written.

## 3. Write each use case

Use the layout in `references/template.md`, one file per use case: `specs/<feature>/use-cases/UC-01-<slug>.md`, and match the length and tone of the worked example in `references/example.md`. Number with two digits (`UC-01` … `UC-99`) so files sort.

**Keep it to one page.** A use case that runs longer gets skimmed, and the skimmed extensions are the ones nobody builds. Aim for under 400 words, the size of the example. To stay there:

- **Three to nine steps** in the main success scenario. Fewer means the goal is really one action; more means it is two goals, or the steps have slipped into UI detail.
- **One line per extension**: the condition, what the system does, and how it ends (`resume at step 3` or `use case fails`). Nest numbered steps under an extension only when one line truly can't hold it.
- **One or two bullets per section.** Stakeholders are the people whose interests change the behavior, not everyone who could care; leave out a section only if it would be empty for a real reason.

- **Steps are actor intentions, not UI.** "Admin enters the invitee's email address", not "Admin types into the #email field and clicks the blue button". The UI will change; the intention won't, and acceptance criteria written from UI steps break on every redesign.
- **Each step is one action by one party**: the actor does something, or the system does something. "Admin submits and system sends the email" is two steps.
- **Every step that can fail gets an extension**, numbered after the step (`3a`, `3b`). Ask of each step: what if the input is invalid, the actor isn't allowed, something already exists, an external system is down, or the actor stops halfway? Each extension says how it ends: rejoining the main scenario at a step, or the use case failing.
- **Guarantees** are what is true when it ends. *Minimal guarantees* hold even on failure (no partial invite is left behind); *success guarantees* hold on success. These become the `Then` clauses of the acceptance criteria.
- **Trace** each use case to the requirement IDs it satisfies, written as plain text, followed by one relative link to the PRD: `FR-1, FR-3 ([PRD](../prd.md#requirements))`. Don't link each ID: the PRD's requirement rows have no anchors, and plain IDs match the `@FR-` tags when someone searches for `FR-1`. Quality targets (`NFR-` IDs in `nfr.md`) stay out of the steps and the trace: a use case says what happens, and `acceptance-criteria` ties the two together. If a step needs behavior the PRD doesn't mention, don't quietly invent a requirement: list it under **Open questions** in the use case and tell the user, since it may belong in the PRD.

## 4. Check coverage

After writing, compare the use cases with the PRD: every `Must` and `Should` functional requirement should be traced by at least one use case. Report any that aren't, and any use case that traces to nothing.

## 5. Keep IDs stable when updating

`acceptance-criteria` files carry the `UC-` ID and each scenario an `AC-` ID derived from it (`AC-03.2` belongs to `UC-03`), so never renumber or reuse a `UC-` number. A dropped use case keeps its file with status `Deprecated` and a one-line reason.

## 6. Report

Tell the user which files you wrote, their word counts, the coverage gaps from §4, and the open questions. Measure the word counts with `wc -w <files>` rather than estimating them: an estimate drifts, and a use case over 400 words needs cutting before you report, not after. Suggest `acceptance-criteria` as the next step.

## 7. With `--print`

A tool or a script reads your reply, not a person, so:

- **Save nothing.** Work out the paths as in §1 anyway and read what is there: existing use cases are still updated with their IDs kept (§5), and new ones continue the numbering.
- **Ask nothing.** Nobody is there to answer, so skip showing the actor list (§2) and list each guess under the use case's **Open questions**.
- **Count without saving**: `wc -w <<'EOF'` with each use case as the heredoc, and cut any over 400.
- **Reply with the use cases and nothing else**: no preamble, no report, no code fence around them, so the caller can save the output as it is. With more than one, put `<!-- file: <path> -->` on the line above each, naming the file it would be saved to, so the caller can split them.
