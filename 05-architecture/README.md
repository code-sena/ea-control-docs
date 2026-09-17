# 05 — Architecture

> The system's design decisions: how it is organized, why, what alternatives
> were evaluated, and how it is deployed. ADRs are the treasure of this section.

---

## Documents in this section

| File | Purpose |
|------|---------|
| [overview.md](./overview.md) | C4 diagrams, microservice catalog, communication patterns |
| [hexagonal-architecture.md](./hexagonal-architecture.md) | Hexagonal architecture guide and folder structure |
| [pattern-guide.md](./pattern-guide.md) | Design patterns used in the project |
| [decisions/](./decisions/) | Architecture Decision Records (ADRs) |

---

## Why this section exists

A system's architecture is the set of decisions that are hard to change later.
Documenting them has three benefits:
1. **New team members** understand the system without having to ask everything from scratch
2. **The team** does not repeat already-resolved discussions
3. **Years later**, everyone remembers why each decision was made

---

## Architecture Decision Records (ADRs)

An ADR records ONE important architectural decision: what was decided, why, what alternatives
were evaluated, and what the consequences are.

**When to create an ADR:**
- Choosing a message broker (RabbitMQ vs Kafka vs Redis Streams)
- Database strategy (one per service vs shared)
- Communication pattern (REST vs gRPC vs events)
- Authentication library
- Any decision that, if changed, requires significant refactoring

### ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Documentation Language | Accepted |
| ADR-002 | Bounded Contexts and Microservice Boundaries | Accepted |
| ADR-003 | Database Strategy | Accepted |
| ADR-004 | Communication Patterns Between Components | Accepted |
| ADR-005 | API Gateway as the External Backend Entry Point | Accepted |
| ADR-006 | JWT Authentication and Service-Level RBAC | Accepted |
| ADR-007 | At-Least-Once Events with Transactional Outbox | Accepted |
| ADR-008 | Database Migration Tool (Liquibase) | Proposed |
| ADR-009 | Internal Service Architecture (Hexagonal) | Proposed |
| ADR-010 | Containerization Strategy (Docker) | Proposed |
| ADR-011 | Production Deployment Strategy | Proposed |
| ADR-012 | Observability Stack | Proposed |
| ADR-013 | Circuit Breaker Adoption | Proposed |
| ADR-014 | Environmental Sensor Variables and Thresholds | Proposed |

---

## Correlations with other sections

| This section is fed by... | And feeds... |
|--------------------------|-------------|
| `02-domain/domain-map.md` → bounded contexts | `09-microservices/` → one service per context |
| `04-requirements/non-functional.md` → NFRs | Decisions about technology and scale |
| ADRs chosen here | `09-microservices/` implements the decided patterns |
