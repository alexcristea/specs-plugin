---
name: acceptance-criteria
description: >-
  Write acceptance criteria as Gherkin scenarios (Given / When / Then) for a feature or use case, one scenario per main path and per extension, each tagged with a stable ID (AC-01.1) and traced to its use case (UC-01) and requirements (FR-1), saved as specs/<feature>/acceptance/UC-01-<slug>.feature so they can drive BDD or end-to-end tests. Use this skill whenever the user wants acceptance criteria, Gherkin, BDD scenarios, a definition of done, or says things like "how do we know this feature works", "write the ACs for X", "turn these use cases into test scenarios", or "what should QA check". Also use it to update scenarios after a use case changes. Not for writing the test code or step definitions themselves, unit tests, PRDs or use cases.
---

# Acceptance criteria

Your job is to turn use cases into scenarios precise enough that the user, a tester and a test runner would all agree whether the feature passes. Gherkin is the format because it is readable by non-developers and executable by Cucumber, SpecFlow, Behave, Playwright-BDD and similar tools, so the spec and the test can be the same file.

A good scenario fails for exactly one reason. If a scenario can't fail, or could fail for five reasons, it isn't telling anyone anything.

## 1. Find the source

Read the use cases in `specs/<feature>/use-cases/` (or wherever the repo keeps specs) and the PRD they trace to. Scenarios come from use cases:

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
