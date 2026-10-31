# ADR-020 — Storage, Retention and Aggregations

- **ID:** ADR-020
- **Date:** 2026-10-29
- **Status:** Accepted
- **Authors:** EduAirControl Development Team (Jota, Mariangel)

---

## Context

EduAirControl stores one atomic measurement per (installation, variable, timestamp) in `environment_monitoring.environment_measurement` (ADR-003, ADR-007). With 4 variables measured every 10 seconds, one environment generates ~34,560 rows/day (~12.6 M/year); 50 environments amount to ≈ 95 GB/year at ~150 bytes/row. Without a strategy, linear growth degrades historical queries, backups, and VPS costs (R-018, R-019). In addition, the frontend needs averages for long periods without scanning millions of rows.

**Known constraints:**
- PostgreSQL 15 is the database engine (ADR-003); Liquibase is used for migrations (ADR-008).
- `measured_at TIMESTAMPTZ` is the actual measurement timestamp (never replaced); `created_at` is the persistence timestamp.
- Idempotency by `(sensor_installation_id, variable_id, measured_at)` (UNIQUE).
- Team of 3, VPS KVM 2 (2 vCPU, 8 GB RAM, 100 GB NVMe).
- Delivery date 2026-11-06: retention, averages (5 min, 1 h, 1 day), and historical queries are mandatory.

---

## Decision

**We decided:** Keep atomic measurements in `environment_measurement` (without a wide row), partition that table by `measured_at` range (monthly), enforce **retention by dropping partitions** (raw data for 90 days), and materialize **aggregation tables** (`measurement_agg_5m`, `measurement_agg_1h`, `measurement_agg_1d`) populated by a scheduled job. Historical queries use the coarsest aggregation that covers the requested range.

**Justification:**
PostgreSQL supports native declarative partitioning (since v10), making the removal of old partitions O(1) and avoiding massive DELETE operations (bloat, WAL, vacuum). Aggregation tables turn queries over millions of rows into queries over thousands. `measured_at` (not `created_at`) is the partition key because it reflects the actual measurement timestamp and allows historical data to be reprocessed.

### What is a "bucket" and why this decision

A **bucket** is a fixed time window (e.g., 5 minutes, 1 hour, 1 day) into which raw measurements are grouped to pre-compute `avg`, `min`, `max`, and `count` per `(installation, variable, bucket)`. Instead of scanning millions of raw rows for a 30-day chart, the query reads ~8,640 buckets (30 days × 24 h × 12 buckets/h for 5-min granularity). This is a standard time-series aggregation pattern: it trades storage (duplicate aggregated rows) for query speed and VPS resource savings. The three granularities (5 min, 1 h, 1 day) form a cascade: each coarser level is built from the previous one, so a single 5-min bucket feeds both the hourly and daily aggregates.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|---|---|---|---|
| **Monthly partitioning + retention by dropping partitions + aggregation tables (selected)** | O(1) partition removal, inexpensive aggregations, fast queries, no bloat | More tables, an aggregation job, partition management | Selected for its cost-benefit balance on the VPS |
| Retention using DELETE with cron | Simple, no partitions | Slow, bloat, heavy vacuuming, risk of locks | Rejected due to performance at high volume |
| MongoDB / external TSDB | Optimized for time series | New infrastructure, additional operations, out of scope (the plan excludes MongoDB) | Rejected due to scope and the team of 3 |
| Single materialized views | Fewer tables | Expensive refresh, no granular retention | Rejected: does not allow raw data partition removal or fine-grained control |

---

## Consequences

**Positive:**
- Removing old partitions is O(1) (no bloat or massive vacuuming).
- Large historical queries use aggregations (thousands of rows instead of millions).
- Retention is configurable by granularity (raw: 90 days, 5 min: 180 days, 1 h: 1 year, 1 day: 5 years).
- Using `measured_at` as the partition key preserves the ability to reprocess data.
- `environment_measurement_id` remains an identifier of the measurement (exposed as `MeasurementView.id` in the API); it is **not** the primary key. The PK is the composite `(sensor_installation_id, variable_id, measured_at)`. `environment_alert.triggering_measurement_id` has no FK today, so this change breaks nothing.
- Verifiable: the Liquibase migration creates `environment_measurement` partitioned by month, 3 aggregation tables, and indexes.
- Verifiable: automatic monthly partitioning — the job creates partitions for the next 3 months (query `pg_partition_tree` or `pg_inherits`).
- Verifiable: retention — partitions with `measured_at < now() - 90 days` are removed (verifiable with `SELECT count(*) FROM pg_inherits`).
- Verifiable: 5-minute aggregation — after inserting 10 measurements into a bucket, `measurement_agg_5m` contains 1 row with `sample_count=10` and the correct `avg_value`.
- Verifiable: aggregation idempotency — rerunning the job does not duplicate rows (upsert).
- Verifiable: historical query — `/measurements` and `/environments/{id}/measurements` use the appropriate aggregation for the requested range (verifiable through the execution plan/logs).
- Verifiable: performance — a 30-day query against the 1-hour aggregation responds in < 1 s with 50 environments (measure on the VPS).

**Negative / Trade-offs:**
- More tables and Liquibase migrations.
- An aggregation job (Spring `@Scheduled` or Quartz) that requires monitoring.
- Management of future partitions (create new partitions automatically or manually).
- Data duplication (raw data + aggregations).

**Impact on the system:**
- Affected services: `ms-environment-monitoring` (owner of measurements and aggregations), PostgreSQL.
- Documents to update: `06-data/domain/ms-environment-monitoring.md`, `05-architecture/overview.md`, `13-operations/observability.md`.
- New tables: `environment_measurement` (partitioned), `measurement_agg_5m`, `measurement_agg_1h`, `measurement_agg_1d`.

