# Upstream specs for the book-swaps feature, so each downstream skill has something to build on.
# usage (after common.sh): book_swaps_prd <dir>; book_swaps_use_case <dir>; book_swaps_nfr <dir>; book_swaps_feature <dir>
book_swaps_prd() {
  mkdir -p "$1"
  cat > "$1/prd.md" <<'P'
# Book swaps — PRD

| Field | Value |
|-------|-------|
| Status | Approved |
| Owner | Priya Shah |
| Last updated | 2026-01-01 |

## Summary

Club members lend their physical books to each other through Shelf instead of a group chat.

## Problem

Members coordinate lending in a group chat, so nobody knows who has which book and copies go missing.

- 14 of 40 members surveyed have lost a lent book in the last year.

## Goals

- Every lent book has a known borrower until it comes back.

## Non-goals

- Shipping books by post: swaps happen in person at meetings.

## Users

| User | Needs to |
|------|----------|
| Owner | Lend a book and know when it comes back |
| Borrower | Find a book in the club and borrow it |

## Requirements

| ID   | Requirement | Priority |
|------|-------------|----------|
| FR-1 | A member can list a physical book they are willing to lend. | Must |
| FR-2 | A member can request to borrow a listed book. | Must |
| FR-3 | The owner can accept or decline a borrow request. | Must |
| FR-4 | The owner can mark a lent book as returned. | Must |
| FR-5 | A member can see which of their books are out and who has them. | Should |
| FR-6 | The owner gets a reminder when a book has been out for 30 days. | Could |

## Success metrics

| Metric | Today | Target |
|--------|-------|--------|
| Lent books reported lost per quarter | 9 | Under 2 |
| Guardrail: books listed for lending | 0 | At least 100 in the first month |

## Open questions

- [ ] Can a member lend to someone outside the club? — Product
P
}
book_swaps_use_case() {
  mkdir -p "$1/use-cases"
  cat > "$1/use-cases/UC-01-borrow-a-book.md" <<'P'
# UC-01: Borrow a book

| Field | Value |
|-------|-------|
| Status | Draft |
| Primary actor | Borrower |
| Supporting actors | Owner |
| Level | User goal |
| Traces to | FR-2, FR-3 ([PRD](../prd.md#requirements)) |

## Stakeholders and interests

- **Borrower**: wants the book before the next meeting.
- **Owner**: wants to know who has the book.

## Preconditions

- The borrower and the owner are members of the same club.

## Trigger

The borrower chooses a listed book.

## Main success scenario

1. Borrower asks to borrow the book.
2. System sends the request to the owner.
3. Owner accepts the request.
4. System records the book as lent to the borrower and tells the borrower.

## Extensions

- **1a.** The book is already lent: System says who has it and since when; use case fails.
- **3a.** The owner declines: System tells the borrower; use case fails.
- **3b.** The owner doesn't answer within 7 days: System cancels the request and tells the borrower; use case fails.

## Guarantees

- **Minimal:** a book is never recorded as lent to two members at once.
- **Success:** the book is recorded as lent to the borrower, and both members can see it.
P
}
book_swaps_nfr() {
  cat > "$1/nfr.md" <<'P'
# Book swaps — NFRs

| Field | Value |
|-------|-------|
| Status | Draft |
| Owner | Priya Shah |
| Last updated | 2026-01-01 |
| Traces to | FR-2, FR-3, FR-5 ([PRD](prd.md#requirements)) |

## Requirements

| ID    | Quality | Requirement | Verified by | Priority |
|-------|---------|-------------|-------------|----------|
| NFR-1 | Performance | 95% of borrow requests reach the owner within 5 minutes (FR-2). | Monitoring | Must |
| NFR-2 | Availability | Lending is available 99.5% of each month (FR-2, FR-3). | Monitoring | Should |
| NFR-3 | Privacy | Only the owner and the borrower can see who has a lent book (FR-5). | Scenario | Must |
P
}
book_swaps_feature() {
  mkdir -p "$1/acceptance"
  cat > "$1/acceptance/UC-01-borrow-a-book.feature" <<'P'
# Source: docs/specs/book-swaps/use-cases/UC-01-borrow-a-book.md
@UC-01
Feature: Borrow a book
  As a club member
  I want to borrow a book another member listed
  So that I can read it before the next meeting

  Background:
    Given "maya@example.com" has listed "Piranesi" for lending

  # Main success scenario
  @AC-01.1 @FR-2 @FR-3
  Scenario: A member borrows a listed book
    Given "leo@example.com" has asked to borrow "Piranesi"
    When "maya@example.com" accepts the request
    Then "Piranesi" is shown as lent to "leo@example.com"
    And "leo@example.com" is told the request was accepted

  # Extension 1a
  @AC-01.2 @FR-2
  Scenario: Asking for a book that is already lent is refused
    Given "Piranesi" is lent to "kim@example.com" since 2026-01-01
    When "leo@example.com" asks to borrow "Piranesi"
    Then "leo@example.com" is told "Piranesi" is lent to "kim@example.com" since 2026-01-01
    And no request for "Piranesi" is sent to "maya@example.com"

  # Extension 3a
  @AC-01.3 @FR-3
  Scenario: A declined request leaves the book with its owner
    Given "leo@example.com" has asked to borrow "Piranesi"
    When "maya@example.com" declines the request
    Then "leo@example.com" is told the request was declined
    And "Piranesi" is not shown as lent
P
}
