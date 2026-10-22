# NFR template

Copy this layout into `specs/<feature-slug>/nfr.md`, next to `prd.md`. Replace every `<…>` placeholder and delete the guidance in parentheses.

```markdown
# <Feature name> — NFRs

| Field | Value |
|-------|-------|
| Status | Draft |
| Owner | <name> |
| Last updated | <YYYY-MM-DD> |
| Traces to | <FR-1, FR-2> ([PRD](prd.md#requirements)) |

## Requirements

| ID    | Quality | Requirement | Verified by | Priority |
|-------|---------|-------------|-------------|----------|
| NFR-1 | <Performance> | <95% of invitation emails arrive within 2 minutes of the invite (FR-1).> | <Monitoring> | <Must> |
| NFR-2 | <Accessibility> | <The invite and join screens meet WCAG 2.2 AA (FR-1, FR-2).> | <Review> | <Should> |

## Inherited

- <A product-wide target this feature must also meet, linked rather than copied: [Platform NFR-2](../platform/nfr.md#requirements). Delete the section if there are none.>

## Open questions

- [ ] <Question> — <who can answer it>
- [ ] Assumed: <a target proposed without confirmation> — <who can confirm it>
```

## Quality

Use the ISO 25010 names so the same quality reads the same across features: Performance, Availability, Recoverability, Security, Privacy, Accessibility, Usability, Compatibility, Compliance.

## Verified by

- **Scenario**: a Gherkin scenario checks it, tagged `@NFR-n`.
- **Load test**: a load or performance test checks it.
- **Monitoring**: measured in production over time.
- **Review**: a person or an audit checks it.
