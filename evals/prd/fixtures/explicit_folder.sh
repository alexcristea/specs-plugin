#!/bin/bash
# No specs anywhere; the user names a folder that doesn't exist yet, so the PRD goes in a feature folder under it.
source "$(dirname "$0")/../../shared/common.sh" "$1"
app
commit "feat: initial app"
record_state
