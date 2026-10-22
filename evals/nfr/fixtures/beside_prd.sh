#!/bin/bash
# The book-swaps PRD exists in docs/specs/; no NFRs yet, so nfr.md goes beside the PRD.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
book_swaps_prd docs/specs/book-swaps
commit "docs: add specs"
record_state
