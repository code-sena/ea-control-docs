# Decisions — ms-monitoreo

> Internal technical decisions of the service that complement the global ADRs.
> Format follows `09-microservices/_template/service/decisions.md`.

---

## [DEC-001] Synchronous analysis with a persisted state machine

**Date:** 2026-09-05
**Status:** Active

**Context:** `environmental_analysis.analysis_status_id` models a lifecycle
(`PENDING` → `RUNNING` → `COMPLETED` | `FAILED`), which suggests an asynchronous job.
The user stories HU-ANA-001 … HU-ANA-004 are synchronous reads: the user selects a
period and the system displays the information, or states that no data exists.

**Decision:** Compute the analysis inside the request. The lifecycle is still persisted
so the state is auditable and failures are recorded, but the caller does not poll:
`POST /analyses` returns `201` with the results already computed.

**Alternatives:**
- `@Scheduled` poller consuming `PENDING` rows — rejected for now: it adds observable
  latency to every analysis, requires a reconciler that must be operated, and makes the
  integration tests time-dependent.
- Transactional outbox + worker (ADR-007) — deferred: the broker is `Planned`, and a
  worker is not justified while the computation is a single aggregate query.

**Consequences:**
- ✅ The user stories are satisfied without a polling loop in the frontend.
- ✅ Failures are recorded as `FAILED` instead of silently disappearing.
- ✅ The state machine stays compatible with a future asynchronous worker.
- ⚠️ Request latency grows with the size of the analyzed window.
- ⚠️ `PENDING` is never observed by clients today; the state remains as groundwork.

---

## [DEC-002] Period resolution is pure domain logic anchored on a reference date

**Date:** 2026-09-05
**Status:** Active

**Context:** `DAY`, `WEEK`, `MONTH` and `YEAR` must resolve to a concrete
`[period_start, period_end)` window. Resolving against "now" makes results
irreproducible and impossible to unit-test deterministically.

**Decision:** A pure domain service `PeriodResolver` maps `(period, referenceDate)` to a
window in UTC. `referenceDate` is optional in the request and defaults to the current
date; when provided it makes the computation reproducible.

**Alternatives:**
- Resolve with the JVM default zone — rejected: the same request would produce different
  windows depending on the server configuration.
- Store the granularity in the table — rejected: see the modeling decision in
  [data-model.md](data-model.md); the window is the authoritative artifact.

**Consequences:**
- ✅ Unit-testable without Spring, a database or a fixed clock.
- ✅ Window boundaries are explicit and auditable (`period_start` inclusive,
  `period_end` exclusive).
- ⚠️ The stored window does not record which granularity produced it, so a `WEEK` and a
  `7-day` window are indistinguishable after the fact.

---

## [DEC-003] Aggregation is read through a port owned by the analysis module

**Date:** 2026-09-05
**Status:** Active

**Context:** `environment_measurement` is owned by the monitoring side of
`ms-monitoreo`. ADR-002 requires the monitoring and analysis modules to stay internally
separated, with separate ports, use cases and contracts. ADR-003 forbids one module from
manipulating another module's tables directly.

**Decision:** The analysis module declares an outbound port for aggregated measurements
and the module that owns the measurements provides the adapter. The analysis use case
never touches `EnvironmentMeasurementRepository`.

**Consequences:**
- ✅ The analysis module can be extracted into its own deployable by replacing the port.
- ✅ The aggregation query stays close to the data it aggregates.
- ⚠️ One more port to maintain in the shared contract package.

---

## [DEC-004] Analysis and monitoring live in separate application modules

**Date:** 2026-09-05
**Status:** Active

**Context:** ADR-002 states that `ms-monitoreo` initially owns both Environmental
Monitoring and Environmental Data Analysis, and that it "must keep monitoring and
analysis modules internally separated", with the risk of becoming a second monolith
mitigated by "separate ports, use cases, and contracts".

**Decision:** The analysis capability is implemented as its own application module with
hexagonal layering, not as a subpackage of the existing monitoring module.

**Consequences:**
- ✅ Complies with ADR-002 and ADR-009.
- ⚠️ The codebase temporarily contains two internal styles: the older layered style and
  the new hexagonal style. The hexagonal one is the target for new work.

---

## Correlations

- Global architecture ADRs → `05-architecture/decisions/records/`
  (ADR-002 boundaries, ADR-003 database, ADR-007 events, ADR-009 hexagonal,
  ADR-014 thresholds)
- Technical security rules → `00-governance/security-rules.md`
- Data model → [data-model.md](data-model.md)
- API contract → `07-api/contracts/openapi/ms-monitoreo.yaml`