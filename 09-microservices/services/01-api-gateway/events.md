# Events — API Gateway

> The API Gateway **does not emit domain events**. Its responsibility is infrastructure
> (routing, authentication, rate limiting), not business.
>
> Domain events (things the business cares about) are emitted by the services behind the gateway.

---

## Published events

**None.** The API Gateway does not publish to the message broker.

---

## Consumed events

**None.** The API Gateway does not subscribe to the message broker.

---

## Access logs (not domain events)

The gateway does produce structured **access logs** for every HTTP request:

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "info",
  "type": "access_log",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status": 200,
  "durationMs": 45,
  "ip": "192.168.1.100",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "upstreamService": "auth-service",
  "upstreamStatus": 200
}
```

These logs go to the observability platform (`13-operations/observability.md`) but are
**not published to the message broker** — they are not business events.

---

## Correlations

- Observability and logs → `13-operations/observability.md`
- Business events of the services → `09-microservices/services/02-auth-service/events.md`
