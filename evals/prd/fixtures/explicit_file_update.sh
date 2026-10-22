#!/bin/bash
# The user names an existing PRD file and asks to add a requirement and drop another: IDs must not move.
source "$(dirname "$0")/../../shared/common.sh" "$1"
app
mkdir -p docs/specs/search
cat > docs/specs/search/prd.md <<'P'
# Book search — PRD

| Field | Value |
|-------|-------|
| Status | Draft |
| Owner | Priya Shah |
| Last updated | 2026-01-01 |

## Summary

Club members can find a book in the catalog by typing part of its title or author.

## Problem

Members scroll a 4,000-book list to find a title, and many give up and add duplicates instead.

- 31% of books added last quarter were duplicates of an existing entry.

## Goals

- Members find an existing book in seconds instead of adding a duplicate.

## Non-goals

- Recommendations: a separate PRD.

## Users

| User | Needs to |
|------|----------|
| Club member | Find a book before adding it |

## Requirements

| ID   | Requirement | Priority |
|------|-------------|----------|
| FR-1 | A member can search the catalog by part of a book's title. | Must |
| FR-2 | A member can search the catalog by part of an author's name. | Must |
| FR-3 | Search suggests titles as the member types. | Should |
| FR-4 | A search with no results offers to add the book. | Should |

## Success metrics

| Metric | Today | Target |
|--------|-------|--------|
| Share of new books that are duplicates | 31% | Under 5% |
| Guardrail: books added per week | 120 | No decrease |

## Open questions

- [ ] Should search cover the book description too? — Product
P
commit "docs: add search PRD"
record_state
