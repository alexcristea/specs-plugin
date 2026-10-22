# Team invites — NFRs

| Field | Value |
|-------|-------|
| Status | Draft |
| Owner | Dana Lee |
| Last updated | 2026-10-22 |
| Traces to | FR-1, FR-2, FR-4, FR-5, FR-6 ([PRD](prd.md#requirements)) |

## Requirements

| ID    | Quality | Requirement | Verified by | Priority |
|-------|---------|-------------|-------------|----------|
| NFR-1 | Performance | 95% of invitation emails arrive within 2 minutes of the invite (FR-1). | Monitoring | Must |
| NFR-2 | Performance | Inviting 50 people at once returns within 5 seconds (FR-5). | Load test | Could |
| NFR-3 | Security | A revoked invitation link stops working within 1 minute (FR-4). | Scenario | Must |
| NFR-4 | Security | An invitation link can't be guessed: fewer than 1 in 10^12 random links is valid (FR-6). | Review | Must |
| NFR-5 | Privacy | Invited email addresses are visible only to admins of that workspace, and are deleted 30 days after an invitation expires (FR-1). | Scenario | Must |
| NFR-6 | Accessibility | The invite and join screens meet WCAG 2.2 AA (FR-1, FR-2). | Review | Should |
| NFR-7 | Usability | 9 in 10 first-time invitees join within 60 seconds of opening the email (FR-2). | Monitoring | Should |

## Inherited

- Workspace availability of 99.9% a month: [Platform NFR-1](../platform/nfr.md#requirements).

## Open questions

- [ ] Do invitations count as personal data under our GDPR retention policy, or only accepted accounts? — Legal
- [ ] Assumed: 2 minutes is fast enough that admins don't resend. — Support
