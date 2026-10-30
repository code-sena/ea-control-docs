# ADR-001 — Documentation Language

| Field | Value |
|-------|-------|
| **ID** | ADR-001 |
| **Date** | 2026-09-08 |
| **Status** | Accepted |
| **Authors** | EduAirControl Development Team |
| **Reviewers** | Development team |

---

## Context


EduAirControl is developed using technologies and frameworks whose official documentation, libraries, technical references, and development tools are primarily available in English. Using different languages across code, documentation, commits, and technical artifacts can create inconsistencies in terminology and make maintenance and collaboration more difficult

A single language standard is required to maintain consistency throughout the project

---

## Evaluated alternatives

### Alternative A — Everything in English (CHOSEN)
- **Pros:** Consistent with programming languages, frameworks, libraries, technical documentation, GitHub, and development tools.
- **Cons:** Some team members may require additional effort when writing or understanding technical content in English

### Alternative B — Everything in Spanish

- **Pros:** Easier communication for Spanish-speaking team members
- **Cons:** Inconsistent with programming conventions and most technical documentation and libraries

### Alternative C — Split by layer (discarded)

- **Pros:** Allows each artifact to use the language most comfortable for its audience
- **Cons:** Creates inconsistent terminology between code and documentation and makes project conventions harder to maintain

---

## Decision

**Alternative A:** Use English as the standard language for code and technical documentation, while supporting four user interface languages through i18n.

| Artifact | Language | Reason |
|----------|----------|--------|
| Variables, functions, and classes | English | Consistency with programming conventions |
| Database tables and columns | English | Coherence with backend code |
| Commits | English | Consistency with Git conventions |
| Git branch names | English | Standardized project naming |
| Markdown documentation | English | Consistent technical documentation |
| ADRs and technical documentation | English | Single technical language |
| OpenAPI contracts | English | Easier understanding for contributors |
| System logs | English | Easier troubleshooting |
| User interface | Spanish, English, Portuguese, French | Internationalization through i18n |
| User-facing messages | Spanish, English, Portuguese, French | Adaptation to the selected user language |

### Supported languages

- **Spanish (`es`)** — Default language
- **English (`en`)**
- **Portuguese (`pt`)**
- **French (`fr`)**

The frontend will use **i18n** to manage translations and allow the user to select the preferred language.

## Consequences

**Positive:**

- Consistent terminology throughout the project.
- Easier maintenance and collaboration.
- Better alignment with technical documentation and development tools.
- Easier integration of future contributors.

**Negative:**

- Team members with limited English proficiency may require additional effort.
- Some business terms may require careful translation.

**Mitigation:**

- Maintain a domain glossary with the canonical English terminology.
- Define ambiguous terms before using them in code or documentation.

---

## References

- Team documentation conventions → `00-governance/documentation-rules.md`
- Domain term glossary → `01-context/glossary.md`
