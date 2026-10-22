# usage: source common.sh <repo_path>
set -e
REPO="$(mkdir -p "$(dirname "$1")" && cd "$(dirname "$1")" && pwd)/$(basename "$1")"; rm -rf "$REPO"; mkdir -p "$REPO"; cd "$REPO"
git init -q -b main
git config user.name "Test User"; git config user.email "test@example.com"
git config commit.gpgsign false
# a small web app whose README names its stack, so a PRD that leaks implementation detail has words to borrow
app() {
  mkdir -p src
  cat > README.md <<'R'
# Shelf

A reading-list app for book clubs. Members save books, rate them and vote on the next club read.

Stack: React front end, Node API, Postgres, Elasticsearch for search, Redis for sessions.
R
  echo 'export const App = () => null;' > src/app.js
}
commit() { git add -A; GIT_AUTHOR_DATE="2026-01-01T10:00:00" GIT_COMMITTER_DATE="2026-01-01T10:00:00" git commit -q -m "$1"; }
# record HEAD once the fixture is built, so the grader can tell what the agent changed
record_state() { git config fixture.head "$(git rev-parse HEAD)"; }
