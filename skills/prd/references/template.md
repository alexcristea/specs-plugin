# PRD template

Copy this layout into `specs/<feature-slug>/prd.md`. Replace every `<…>` placeholder; delete guidance lines in parentheses.

```markdown
# <Feature name> — PRD

| Status | Owner | Last updated |
|--------|-------|--------------|
| Draft  | <name> | <YYYY-MM-DD> |

## Problem

<Who has what problem, and what it costs them today. Include evidence: tickets, metrics, quotes.>

## Users

| User | Goal |
|------|------|
| <Workspace admin> | <Get a new teammate working without filing an IT ticket> |

## Goals

- <Outcome the feature must achieve, phrased as a change in the world, not a feature.>

## Non-goals

- <Something a reader might reasonably expect that this version will not do, and why.>

## Requirements

### Functional

| ID   | Requirement | Priority |
|------|-------------|----------|
| FR-1 | <An admin can invite a person by email address.> | Must |
| FR-2 | <An invitation expires 7 days after it is sent.> | Should |

### Non-functional

| ID    | Requirement | Priority |
|-------|-------------|----------|
| NFR-1 | <Invitation emails are sent within 60 seconds of the invite.> | Must |

## Success metrics

| Metric | Today | Target | How measured |
|--------|-------|--------|--------------|
| <Median time from invite to first login> | <3 days> | <1 day> | <Product analytics, 30-day window> |

## Assumptions

- <Something treated as true without confirmation. Each one is a risk until confirmed.>

## Open questions

- [ ] <Question> — <who can answer it>

## Change log

| Date | Change |
|------|--------|
| <YYYY-MM-DD> | First draft. |
```

## Priority (MoSCoW)

- **Must**: the release is pointless without it.
- **Should**: important, but the release still works without it.
- **Could**: nice to have; first to go when time runs short.
- **Won't**: explicitly out of this release. Keeping it listed stops it from creeping back in.
