#!/bin/bash
# PRD, UC-01 and nfr.md exist; NFR-3 is verified by Scenario and applies to this use case's path.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
book_swaps_prd docs/specs/book-swaps; book_swaps_use_case docs/specs/book-swaps; book_swaps_nfr docs/specs/book-swaps
commit "docs: add specs"
record_state
