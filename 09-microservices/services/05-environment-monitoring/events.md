# Events — ms-environment-monitoring

> Events published and consumed by this service. Names are always in past tense and use
> the ubiquitous language of the domain (`02-domain/domain-events.md`).

`ms-environment-monitoring` consumes environmental facts via RabbitMQ and keeps a
evento interno para los analisis que completa. Los nombres siguen el lenguaje
ubicuo del dominio (`02-domain/domain-events.md`).

---

## Published events

| Field | Value |
|-------|-------|
| **Name** | `EnvironmentalDataAnalyzed` |
| **Bounded Context** | Environmental Data Analysis |
| **Aggregate** | Environmental Data Analysis |
| **Trigger** | Environmental data is analyzed for a selected time period |
| **Consumers** | Environmental Dashboard (in-app), `ms-user-experience` when extracted |
| **Channel (topic)** | In-process Spring application event for now |
| **Schema version** | `v1` |
| **Delivery guarantee** | At-most-once in the service; at-least-once when a broker outbox is adopted |

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

### `EnvironmentalDataRecorded`

| Field | Value |
|-------|-------|
| **Name** | `EnvironmentalDataRecorded` |
| **Bounded Context** | Environmental Monitoring |
| **Aggregate** | Environmental Data |
| **Trigger** | Accepted sensor readings are published for an educational environment |
| **Publisher** | `ms-sensor-management` (currently produced by the monolith ingestion path) |
| **Consumer** | `ms-environment-monitoring` measurement projection |
| **Channel (topic)** | Exchange `eduaircontrol.environmental-data`, routing key `environmental.data.recorded` |
| **Schema version** | `v1` |
| **Delivery guarantee** | At-least-once |

**Payload:**

```json
{
  "eventId": "UUID",
  "eventType": "EnvironmentalDataRecorded",
  "aggregateId": "UUID",
  "aggregateType": "EnvironmentalData",
  "occurredAt": "ISO 8601",
  "version": 1,
  "payload": {
    "environmentId": "UUID",
    "temperature": 23.5,
    "humidity": 58.2,
    "co2": 650,
    "noiseLevel": 42.5
  },
  "metadata": {
    "correlationId": "UUID",
    "causationId": null,
    "userId": null
  }
}
```

**Guarantees and handling:**
- The `eventId` is the idempotency key. It is claimed in `inbox_message` in the
  same transaction that writes the projected rows.
- The broker `message_id` is only a fallback when the envelope omits `eventId`.
- A flat payload is projected to atomic rows, one per reported variable; absent
  variables generate no row. `noiseLevel` resolves to the catalog code `noise`.
- A message without an envelope identifier or without a payload goes to the dead-letter queue.
- Retries use exponential backoff (`1s`, `2s`, `4s`, `8s`). After four attempts, the
  message goes to `<queue>.dlq`, retained for seven days.

---

## Retries, dead letters and alerts

- Retries on consumption failures: four attempts with exponential backoff.
- Dead-letter queue: `<queue>.dlq`, with a seven-day TTL.
- `inbox_message` makes redeliveries safe; no separate replay procedure is needed for
  duplicate delivery.