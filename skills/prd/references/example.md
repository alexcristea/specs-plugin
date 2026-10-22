# Team invites — PRD

**Status:** Draft · **Owner:** Dana Lee · **Last updated:** 2026-10-22

## Summary

Workspace admins can invite teammates to their workspace by email, without going through support.

## Problem

Today only our support team can add someone to a workspace, so admins file a ticket and wait. New teammates sit idle for days, and some teams give up and share one login.

- 38% of support tickets last quarter were access requests (median wait: 3 days).
- 4 of 6 admins we interviewed said they share logins "until IT gets to it".

## Goals

- New teammates can start work on the day they are invited.
- Admins manage access themselves, without contacting support.

## Non-goals

- Single sign-on and SCIM provisioning: enterprise needs, planned separately.
- Custom roles: everyone joins as a member; admins can promote them later.

## Users

| User | Needs to |
|------|----------|
| Workspace admin | Add and remove teammates without filing a ticket |
| Invited teammate | Join the right workspace from an email in under a minute |

## Requirements

| ID   | Requirement | Priority |
|------|-------------|----------|
| FR-1 | An admin can invite a person by email address. | Must |
| FR-2 | An invited person can join by following the link in the invitation email. | Must |
| FR-3 | An invitation expires 7 days after it is sent. | Should |
| FR-4 | An admin can revoke an invitation that has not been accepted. | Should |
| FR-5 | An admin can invite up to 50 people at once by pasting a list. | Could |
| FR-6 | An invitation link works once, and only for the email address it was sent to. | Must |

## Success metrics

| Metric | Today | Target |
|--------|-------|--------|
| Median time from invite to first login | 3 days | Under 1 day |
| Access-request support tickets | 120/month | Under 30/month |
| Guardrail: workspaces with a shared login | 22% | No increase |

## Risks and dependencies

- Invitation emails may land in spam; depends on the email team's sender domain work.
- Admins could invite the wrong address; FR-4 limits the damage.

## Open questions

- [ ] Should inviting someone outside the company's email domain need a second admin? — Security
- [ ] Assumed: every workspace has at least one admin today. — Support
