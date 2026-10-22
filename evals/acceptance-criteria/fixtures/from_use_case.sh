#!/bin/bash
# PRD and UC-01 exist with three extensions; no feature files yet.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
book_swaps_prd docs/specs/book-swaps; book_swaps_use_case docs/specs/book-swaps
commit "docs: add specs"
record_state
