# Events — ms-classroom-management

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
| EducationalEnvironmentCreated | `classroom.educational_environment.created` | New space registered | `{educationalEnvironmentId, campusId, code, name, environmentTypeId, status}` |
| EducationalEnvironmentUpdated | `classroom.educational_environment.updated` | Space fields changed | `{educationalEnvironmentId, changedFields…}` |
| EducationalEnvironmentStatusChanged | `classroom.educational_environment.status_changed` | `ACTIVE` ↔ `INACTIVE` transition | `{educationalEnvironmentId, previousStatus, currentStatus}` |
| CampusCreated / CampusUpdated | `classroom.campus.*` | Campus created/updated | `{campusId, code, name, city, status}` |
| EnvironmentTypeCreated / EnvironmentTypeUpdated | `classroom.environment_type.*` | Type created/updated | `{environmentTypeId, code, name}` |

### Event envelope (planned)

```json
{
  "eventId": "uuid",
  "eventType": "EducationalEnvironmentCreated",
  "timestamp": "2026-09-30T12:00:00Z",
  "version": "1.0",
  "source": "ms-classroom-management",
  "payload": {
    "educationalEnvironmentId": "uuid",
    "campusId": "uuid",
    "code": "A-101",
    "name": "Aula 101",
    "environmentTypeId": "uuid",
    "status": "ACTIVE"
  }
}
```

> Soft deletes are intentionally **not** published as events in the MVP; a future
> `EducationalEnvironmentDeleted` event can be added if consumers need it.

---

## Events this service CONSUMES

| Event | Published by | Topic/Exchange | Action |
|-------|-------------|----------------|--------|
| — | — | — | None in the MVP |

---

## Delivery guarantees (when messaging is introduced)

| Guarantee | Value | Implication |
|-----------|-------|-------------|
| At-least-once | Yes | Consumers must be idempotent |
| At-most-once | No | — |

Broker: RabbitMQ (ADR-004), versioned payloads (`version` field), topic exchange
per bounded context (`classroom.*`).
