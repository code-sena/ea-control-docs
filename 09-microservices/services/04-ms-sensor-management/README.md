# ms-sensor-management

> **Authoritative owner** of the sensors bounded context: sensors, their
> installation history, the measured variables, and the sensor↔variable
> associations.

---

## Responsibility

Manage the lifecycle of environmental sensors: registration (serial number,
model/status), installation history in educational environments, the variables
each sensor measures, and the N:M associations between them. Owns the `sensors`
schema exclusively.

## Location in the architecture

| Field | Value |
|-------|-------|
| Number in catalog | 04 |
| Local port | 3004 |
| Repository | Local repo `ms-sensor-management/` (remote not created yet) |
| DB engine | PostgreSQL (schema `sensors`, dedicated database/credentials) |
| Communicates with | — (no outbound calls in the MVP; `educationalEnvironmentId` is a logical reference) |
| Consumed by | api-gateway (frontend), ms-environment-monitoring (via API or logical reference) |

## Responsibilities (what this service DOES)

- CRUD for `sensor` and `variable`; create/list/close for `sensor_installation`;
  associate/dissociate for `sensor_variable`.
- Enforce domain rules: unique serial number, unique variable `code`,
  **maximum one active installation per sensor** (periods must not overlap),
  `removed_at > installed_at`, composite PK uniqueness.
- Paginated, filtered list endpoints (`q`, `sensorModelId`, `sensorStatusId`,
  `sensorId`, `educationalEnvironmentId`, `active`).
- Own its schema migrations (Liquibase) and health endpoint.

## Out of scope (what it does NOT do)

- **Does not manage sensor models/statuses or measurement units** — those
  catalogs are excluded from the MVP (logical UUID references only).
- **Does not store measurements, thresholds, analyses, or alerts** — those belong
  to `ms-environment-monitoring`.
- **Does not validate that an educational environment exists** — cross-domain
  references are logical per ADR-003; the environment lives in
  `ms-classroom-management`.
- **Does not manage users or authentication** — that is `ms-security`.

## How to run it locally

```bash
# From the service repository root (includes its own PostgreSQL on port 5434)
docker compose up -d

# Verify
curl http://localhost:3004/health
# {"status":"ok","timestamp":"...","dependencies":{"database":"ok"}}

# Swagger UI
open http://localhost:3004/swagger-ui.html
```

Without Docker (point `POSTGRES_URL`/`POSTGRES_USER`/`POSTGRES_PASSWORD` at any
PostgreSQL; JWT validation reads `security.jwks-uri` (defaults to the local
ms-security, `http://localhost:8081/api/v1/auth/jwks`)):

```bash
./mvnw spring-boot:run
```

## Architecture

Hexagonal (ADR-009): `domain` → `application` (use cases + ports) →
`infrastructure` (REST inbound adapter, JPA outbound adapter, JWT filter).
See `decisions.md` for service-specific choices.

## Related documents

- [data-model.md](./data-model.md) — DB schema (`sensors`)
- [events.md](./events.md) — events it publishes and consumes
- [decisions.md](./decisions.md) — internal design decisions
- [runbook.md](./runbook.md) — operation
- [API Contract](../../../07-api/contracts/openapi/ms-sensor-management.yaml)
- Canonical model: `06-data/domain/ms-sensor-management.md`