---

## Detailed design

**1. Partitioning `environment_measurement`**

```sql
CREATE TABLE environment_monitoring.environment_measurement (
    environment_measurement_id UUID NOT NULL,
    sensor_installation_id     UUID NOT NULL,
    variable_id                UUID NOT NULL,
    measured_value             NUMERIC(12,4) NOT NULL,
    measured_at                TIMESTAMPTZ NOT NULL,
    quality_flag_id            UUID NOT NULL,
    created_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT pk_environment_measurement PRIMARY KEY (sensor_installation_id, variable_id, measured_at)
) PARTITION BY RANGE (measured_at);
```

- Monthly partitions: `environment_measurement_2026_10`, `..._2026_11`, etc.
- The composite PK includes `measured_at` (required by PostgreSQL for partitioned tables).
- The original UNIQUE constraint `(sensor_installation_id, variable_id, measured_at)` becomes the partitioned table's PK (idempotency is preserved).
- `environment_measurement_id` remains an identifier of the measurement (exposed as `MeasurementView.id` in the API); it is not the PK.

**2. Retention (by dropping partitions)**

| Granularity | Table | Retention | Mechanism |
|---|---|---|---|
| Raw | `environment_measurement` | > 90 days | Drop monthly partition when `measured_at < now() - 90 days` |
| 5 min | `measurement_agg_5m` | 180 days | DELETE by range (manageable volume) or partition drop |
| 1 hour | `measurement_agg_1h` | 1 year | DELETE by range |
| 1 day | `measurement_agg_1d` | 5 years | DELETE by range |

Retention job: a daily `@Scheduled` job (03:00 UTC) that executes `DROP TABLE ..._YYYY_MM` for expired partitions and `DELETE` on aggregations.

**3. Aggregation tables**

```sql
CREATE TABLE environment_monitoring.measurement_agg_5m (
    sensor_installation_id UUID NOT NULL,
    variable_id            UUID NOT NULL,
    bucket_start           TIMESTAMPTZ NOT NULL,   -- truncated to 5 min
    avg_value              NUMERIC(12,4) NOT NULL,
    min_value              NUMERIC(12,4) NOT NULL,
    max_value              NUMERIC(12,4) NOT NULL,
    sample_count           INTEGER NOT NULL,
    PRIMARY KEY (sensor_installation_id, variable_id, bucket_start)
);
```

Equivalent tables are used for `measurement_agg_1h` (1-hour buckets) and `measurement_agg_1d` (1-day buckets).

**4. Aggregation job**

- Spring `@Scheduled` every 5 minutes (or Quartz if persistence is required).
- In each run, **recalculate the buckets of the last 25 hours** from raw data using idempotent upsert (`INSERT ... ON CONFLICT (PK) DO UPDATE`), so that measurements arriving late (e.g., from a node returning after a temporary outage of up to 24 h) are incorporated into already-closed buckets.
- Propagate the cascade: `measurement_agg_5m` → `measurement_agg_1h` → `measurement_agg_1d`.
- Idempotent: upsert by bucket PK.

**5. Historical queries**

The service selects the granularity according to the requested range:
- ≤ 24 h → raw (`environment_measurement`).
- ≤ 7 days → `measurement_agg_5m`.
- ≤ 90 days → `measurement_agg_1h`.
- > 90 days → `measurement_agg_1d`.

The frontend (dashboard, analytics) receives aggregated data for long periods (plan D5). Historical endpoints: `/measurements` and `/environments/{id}/measurements` (the previously cited `/api/v1/environmental-data` does not exist in the OpenAPI contract).

---

## Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Partition not created in time → insertion fails | Medium | High | Job that creates future partitions (3 months ahead) + alert |
| Aggregation job falls behind → missing data | Medium | Medium | Monitor lag; rerun idempotently (25 h recalculation) |
| Accidental removal of a partition containing valid data | Low | High | Validate `measured_at < now() - retention` before dropping; dry run |
| Aggregation growth | Low | Medium | Retention defined by granularity; monitor size |

---

## References

- Plan PLAN-001 §7 (estimates), §D4-D5 (implementation), §11 (acceptance criteria).
- ADR-003 (Database Strategy), ADR-007 (Outbox), ADR-008 (Liquibase), ADR-014 (Variables/Thresholds).
- PostgreSQL declarative partitioning: https://www.postgresql.org/docs/15/ddl-partitioning.html

---

### Plan de ejecución
1. Crear `Docs-ea-control/05-architecture/decisions/records/ADR-020-storage-retention-and-aggregations.md` con el contenido anterior.
2. Añadir fila en `Docs-ea-control/05-architecture/decisions/README.md`: `| ADR-020 | Storage, Retention and Aggregations | Accepted | 2026-10-29 |`.
3. Añadir fila en `Docs-ea-control/05-architecture/README.md` (índice ADR): `| ADR-020 | Storage, Retention and Aggregations | Accepted |`.
4. Commit en rama `docs/adr-020-storage-retention` → push → PR a `main`.

¿Apruebas? Sal del modo plan y lo escribo.<|end|><|start|>user<|channel|>hazlo <|end|><|start|><|start|>assistant<|channel|>analysis<|message|>Build mode now. Let me write the ADR-020 file, update the two README index files, commit, and push. I'll do all of this now.

First, write the ADR file. I have the full content from my previous response. Let me write it to the file.<|end|><|start|><|repo_name|>assistant to=bash<|channel|>analysis <|constrain|>xml<|message|><rfl:parameter name="command">
cd Docs-ea-control; git checkout -b docs/adr-020-storage-retention main 2>&1 | Select-Object -Last 2