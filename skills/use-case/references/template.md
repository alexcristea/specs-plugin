# Use case template

One file per use case: `specs/<feature-slug>/use-cases/UC-<nn>-<slug>.md`. Replace every `<…>` placeholder.

```markdown
# UC-<nn>: <Goal as a short verb phrase, e.g. Invite a teammate>

**Status:** Draft · **Primary actor:** <Workspace admin> · **Supporting actors:** <Email service> · **Level:** User goal · **Traces to:** <FR-1, FR-3>

## Stakeholders and interests

- **<Workspace admin>**: <wants the teammate working today, without a support ticket.>
- **<Invitee>**: <wants to be sure the invite is genuine before following the link.>

## Preconditions

- <What must already be true; the use case doesn't check it. E.g. The admin is signed in.>

## Trigger

<What starts the use case. E.g. The admin chooses to invite someone.>

## Main success scenario

1. <Admin> <gives the person's email address>.
2. <System> <creates a pending invitation that expires in 7 days>.
3. <System> <sends the invitation email>.
4. <System> <shows the invitation as pending>.

## Extensions

- **1a.** <The address is not a valid email>: <System says what is wrong>; resume at step 1.
- **1b.** <The person is already a member>: <System says so and creates nothing>; use case fails.
- **3a.** <The email service is unavailable>: <System keeps the invitation and retries>; resume at step 4.

## Guarantees

- **Minimal:** <true whatever happens. E.g. No invitation exists without a record of the admin who sent it.>
- **Success:** <true on success. E.g. A pending invitation exists and the invitee has been emailed a link to it.>

## Open questions

- [ ] <Behavior a step needs that the PRD doesn't specify.>
```

## Naming

- **Level** is almost always *User goal*. Use *Summary* for a use case that strings several user-goal ones together, and *Subfunction* for a step reused by several (e.g. *Authenticate*); keep both rare.
- Extension numbers point at the step that fails: `3a` is the first thing that can go wrong at step 3. `*a` is an extension that can happen at any step (the actor's session expires).
- An extension that needs more than one step lists them as a nested numbered list under it; keep that for the rare case that can't be said in one line.
