# ms-environment-monitoring

> Environmental data collection and analysis. Owns the environmental measurements,
> threshold evaluation and the materialized historical analyses consumed by the dashboard.

## Service sheet

| Field | Value |
|-------|-------|
| Number in catalog | 05 |
| Local port | 3003 |
| Repository | `ms-environment-monitoring` (standalone service repository) |
| Owner team | Development Team |
| DB engine | PostgreSQL 15 (`environment_monitoring` schema) |
| Status | In development |

## Responsibility

`ms-environment-monitoring` is the authoritative owner of:

```text
environment_measurement
environmental_analysis
analysis_result
```

One sentence: **it projects environmental readings and turns them into historical
analysis per period for an educational environment.**

### Responsibilities (what this service DOES)

- Consume `EnvironmentalDataRecorded` from `ms-sensor-management` through RabbitMQ.
- Maintain a local atomic projection of measurements plus read-only catalog replicas.
- Evaluate the replicated warning threshold active for each variable and environment type.
- Resolve the analysis period (`DAY`, `WEEK`, `MONTH`, `YEAR`) into a concrete
  `[period_start, period_end)` window in UTC.
- Materialize the aggregation of a period into `environmental_analysis` plus one
  `analysis_result` row per variable (min, max, avg, sample count, exceedance count).
- Publish the internal domain event `EnvironmentalDataAnalyzed`.
- Serve the dashboard summary and series queries.

### Out of scope

- Educational environments, environment types and campuses — owned by `ms-classroom-management`.
- Sensors, installations and the variable catalog — owned by `ms-sensor-management`.
- Alert generation and lifecycle — owned by `ms-alert`.
- User preferences and experience — owned by `ms-user-experience`.

## Main endpoints

Base path `/api/v1`. Full contract: [ms-environment-monitoring.yaml](../../../07-api/contracts/openapi/ms-environment-monitoring.yaml).

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/analyses` | Request and compute the analysis of an environment for a period |
| GET | `/analyses` | List analyses, filterable by environment, period and status |
| GET | `/analyses/{id}` | Get one analysis with its per-variable results |
| GET | `/dashboard/summary` | Counts and averages for the dashboard |
| GET | `/dashboard/series` | Aggregated historical series |

## Analysis lifecycle

```text
POST /analyses
      │
      ├─ persist PENDING ──► RUNNING ──► COMPLETED   (aggregation ok)
      │                                  └───────► FAILED  (aggregation error)
      └─ response already contains results when COMPLETED
```

The computation is synchronous: the state machine is persisted for traceability and
failure recording, but the caller does not have to poll for the results.

Period resolution is deterministic and anchored on `referenceDate` (UTC), which makes
`DAY`, `WEEK`, `MONTH` and `YEAR` reproducible and unit-testable.

## Documents

| Document | Content |
|----------|---------|
| [data-model.md](data-model.md) | Tables owned by this service and modeling decisions |
| [events.md](events.md) | Published and consumed events |
| [decisions.md](decisions.md) | Internal technical decisions of the service |
| [runbook.md](../../_template/service/runbook.md) | Operational procedures — template, required before the first deploy to staging |