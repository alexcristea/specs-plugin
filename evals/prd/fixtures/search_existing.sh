#!/bin/bash
# The repo already keeps PRDs in docs/specs/<feature>/; no argument, so a new PRD must follow that.
source "$(dirname "$0")/../../shared/common.sh" "$1"
app
mkdir -p docs/specs/club-voting
cat > docs/specs/club-voting/prd.md <<'P'
# Club voting — PRD

| Field | Value |
|-------|-------|
| Status | Approved |
| Owner | Priya Shah |
| Last updated | 2026-01-01 |

## Summary

Club members vote on which saved book the club reads next.

## Requirements

| ID   | Requirement | Priority |
|------|-------------|----------|
| FR-1 | A member can vote for one book per round. | Must |
| FR-2 | The organizer can close a round and see the winner. | Must |
P
commit "docs: add club voting PRD"
record_state
