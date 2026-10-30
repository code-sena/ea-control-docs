# Measurement Idempotency and Data Model — ms-environment-monitoring

> **Scope:** persistence rules that let a measurement be sent more than once without being
> stored more than once. Covers the key, atomic insert, indexes, main queries and the
> integrity tests. Plan reference: PLAN-001, Issue #4.
>
> **Out of scope:** partitioning, raw retention and aggregation tables (ADR-020, Issue #9) and
> the batch payload and HTTP codes (OpenAPI, Issue #3). Everything here holds with or without
> partitioning.

- **Date:** 2026-10-30
- **Authors:** Jhon-Cortez
- **Related:** ADR-021 (offline buffer, device-side `measuredAt`), ADR-020 (storage), ADR-007

---

## 1. Why this is needed

With the offline buffer of ADR-021, the node re-sends readings after outages and after `5xx`
or `429` answers. The same reading will reach the service more than once, sometimes
concurrently. Persistence must turn "N sends" into "1 row" without raising an error.

## 2. Identity of a measurement

| Concept | Definition |
|---------|------------|
| Natural key (idempotency) | `(sensor_installation_id, variable_id, measured_at)` |
| Enforced by | `UNIQUE` constraint `uq_environment_measurement_inst_var_time` (already deployed) |
| Technical id | `environment_measurement_id` (UUID). Identifies a stored row for the API (`MeasurementView.id`). It is **not** the idempotency key. |
| `measured_at` | Whole seconds, UTC, set by the device (ADR-021). Stored as received. |

Under ADR-020 partitioning the primary key becomes the natural key (PostgreSQL requires the
partition column in every unique key). The technical id stays as a column. The rules below do
not change.

## 3. Gap found in the current code

`MeasurementService.record` does `existsBy…` and then `save`. Two requests with the same key
that run at the same time both pass the check; the second `save` hits the unique constraint
and surfaces as a server error instead of "duplicate". The batch endpoint multiplies this
problem. The fix is to let the database decide, atomically.

## 4. Persistence rule

A reading is written with a single statement and the number of rows actually inserted decides
what happens next:

```sql
INSERT INTO environment_monitoring.environment_measurement
    (environment_measurement_id, sensor_installation_id, variable_id,
     measured_value, measured_at, quality_flag_id, created_at)
VALUES (:id, :installation, :variable, :value, :measured_at, :quality, now())
ON CONFLICT (sensor_installation_id, variable_id, measured_at) DO NOTHING
RETURNING environment_measurement_id;
```

- One row returned → inserted. Evaluate alerts for it, in the same transaction (existing rule).
- No row returned → duplicate. Success, no side effects, **no alert evaluation**.
- Batch: one multi-row statement (`INSERT … SELECT FROM unnest(:ids, :installations, …)`) with
  the same `ON CONFLICT … DO NOTHING RETURNING …`. The result separates `inserted` from
  `duplicate` per reading. Maximum batch size is defined by the OpenAPI contract (Issue #3).

### Same key, different value

First write wins. Measurements are immutable (`06-data` rule: "keep historical measurements
immutable from the point of insertion"), so a later send with another `measured_value` for the
same key is treated as a duplicate and **not** applied. The service logs it at `WARN` with the
key so a faulty device can be detected. It is not an error for the caller.

## 5. Indexes

| Index | Columns | Status | Notes |
|-------|---------|--------|-------|
| `uq_environment_measurement_inst_var_time` | `(sensor_installation_id, variable_id, measured_at)` | Keep | Unique index created by the constraint. Serves idempotency, latest-value and history queries. |
| `ix_environment_measurement_inst_var_time` | same three columns | **Redundant — propose drop** | Duplicates the unique index above. It doubles index writes on the highest-volume table and adds no read benefit. |
| `ix_environment_measurement_time` | `(measured_at)` | Keep | Needed by the aggregation recompute window (ADR-020/ADR-021 contract) and by retention. |
| `ix_environment_measurement_variable` | `(variable_id)` | **Low value — verify, then drop** | Queries always filter by installation first (through `installation_projection`); a single-column low-cardinality index costs writes and is unlikely to be chosen. |

Rule: drop an index only after `EXPLAIN (ANALYZE, BUFFERS)` of the main queries (section 6)
shows it is unused. If ADR-020 partitioning lands first, apply the same decision to the
partitioned table; indexes defined on the parent are created per partition.

### Proposed changeSet (independent of partitioning)

```sql
--liquibase formatted sql
--changeset jhon-cortez:drop-redundant-measurement-indexes
DROP INDEX IF EXISTS environment_monitoring.ix_environment_measurement_inst_var_time;
-- DROP INDEX IF EXISTS environment_monitoring.ix_environment_measurement_variable;
--   ^ enable only after EXPLAIN confirms it is unused.
--rollback CREATE INDEX ix_environment_measurement_inst_var_time ON environment_monitoring.environment_measurement (sensor_installation_id, variable_id, measured_at);
--rollback CREATE INDEX ix_environment_measurement_variable ON environment_monitoring.environment_measurement (variable_id);
```

No schema change is needed for idempotency itself: the constraint already exists. Liquibase
(ADR-008) rules apply: the file goes in the canonical `10_indexes` folder of the service
repository and is applied by the implementation task, not by this document.

## 6. Main queries

| # | Query | Access path |
|---|-------|-------------|
| Q1 | Idempotent insert (single and batch) | Unique index, `ON CONFLICT` |
| Q2 | Latest value per variable for an environment (`latestByEnvironment`) | `(installation, variable, measured_at)` via `installation_projection` |
| Q3 | History of an environment in `[from, to)`, optionally one variable, paged (`history`) | Same index plus range on `measured_at` |
| Q4 | Count of readings of active installations of an institution (`countByInstitution`) | Scan by installation |
| Q5 | Aggregation recompute: readings of the last 25 h grouped by 5-minute bucket (ADR-020 job, per ADR-021 contract) | `ix_environment_measurement_time` |
| Q6 | Retention: readings older than the raw retention period | Partition drop (ADR-020), otherwise `ix_environment_measurement_time` |

## 7. Integrity tests to implement (Issue #6 and #13)

Run them against real PostgreSQL (Testcontainers), not H2, because they depend on
`ON CONFLICT` and on concurrency.

| ID | Case | Expected |
|----|------|----------|
| T1 | Same reading sent twice, sequentially | 1 row; second call reports duplicate; no error |
| T2 | Same reading sent by 20 threads at once | 1 row; no unique-violation error reaches the caller |
| T3 | Batch with 10 new + 5 already stored readings | 10 inserted, 5 duplicate, 15 results |
| T4 | Same batch sent twice | Second time: 0 inserted, all duplicate |
| T5 | Duplicate inside the same batch | Stored once; counted once as duplicate |
| T6 | Same key, different `measured_value` | Stored value unchanged; `WARN` logged; counted as duplicate |
| T7 | Same instant and variable, different installation | Both rows stored |
| T8 | Same installation and instant, different variable | Both rows stored |
| T9 | Duplicate reading | No new alert is created |
| T10 | Batch where one reading fails validation | Valid readings stored; failing one reported individually |
| T11 | Failure after the insert (alert evaluation throws) | Whole transaction rolls back: no row and no alert |
| T12 | `measured_at` is `NULL` | Rejected before reaching the database; column stays `NOT NULL` |

## 8. Open points handed to other tasks

| Point | Owner |
|-------|-------|
| Partitioned table, composite PK, retention | Issue #9 (ADR-020) |
| Batch payload, size limit, HTTP codes | Issue #3 (OpenAPI) |
| Rewrite `MeasurementService.record` and the adapter to use the atomic insert | Issue #6 |
| `06-data/domain/ms-environment-monitoring.md` section 14 still lists `educational_environment_id` and `measurement_at` columns that do not exist | Align when ADR-020 data model is merged |
