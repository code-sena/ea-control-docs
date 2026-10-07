# Data Model — ms-classroom-management

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables directly; they reference them by
> logical UUID (ADR-003) and go through this service's API.

---

## Database engine

**Engine:** PostgreSQL
**Justification:** Strong relational integrity (FKs, CHECKs, uniqueness) for a
registry domain, consistent with the MVP platform choice (ADR-003). One schema per
service in a shared instance.

**Schema:** `classrooms` (created by changeset `000-create-schema`).

---

## Schema

### Table: campuses

**Purpose:** Physical campuses (main sites) that group educational environments.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| campus_id | UUID | No | Unique identifier | PK, default `gen_random_uuid()` |
| code | VARCHAR(30) | No | Campus code | UNIQUE, normalized to uppercase |
| name | VARCHAR(150) | No | Display name | NOT NULL |
| city | VARCHAR(100) | Yes | City | — |
| status | VARCHAR(30) | No | Lifecycle state (`ACTIVE`/`INACTIVE`) | Default `ACTIVE` |
| created_at | TIMESTAMPTZ | No | Creation date | Default `now()` |
| updated_at | TIMESTAMPTZ | No | Last modification | Updated by JPA callbacks |
| deleted_at | TIMESTAMPTZ | Yes | Soft delete | NULL = active record |

### Table: environment_types

**Purpose:** Classification of spaces (aula, laboratory, library…). Also drives
threshold selection in monitoring (it is a business table, not a parameter catalog).

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| environment_type_id | UUID | No | Unique identifier | PK, default `gen_random_uuid()` |
| code | VARCHAR(30) | No | Type code | UNIQUE, normalized to uppercase |
| name | VARCHAR(80) | No | Display name | UNIQUE |
| description | VARCHAR(255) | Yes | Free-text description | — |
| created_at | TIMESTAMPTZ | No | Creation date | Default `now()` |
| updated_at | TIMESTAMPTZ | No | Last modification | Updated by JPA callbacks |
| deleted_at | TIMESTAMPTZ | Yes | Soft delete | NULL = active record |

> No `status` column: types are referenced by active lookups and soft-deleted only.

### Table: educational_environment

**Purpose:** The monitored physical space (classroom/aula). Central entity of the
domain; other domains reference it by UUID.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| educational_environment_id | UUID | No | Unique identifier | PK, default `gen_random_uuid()` |
| campus_id | UUID | No | Owning campus | FK → `campuses.campus_id` (RESTRICT) |
| code | VARCHAR(30) | No | Code within the campus | UNIQUE `(campus_id, code)`, uppercase |
| name | VARCHAR(120) | No | Display name | NOT NULL |
| environment_type_id | UUID | No | Classification | FK → `environment_types.environment_type_id` (RESTRICT) |
| floor | INTEGER | Yes | Floor number | CHECK `floor IS NULL OR floor >= 0` |
| area_m2 | NUMERIC(8,2) | Yes | Area in m² | CHECK `area_m2 IS NULL OR area_m2 > 0` |
| occupancy_capacity | INTEGER | Yes | Max occupancy | CHECK `occupancy_capacity IS NULL OR occupancy_capacity > 0` |
| status | VARCHAR(30) | No | Lifecycle state (`ACTIVE`/`INACTIVE`) | Default `ACTIVE` |
| created_at | TIMESTAMPTZ | No | Creation date | Default `now()` |
| updated_at | TIMESTAMPTZ | No | Last modification | Updated by JPA callbacks |
| deleted_at | TIMESTAMPTZ | Yes | Soft delete | NULL = active record |

**Relationships:**

- `campus_id` → FK to `campuses` (physical, intra-domain)
- `environment_type_id` → FK to `environment_types` (physical, intra-domain)
- Referenced by `sensors.*`, `monitoring.*` as **logical** UUID references only

### Indexes

| Name | Table | Fields | Justification |
|------|-------|--------|---------------|
| idx_educational_environment_campus | educational_environment | campus_id | Filter environments by campus |
| idx_educational_environment_type | educational_environment | environment_type_id | Filter by type |
| idx_educational_environment_status | educational_environment | status | Active/inactive listings |

---

## Modeling decisions

- **Soft delete keeps unique constraints:** `code` uniqueness spans soft-deleted
  rows (DB constraint is unconditional); a deleted campus code cannot be reused.
- **Status independent from soft delete:** `status = INACTIVE` + `deleted_at = NULL`
  is a valid intentional state (§6 of the canonical model).
- **No `created_by`:** attribution arrives with the gateway user context later;
  not needed for the MVP.

---

## Schema migration

**Tool:** Liquibase (via `spring-boot-starter-liquibase`)
**Script location:** `src/main/resources/db/changelog/` (`db.changelog-master.yaml` + `changes/`)
**Naming convention:** `NNN-description.yaml` per §12 of `06-data/domain/ms-classroom-management.md`

**Changesets:**

| ID | Content |
|----|---------|
| 000-create-schema | `CREATE SCHEMA IF NOT EXISTS classrooms` |
| 001-create-campuses | Table `campuses` |
| 002-create-environment-types | Table `environment_types` |
| 003-create-educational-environments | Table `educational_environment` |
| 004-add-environment-constraints | 2 FKs, unique `(campus_id, code)`, 3 CHECKs (raw SQL) |
| 005-create-indexes | 3 indexes |

**Rollback policy:** every changeset declares `<rollback>` (drop in reverse order);
verified against PostgreSQL 15 with `rollbackCount 6` → schema fully removed.
