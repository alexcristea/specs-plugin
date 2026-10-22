# Use case template

One file per use case: `specs/<feature-slug>/use-cases/UC-<nn>-<slug>.md`. Replace every `<…>` placeholder.

```markdown
# UC-<nn>: <Goal as a short verb phrase, e.g. Invite a teammate>

| Field | Value |
|-------|-------|
| Status | Draft |
| Primary actor | <Workspace admin> |
| Supporting actors | <Email service> |
| Level | User goal |
| Traces to | <FR-1, FR-2, NFR-1> |

## Stakeholders and interests

- **<Workspace admin>**: <wants the teammate working today, without an IT ticket.>
- **<Invitee>**: <wants to be sure the invite is genuine before clicking it.>

## Preconditions

- <What must already be true; the use case doesn't check it. E.g. The admin is signed in.>

## Trigger

<What starts the use case. E.g. The admin chooses to invite someone.>

## Main success scenario

1. <Admin> <asks to invite a person>.
2. <System> <asks for the person's email address and role>.
3. <Admin> <enters the email address and chooses a role>.
4. <System> <creates a pending invitation valid for 7 days>.
5. <System> <sends the invitation email>.
6. <System> <shows the invitation as pending>.

## Extensions

- **3a.** <The email address is not valid>:
  1. <System> <says what is wrong with the address>.
  2. Resume at step 3.
- **3b.** <The person is already a member>:
  1. <System> <says so and does not create an invitation>.
  2. Use case ends in failure.
- **5a.** <The email service is unavailable>:
  1. <System> <keeps the invitation and retries sending>.
  2. Resume at step 6, showing the invitation as "sending".

## Minimal guarantees

- <True whatever happens. E.g. No invitation exists without a recorded inviting admin.>

## Success guarantees

- <True on success. E.g. A pending invitation exists and the invitee has been emailed a link to it.>

## Open questions

- [ ] <Behavior a step needs that the PRD doesn't specify.>
```

## Naming

- **Level** is almost always *User goal*. Use *Summary* for a use case that strings several user-goal ones together, and *Subfunction* for a step reused by several (e.g. *Authenticate*); keep both rare.
- Extension numbers point at the step that fails: `3a` is the first thing that can go wrong at step 3. `*a` is an extension that can happen at any step (the actor's session expires).
