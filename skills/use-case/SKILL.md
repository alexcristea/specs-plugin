---
name: use-case
description: >-
  Write one-page fully dressed use cases (Cockburn style) for a feature: primary actor, goal, preconditions, guarantees, a numbered main success scenario and extensions for every step that can fail, each traced to the PRD requirements (FR-1) it covers, saved as specs/<feature>/use-cases/UC-01-<slug>.md. Use this skill whenever the user wants use cases, user flows written as steps, actor goals, or says things like "write the use cases for X", "what are the scenarios for this feature", "walk through how a user does Y", "break the PRD into use cases", or "what can go wrong when a user does Z". Also use it to update use cases after the PRD changes. Not for user stories in a backlog tool, UML diagrams, PRDs or Gherkin acceptance criteria.
---

# Use cases

Your job is to describe, step by step, how each actor reaches a goal with the system, and every way that can go wrong. A use case is where vague requirements meet concrete behavior: "admins can invite people" becomes what happens when the email is already a member, when the invite expires, when the admin loses permission halfway through.

The extensions are where the value is. A main success scenario alone is the demo path; the extensions are the bugs that would otherwise be found in production. Each one later becomes a scenario in `acceptance-criteria`.

## 1. Find the PRD and the existing use cases

Look for the feature's PRD (`specs/<feature>/prd.md`, or wherever the repo keeps specs) and read it. Use cases trace to its `FR-` IDs, so you need them.

If there is no PRD, say so and offer `prd` first. If the user wants use cases anyway, write them and leave the **Traces to** row as `none (no PRD yet)`, rather than inventing requirement IDs that don't exist.

Read existing files in `specs/<feature>/use-cases/` too: you may be adding to them or updating them, and numbering continues from the highest existing `UC-` number.

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
- **Trace** each use case to the requirement IDs it satisfies. If a step needs behavior the PRD doesn't mention, don't quietly invent a requirement: list it under **Open questions** in the use case and tell the user, since it may belong in the PRD.

## 4. Check coverage

After writing, compare the use cases with the PRD: every `Must` and `Should` functional requirement should be traced by at least one use case. Report any that aren't, and any use case that traces to nothing.

## 5. Keep IDs stable when updating

`acceptance-criteria` files carry the `UC-` ID and each scenario an `AC-` ID derived from it (`AC-03.2` belongs to `UC-03`), so never renumber or reuse a `UC-` number. A dropped use case keeps its file with status `Deprecated` and a one-line reason.

## 6. Report

Tell the user which files you wrote, their word counts, the coverage gaps from §4, and the open questions. Suggest `acceptance-criteria` as the next step.
