## ADR-004 — Communication Patterns Between Components

- **ID:** ADR-004
- **Date:** 2026-09-09
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl has immediate user-facing queries, internal service interactions, and environmental measurements arriving from sensors. The documentation mentions REST, MQTT, HTTP, RabbitMQ, and event-driven communication, but it does not define which interaction uses which channel or whether a channel is mandatory.
The decision is needed to prevent accidental coupling and to make API contracts, event schemas, retries, and operational ownership implementable.

**Known constraints:**
- The React frontend requires immediate responses for authentication, management, monitoring, and dashboard queries.
- Sensor ingestion may be asynchronous and may tolerate eventual consistency for historical analysis.
- Existing domain events include UserRegistered, EnvironmentalDataRecorded, and EnvironmentalDataAnalyzed.

---

## Decision

**We decided:** Use REST/HTTPS with OpenAPI contracts for frontend-to-gateway and synchronous request/response operations. Use MQTT or HTTPS for sensor-to-ms-sensores ingestion, depending on the sensor capability. Use RabbitMQ with versioned domain events for asynchronous propagation from ms-sensores/ms-monitoreo to downstream processing when the operation does not require an immediate response.
The API Gateway is the only public backend entry point. Services must not expose direct public endpoints for frontend access.

**Justification:**
REST is appropriate for immediate queries and commands, while asynchronous messaging decouples sensor ingestion from historical processing. The choice matches the defined user stories, the context map, and the existing event catalog without forcing every interaction through a broker.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| REST for synchronous work, MQTT/HTTPS for sensors, RabbitMQ for asynchronous events — chosen | Fits interaction needs; decouples non-urgent processing; supports heterogeneous sensors | Requires multiple contracts and operational components | Chosen for the MVP |
| REST/HTTPS for all communication | Simple tooling and debugging | Tight coupling for sensor bursts and background processing; weaker decoupling | Discarded because environmental ingestion and analysis are asynchronous candidates |
| RabbitMQ/events for all communication | Strong decoupling and buffering | Adds latency and complexity to login, CRUD, and dashboard queries | Discarded because user-facing operations need immediate responses |
| gRPC for internal calls | Strong typing and efficient transport | Additional tooling; not aligned with current OpenAPI/REST backlog | Deferred unless internal performance needs justify it |


---

## Consequences

**Positive:**
- User-facing APIs remain predictable and contract-first.
- Sensor ingestion can absorb transient downstream delays.
- Domain events provide a controlled integration boundary between contexts.

**Negative / Trade-offs:**
- The system must operate and monitor both HTTP and messaging infrastructure.
- Asynchronous consumers must handle eventual consistency and duplicate messages.
- Each event requires schema ownership and compatibility rules.

**Impact on the system:**
- Affected services: api-gateway, ms-sensores, ms-monitoreo, React frontend, and any future analysis consumer.
- Documents that must be updated: 05-architecture/overview.md, 02-domain/dominio-map.md, 02-domain/domain-events.md, 07-api/README.md, 09-microservices/service-catalog.md, 10-devops/environments.md.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| REST and events expose inconsistent domain models | Medium | High | Define canonical contracts and anti-corruption mappings per consumer |
| Message backlog delays historical analysis | Medium | High | Monitor queue depth, define alerts, and scale consumers independently |
| Sensor protocols produce incompatible payloads | Medium | High | Normalize all input in ms-sensores before publishing domain events |

---

## References

- Context relationships → 02-domain/dominio-map.md
- Event catalog and schema evolution → 02-domain/domain-events.md
- API-first principle → 05-architecture/overview.md
- Related to: ADR-002, ADR-005, ADR-007