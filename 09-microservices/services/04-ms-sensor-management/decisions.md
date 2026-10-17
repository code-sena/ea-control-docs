# Design Decisions — ms-sensor-management

> Technical decisions specific to this service (not global architectural ones —
> those live in `05-architecture/decisions/`).

---

## DEC-001 Hexagonal layering with pragmatic JPA entities

**Date:** 2026-10-06
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
- Full persistence-model separation (mapper + second entity set): rejected for
  the MVP as boilerplate with no mapping complexity yet.

**Consequences:**
- ✅ Controllers never touch JPA; business rules sit in `application` services,
  unit-testable with mocked ports (`SensorServiceTest`, `SensorInstallationServiceTest`,
  `VariableServiceTest`).
- ⚠️ Domain layer is bound to JPA annotations; a persistence swap requires
  entity refactoring.

---

## DEC-002 JWT validation (superseded interim: shared secret HS256)

**Date:** 2026-10-06
**Status:** Superseded (2026-10-17)

**Context:**
ADR-006 defines RS256 access tokens validated by the api-gateway with JWKS from
`ms-security`. Neither service exists yet, but tokens issued today by the
monolith (HS256, shared `JWT_SECRET`, claim `role`) must keep working.

**Decision (superseded 2026-10-17):**
Validated `Authorization: Bearer` JWTs with the shared `JWT_SECRET` (HS256),
extracting `sub` and `role`.

**Current state:** **RS256 only.** Since 2026-10-08 the service validates RS256
tokens against the ms-security JWKS (`security.jwks-uri`, ADR-006/TD-019); the
shared secret is gone. Since 2026-10-17 (ADR-018, R-001) the service is
**JWT-only**: `X-User-*` headers are never trusted. Reads require any valid
token; writes (`POST`/`PATCH`/`DELETE`) require `ROLE_ADMIN`.

**Consequences:**
- ✅ No shared secrets across services; each verifies the token locally via JWKS.
- Tests mint RS256 tokens from an in-memory key pair (`TestTokenMint`).


---

## DEC-003 Liquibase YAML changesets per service

**Date:** 2026-10-06
**Status:** Active

**Context:**
The reference implementation `EduAirControl/database/negocio/` aggregates all
four domains in one SQL changelog and is kept as the global reference (not
modified by this service). Each service must own its migrations (ADR-008).

**Decision:**
Service-owned migrations: `db.changelog-master.yaml` includes `000…006` in
order. Changesets 000 and 005 use raw `sql` because Liquibase 5 removed
`createSchema` and does not express `ON DELETE …` actions declaratively in the
forms used; DDL otherwise uses native YAML (`createTable`, `addPrimaryKey`,
`createIndex`). Every changeset ships an explicit rollback.

**Consequences:**
- ✅ The service is deployable standalone; migrations version with the service.
- ⚠️ Two sources exist (service changelog vs `database/negocio`): when a domain
  model changes, update `database/negocio` first, then port it here.

---

## DEC-004 Own database + credentials, shared instance

**Date:** 2026-10-06
**Status:** Active

**Context:**
ADR-003: one PostgreSQL instance is acceptable for the MVP, but each service must
own its schema/namespace and credentials; no cross-service table access.

**Decision:**
Database `eduaircontrol_sensors`, dedicated credentials, schema `sensors`.
`docker-compose.yml` in this repo runs its own `postgres:15` (host port **5434**
to avoid clashing with the main stack and other services) so the service is
self-contained.

**Consequences:**
- ✅ Independent development and CI; no coupling to the monolith's database.
- ⚠️ Local multi-service setups need a compose overlay to converge on one
  PostgreSQL instance later.

---

## DEC-005 Tests: H2 without Liquibase, real-PostgreSQL smoke outside CI

**Date:** 2026-10-06
**Status:** Active

**Context:**
The changesets use PostgreSQL-only features (`TIMESTAMPTZ`,
`gen_random_uuid()`, raw FK SQL) that H2 cannot execute.

