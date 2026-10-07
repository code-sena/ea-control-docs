# ms-monitoreo

> Environmental data collection and analysis. Owns the environmental measurements,
> threshold evaluation and the materialized historical analyses consumed by the dashboard.

## Service sheet

| Field | Value |
|-------|-------|
| Number in catalog | 05 |
| Local port | 3003 |
| Repository | `EduAirControl` (`Web/backend`, module `analysis`) |
| Owner team | Development Team |
| DB engine | PostgreSQL 15 (`monitoring` schema) |
| Status | In development |

## Responsibility

`ms-monitoreo` is the authoritative owner of:

```text
environment_measurement
environmental_analysis
analysis_result
```

One sentence: **it records environmental readings and turns them into historical
analysis per period for an educational environment.**

### Responsibilities (what this service DOES)

- Ingest environmental measurements coming from sensors.
- Evaluate the active threshold per variable and environment type.
- Resolve the analysis period (`DAY`, `WEEK`, `MONTH`, `YEAR`) into a concrete
  `[period_start, period_end)` window in UTC.
- Materialize the aggregation of a period into `environmental_analysis` plus one
  `analysis_result` row per variable (min, max, avg, sample count, exceedance count).
- Publish the internal domain event `EnvironmentalDataAnalyzed`.
- Serve the dashboard summary and series queries.

### Out of scope

- Educational environments, environment types and campuses — owned by `ms-aulas`.
- Sensors, installations and the variable catalog — owned by `ms-sensores`.
- Alert generation and lifecycle — owned by `ms-alert`.
- User preferences and experience — owned by `ms-user-experience`.

## Main endpoints

Base path `/api/v1`. Full contract: [ms-monitoreo.yaml](../../../07-api/contracts/openapi/ms-monitoreo.yaml).

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