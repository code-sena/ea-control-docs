# Events — ms-sensor-management

> Events are how microservices communicate asynchronously.
> This document lists the events this service publishes and consumes.

**MVP status: no active messaging.** The MVP communicates synchronously via
REST/HTTPS through the api-gateway (ADR-004). The events below are the contract
to implement incrementally when RabbitMQ is introduced; they are documented so
downstream services can plan against them.

---

## Events this service PUBLISHES

| Event | Topic/Exchange | When it is emitted | Payload (key fields) |
|-------|---------------|--------------------|---------------------|
| SensorRegistered | `sensor.sensor.registered` | New sensor created | `{sensorId, serialNumber, sensorModelId, sensorStatusId}` |
| SensorUpdated | `sensor.sensor.updated` | Sensor fields changed | `{sensorId, changedFields…}` |
| SensorStatusChanged | `sensor.sensor.status_changed` | `sensorStatusId` updated | `{sensorId, previousStatusId, currentStatusId}` |
| SensorInstalled | `sensor.installation.created` | Installation registered | `{sensorInstallationId, sensorId, educationalEnvironmentId, installedAt}` |
| SensorRemoved | `sensor.installation.closed` | Installation closed (`removed_at`) | `{sensorInstallationId, sensorId, educationalEnvironmentId, installedAt, removedAt}` |
| VariableRegistered | `sensor.variable.registered` | New variable created | `{variableId, code, name, measurementUnitId}` |
| SensorVariableAssociated | `sensor.sensor_variable.associated` | Pair created | `{sensorId, variableId}` |
| SensorVariableRemoved | `sensor.sensor_variable.removed` | Pair deleted | `{sensorId, variableId}` |

### Event envelope (planned)

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
| At-least-once | Yes | Consumers must be idempotent |
| At-most-once | No | — |

Broker: RabbitMQ (ADR-004), versioned payloads (`version` field), topic exchange
per bounded context (`sensor.*`).