**Decision:**
Controller/service tests run on H2 with `spring.liquibase.enabled=false`,
`ddl-auto=create-drop`, and schema `sensors` pre-created in the JDBC URL
(`INIT=CREATE SCHEMA IF NOT EXISTS sensors`). The composite PK of
`sensor_variable` is created by Hibernate `@IdClass`. Migration correctness is
verified against a disposable PostgreSQL 15 (apply → object inventory →
rollback), not in the unit test suite.

**Consequences:**
- ✅ Fast tests, no Docker dependency in `./mvnw verify`.
- ⚠️ H2 does not materialize the FKs between tables (they are plain UUID
  columns in the entities); referential behavior is enforced in the services and
  by PostgreSQL — covered by the real-PostgreSQL smoke.

---

## DEC-006 Physical delete + closed installation history (no soft delete)

**Date:** 2026-10-06
**Status:** Active

**Context:**
The canonical model (`06-data/domain/ms-sensor-management.md` §12) defines no
`deleted_at` for this domain, and `sensor_installation` is a history table
(`removed_at` marks closure).

**Decision:**
- `DELETE /sensors/{id}`: physical row delete, guarded by installation history
  (`409`); its `sensor_variable` pairs are removed in the same transaction.
- `DELETE /variables/{id}`: physical row delete, guarded by associations (`409`).
- Installations are **never deleted**: `POST /sensor-installations/{id}/remove`
  sets `removed_at = now()` (second close → `409`; `installed_at` in the future →
  `400`).

**Alternatives considered:**
- Soft delete à la classrooms (`deleted_at` column): rejected — the reference
  model has no such column here and installation history must stay immutable.

**Consequences:**
- ✅ History is preserved; deletes are explicit and guarded at both service and
  DB level (FK RESTRICT).
- ⚠️ A sensor that has ever been installed cannot be deleted (by design) —
  deactivate it via `sensorStatusId` instead.

---

## DEC-007 Logical references validated as UUID only

**Date:** 2026-10-06
**Status:** Active

**Context:**
`sensorModelId`, `sensorStatusId`, and `measurementUnitId` point to catalogs that
are **excluded from the MVP** (implementation decision, see `06-data/README.md`),
and `educationalEnvironmentId` lives in another service's schema
(`ms-classroom-management`). There is no cross-service communication in the MVP
and no tables to check against.

**Decision:**
All four are validated as **UUID format only** (bean validation `@NotNull`;
no existence check). The DB enforces intra-domain FKs; cross-domain and catalog
references remain logical (ADR-003).

**Alternatives considered:**
- Call `ms-classroom-management` synchronously to verify the environment:
  rejected for the MVP (no inter-service calls exist yet; would couple the
  services on the write path).
- Create local shadow tables for the excluded catalogs: rejected (duplicated
  ownership).

**Consequences:**
- ✅ No coupling; service stands alone and tests stay hermetic.
- ⚠️ A misspelled UUID is accepted and stored; when `EducationalEnvironment*`
  events arrive (events.md), validate/cache them before enforcing referential
  behavior.

---

## DEC-008 Overlap rule for installations

**Date:** 2026-10-06
**Status:** Active

**Context:**
§12 of the canonical model: "A sensor should not have overlapping active
installations… Historical installations may exist as long as their validity
periods do not overlap." A new installation is always open (`removed_at IS NULL`
until closed).

**Decision:**
On create, reject (`409`) when the sensor already has an installation where
`removed_at IS NULL` **or** `removed_at > installedAt` of the new record — i.e.
the new open period `[installedAt, ∞)` would overlap any existing period.
Expressed as a single specification
(`existsOverlapForSensor`) in the outbound adapter.

**Consequences:**
- ✅ At most one active installation per sensor; historical periods never overlap.
- ⚠️ Installing a sensor "back-dated" requires closing the current installation
  first (intentional sequencing).
