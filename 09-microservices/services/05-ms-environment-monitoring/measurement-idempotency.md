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

## 3. Gap found in the current code (measured)

`MeasurementService.record` does `existsBy…` and then `save`. Two requests with the same key
that run at the same time both pass the check; the second `save` hits the unique constraint
and would surface as a server error instead of "duplicate".

Measured (section 9, test 3): 20 concurrent clients sending 10,000 readings over 200 distinct
keys with the current pattern produced **15, 24 and 22 unique-violation errors** in three
runs (0.15–0.24 %). The same load with `ON CONFLICT DO NOTHING` produced **0 errors**. Both
patterns ended with exactly 200 rows: the constraint never lets a duplicate be stored, the
defect is the error returned to the caller. The batch endpoint, which replays hundreds of
readings after an outage, makes the exposure larger.

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
same key is treated as a duplicate and **not** applied (verified: the second send returns no
row and the stored value stays unchanged). The service logs it at `WARN` with the
key so a faulty device can be detected. It is not an error for the caller.

## 5. Indexes — decision

| Index | Columns | Decision | Evidence (section 9) |
|-------|---------|----------|----------------------|
| `uq_environment_measurement_inst_var_time` | `(sensor_installation_id, variable_id, measured_at)` | **Keep** | Takes over every read once the duplicate is gone (42 scans in the test); serves idempotency. |
| `ix_environment_measurement_inst_var_time` | same three columns | **Drop** | Same query times with and without it (differences within noise). Removing it cuts insert time by ~29 % and index size by ~40 %. |
| `ix_environment_measurement_variable` | `(variable_id)` | **Drop** | 0 scans across all main queries. Removing it saves another ~13 % of insert time. |
| `ix_environment_measurement_time` | `(measured_at)` | **Keep** | Used by the 24 h history and the aggregation recompute window; also needed for retention. |
| `environment_measurement_pkey` | `(environment_measurement_id)` | **Keep** | Not used by the list queries, but needed to fetch a reading by id. |

Note: when the redundant index existed, the planner preferred it over the unique one, only
because it was smaller after being built in one pass (195 MB vs 348 MB for the unique index
built incrementally during loading). After `REINDEX` the unique index is also 195 MB and read
timings are identical. In production the unique index grows incrementally, so schedule a
`REINDEX … CONCURRENTLY` of it after the initial bulk load or any large backfill.

If ADR-020 partitioning lands first, apply the same decision to the partitioned table
(indexes defined on the parent are created per partition).

### changeSet (independent of partitioning)

```sql
--liquibase formatted sql
--changeset jhon-cortez:drop-redundant-measurement-indexes
DROP INDEX IF EXISTS environment_monitoring.ix_environment_measurement_inst_var_time;
DROP INDEX IF EXISTS environment_monitoring.ix_environment_measurement_variable;
--rollback CREATE INDEX ix_environment_measurement_inst_var_time ON environment_monitoring.environment_measurement (sensor_installation_id, variable_id, measured_at);
--rollback CREATE INDEX ix_environment_measurement_variable ON environment_monitoring.environment_measurement (variable_id);
```

No schema change is needed for idempotency itself: the constraint already exists. The file goes
in the canonical `10_indexes` folder of the service repository (ADR-008) and is applied by the
implementation task, not by this document.

## 6. Main queries

| # | Query | Access path |
|---|-------|-------------|
| Q1 | Idempotent insert (single and batch) | Unique index, `ON CONFLICT` |
| Q2 | Latest value per variable for an environment (`latestByEnvironment`) | `(installation, variable, measured_at)` via `installation_projection` |
| Q3 | History of an environment in `[from, to)`, optionally one variable, paged (`history`) | Same index plus range on `measured_at` |
| Q4 | Count of readings of active installations of an institution (`countByInstitution`) | Scan by installation |
| Q5 | Aggregation recompute: readings of the last 25 h grouped by 5-minute bucket, excluding `BAD` readings (ADR-020 job, per ADR-021 contract and the ADR-014 amendment) | `ix_environment_measurement_time` |
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
| T13 | Reading outside the variable's valid range (ADR-014 amendment 2026-10-30), sent twice | Stored once with `BAD`; no alert; first value kept on the retry |
| T14 | Aggregation recompute window with a `BAD` reading inside it | The `BAD` reading is excluded from the averages |

## 8. Open points handed to other tasks

| Point | Owner |
|-------|-------|
| Partitioned table, composite PK, retention | Issue #9 (ADR-020) |
| Batch payload, size limit, HTTP codes | Issue #3 (OpenAPI) |
| Rewrite `MeasurementService.record` and the adapter to use the atomic insert | Issue #6 |
| `06-data/domain/ms-environment-monitoring.md` section 14 still lists `educational_environment_id` and `measurement_at` columns that do not exist | Align when ADR-020 data model is merged |

## 9. Evidence: how the decisions were measured

Lab: disposable PostgreSQL 15.19 in Docker, real service DDL (`canonical/` files), 3,456,000
readings (50 environments × 4 variables × 2 days at 10 s), 50 installations. The service's own
SQL for Q2–Q4 was used unchanged; Q5 is the 25 h recompute from ADR-020/ADR-021.

**Test 1 — read queries, best of 3 runs (ms)**

| Query | All 3 indexes | Without redundant index | Without it + `REINDEX` of the unique index |
|-------|--------------:|------------------------:|-------------------------------------------:|
| Q2 latest per variable | 162.8 | 164.0 | 163.5 |
| Q3a 1 h, one variable | 2.5 | 2.5 | 2.5 |
| Q3b 24 h, all variables | 40.8 | 42.1 | 40.4 |
| Q4 count by institution | 661.5 | 665.7 | 665.1 |
| Q5 25 h, 5-min buckets | 1,674.6 | 1,694.3 | 1,660.3 |

Index scans over the whole workload: the variable index 0, the primary key 0, the time index 3–6.
At this volume (50 environments) the Q5 recompute takes ~1.7 s, acceptable for a job that runs
every 5 minutes.

**Test 2 — insert cost, 1,000,000 time-ordered rows, two runs each**

| Index set | Time | Index size |
|-----------|-----:|-----------:|
| Current (PK + unique + plain + variable + time) | 17.9 s / 17.9 s | 252 MB |
| Without the redundant index | 12.7 s / 12.8 s | 152 MB |
| Also without the variable index | 11.0 s / 11.0 s | 146 MB |

**Test 3 — concurrency**: see section 3 (15/24/22 errors vs 0).

**Limits of these measurements**
- One machine, one Docker container, warm cache; absolute times will differ on the VPS. The
  comparisons between variants are what matter. Re-run Test 2 on the VPS before the final
  deployment if capacity numbers depend on write throughput.
- Inserts were sequential and time-ordered; real traffic interleaves installations, so the
  absolute saving may differ.
- Data is synthetic and uniformly distributed.
- The race was modelled in PL/pgSQL with the same check-then-insert order as the service, not
  by calling the Java service. Test T2 (section 7) must confirm it end to end.

