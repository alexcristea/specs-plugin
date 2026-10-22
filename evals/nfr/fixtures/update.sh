#!/bin/bash
# An nfr.md with NFR-1..3 exists; the user tightens one target and drops another: IDs must not move.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
book_swaps_prd docs/specs/book-swaps; book_swaps_nfr docs/specs/book-swaps
commit "docs: add specs"
record_state
