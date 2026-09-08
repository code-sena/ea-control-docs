# ADR-NNN — [Decision Title]

> **Copy this file** to `records/ADR-NNN-short-title.md`
> Replace NNN with the sequential number (001, 002, 003...)

- **ID:** ADR-001
- **Date:** 2026-09-08
- **Status:**  Accepted 
- **Authors:** team eduaircontrol

---

## Context

> Describe the problem or situation that requires a decision.
> Why is it important to decide this now? What happens if it is not decided?

EduAirControl requires separating the system's core functionalities to facilitate development, maintenance, and evolution. The project must handle authentication, users, classrooms, sensors, and environmental monitoring without concentrating all logic within a single application.

Failure to define an architecture from the outset could lead to tight coupling between modules, difficulties in making changes, and issues scaling specific functionalities.

**Known constraints:**

- The project is being developed using Java and Spring Boot.
- The frontend uses React.
- Integration with environmental sensors is required.
- The project uses Docker.
- The team has limited resources and development time.
- A single PostgreSQL infrastructure is used, logically organized by domain.

---

## Decision

> One sentence that clearly describes what is being decided.

**We decided:** to implement the microservices `ms-security`, `ms-usuarios`, `ms-aulas`, `ms-sensores`, and `ms-monitoreo`, using Spring Cloud Gateway as the entry point to the backend.

**Justification:**
This option allows for the separation of responsibilities by domain, facilitates maintenance, and enables each service to evolve independently. The deciding factor was the **separation of responsibilities and system maintainability**.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Microservices + API Gateway — chosen | Domain separation, maintainability, independent scalability | Increased configuration and communication complexity | — (chosen) | | Modular monolith | Lower initial complexity, simpler development | Higher coupling and lower independence between modules | Discarded due to the need to separate core domains |
| Microservices without API Gateway | Independent services, lower initial infrastructure | No central point for routing and controlling requests | Discarded because a centralized entry point is required |

---

## Consequences

- Clear separation of responsibilities.
- Easier maintenance and evolution of each domain.

**Negative / Trade-offs:**

- Increased complexity in communication and configuration.
- Requires managing multiple services and containers.

**Impact on the system:**

- Affected services: `ms-security`, `ms-usuarios`, `ms-aulas`, `ms-sensores`, `ms-monitoreo`, API Gateway, and Frontend.
- Documents requiring updates: Architecture documentation, domain map, and architecture diagrams.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Complexity in inter-service communication | Medium | High | Define REST contracts and clear responsibilities |
| Microservice failure | Medium | High | Implement health checks and recovery mechanisms |
| Inconsistent configuration across services | Medium | Medium | Centralize configuration using environment variables and Docker |

---

## References

- Official Spring Boot and Spring Cloud documentation.
- EduAirControl architecture documentation.
- Related to: ADR-002