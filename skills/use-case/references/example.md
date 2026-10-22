# UC-01: Invite a teammate

| Field | Value |
|-------|-------|
| Status | Draft |
| Primary actor | Workspace admin |
| Supporting actors | Email service |
| Level | User goal |
| Traces to | FR-1, FR-3 |

## Stakeholders and interests

- **Workspace admin**: wants the teammate working today, without a support ticket.
- **Invitee**: wants to be sure the invite is genuine before following the link.

## Preconditions

- The admin is signed in to the workspace.

## Trigger

The admin chooses to invite someone.

## Main success scenario

1. Admin gives the person's email address.
2. System creates a pending invitation that expires in 7 days.
3. System sends the invitation email.
4. System shows the invitation as pending.

## Extensions

- **1a.** The address is not a valid email: System says what is wrong; resume at step 1.
- **1b.** The person is already a member or already invited: System says so and creates nothing; use case fails.
- **3a.** The email service is unavailable: System keeps the invitation and retries; resume at step 4, showing it as "sending".

## Guarantees

- **Minimal:** no invitation exists without a record of the admin who sent it.
- **Success:** a pending invitation exists and the invitee has been emailed a link to it.

## Open questions

- [ ] How long should the system retry before telling the admin the email could not be sent?
