# Design Decisions — ms-classroom-management

> Technical decisions specific to this service (not global architectural ones —
> those live in `05-architecture/decisions/`).

---

## DEC-001 Hexagonal layering with pragmatic JPA entities

**Date:** 2026-09-29
**Status:** Active

**Context:**
ADR-009 mandates hexagonal architecture for all microservices. A strict reading
would keep JPA annotations out of the domain layer (separate persistence
entities + mappers).

**Decision:**
Layer structure `domain` → `application` (use cases + outbound ports) →
`infrastructure` (adapters), but entities carry JPA mapping annotations directly
and the Spring Data interfaces live behind port interfaces
(`application/port/*Repository`), implemented by adapters
(`infrastructure/outbound/persistence/*Adapter`).

**Alternatives considered:**
- Full persistence-model separation (mapper + second entity set): rejected for the
  MVP as boilerplate with no mapping complexity yet.

**Consequences:**
- ✅ Controllers never touch JPA; business rules sit in `application` services,
  unit-testable with mocked ports (`CampusServiceTest`).
- ⚠️ Domain layer is bound to JPA annotations; a persistence swap requires
  entity refactoring.

---

## DEC-002 Interim JWT validation with shared secret (HS256)

**Date:** 2026-09-29
**Status:** Active (to be superseded)

**Context:**
ADR-006 defines RS256 access tokens validated by the api-gateway with JWKS from
`ms-security`. Neither service exists yet, but tokens issued today by the
monolith (HS256, shared `JWT_SECRET`, claim `role`) must keep working.

**Decision:**
Validate `Authorization: Bearer` JWTs with `jjwt` 0.11.5 and the shared
`JWT_SECRET` (HS256-compatible HMAC key), extracting `sub` and `role`. Reads
require any valid token; writes (`POST`/`PATCH`/`DELETE`) require `ROLE_ADMIN`.

**Alternatives considered:**
- Skip authentication until the gateway exists: rejected (contract documents 401/403).
- RS256 now without a key issuer: rejected (no JWKS source).

**Consequences:**
- ✅ Compatible with today's monolith tokens; drop-in tests generate tokens locally.
- ⚠️ Shared secret across services; supersede with RS256 + JWKS
  (ADR-006) when `ms-security` and api-gateway land — replace
  `infrastructure/security/JwtService` only.

---

## DEC-003 Liquibase YAML changesets per domain pattern (§12)

**Date:** 2026-09-29
**Status:** Active

**Context:**
The canonical model prescribes the migration layout (§12 of
`06-data/domain/ms-classroom-management.md`): master + ordered YAML changesets in
`src/main/resources/db/changelog/`. The reference implementation
`EduAirControl/database/negocio/` aggregates all four domains in one SQL changelog
and is kept as the global reference (not modified by this service).

**Decision:**
Service-owned migrations: `db.changelog-master.yaml` includes `000…005` in
order. Changesets 000 and 004 use raw `sql` because Liquibase 5 removed
`createSchema` and `addCheckConstraint`; DDL otherwise uses native YAML
(`createTable`, `createIndex`). Every changeset ships an explicit rollback.

**Consequences:**
- ✅ The service is deployable standalone; migrations version with the service.
- ⚠️ Two sources exist (service changelog vs `database/negocio`): when a domain
  model changes, update `database/negocio` first, then port it here.

---

## DEC-004 Own database + credentials, shared instance

**Date:** 2026-09-29
**Status:** Active

**Context:**
ADR-003: one PostgreSQL instance is acceptable for the MVP, but each service must
own its schema/namespace and credentials; no cross-service table access.

**Decision:**
Database `eduaircontrol_classrooms`, dedicated credentials, schema `classrooms`.
`docker-compose.yml` in this repo runs its own `postgres:15` (host port **5433**
to avoid clashing with the main stack) so the service is self-contained.

**Consequences:**
- ✅ Independent development and CI; no coupling to the monolith's database.
- ⚠️ Local multi-service setups need a compose overlay to converge on one
  PostgreSQL instance later.

---

## DEC-005 Tests: H2 without Liquibase, real-PostgreSQL smoke outside CI

**Date:** 2026-09-29
**Status:** Active

**Context:**
The changesets use PostgreSQL-only features (`TIMESTAMPTZ`, `gen_random_uuid()`,
raw `CHECK` SQL) that H2 cannot execute, and the monolith already tests against H2.

**Decision:**
Controller/service tests run on H2 with `spring.liquibase.enabled=false`,
`ddl-auto=create-drop`, and schema `classrooms` pre-created in the JDBC URL
(`INIT=CREATE SCHEMA IF NOT EXISTS classrooms`). Bean validation mirrors the DB
CHECKs (floor ≥ 0, area > 0, capacity ≥ 1). Migration correctness is verified
against a disposable PostgreSQL 15 (apply → object inventory → rollback), not in
the unit test suite.

**Consequences:**
- ✅ Fast tests, no Docker dependency in `./mvnw verify`.
- ⚠️ Liquibase changesets are not exercised by CI; a scheduled PostgreSQL smoke
  (or Testcontainers later) is recommended.
