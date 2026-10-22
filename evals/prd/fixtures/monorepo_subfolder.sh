#!/bin/bash
# A monorepo with no specs; Claude is started in packages/web, so the fallback must be specs/ at the repo root.
source "$(dirname "$0")/../../shared/common.sh" "$1"
app
mkdir -p packages/web/src packages/api/src
echo '{ "name": "@shelf/web" }' > packages/web/package.json
echo '{ "name": "@shelf/api" }' > packages/api/package.json
echo '{ "private": true, "workspaces": ["packages/*"] }' > package.json
commit "chore: split into workspaces"
record_state
