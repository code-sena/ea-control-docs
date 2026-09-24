# ADR-009 — Internal Service Architecture (Hexagonal)

- **ID:** ADR-009
- **Date:** 2026-09-17
- **Status:** Proposed
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl microservices require a consistent internal architecture pattern that promotes testability, maintainability, and separation of concerns. The `05-architecture/hexagonal-architecture.md` document extensively describes the Hexagonal (Ports and Adapters) pattern but lacks a formal ADR documenting the decision to adopt it.

A decision is required now because:
- Developers need clear guidance on code organization within each service
- Testing strategy depends on the ability to isolate business logic from infrastructure
- Consistent architecture across services simplifies onboarding and code reviews

**Known constraints:**
- The team of three needs a pattern that is easy to understand and implement
- Spring Boot ecosystem should be leveraged
- Each microservice must be independently testable
- Infrastructure components (databases, message brokers) may change in the future

---

## Decision

**We decided:** Adopt Hexagonal Architecture (Ports and Adapters) as the internal architecture pattern for all microservices.

**Justification:**
Hexagonal Architecture cleanly separates business logic (domain) from infrastructure concerns (database, messaging, HTTP). This separation:
- Enables unit testing of business logic without infrastructure
- Allows swapping infrastructure components without changing business code
- Aligns with Domain-Driven Design principles already adopted
- Provides clear layer boundaries (domain → application → infrastructure)

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Hexagonal Architecture — chosen | Clear separation, testable, infrastructure-agnostic, DDD-aligned | More initial setup, requires discipline to maintain boundaries | Chosen for long-term maintainability |
| Layered Architecture (traditional) | Simple, well-known, easy to start | Business logic often leaks into infrastructure, harder to test in isolation | Rejected due to testing limitations |
| Clean Architecture | Similar benefits to Hexagonal, more prescriptive | More complex, harder to implement correctly, over-engineered for current needs | Hexagonal is simpler and sufficient |
| Vertical Slice Architecture | Feature-focused, easy to understand | Less infrastructure separation, may lead to code duplication | Not suitable for domain-driven approach |

---

## Consequences

**Positive:**
- Business logic is isolated and independently testable
- Infrastructure can be swapped without affecting business code
- Clear separation of concerns across layers
- Aligns with DDD principles and bounded contexts
- Improves code maintainability and readability

**Negative / Trade-offs:**
- Initial setup requires more boilerplate code
- Developers need training on the pattern
- More files and packages to navigate
- Risk of over-engineering for simple services

**Impact on the system:**
- Affected services: All microservices (ms-security, ms-classroom-management, ms-sensor-management, ms-environment-monitoring, ms-alert, ms-user-experience)
- Documents that must be updated: `05-architecture/hexagonal-architecture.md`, service-specific documentation, coding standards

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Developers bypass architecture layers | Medium | Medium | Code reviews, architecture tests, clear documentation |
| Over-engineering for simple CRUD services | Medium | Low | Allow simpler patterns for infrastructure-only services (e.g., api-gateway) |
| Inconsistent implementation across services | Low | Medium | Shared coding standards, template projects, regular reviews |

---

## References

- Hexagonal Architecture guide: `05-architecture/hexagonal-architecture.md`
- Pattern catalog: `05-architecture/pattern-guide.md`
- Related to: ADR-002 (Microservice Boundaries), ADR-010 (Containerization Strategy)
