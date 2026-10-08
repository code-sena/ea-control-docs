# Events — ms-environment-monitoring

> Events published and consumed by this service. Names are always in past tense and use
> the ubiquitous language of the domain (`02-domain/domain-events.md`).

`ms-environment-monitoring` consumes environmental facts via RabbitMQ and keeps a
evento interno para los analisis que completa. Los nombres siguen el lenguaje
ubicuo del dominio (`02-domain/domain-events.md`).

---

## Consumed events

Two exchanges, because the producers are different services and the grain of the
messages is different. Exchange, queues and bindings are declared by this service,
not by the producers: whoever receives the message is the one who knows it needs it.

### Installation projection

| Field | Value |
|-------|-------|
| **Producer** | `ms-sensor-management` |
| **Exchange** | `eduaircontrol.sensor` (topic, durable) |
| **Queue** | `eduaircontrol.sensor.ms-environment-monitoring` |
| **Binding** | `sensor.installation.*` |
| **Events** | `SensorInstalled`, `SensorRemoved` |
| **Consumer** | `installation-projection` |
| **Schema version** | `v1` |
| **Delivery guarantee** | At-least-once |

Feeds `environment_monitoring.installation_projection`, the local replica declared in
DEC-006 §4.3. This service does not own `sensor_installation`, so without that
replica the measurements reported by the devices are stored but **invisible**:
`latestByEnvironment`, `history` and `MeasurementAggregationDao` all JOIN the
projection.

Idempotency uses the same `inbox_message` table as the measurement projection,
deduplicating on `eventId`. Both `SensorInstalled` and `SensorRemoved` are applied
with one upsert: a close sets `removed_at`, and the read queries already filter on
`p.removed_at is null`, so no row is ever deleted (it remains valid history).

> `environment_type_id` is written as NULL until this service's
> `educational_environment` replica knows the environment. The producer does not
> carry the value (DEC-007: it only validates the UUID). Failing here instead would
> push a perfectly valid installation to the dead-letter queue just because its
> environment has not arrived yet.

### Measurement projection

| Field | Value |
|-------|-------|
| **Producer** | `ms-sensor-management` (planned) / `EduAirControl` monolith (current) |
| **Exchange** | `eduaircontrol.environmental-data` (topic, durable) |
| **Queue** | `eduaircontrol.environmental-data.ms-environment-monitoring` |
| **Binding** | `environmental.data.*` |
| **Event** | `EnvironmentalDataRecorded` |
| **Consumer** | `environmental-measurement-projection` |

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