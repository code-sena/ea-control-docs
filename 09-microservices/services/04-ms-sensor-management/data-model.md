# Data Model — ms-sensor-management

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables directly; they reference them by
> logical UUID (ADR-003) and go through this service's API.

---

## Database engine

**Engine:** PostgreSQL
**Justification:** Referential integrity (FKs, composite PK, uniqueness) for a
registry domain with an installation history, consistent with the MVP platform
choice (ADR-003). One schema per service in a shared instance.

**Schema:** `sensors` (created by changeset `000-create-schema`).

---

## Schema

### Table: sensor

**Purpose:** Registered environmental sensor device.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| sensor_id | UUID | No | Unique identifier | PK, default `gen_random_uuid()` |
| serial_number | VARCHAR(60) | No | Device serial | UNIQUE, stored as provided |
| sensor_model_id | UUID | No | Model reference | NOT NULL, **logical** (excluded catalog) |
| sensor_status_id | UUID | No | Status reference | NOT NULL, **logical** (excluded catalog) |
| last_seen_at | TIMESTAMPTZ | Yes | Last contact | — |
| created_at | TIMESTAMPTZ | No | Creation date | Default `now()` |
| updated_at | TIMESTAMPTZ | Yes | Last modification | Updated by JPA callbacks |

> No soft delete (`deleted_at`) and no status column: lifecycle status lives in
> the excluded `sensor_statuses` catalog (logical `sensor_status_id`).

### Table: sensor_installation

**Purpose:** Historical record of where and when a sensor has been installed.
Rows are never deleted — they are closed with `removed_at`.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| sensor_installation_id | UUID | No | Unique identifier | PK, default `gen_random_uuid()` |
| sensor_id | UUID | No | Installed sensor | FK → `sensor.sensor_id` (RESTRICT) |
| educational_environment_id | UUID | No | Target space | NOT NULL, **logical** (classrooms domain) |
| installed_at | TIMESTAMPTZ | No | Installation date | NOT NULL |
| removed_at | TIMESTAMPTZ | Yes | Removal date | NULL = active installation |

**Relationships:**

- `sensor_id` → FK to `sensor` (physical, intra-domain)
- `educational_environment_id` → **logical** UUID reference to
  `classrooms.educational_environment` (no FK across schemas)

### Table: variable

**Purpose:** Measured variable catalog owned by this service (CO₂, humidity, noise,
temperature… per ADR-014).

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| variable_id | UUID | No | Unique identifier | PK, default `gen_random_uuid()` |
| code | VARCHAR(30) | No | Variable code | UNIQUE, normalized to uppercase |
| name | VARCHAR(80) | No | Display name | NOT NULL |
| measurement_unit_id | UUID | No | Unit reference | NOT NULL, **logical** (excluded catalog) |
| description | VARCHAR(255) | Yes | Free text | — |
| created_at | TIMESTAMPTZ | No | Creation date | Default `now()` |

> No `updated_at`: the reference model does not track variable edits.

### Table: sensor_variable

**Purpose:** N:M association — which variables a sensor measures.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| sensor_id | UUID | No | Associated sensor | PK part, FK → `sensor.sensor_id` (CASCADE) |
| variable_id | UUID | No | Associated variable | PK part, FK → `variable.variable_id` (RESTRICT) |

**Relationships:**

- `(sensor_id, variable_id)` → composite PK (uniqueness by construction)
- `sensor_id` FK CASCADE (associations go away with the sensor)
- `variable_id` FK RESTRICT (a measured variable cannot be deleted while in use)

### Indexes

| Name | Table | Fields | Justification |
|------|-------|--------|---------------|
| idx_sensor_installation_sensor_installed | sensor_installation | sensor_id, installed_at | History per sensor |
| idx_sensor_installation_environment_installed | sensor_installation | educational_environment_id, installed_at | History per space |

---

## Modeling decisions

- **No soft delete in this domain** (§12 of the canonical model): `DELETE` is
  physical and guarded — a sensor with installation history returns `409`; a
  variable referenced by associations returns `409`.
- **Installations are history, not lifecycle:** they are closed
  (`removed_at = now()`), never deleted; at most one open installation per sensor.
- **Catalogs are excluded:** `sensor_model_id`, `sensor_status_id`, and
  `measurement_unit_id` are UUID-only logical references (see decisions.md
  DEC-007).
- **Case handling:** variable `code` is uppercased; `serial_number` is stored as
  provided (device serials are case-sensitive).

---

## Schema migration

**Tool:** Liquibase (via `spring-boot-starter-liquibase`)
**Script location:** `src/main/resources/db/changelog/` (`db.changelog-master.yaml` + `changes/`)
**Naming convention:** `NNN-description.yaml` (same pattern as §12 of the
canonical models)

**Changesets:**

| ID | Content |
|----|---------|
| 000-create-schema | `CREATE SCHEMA IF NOT EXISTS sensors` |
| 001-create-sensor | Table `sensor` |
| 002-create-sensor-installation | Table `sensor_installation` |
| 003-create-variable | Table `variable` |
| 004-create-sensor-variable | Table `sensor_variable` + composite PK |
| 005-add-foreign-keys | 3 FKs (RESTRICT / CASCADE / RESTRICT, raw SQL) |
| 006-create-indexes | 2 composite indexes |

**Rollback policy:** every changeset declares `<rollback>` (drop in reverse
order); verified against PostgreSQL 15 with `rollbackCount 7` → schema fully
removed.
