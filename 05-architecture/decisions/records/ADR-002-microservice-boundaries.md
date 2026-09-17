# ADR-002 — Bounded Contexts and Microservice Boundaries

- **ID:** ADR-002
- **Date:** 2026-09-09
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl identifies the bounded contexts User Management, Environmental Monitoring, and Environmental Data Analysis. The current architecture lists ms-security, ms-usuarios, ms-aulas, ms-sensores, ms-monitoreo, ms-alert, and ms-user-experience, but the mapping between domain boundaries and deployable services is not yet explicit.

A decision is required before implementation continues because service boundaries determine ownership, APIs, data access, deployment units, and team responsibilities. Without an agreed decomposition, functionality may be duplicated or services may become tightly coupled.

**Known constraints:**
- The MVP is developed by a team of three people.
- The project already targets Spring Boot microservices and Docker.
- The current bounded contexts and user stories are the source of the initial decomposition.
- The initial scope does not require independent scaling of every small capability.

---

## Decision

**We decided:** Adopt domain-oriented microservice boundaries based on bounded contexts, with ms-security for authentication and authorization, ms-usuarios for user management, ms-aulas for educational environments, ms-sensores for sensor management and ingestion, ms-monitoreo for environmental measurements, historical analysis, and dashboard queries, ms-alert for alert generation and management, and ms-user-experience for user preferences and experience management.

api-gateway and the React frontend are platform containers, not domain bounded contexts. ms-monitoreo initially owns both Environmental Monitoring and Environmental Data Analysis because the current team size and MVP scope do not justify deploying a separate analysis service. ms-alert and ms-user-experience are added as specialized services to handle alerting logic and user experience features independently.

**Justification:**
The decision preserves domain ownership while avoiding excessive fragmentation. The monitoring and analysis capabilities share the same environmental data flow and are currently assigned to the same service in the requirements and traceability matrix. A future split is allowed if independent scaling, deployment cadence, or domain complexity justifies it.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Domain-oriented services with monitoring and analysis together — chosen | Clear ownership; manageable for a three-person team; matches current backlog | ms-monitoreo has a broad responsibility | Chosen for the MVP |
| One service per bounded context, including a separate analysis service | Maximum conceptual separation; independent scaling | More deployment, testing, and operational overhead | overhead
Discarded for the MVP due to team size and shared data flow |
| One monolith | Lowest initial operational complexity | High coupling; weaker independent evolution; conflicts with the adopted architecture | Discarded because the project already targets microservices and bounded contexts |

---

## Consequences

**Positive:**
- Each service has an explicit business responsibility and data owner.
- The decomposition is traceable to the domain map, epics, and user stories.
- A future extraction of data analysis remains possible without changing the external product scope.

**Negative / Trade-offs:**
- Seven domain services create deployment and integration overhead.
- ms-monitoreo must keep monitoring and analysis modules internally separated.
- Cross-context data must be exchanged through APIs or events rather than direct table access.
- ms-alert and ms-user-experience add operational complexity but provide clear separation of concerns.

**Impact on the system:**
- Affected services: api-gateway, ms-security, ms-usuarios, ms-aulas, ms-sensores, ms-monitoreo, ms-alert, ms-user-experience.
- Documents that must be updated: 02-domain/dominio-map.md, 05-architecture/overview.md, 09-microservices/service-catalog.md, 04-requirements/traceability-matrix.md.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| ms-monitoreo grows into a second monolith | Medium | High | Keep monitoring and analysis as explicit modules with separate ports, use cases, and contracts |
| Services are split by technical convenience instead of domain ownership | Medium | High | Require a bounded-context review before creating a new service |
| Small team cannot operate all services reliably | Medium | High | Use Docker Compose locally, automate CI/CD, and defer non-essential service extraction |
| ms-alert and ms-user-experience become unnecessary overhead | Low | Medium | Validate necessity during sprint reviews; merge into existing services if not justified by domain complexity |

---

## References

- Domain map and bounded contexts → 02-domain/dominio-map.md
- Service catalog → 09-microservices/service-catalog.md
- System architecture → 05-architecture/overview.md
- Related to: ADR-003, ADR-004