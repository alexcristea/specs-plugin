#!/bin/bash
# A monorepo with no specs; Claude starts in packages/web, so use cases go to specs/ at the root with no FR- IDs.
SHARED="$(cd "$(dirname "$0")/../../shared" && pwd)"
source "$SHARED/common.sh" "$1"; source "$SHARED/specs.sh"
app
mkdir -p packages/web packages/api; echo "{}" > packages/web/package.json; echo "{}" > packages/api/package.json
commit "docs: add specs"
record_state
