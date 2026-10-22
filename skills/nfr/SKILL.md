---
name: nfr
description: >-
  Write or update one-page non-functional requirements (NFRs) for a feature or product: quality targets for performance, availability, security, privacy, accessibility, usability and compliance, each with a stable ID (NFR-1), a measurable target, how it is verified and the requirements (FR-1) it applies to, saved as specs/<feature>/nfr.md. Use this skill whenever the user wants NFRs, quality attributes, quality requirements, performance or availability targets, or says things like "how fast does this need to be", "what are the security requirements for X", "what uptime do we need", "does this need to be accessible", or "add the non-functionals", even if they never say "NFR". Also use it to review whether existing quality requirements are measurable. Not for functional requirements or PRDs, architecture decisions or ADRs, SLO dashboards or alert config, load-test scripts, use cases or acceptance criteria. Takes an optional path, and --print to return the NFRs without saving them.
argument-hint: "[path] [--print]"
---

# Non-functional requirements

Your job is to say **how well** the feature has to work, in numbers someone can check. The PRD's `FR-` requirements say what a user can do; an NFR says how fast, how available, how secure or how accessible it has to be while they do it. These are the requirements that shape the architecture, so they need to exist before anyone makes that architecture's decisions.

An NFR without a number can't fail. "The page is fast" passes every review and every release; "95% of searches return in under 300 ms" can be measured, argued about and tested. Turning the adjective into a number is most of the work.

Arguments: `$ARGUMENTS`

- **A path**: the first word, if it contains a `/`, ends in `.md`, or exists. It says where the NFRs go (§1).
- **`--print`**, anywhere: return the NFRs instead of saving them, for a tool or script that only needs the text (§6).
- Anything else describes the feature.

## 1. Find the PRD and existing NFRs

`nfr.md` sits beside the feature's `prd.md`. Take the first match, in this order:

1. **A path in the arguments.** A `prd.md` is the PRD to read, and `nfr.md` goes next to it. Any other `.md` file is the NFR file itself. A folder that holds a `prd.md` or `nfr.md` is that feature's folder. Any other folder is where feature folders go: `<folder>/<feature-slug>/nfr.md`. Create what doesn't exist yet: the user named the place on purpose.
2. **The feature's PRD in the repo.** Look for it (`git ls-files | grep -iE '(^|/)(prd|nfr)\.md$'`) and write beside it. With no PRD for this feature, follow where the repo keeps other specs.
3. **`specs/` at the project root**: `$(git rev-parse --show-toplevel)/specs/<feature-slug>/nfr.md`, or the working directory outside a git repo. The root, not the folder you were started in, because the other specs skills look there.

Read the feature's PRD: NFRs apply to its `FR-` requirements, and its success metrics and risks often hint at quality targets. If there is no PRD, say so and offer `prd` first; if the user wants NFRs anyway, write them and leave the **Traces to** row as `none (no PRD yet)`, with no link.

If the feature's `nfr.md` exists, you are updating it: read it and keep its IDs (see §4). Look for product-wide quality targets too (a `specs/platform/nfr.md`, an SLO doc, a security policy, an accessibility statement). Reference those rather than copying them, so a target changes in one place.

## 2. Find the qualities that matter

Walk the ISO 25010 qualities as a checklist, and keep only the ones where this feature could plausibly let someone down:

- **Performance**: response time, throughput, time until something arrives (an email, a sync).
- **Availability** and **recoverability**: uptime, what happens to in-flight work when a dependency fails.
- **Security** and **privacy**: who can see or do what, how long data is kept, what is logged.
- **Accessibility** and **usability**: a WCAG level, a task completion time.
- **Compatibility**: browsers, devices, API versions it must support.
- **Compliance**: regulations or contracts that impose a rule from outside (GDPR, SOC 2, data residency).

Read the PRD, the repo and the conversation before asking. Then ask about the gaps in one short batch (at most five questions). The user rarely knows the number, so ask for a range or a comparison ("as fast as search is today?") and say what is typical. If they want a draft anyway, propose a number and list it under **Open questions** as `Assumed: …`.

## 3. Write it

Use the layout in `references/template.md`, and match the length and tone of the worked example in `references/example.md`, which continues the `prd` skill's team-invites example. Aim for under 400 words and at most about ten requirements; more usually means product-wide targets that belong in a shared file.

Each requirement should be:

- **Measurable**: a number, a unit and a condition. "95% of invitation emails arrive within 2 minutes", not "emails arrive quickly". A percentile beats an average, because an average hides the slow tail users remember.
- **Scoped**: name the `FR-` requirements it applies to in parentheses, so `acceptance-criteria` can tag scenarios with both IDs. Leave the scope out only when it applies to the whole feature.
- **About the outcome, not the mechanism**: "an invitation link can't be used after it is revoked", not "store tokens in Redis with a TTL". The mechanism is an architecture decision, and naming it here takes that decision away from the people who own it.
- **Verified somehow**: the **Verified by** column says how anyone will know, using one of:
  - `Scenario`: a Gherkin scenario can check it; `acceptance-criteria` tags it `@NFR-n`.
  - `Load test`: needs a load or performance test.
  - `Monitoring`: only measurable in production, over time (uptime, delivery rate).
  - `Review`: checked by a person or an audit (an accessibility audit, a security review).
- **Prioritized** with MoSCoW, like the PRD, so a target can be relaxed deliberately rather than silently missed.

Requirements are numbered `NFR-1`, `NFR-2`, … in their own sequence, separate from `FR-`.

## 4. Keep IDs stable when updating

Scenarios tag these IDs, and architecture decisions cite them as drivers, so:

- Never renumber or reuse a number. New requirements take the next free one.
- A dropped requirement stays, struck through with a reason: `~~NFR-3: …~~ (removed 2026-10-22: covered by platform NFR-2)`.
- When a target changes, tell the user what cites it (`grep -rn "NFR-3" specs/ docs/ architecture/`), since a tighter target can invalidate a design decision. Bump **Last updated**.

## 5. Report

Tell the user where the file is, its word count, how many requirements it has by priority and by **Verified by**, and the open questions and assumptions they need to settle. Measure the word count with `wc -w <file>` rather than estimating it: an estimate drifts, and a file over 400 words needs cutting before you report, not after. Then point to the next steps:

- `acceptance-criteria` for the `Scenario` rows: each becomes a scenario in the `.feature` file of the use case (`UC-`) whose path it checks, with its own `AC-` ID and an `@NFR-` tag beside the `@FR-` one.
- An architecture decision record for any target that forces a design choice (a latency target that rules out a synchronous call, a residency rule that picks a region), citing the `NFR-` IDs as its drivers. Offer it rather than writing it; ADRs belong with the architecture docs, not in `specs/`.

## 6. With `--print`

A tool or a script reads your reply, not a person, so:

- **Save nothing.** Work out the path as in §1 anyway and read what is there: an existing `nfr.md` is still updated with its IDs kept (§4), and you return the updated text.
- **Ask nothing.** Nobody is there to answer. Propose the numbers and list each guess under **Open questions** as `Assumed: …`.
- **Count without saving**: `wc -w <<'EOF'` with the NFRs as the heredoc, and cut if it is over 400.
- **Reply with the NFRs and nothing else**: no preamble, no report, no code fence around them, so the caller can save the output as it is.
