# Source: specs/team-invites/use-cases/UC-01-invite-a-teammate.md
@UC-01
Feature: Invite a teammate
  As a workspace admin
  I want to invite a person by email address
  So that they can start work without a support ticket

  Background:
    Given the admin "ana@example.com" is signed in to workspace "Acme"

  # Main success scenario
  @AC-01.1 @FR-1 @FR-3
  Scenario: Admin invites a new teammate
    When the admin invites "sam@example.com"
    Then "sam@example.com" receives an invitation email to join "Acme"
    And the invitation to "sam@example.com" is shown as pending, sent by "ana@example.com"
    And the invitation expires in 7 days

  # Extension 1a
  @AC-01.2 @FR-1
  Scenario Outline: An invalid email address is rejected
    When the admin invites "<email>"
    Then the admin is told the email address is not valid
    And no invitation to "<email>" exists

    Examples:
      | email           |
      | sam@            |
      | sam example.com |
      | @example.com    |

  # Extension 1b: one extension, two starting states, so two scenarios
  @AC-01.3 @FR-1
  Scenario: Inviting an existing member is rejected
    Given "sam@example.com" is a member of "Acme"
    When the admin invites "sam@example.com"
    Then the admin is told "sam@example.com" is already a member
    And no invitation to "sam@example.com" exists

  # Extension 1b
  @AC-01.4 @FR-1
  Scenario: Inviting someone twice is rejected
    Given "sam@example.com" has a pending invitation to "Acme"
    When the admin invites "sam@example.com"
    Then the admin is told "sam@example.com" is already invited
    And "sam@example.com" has exactly one pending invitation

  # Extension 3a
  @AC-01.5 @FR-1
  Scenario: The invitation is kept while the email service is down
    Given the email service is unavailable
    When the admin invites "sam@example.com"
    Then the invitation to "sam@example.com" is shown as "sending"

  # Extension 3a: the retry, with the earlier invite moved into Given as state
  @AC-01.6 @FR-1
  Scenario: A waiting invitation is sent once the email service recovers
    Given the invitation to "sam@example.com" is shown as "sending"
    When the email service becomes available
    Then "sam@example.com" receives an invitation email to join "Acme"
    And the invitation to "sam@example.com" is shown as pending

  # Not covered: how long to retry before telling the admin the email failed.
  # UC-01 leaves it as an open question, so there is no scenario until it is answered.
