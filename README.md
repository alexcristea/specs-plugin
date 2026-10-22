# specs

A Claude Code plugin for specs-driven development: write the product specs before the code, and keep every spec traceable to the one before it. It has four skills that chain together: `prd` writes a product requirements document with numbered requirements, `nfr` adds measurable quality targets for them, `use-case` turns the requirements into fully dressed use cases, and `acceptance-criteria` turns the use cases into Gherkin scenarios that can drive tests.

## What this plugin gives you

| Skill                        | Purpose                                                                                       |
|------------------------------|-----------------------------------------------------------------------------------------------|
| `/specs:prd`                 | Write or update a one-page PRD (under 600 words, a 1–2 minute read): one-sentence summary, problem and evidence, goals, non-goals, users, `FR-` requirements with MoSCoW priority, success metrics with a guardrail, risks, open questions. |
| `/specs:nfr`                 | Write one-page non-functional requirements (under 400 words): `NFR-` IDs with a measurable target, the ISO 25010 quality, the `FR-` IDs they apply to, how each is verified (scenario, load test, monitoring, review) and MoSCoW priority. |
| `/specs:use-case`            | Write one-page Cockburn-style use cases (under 400 words): actor, preconditions, guarantees, main success scenario and an extension for each step that can fail, traced to `FR-` IDs. |
| `/specs:acceptance-criteria` | Write Gherkin scenarios for each use case path, tagged `@AC-01.1 @UC-01 @FR-1` (plus `@NFR-3` when a scenario checks a quality target), and report coverage gaps. |

You rarely need the slash commands. The skills trigger on ordinary requests such as "spec out team invites", "what can go wrong when a user resets their password?", "how fast does search need to be?" or "how do we know this feature works?".

## Prerequisites

- [Claude Code](https://docs.claude.com/claude-code)

## Install

From a local clone:

```sh
git clone https://github.com/alexcristea/specs-plugin.git
claude --plugin-dir "$PWD/specs-plugin"
```

## What gets written

```
specs/<feature>/
├── prd.md                                # FR-1, FR-2 …
├── nfr.md                                # NFR-1 (FR-1) …
├── use-cases/
│   └── UC-01-invite-a-teammate.md        # Traces to: FR-1, FR-2
└── acceptance/
    └── UC-01-invite-a-teammate.feature   # @AC-01.1 @UC-01 @FR-1
```

If the repo already keeps specs somewhere else (`docs/specs/`, existing `.feature` files), the skills follow that instead. `specs/` is created at the repo root, even when Claude starts in a subfolder.

## Arguments

Every skill takes the same two optional arguments: `/specs:<skill> [path] [--print]`.

- **`path`** says where the spec goes or what it builds on. A spec file is updated in place (`/specs:prd docs/specs/search/prd.md add a genre filter`). An input file points at its feature (`/specs:use-case docs/specs/search/prd.md` writes `docs/specs/search/use-cases/`). Any other folder holds feature folders (`/specs:prd docs/product team invites` writes `docs/product/team-invites/prd.md`). Without a path, the skill searches the repo, then falls back to `specs/` at the root.
- **`--print`** returns the spec as the reply and saves nothing, for tools and scripts that only need the text: `claude -p "/specs:prd --print team invites" > prd.md`. The skill doesn't ask questions in this mode, so its guesses show up as `Assumed:` open questions. When several files come back, each starts with a marker naming its path (`<!-- file: … -->`, or `# file: …` in `.feature` files).

## What the skills follow

**Every spec traces to the one before it.** Requirements get `FR-` IDs and quality targets `NFR-` IDs, use cases cite the `FR-` IDs and get `UC-` IDs, scenarios get `AC-` IDs and tag both. A test runner can then answer "is FR-1 tested?" with `--tags @FR-1`.

**IDs never change.** New items take the next free number; removed ones are struck through or deprecated, never reused. Downstream specs and tests refer to these IDs, so renumbering would silently break them.

**Gaps become questions, not guesses.** When a use case needs behavior the PRD doesn't specify, or a scenario's expected result isn't decided, the skill lists it as an open question for you instead of inventing an answer.

**Quality targets are numbers.** "Fast" can't fail a check, so every NFR has a measurable target and says how it will be verified. When a target forces a design choice, record that choice as an ADR with your architecture docs and cite the `NFR-` ID as its driver; specs say what and how well, not how.

**What, not how.** Specs describe behavior an actor can observe. Steps are intentions ("admin invites Sam"), not UI clicks or database writes, so they survive a redesign.
