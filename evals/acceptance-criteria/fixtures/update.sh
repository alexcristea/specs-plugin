#!/bin/bash
# UC-01 has a feature file covering the main path, 1a and 3a; 3b is uncovered. AC IDs must not move.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
book_swaps_prd docs/specs/book-swaps; book_swaps_use_case docs/specs/book-swaps; book_swaps_feature docs/specs/book-swaps
commit "docs: add specs"
record_state
