# Events — ms-monitoreo

> Events published and consumed by this service. Names are always in past tense and use
> the ubiquitous language of the domain (`02-domain/domain-events.md`).

Because EduAirControl currently runs as a monolith, events are implemented as **internal
domain/application events** and exposed to the application event bus. If the system is
split into deployable microservices, the same payloads are published to RabbitMQ through a
transactional outbox (ADR-007), which is still `Planned`.

---

## Published events

| Field | Value |
|-------|-------|
| **Name** | `EnvironmentalDataAnalyzed` |
| **Bounded Context** | Environmental Data Analysis |
| **Aggregate** | Environmental Data Analysis |
| **Trigger** | Environmental data is analyzed for a selected time period |
| **Consumers** | Environmental Dashboard (in-app), `ms-user-experience` when extracted |
| **Channel (topic)** | Internal application event (future: `environmental.data.analyzed`) |
| **Schema version** | `v1` |
| **Delivery guarantee** | At-most-once in the monolith; at-least-once once the outbox is adopted |

**Payload:**

```json
{
  "eventId": "UUID",
  "eventType": "EnvironmentalDataAnalyzed",
  "aggregateId": "UUID",
  "aggregateType": "EnvironmentalDataAnalysis",
  "occurredAt": "ISO 8601",
  "version": 1,
  "payload": {
    "environmentId": "UUID",
    "period": "DAY | WEEK | MONTH | YEAR",
    "periodStart": "ISO 8601",
    "periodEnd": "ISO 8601",
    "analysisId": "UUID",
    "results": [
      {
        "variableCode": "TEMP",
        "minValue": 21.4,
        "maxValue": 26.9,
        "avgValue": 23.8,
        "sampleCount": 24,
        "exceedanceCount": 2
      }
    ]
  }
}
```

**Guarantees and handling:**
- Published only when the analysis reaches `COMPLETED`. A `FAILED` analysis publishes nothing.
- The `eventId` is generated once per publication and is the idempotency key consumers
  must use when the outbox is adopted.
- Consumers must be idempotent: re-processing the same `eventId` must not duplicate
  derived state.

---

## Consumed events

**None currently.** This service does not react to events from other services.

The following events are relevant to this domain but are resolved synchronously through
API contracts while the system remains monolithic:

| Event | Origin | Deferred handling |
|-------|--------|--------------------|
| `SensorRegistered` | `ms-sensores` | Sensor inventory is read through `InstallationPort` |
| `SensorStatusChanged` | `ms-sensores` | Offline detection is computed from `last_seen_at` at query time |
| `VariableConfigurationUpdated` | `ms-sensores` | Variable catalog is read through `VariableCatalogPort` |
| `EducationalEnvironmentStatusChanged` | `ms-aulas` | Environment metadata is read through `EnvironmentLookupPort` |

---

## Retries, dead letters and alerts

Not applicable while events stay in-process: there is no broker, so there is no retry
budget and no dead-letter queue. When the outbox from ADR-007 is adopted, this service
must add:

- exponential backoff on publication failures,
- a dead-letter queue with an alert on depth,
- a replay procedure documented in the service runbook (required before the first deploy
  to staging).