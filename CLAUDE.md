# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`specs` is a Claude Code plugin for specs-driven development. There is no build step and no application code: the product is prompt text in `skills/<name>/SKILL.md` (plus `references/`), and the manifest is `.claude-plugin/plugin.json`. There are four skills that form a chain: `prd` (`/specs:prd`) → `use-case` (`/specs:use-case`) → `acceptance-criteria` (`/specs:acceptance-criteria`), with `nfr` (`/specs:nfr`) beside `prd` adding quality targets that scenarios can tag.

## Layout rules that aren't obvious

- **The skills share one contract.** Specs go to `specs/<feature>/` (`prd.md`, `nfr.md`, `use-cases/UC-nn-<slug>.md`, `acceptance/UC-nn-<slug>.feature`), and IDs flow `FR-n` → `UC-nn` → `AC-nn.n`, with `NFR-n` scoped to `FR-` IDs and tagged on scenarios. Every skill takes `[--path <path>] [--print]` and resolves the path the same way (`--path`, then repo search, then `specs/` at the git root). Changing a path, ID format or argument in one skill means changing all four; `tests/` checks every skill mentions each ID prefix and the shared arguments. Evals live in `evals/<skill>/` (run with subagents, graded by `grade.py`); run output goes to the gitignored `.eval-runs/`.
- **Rules go in `SKILL.md`, the file layout in `references/template.md`.** `SKILL.md` is loaded when the skill triggers; `references/` is read on demand. Every file under `references/` must be named in its `SKILL.md`, and every path named must exist (tests enforce both).
- **Only the frontmatter `description` drives triggering.** Write it as `description: >-` (tests enforce this). Near misses must not trigger: technical design docs and RFCs (not `prd`), ADRs, SLO dashboards and load-test scripts (not `nfr`), UML and backlog user stories (not `use-case`), step definitions and unit tests (not `acceptance-criteria`).
- **Eval material never goes under `skills/`.** Claude can read everything in a skill folder at runtime.
- Explain the reason behind a rule instead of writing it in capitals.

## Commands

```sh
python3 -m unittest discover -s tests       # manifest, layout, frontmatter, trace IDs
claude plugin validate .                    # manifest and layout
claude --plugin-dir /absolute/path/to/repo  # try it by hand, from a scratch repo
```

CI (`.github/workflows/ci.yml`) runs the tests on Ubuntu and macOS plus `claude plugin validate .`.

## Workflow conventions

- TDD: add a failing test (or eval, once `evals/` exists) before changing behavior.
- Update `README.md` in the same change when behavior changes.
- Commits use Conventional Commits with `specs` as the scope.
