# 02 — Problem Domain

> The mental model of the business. It is not technology — it is understanding
> the problem the system solves before writing code. This section comes from Domain-Driven Design (DDD).

---

## Documents in this section

| File | Purpose |
|------|---------|
| [domain-map.md](./domain-map.md) | Bounded contexts and their relationships |
| [entities-and-rules.md](./entities-and-rules.md) | Entities, value objects, and business rules |
| [domain-events.md](./domain-events.md) | Events that occur in the domain |

---

## Why this section exists

The most costly mistakes in software are not bugs — they are domain misunderstandings.
When developers do not deeply understand the business:
- They create incorrect abstractions that have to be rewritten
- Names in the code do not match the business's names → permanent confusion
- Microservice boundaries are drawn incorrectly

This section captures domain knowledge **before** designing the architecture.

---

## Key concepts

**Entity:** Domain object with a unique identity (e.g.: a `Student` identified by their code).

**Value Object:** Object with no identity of its own, defined by its attributes (e.g.: `Address`, `Price`).

**Aggregate:** Group of entities treated as a unit. Only the aggregate root can be referenced from outside.

**Domain Event:** Something that occurred in the business that other parts of the system must know (e.g.: `StudentEnrolled`, `PaymentApproved`). They are facts, stated in past tense.

**Bounded Context:** Area of the system where a particular model applies. Each microservice generally corresponds to a bounded context.

---

## Correlations with other sections

| This section feeds... | Why |
|-----------------------|-----|
| `05-architecture/overview.md` | Bounded contexts → microservices |
| `06-data/domain/` | Entities → data tables |
| `07-api/contracts/` | Domain events → events in async APIs |
| `04-requirements/user-stories.md` | Business rules → acceptance criteria |
