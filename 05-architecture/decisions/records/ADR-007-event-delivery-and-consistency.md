## ADR-007 — At-Least-Once Events with Transactional Outbox

- **ID:** ADR-007
- **Date:** 2026-09-09
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

The event catalog defines UserRegistered, EnvironmentalDataRecorded, and EnvironmentalDataAnalyzed. It also describes at-least-once delivery, idempotent consumers, retries, and a dead-letter queue, but the project has not selected a publication mechanism that prevents the database state and published event from diverging.
For environmental monitoring, losing an event after persisting a measurement would leave historical analysis incomplete. Publishing an event before the database transaction commits could produce an event for data that was ultimately rolled back.

**Known constraints:**
- RabbitMQ is the selected candidate broker in the architecture overview.
- Domain data is persisted in PostgreSQL according to ADR-003.
- Consumers may receive duplicate messages.
- The MVP does not require distributed ACID transactions.

---

## Decision

**We decided:** Publish integration events through RabbitMQ using a transactional outbox. The producing service writes its domain data and an outbox record in the same PostgreSQL transaction. A background publisher sends pending outbox records to RabbitMQ, marks them as published, and retries failures with exponential backoff. Consumers must be idempotent using eventId and a processed-event record. Messages that exceed the retry limit go to a dead-letter queue.
The initial delivery guarantee is at least once. Exactly-once delivery is not promised.

**Justification:**
The outbox closes the most important failure window between committing business data and publishing an event. At-least-once delivery with idempotent consumers is realistic with RabbitMQ and supports recovery without introducing distributed transactions.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Transactional outbox + RabbitMQ + idempotent consumers — chosen | Prevents lost events; supports retries and recovery; fits current patterns | Requires outbox tables, publisher process, and duplicate handling | Chosen for reliable MVP integration |
| Publish directly after database commit | Simple implementation | Process failure can lose the event; retries are difficult to coordinate | Discarded because environmental history depends on event propagation |
| Distributed two-phase commit | Strong atomicity across systems | High complexity, poor availability, and broker/database coupling | Discarded because it is disproportionate to the MVP |
| Event sourcing | Complete event history and replay | Major modeling and operational complexity; not required by scope | Discarded because the system needs relational current state and historical measurements, not event-sourced aggregates |


---

## Consequences

**Positive:**
- Persisted measurements and integration events remain recoverable as one local transaction.
- Duplicate delivery becomes an explicit, testable consumer behavior.
- Failed messages can be inspected and replayed from the dead-letter queue.

**Negative / Trade-offs:**
- Every event-producing service needs an outbox table and publisher process.
- Eventual consistency is visible to consumers and dashboard analysis.
- Operational monitoring is required for outbox backlog, retries, and dead-letter messages.

**Impact on the system:**
- Affected services: ms-sensores, ms-monitoreo, RabbitMQ, and future event consumers.
- dcfdDocuments that must be updated: 02-domain/domain-events.md, 05-architecture/overview.md, 05-architecture/pattern-guide.md, 06-data/models.md, 09-microservices/service-catalog.md, 13-operations/observability.md.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Outbox backlog delays analysis | Medium | Medium | Monitor age and count of pending records; scale publisher and consumers |
| Consumer processes an event twice | High | Medium | Unique eventId constraint and atomic processed-event handling |
| Poison message remains in the queue | Medium | High | Bounded retries, exponential backoff, DLQ alerting, and replay runbook |

---

## References

- Domain event catalog → 02-domain/domain-events.md
- Outbox and resilience patterns → 05-architecture/pattern-guide.md
- Data ownership and migrations → 06-data/models.md
- Related to: ADR-003, ADR-004