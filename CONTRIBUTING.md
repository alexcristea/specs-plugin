# Contributing

The product here is prompt text. Each skill is a `skills/<name>/SKILL.md` plus the template and example in its `references/` folder, and Claude reads them when the skill triggers. Changing a sentence changes behavior, so a skill change is tested like a code change: unit tests for the structure, evals for what Claude does with it.

## Setup

You need Python 3.9 or later, git, and [Claude Code](https://docs.claude.com/claude-code). There are no dependencies to install.

```sh
python3 -m unittest discover -s tests       # manifest, layout, frontmatter, trace IDs, graders
claude plugin validate .                    # manifest and layout, as CI checks it
claude --plugin-dir /absolute/path/to/repo  # try the skills by hand, from a scratch repo
```

Try the skills from a separate scratch repo, not from this one. This repo's own CLAUDE.md and evals would steer what Claude does.

## Rules for changing a skill

- **The four skills share one contract.** They agree on:
  - the paths under `specs/<feature>/`
  - the ID formats (`FR-n`, `NFR-n`, `UC-nn`, `AC-nn.n`)
  - the `[--path <path>] [--print]` arguments and the order paths are resolved in

  Each skill reads what the one before it wrote, so a change to any of these goes into all four in the same change. `tests/test_skills.py` checks that every skill names each ID prefix and the shared arguments.
- **The rules go in `SKILL.md`, the file layout in `references/template.md`.** Claude loads `SKILL.md` when the skill triggers and reads `references/` only when the skill sends it there. Every file under `references/` must be named in its `SKILL.md`, and every path a skill names must exist. The tests check both.
- **Only the frontmatter `description` decides when a skill triggers.** Write it as `description: >-`, which the tests enforce. It has to turn away near misses, as well as catch real requests:
  - `prd`: not technical design docs or RFCs
  - `nfr`: not ADRs, SLO dashboards or load-test scripts
  - `use-case`: not UML or backlog user stories
  - `acceptance-criteria`: not step definitions or unit tests
- **Explain the reason instead of writing it in capitals.** "Never reuse an ID: scenarios tag these IDs" holds up better than "NEVER reuse IDs", because Claude can apply the reason to cases the rule doesn't name.
- **Eval material never goes under `skills/`.** Claude can read everything in a skill folder at runtime, so a fixture or grader kept there would leak into its answers.
- **Update `README.md` in the same change** when what a user sees changes.

## Evals

Each skill has its evals in `evals/<skill>/`:

| File | What it holds |
|---|---|
| `cases.json` | The cases: a fixture, the prompt the user types, the path the spec should land at, and the names of the checks to apply |
| `fixtures/*.sh` | Builds a fresh git repo for a case, from the helpers in `evals/shared/` |
| `grade.py` | Grades every run by reading its repo and reply |
| `baseline.json` | The last accepted results, with and without the skill |
| `triggers.json` | 10 requests that should trigger the skill and 10 near misses |

Evals call Claude and cost money, so CI doesn't run them. Run them yourself when you change a skill, before the change is merged.

### Behavior evals

Run each case at least 3 times with the skill and 3 times without it. A case the baseline passes just as well tests nothing the skill adds. Each run is a separate Claude session that:

1. Builds its fixture: `bash evals/<skill>/fixtures/<fixture>.sh <run>/repo`.
2. Works in `<run>/repo` as if Claude Code had started there, and gets the case's prompt. Without the skill, the prompt says no such command exists and the text after the command name is the request.
3. Can't ask questions. Where the skill would ask, it drafts.
4. Commits nothing, and writes its final reply to `<run>/notes.md`.

The runs so far were driven by skill-creator, one subagent per run. Run output is gitignored and goes here:

```
.eval-runs/<skill>/iteration-<n>/eval-<id>-<case name>/{with_skill,without_skill}/run-<n>/
├── repo/        # the fixture, as the run left it
├── notes.md     # the reply
└── timing.json  # optional: tokens and duration, for the benchmark
```

Then grade every run in the iteration. The grader writes a `grading.json` beside each `notes.md`:

```sh
python3 evals/<skill>/grade.py .eval-runs/<skill>/iteration-<n>
```

skill-creator's `scripts.aggregate_benchmark` adds the results up into `benchmark.json`.

When a grader gets a run wrong, fix the grader, add a unit test for the case it missed in `tests/test_grade.py`, and regrade. Don't reword a case until it passes; that just tunes the eval to the result. Helpers that every grader uses belong in `evals/shared/grading.py`, and a test stops a grader from keeping its own copy.

### Trigger evals

Run these whenever a `description` changes. Use skill-creator's `run_eval`, started from an empty folder that has its own `.claude/`. It writes a temporary command into the nearest `.claude/commands/`, which would otherwise be `~/.claude`.

```sh
mkdir -p /tmp/triggers/.claude && cd /tmp/triggers
PYTHONPATH=<skill-creator>/skills/skill-creator python3 -m scripts.run_eval \
  --eval-set /abs/path/evals/prd/triggers.json --skill-path /abs/path/skills/prd \
  --num-workers 1 --runs-per-query 2 --timeout 60
```

- **Keep `--num-workers 1`.** Parallel workers write near-identical copies of the skill side by side, and Claude picking another worker's copy is scored as a miss.
- **Check before trusting a round of all misses.** If the usage limit runs out mid-run, every call after it returns no tool call, which scores as a miss.

### Baselines

When a skill change is accepted, update `evals/<skill>/baseline.json` in the same change:
- the skill's commit SHA, the model and the date
- the pass rates with and without the skill, or the trigger score
- a note on what the baseline gets wrong, or what changed since the last baseline

A drop against the recorded baseline is what tells the next contributor that a change made something worse.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) with `specs` as the scope. For example:

- `feat(specs): …` for a new skill behavior
- `fix(specs): …` for a skill that did the wrong thing
- `test(specs): …` for tests, evals and baselines
- `refactor(specs): …` for graders and helpers that grade the same afterwards

Put the eval results that justify a skill change in the commit body: the pass rates with and without the skill, and the run count.
