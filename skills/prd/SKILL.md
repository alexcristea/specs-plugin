---
name: prd
description: >-
  Write or update a product requirements document (PRD) for a feature or product: the problem, who it is for, goals and non-goals, numbered functional and non-functional requirements (FR-1, NFR-1), success metrics and open questions, saved as specs/<feature>/prd.md. Use this skill whenever the user wants a PRD, a product spec, a requirements doc, or says things like "spec out this feature", "write the requirements for X", "turn this idea into a PRD", "what should v1 of this do", or wants to capture a product idea before building it, even if they never say "PRD". Also use it to revise, review or tighten an existing PRD. Not for technical design docs, RFCs, architecture decisions, use cases or acceptance criteria.
---

# Product requirements document

Your job is to turn a product idea into a PRD that the rest of the specs (use cases, acceptance criteria) and eventually the code can be traced back to. The PRD says **what** and **why**, never **how**: once it names a database or a framework, it stops being a product decision and starts constraining the engineers who should own that choice.

The numbered requirements are the point. `use-case` traces each use case to `FR-` IDs, and `acceptance-criteria` traces each scenario through a `UC-` ID to an `AC-` ID, so a requirement without an ID can't be tested and a renumbered one breaks every link downstream.

## 1. Find where specs live

Look for an existing specs folder before creating one: `specs/`, `docs/specs/`, `docs/prd/`, or whatever an existing PRD in the repo uses. Follow what is there. With nothing to follow, write to `specs/<feature-slug>/prd.md`, where the slug is short and kebab-case (`team-invites`, not `the-new-team-invitation-flow`).

If a PRD for this feature already exists, you are updating it, not starting over: read it first and keep its IDs (see §4).

## 2. Gather what you need

A PRD built on guesses reads as confident and is wrong in ways nobody notices until the code exists. Before writing, check you know:

- **The problem**, and who has it. Evidence if there is any (support tickets, metrics, user quotes).
- **The users**: which kinds of user, and what each one is trying to get done.
- **What success looks like**, in something measurable.
- **What is out of scope** for this version.

Read what the repo and the conversation already say first; don't ask the user for what you can find. Then ask about the gaps in one short batch (at most five questions), not one at a time. If the user wants a draft anyway, write it, and record each guess under **Assumptions** so it is visible rather than buried in the prose.

## 3. Write it

Use the layout in `references/template.md`. Leave out a section only if it would be empty for a real reason (a solo internal tool may have no stakeholders worth listing); don't pad sections to fill the template.

Requirements are where PRDs usually go wrong. Each one should be:

- **Testable**: someone could write a pass/fail check for it. "Search is fast" isn't; "search returns results within 500 ms at p95 for 10k items" is.
- **One thing**: "users can invite and remove members" is two requirements, because they can ship and fail separately.
- **About behavior, not implementation**: "invites expire after 7 days", not "store `expires_at` in Postgres".
- **Prioritized** with MoSCoW (Must / Should / Could / Won't), so scope can be cut deliberately.

Functional requirements are `FR-1`, `FR-2`, …; non-functional ones (performance, security, accessibility, compliance) are `NFR-1`, `NFR-2`, …. Group them under headings if there are many, but keep one numbering sequence per kind across the document.

## 4. Keep IDs stable when updating

Other specs and tests refer to these IDs, so:

- Never renumber. New requirements take the next free number, even if that puts `FR-12` between `FR-3` and `FR-4` in the reading order.
- Never reuse a number. A dropped requirement stays, struck through with a reason: `~~FR-5: …~~ (removed 2026-10-22: replaced by FR-12)`.
- When a requirement's meaning changes, say so in the change log, and mention which use cases cite it so the user knows what to revisit (`grep -rn "FR-5" specs/`).

## 5. Report

Tell the user where the file is, how many requirements it has by priority, and list the open questions and assumptions they need to settle. Suggest `use-case` as the next step once the Must requirements look right.
