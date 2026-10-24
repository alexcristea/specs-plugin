#!/bin/bash
# An nfr.md with NFR-1..3 exists, and an ADR cites NFR-1 as its driver. The user tightens NFR-1, drops NFR-2
# and asks for a vague new one: IDs must not move, the new one needs a number, and the ADR is at risk.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
book_swaps_prd docs/specs/book-swaps; book_swaps_nfr docs/specs/book-swaps
mkdir -p docs/architecture/decisions
cat > docs/architecture/decisions/0004-batch-borrow-notifications.md <<'A'
# 4. Send borrow notifications in 5-minute batches

Date: 2026-01-01

## Status

Accepted

## Context

NFR-1 gives a borrow request 5 minutes to reach the owner. Sending one email per request would
cost more than the club's mail plan allows at meeting-night peaks.

## Decision

Collect borrow requests and send each owner one notification every 5 minutes.

## Consequences

Owners hear about a request up to 5 minutes late, which NFR-1 allows.
A
commit "docs: add specs"
record_state
