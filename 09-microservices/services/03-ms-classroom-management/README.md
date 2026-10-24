# ms-classroom-management

> **Authoritative owner** of the classrooms bounded context: campuses, environment
> classification, and the educational environments (physical spaces) the platform
> monitors.

---

## Responsibility

Manage the lifecycle of educational environments: campus registration, environment
types, and the spaces themselves (code, floor, area, capacity, status). Owns the
`classrooms` schema exclusively.

## Location in the architecture

| Field | Value |
|-------|-------|
| Number in catalog | 03 |
| Local port | 3002 |
| Repository | Local repo `ms-classroom-management/` (remote not created yet) |
| DB engine | PostgreSQL (schema `classrooms`, dedicated database/credentials) |
| Communicates with | — (no outbound calls in the MVP; referential checks are intra-schema) |
| Consumed by | api-gateway (frontend), ms-sensor-management / ms-environment-monitoring (via API or logical reference) |

## Responsibilities (what this service DOES)

- CRUD for `campuses`, `environment_types`, and `educational_environment`.
- Enforce domain rules: unique codes, unique `(campus_id, code)`, lifecycle
  `ACTIVE`/`INACTIVE`, soft delete via `deleted_at`, floor/area/capacity CHECKs.
- Paginated, filtered list endpoints (`q`, `status`, `campusId`, `environmentTypeId`).
- Own its schema migrations (Liquibase) and health endpoint.

## Out of scope (what it does NOT do)

- **Does not manage users, roles, or authentication** — that is `ms-security`.
- **Does not store measurements, analyses, or alerts** — other domains reference
  an educational environment by UUID (logical reference, ADR-003).
- **Does not expose user preferences or favorites** — those live in
  `ms-user-experience`.

## How to run it locally

```bash
# From the service repository root (includes its own PostgreSQL on port 5433)
docker compose up -d

# Verify
curl http://localhost:3002/health
# {"status":"ok","timestamp":"...","dependencies":{"database":"ok"}}

# Swagger UI
open http://localhost:3002/swagger-ui.html
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

- [data-model.md](./data-model.md) — DB schema (`classrooms`)
- [events.md](./events.md) — events it publishes and consumes
- [decisions.md](./decisions.md) — internal design decisions
- [runbook.md](./runbook.md) — operation
- [API Contract](../../../07-api/contracts/openapi/ms-classroom-management.yaml)
- Canonical model: `06-data/domain/ms-classroom-management.md`
