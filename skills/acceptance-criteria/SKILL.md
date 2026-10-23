---
name: acceptance-criteria
description: >-
  Write acceptance criteria as Gherkin scenarios (Given / When / Then) for a feature or use case, one scenario per main path and per extension, each tagged with a stable ID (AC-01.1) and traced to its use case (UC-01) and requirements (FR-1), saved as specs/<feature>/acceptance/UC-01-<slug>.feature so they can drive BDD or end-to-end tests. Use this skill whenever the user wants acceptance criteria, Gherkin, BDD scenarios, a definition of done, or says things like "how do we know this feature works", "write the ACs for X", "turn these use cases into test scenarios", or "what should QA check". Also use it to update scenarios after a use case changes. Not for writing the test code or step definitions themselves, unit tests, PRDs or use cases. Takes --path to say where the scenarios go, and --print to return the scenarios without saving them.
argument-hint: "[--path <path>] [--print]"
---

# Acceptance criteria

Your job is to turn use cases into scenarios precise enough that the user, a tester and a test runner would all agree whether the feature passes. Gherkin is the format because it is readable by non-developers and executable by Cucumber, SpecFlow, Behave, Playwright-BDD and similar tools, so the spec and the test can be the same file.

A good scenario fails for exactly one reason. If a scenario can't fail, or could fail for five reasons, it isn't telling anyone anything.

Arguments: `$ARGUMENTS`

- **`--path <path>`**: what to read and where the scenarios go (§1).
- **`--print`**: return the scenarios instead of saving them, for a tool or script that only needs the text (§6).
- Everything else describes the feature or the use cases to cover, even when it contains a `/` (`v2/search` is a feature name, not a path).

## 1. Find the source

Feature files go in an `acceptance/` folder beside the feature's `use-cases/`. Take the first match, in this order:

1. **`--path`.** A `.feature` file is the file to write or update. A use case `.md` is the one source to cover, and its feature file is `../acceptance/<same name>.feature`. A `prd.md` means its whole folder is the feature. An `acceptance/` folder is where the files go. A folder that holds `use-cases/`, `acceptance/` or a `prd.md` is that feature's folder. Any other folder is where feature folders go: `<folder>/<feature-slug>/acceptance/`. Create what doesn't exist yet: the user named the place on purpose.
2. **The feature's specs in the repo.** Look for them (`git ls-files | grep -iE '(^|/)prd\.md$|/use-cases/|\.feature$'`) and write beside them.
3. **`specs/` at the project root**: `$(git rev-parse --show-toplevel)/specs/<feature-slug>/acceptance/`, or the working directory outside a git repo. The root, not the folder you were started in, because the other specs skills look there.

Read the feature's use cases and the PRD they trace to. Scenarios come from use cases:

- The **main success scenario** becomes one scenario.
- Each **extension** (`3a`, `5a`, …) becomes at least one scenario.
- **Success and minimal guarantees** become `Then` steps: the success guarantees on the happy path, the minimal guarantees on every failure path.
If there are no use cases, say so and offer `use-case` first. If the user wants criteria straight from a PRD or a plain description, write them, tag them with the `FR-` IDs you can trace, and leave out the `@UC-` tag rather than inventing one.

If the repo already has `.feature` files, read a few and follow their language, tags and step phrasing, so the new steps reuse existing step definitions instead of needing new ones.

## 2. Write the scenarios

Use the layout in `references/template.md`: one `.feature` file per use case, `specs/<feature>/acceptance/UC-<nn>-<slug>.feature`, matching the use case's file name. Match the step phrasing and coverage of the worked example in `references/example.feature`, which turns the `use-case` skill's example (UC-01, Invite a teammate) into scenarios: every extension covered, a retry split into two scenarios so each has one `When`, and an unanswered open question left without a scenario rather than guessed.

- **Declarative, not imperative.** `When the admin invites "sam@example.com" as a Member`, not `When I click "Invite" And I type "sam@example.com" in "Email"`. UI-driven steps break on every redesign and hide what is being tested.
- **One `When` per scenario.** Several actions in a row mean several behaviors under test; split the scenario, or move the earlier actions into `Given` as state.
- **`Given` is state, not history.** `Given "sam@example.com" is already a member`, not `Given the admin invited Sam and Sam accepted`.
- **`Then` is observable.** Check what a user or an API caller can see (a message, an email, a status), not a database row, so the scenario survives a schema change.
- **Concrete values.** `"sam@example.com"` and `7 days`, not `a valid email` and `the expiry period`. Use a `Scenario Outline` with `Examples` when the same rule holds for several values (every invalid email format), not a copy per value.
- **Name the behavior**: `Scenario: Inviting an existing member is rejected`, not `Scenario: Test 3b`.

## 3. Tag for traceability

Every scenario gets tags on the line above it:

```gherkin
@AC-01.2 @UC-01 @FR-1
Scenario: Inviting an existing member is rejected
```

- `@AC-<nn>.<n>` is the scenario's own ID: the use case number, then a sequence number within it. It is stable: never renumber or reuse one; a removed scenario's number stays retired.
- **When updating, leave existing scenarios as they are.** Add new scenarios for what is missing, and change an existing one only when the use case step it covers has changed, telling the user which one and why. A scenario that already passes is a promise the code keeps; an extra `Then` quietly moves the bar for every test run that relies on it. If you think an existing scenario is too weak, say so in the report instead.
- `@UC-<nn>` and the `@FR-` tags are where it comes from. Test runners can filter on them (`--tags @FR-1`), which is how you answer "is FR-1 tested?".
- Add an `@NFR-` tag when the scenario checks a quality target from `specs/<feature>/nfr.md` marked **Verified by** `Scenario` (a revoked link stops working within 1 minute). Put such a scenario in the file of the use case whose path it exercises.
- Add a comment with the use case step it covers when that isn't obvious from the name: `# UC-01 extension 3b`.

## 4. Check coverage

Compare the scenarios with their source and report:

- Use case extensions with no scenario.
- `Must` requirements with no scenario tagged for them, including `NFR-` requirements verified by `Scenario`.
- Scenarios whose expected result the use case or PRD doesn't specify. Don't settle these by guessing: list them as open questions, since the answer is a product decision.

## 5. Report

Tell the user which files you wrote, how many scenarios each has, and the coverage gaps and open questions from §4. Writing step definitions or test code is a separate task; offer it rather than starting it.

## 6. With `--print`

A tool or a script reads your reply, not a person, so:

- **Save nothing.** Work out the paths as in §1 anyway and read what is there: an existing `.feature` file is still updated with its `AC-` IDs kept (§3).
- **Ask nothing.** Nobody is there to answer. Scenarios whose expected result isn't decided still stay out; put each as a `# Open question: …` comment at the end of its feature file instead of in a report.
- **Reply with the feature files and nothing else**: no preamble, no report, no code fence around them, so the caller can save the output as it is. With more than one, put `# file: <path>` on the line above each, naming the file it would be saved to, so the caller can split them.
