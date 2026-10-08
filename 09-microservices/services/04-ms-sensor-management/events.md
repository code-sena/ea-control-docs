# Events — ms-sensor-management

> Events are how microservices communicate asynchronously.
> This document lists the events this service publishes and consumes.

**MVP status: partial.** `SensorInstalled` and `SensorRemoved` are **implemented**
and published through a transactional outbox (ADR-007). The remaining events in the
table below are still only a contract, documented so downstream services can plan
against them.

### What is live

| | |
|---|---|
| Exchange | `eduaircontrol.sensor` (topic, durable) |
| Routing keys | `sensor.installation.created`, `sensor.installation.closed` |
| Transport | RabbitMQ over AMQP |
| Persistence | `sensors.outbox_event`, written in the same transaction as the installation |
| Publisher | `OutboxRelay` (1 s) / `OutboxPublisher` (one transaction per event) |
| Config | `app.outbox.*` — set `OUTBOX_ENABLED=false` to disable without code changes |

Because the row is written inside the business transaction, an installation that
rolls back leaves no event behind, and a broker outage delays the event instead of
losing it. Delivery is **at-least-once**: `ms-environment-monitoring` deduplicates by
`eventId`.

---

## Events this service PUBLISHES

| Event | Topic/Exchange | When it is emitted | Payload (key fields) |
|-------|---------------|--------------------|---------------------|
| SensorRegistered | `sensor.sensor.registered` | New sensor created | `{sensorId, serialNumber, sensorModelId, sensorStatusId}` |
| SensorUpdated | `sensor.sensor.updated` | Sensor fields changed | `{sensorId, changedFields…}` |
| SensorStatusChanged | `sensor.sensor.status_changed` | `sensorStatusId` updated | `{sensorId, previousStatusId, currentStatusId}` |
| **SensorInstalled** ✅ | `sensor.installation.created` | Installation registered | `{sensorInstallationId, sensorId, educationalEnvironmentId, installedAt}` |
| **SensorRemoved** ✅ | `sensor.installation.closed` | Installation closed (`removed_at`) | `{sensorInstallationId, sensorId, educationalEnvironmentId, installedAt, removedAt}` |
| VariableRegistered | `sensor.variable.registered` | New variable created | `{variableId, code, name, measurementUnitId}` |
| SensorVariableAssociated | `sensor.sensor_variable.associated` | Pair created | `{sensorId, variableId}` |
| SensorVariableRemoved | `sensor.sensor_variable.removed` | Pair deleted | `{sensorId, variableId}` |

> **`environmentTypeId` is not in the payload, on purpose.** This service does not
> own that value: it only validates that `educationalEnvironmentId` is a UUID
> (DEC-007). `ms-environment-monitoring` resolves the type from its local
> `educational_environment` replica, and `installation_projection.environment_type_id`
> stays NULL until it does.

### Event envelope

```json
{
  "eventId": "uuid",
  "eventType": "SensorRegistered",
  "timestamp": "2026-10-06T12:00:00Z",
  "version": "1.0",
  "source": "ms-sensor-management",
  "payload": {
    "sensorId": "uuid",
    "serialNumber": "SN-2026-0001",
    "sensorModelId": "uuid",
    "sensorStatusId": "uuid"
  }
}
```

> Physical deletes are intentionally **not** published as events in the MVP; the
> `409` guard already prevents deleting referenced records.

---

## Events this service CONSUMES

| Event | Published by | Topic/Exchange | Action |
|-------|-------------|----------------|--------|
| EducationalEnvironmentCreated | ms-classroom-management | `classroom.educational_environment.created` | Cache/acknowledge the environment UUID for installation validation (future) |
| EducationalEnvironmentUpdated | ms-classroom-management | `classroom.educational_environment.updated` | Refresh cached fields |
| EducationalEnvironmentStatusChanged | ms-classroom-management | `classroom.educational_environment.status_changed` | Flag installations in a deactivated space |

> In the MVP these validations are **not** active: `educationalEnvironmentId` is
> accepted as a UUID only (decisions.md DEC-007). Consumption starts when the
> broker lands (ADR-004).

---

## Delivery guarantees (when messaging is introduced)

| Guarantee | Value | Implication |
|-----------|-------|-------------|
| At-least-once | Yes | Consumers must be idempotent (`ms-environment-monitoring` uses `inbox_message`) |
| At-most-once | No | — |

Broker: RabbitMQ (ADR-004), versioned payloads (`version` field), topic exchange
per bounded context (`sensor.*`).

---

## Re-synchronisation

The outbox only captures **future** changes. An installation that already existed
when the publisher was deployed never emitted an event, so it has no row in
`ms-environment-monitoring.installation_projection` and its measurements are stored
but invisible: every read query JOINs that projection.

There is no re-sync endpoint. To bring an existing installation into the
projection, re-emit the event by closing and reopening it
(`POST /api/v1/sensor-installations/{id}/remove` then `POST /api/v1/sensor-installations`),
or insert the row directly. A proper fix is a `POST /api/v1/sensor-installations/re-sync`
that re-emits every active installation.
