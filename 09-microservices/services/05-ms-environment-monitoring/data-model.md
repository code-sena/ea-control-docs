# Data Model — ms-environment-monitoring

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables directly.

---

## Database engine

**Engine:** PostgreSQL 15
**Justification:** ADR-003 selects PostgreSQL for the MVP with one logical ownership
boundary per microservice. The monitoring domain needs `TIMESTAMPTZ` precision for
historical windows, numeric aggregates and `DISTINCT ON` / `date_trunc` bucketing over
large measurement volumes — all native to PostgreSQL.

**Schema:** `environment_monitoring`. Cross-domain references (`educational_environment_id`,
`variable_id`) are logical UUIDs without a foreign key, per ADR-003.

---

## Schema

### Table: environment_measurement

**Purpose:** Local atomic projection of accepted readings: one row per environment,
variable and instant.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| environment_measurement_id | UUID | No | Local projection identifier | PK, `gen_random_uuid()` |
| environment_id | UUID | No | Environment measured | Logical ref to `ms-classroom-management` |
| variable_id | UUID | No | Variable measured | Logical ref to `ms-sensor-management` |
| measured_value | NUMERIC(12,4) | No | Recorded value | |
| measured_at | TIMESTAMPTZ | No | Instant attributed to the reading | |
| quality_flag | VARCHAR(20) | Yes | Quality classification | |
| received_at | TIMESTAMPTZ | No | Projection receipt time | Default `now()` |

**Relationships:**
- `(environment_id, variable_id, measured_at)` → unique natural key used for
  idempotent projection.

### Read-only catalog replicas

The service also maintains local replicas of `variable`,
`educational_environment` and `variable_threshold`. They are lookup data only;
canonical administration remains with `ms-sensor-management` and
`ms-classroom-management`.

### Table: environmental_analysis

**Purpose:** Materializes one analysis request: which environment, which period and the
lifecycle state of the aggregation.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| environmental_analysis_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| educational_environment_id | UUID | No | Environment analyzed | Logical ref to `classrooms.educational_environment` |
| period_start | TIMESTAMPTZ | No | Inclusive start of the window | `CHECK period_start < period_end` |
| period_end | TIMESTAMPTZ | No | Exclusive end of the window | `CHECK period_start < period_end` |
| analysis_status_id | UUID | No | Lifecycle state | FK to `environment_monitoring.analysis_statuses` |
| requested_by | UUID | Yes | User that requested the analysis | Logical ref to `ms-security` / `ms-user-management` |
| computed_at | TIMESTAMPTZ | Yes | When the aggregation finished | NULL while PENDING/RUNNING |

**Relationships:**
- `educational_environment_id` → logical reference to `ms-classroom-management`
- `analysis_status_id` → FK to `analysis_statuses` (same schema)
- 1 ─── N `analysis_result`

### Table: analysis_result

**Purpose:** Aggregated outcome of an analysis, one row per variable.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| analysis_result_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| environmental_analysis_id | UUID | No | Owning analysis | FK to `environmental_analysis` (ON DELETE CASCADE) |
| variable_id | UUID | No | Variable aggregated | Logical ref to `sensors.variable` |
| min_value | NUMERIC(12,4) | No | Lowest sample in the window | |
| max_value | NUMERIC(12,4) | No | Highest sample in the window | |
| avg_value | NUMERIC(12,4) | No | Average sample in the window | |
| sample_count | INTEGER | No | Amount of aggregated samples | |
| exceedance_count | INTEGER | No | Samples outside the active warning threshold | |

**Relationships:**
- `environmental_analysis_id` → FK to `environmental_analysis` (same schema)
- `variable_id` → logical reference to `ms-sensor-management`

### Table: analysis_statuses

**Purpose:** Lookup catalog of the analysis lifecycle.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| analysis_status_id | UUID | No | Unique identifier | PK |
| code | VARCHAR | No | Status code | Unique, not null |
| name | VARCHAR | No | Display name | |

**Seeded values:** `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`.

### Indexes

| Name | Fields | Type | Justification |
|------|--------|------|---------------|
| idx_environmental_analysis_environment | (educational_environment_id, period_start) | BTREE | "Latest analyses of an environment" — the dashboard entry point |
| idx_environmental_analysis_period | (period_start, period_end) | BTREE | Window overlap checks when detecting duplicate requests |
| uq_analysis_result_period_variable | (environmental_analysis_id, variable_id) | UNIQUE | One aggregated row per variable; also serves as the lookup index |

`analysis_result` needs no extra index: its `UNIQUE (environmental_analysis_id, variable_id)`
constraint already provides the index used to load results of an analysis.

---

## Modeling decisions

- **The period is stored as a window, not as an enum:** `period_start` / `period_end`
  materialize the concrete window. The requested granularity (`DAY`, `WEEK`, `MONTH`,
  `YEAR`) is resolved into that window by the domain and is not persisted, because the
  stored window is the authoritative, self-describing artifact and stays correct even
  if the resolution rules change.
- **No denormalized copy of the threshold:** `exceedance_count` is computed with the
  threshold that was active at query time, so thresholds are never duplicated into the
  analysis rows (ADR-014 rule 6 — thresholds are invalidated with `valid_to`, never
  deleted or rewritten).
- **Raw measurements remain the source of truth:** `environmental_analysis` is a
  materialized view of `environment_measurement`, not a replacement. Deleting an
  analysis never destroys history.
- **`analysis_result` cascades from its analysis:** an analysis without results has no
  analytical meaning, so results are removed with their analysis.

---

## Schema migration

**Tool:** Liquibase (ADR-008)
**Script location:** `ms-environment-monitoring/src/main/resources/db/changelog/`
**Naming convention:** `db.changelog-master.yaml` with `changes/NNN-<verb>-<noun>.yaml`
and canonical SQL under `canonical/`.

**Current changesets.** The service owns a separate Liquibase history for the
`environment_monitoring` schema:

| Change | File |
|--------|------|
| Schema | `canonical/01_schemas/001_schemas.sql` |
| Read model and consumer inbox | `canonical/03_tables/02_read_model/001_environment_measurement.sql`, `002_inbox_message.sql` |
| Local catalog replicas | `canonical/03_tables/01_catalogos/001_variable.sql`, `002_educational_environment.sql`, `003_variable_threshold.sql` |
| Analysis core | `canonical/03_tables/03_analisis/001_analysis_statuses.sql`, `002_environmental_analysis.sql`, `003_analysis_result.sql` |
| Indexes | `canonical/10_indexes/001_indexes.sql` |
| Reference seeds | `changes/010-seed-reference.yaml` |

This history recreates the model in the service-owned namespace; it does not
reuse the monolith DDL in place.

**Rollback policy:**
- Liquibase supports rollback for most change types.
- Use explicit `rollback` blocks within changesets.
- Already executed changesets must never be modified.