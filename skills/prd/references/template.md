# PRD template

Copy this layout into `specs/<feature-slug>/prd.md`. Replace every `<…>` placeholder and delete the guidance in parentheses. The budget in each heading's guidance is a ceiling, not a target.

```markdown
# <Feature name> — PRD

**Status:** Draft · **Owner:** <name> · **Last updated:** <YYYY-MM-DD>

## Summary

<What we are building and for whom, in one sentence. The why goes in Problem.>

## Problem

<Who cannot do what today, and what it costs them. Two to four sentences.>

- <Evidence: a metric, ticket count, quote or research link. One to three bullets.>

## Goals

- <An outcome for users or the business, not a feature. Up to three.>

## Non-goals

- <Something a reader would reasonably expect that this version will not do, and why. Up to three.>

## Users

| User | Needs to |
|------|----------|
| <Workspace admin> | <Get a new teammate working without filing an IT ticket> |

## Requirements

| ID   | Requirement | Priority |
|------|-------------|----------|
| FR-1 | <An admin can invite a person by email address.> | Must |
| FR-2 | <An invitation expires 7 days after it is sent.> | Should |

## Success metrics

| Metric | Today | Target |
|--------|-------|--------|
| <Median time from invite to first login> | <3 days> | <1 day> |
| <Guardrail: support tickets about access> | <40/week> | <No increase> |

## Risks and dependencies

- <What could make this fail, or what it waits on (a team, a service, a decision). Up to three.>

## Open questions

- [ ] <Question> — <who can answer it>
- [ ] Assumed: <something treated as true without confirmation> — <who can confirm it>
```

## Priority (MoSCoW)

- **Must**: the release is pointless without it.
- **Should**: important, but the release still works without it.
- **Could**: nice to have; first to go when time runs short.
- **Won't**: explicitly out of this release. Keeping it listed stops it from creeping back in.
