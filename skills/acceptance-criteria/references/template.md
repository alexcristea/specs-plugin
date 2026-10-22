# Acceptance criteria template

One file per use case: `specs/<feature-slug>/acceptance/UC-<nn>-<slug>.feature`. Replace every `<…>` placeholder.

```gherkin
# Source: specs/<feature-slug>/use-cases/UC-<nn>-<slug>.md
@UC-<nn>
Feature: <Use case goal, e.g. Invite a teammate>
  As a <workspace admin>
  I want to <invite a person by email>
  So that <they can start working without an IT ticket>

  Background:
    Given <the admin "ana@example.com" is signed in to workspace "Acme">

  # Main success scenario
  @AC-<nn>.1 @FR-1 @FR-2
  Scenario: <Admin invites a new teammate>
    When <the admin invites "sam@example.com" as a Member>
    Then <"sam@example.com" receives an invitation email>
    And <the invitation is shown as pending>
    And <the invitation expires in 7 days>

  # Extension 3a
  @AC-<nn>.2 @FR-1
  Scenario Outline: <An invalid email address is rejected>
    When <the admin invites "<email>" as a Member>
    Then <the admin is told "<message>">
    And <no invitation is created>

    Examples:
      | email           | message                           |
      | sam@            | Enter a complete email address    |
      | sam example.com | Email addresses can't have spaces |

  # Extension 3b
  @AC-<nn>.3 @FR-1
  Scenario: <Inviting an existing member is rejected>
    Given <"sam@example.com" is already a member of "Acme">
    When <the admin invites "sam@example.com" as a Member>
    Then <the admin is told "sam@example.com is already a member">
    And <no invitation is created>
```

## Notes

- **Background** holds the `Given` steps shared by every scenario in the file. Keep it short; if only some scenarios need a step, it doesn't belong there.
- The **Feature** description (As a / I want / So that) is taken from the use case's primary actor, goal and stakeholder interest.
- The minimal guarantees of the use case (here: *no invitation is created*) appear as a `Then` on every failure scenario, because a failure that leaves partial state behind is a bug even when the error message is right.
