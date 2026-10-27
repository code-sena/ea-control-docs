# Decisions — ms-environment-monitoring

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
**Status:** Superseded by DEC-005

**Context:** `environment_measurement` is owned by the monitoring side of
`ms-environment-monitoring`. ADR-002 requires the monitoring and analysis modules to stay internally
separated, with separate ports, use cases and contracts. ADR-003 forbids one module from
manipulating another module's tables directly.

**Decision:** The analysis module declares an outbound port for aggregated measurements
and the module that owns the measurements provides the adapter. The analysis use case
never touches `EnvironmentMeasurementRepository`.

**Consequences when written:**
- ✅ The analysis module can be extracted into its own deployable by replacing the port.
- ✅ The aggregation query stays close to the data it aggregates.
- ⚠️ One more port to maintain in the shared contract package.

**Update 2026-10-07:** the extraction happened. The standalone service keeps the same
port, but the adapter now queries `environment_monitoring.environment_measurement`
instead of another module’s tables.

---

## [DEC-004] Analysis and monitoring live in separate application modules

**Date:** 2026-09-05
**Status:** Superseded by DEC-005

**Context:** ADR-002 states that `ms-environment-monitoring` initially owns both Environmental
Monitoring and Environmental Data Analysis, and that it "must keep monitoring and
analysis modules internally separated", with the risk of becoming a second monolith
mitigated by "separate ports, use cases, and contracts".

**Decision:** The analysis capability is implemented as its own application module with
hexagonal layering, not as a subpackage of the existing monitoring module.

**Consequences when written:**
- ✅ Complies with ADR-002 and ADR-009.
- ⚠️ The codebase temporarily contains two internal styles: the older layered style and
  the new hexagonal style. The hexagonal one is the target for new work.

**Update 2026-10-07:** the module separation became a standalone repository,
`ms-environment-monitoring`; see DEC-005.

---

## [DEC-005] Standalone `ms-environment-monitoring` with canonical names and event contract

**Date:** 2026-10-07
**Status:** Active

**Context:** The canonical glossary forbids the legacy alias `ms-monitoreo` and fixes
the service name as `ms-environment-monitoring`. The domain contract also fixes
`EnvironmentalDataRecorded`, envelope idempotency, retry behavior, atomic measurements,
and ADR-003’s one-schema-per-service ownership.

**Decision:** Implement the service as a standalone repository named
`ms-environment-monitoring`, with:
- local port `3003`;
- PostgreSQL schema `environment_monitoring`;
- canonical table name `environment_measurement`;
- canonical event envelope `EnvironmentalDataRecorded`;
- `eventId` idempotency with a broker-message fallback;
- four broker retries with exponential backoff and a seven-day dead-letter queue.

**Consequences:**
- ✅ Code, database, messaging topology and documentation use the same canonical names.
- ✅ The consumer honors the atomic-measurement rule and the domain event envelope.
- ⚠️ The monolith ingestion path now owns the canonical publisher responsibility until
  `ms-sensor-management` is extracted.

---

## [DEC-006] Resolución de decisiones abiertas §12 y aceptación de ADR-014

**Date:** 2026-10-07
**Status:** Active

**Context:** La especificación de construcción deja seis decisiones abiertas en §12.
Sin cerrarlas no se puede codificar umbrales, alertas ni la proyección. ADR-014 está
en estado `Proposed` y bloquea la implementación de umbrales.

**Decision:** Se acepta ADR-014 tal cual y se resuelven las seis decisiones:

1. **Semántica de excedencia:** alerta cuando la medición supera los límites del
   umbral activo en severidad `WARNING` o `CRITICAL`. `INFO` es solo informativo.
   La banda bilateral se modela con `min_value`/`max_value` por severidad.
2. **`quality_flag`:** catálogo local propio (`VALID`, `SUSPECT`, `BAD`). El servicio
   no referencia el catálogo del monolito.
3. **Estado de alerta:** columnas `acknowledged_at`/`acknowledged_by` (modelo canónico).
   No se usa catálogo `alert_status`.
4. **Ingesta:** los sensores hablan con `ms-sensor-management` (ADR-004). Este servicio
   consume `EnvironmentalDataRecorded` por RabbitMQ. No hay ingesta directa MQTT/HTTP
   en la v1 del servicio.
5. **`environment_type_id`:** proyección local (`sensor_installation → educational_environment
   → environment_type`) alimentada por eventos + refresh periódico.
6. **Umbrales:** solo por `environment_type_id`, sin `educational_environment_id`
   (ADR-014 tal cual). Se rechaza explícitamente la columna del monolito.

**Consequences:**
- ✅ ADR-014 pasa a `Accepted` y desbloquea la codificación de umbrales.
- ✅ Las seis decisiones quedan trazables en esta DEC.
- ⚠️ Si el negocio cambia la semántica de excedencia, hay que versionar el evento
  o la regla (no es un cambio compatible silencioso).

---

## [DEC-007] Projections are last-write-wins; event ordering is a known limit

**Date:** 2026-10-27
**Status:** Active

**Context:** `installation_projection` and `educational_environment` are fed by
at-least-once events (ADR-007). Idempotency is guaranteed per event through
`inbox_message`, but ordering is not: the `UPSERT` in `InstallationProjectionDao` and
`ClassroomEnvironmentDao` overwrites the row with whatever event arrives last. The
event `version` is the schema version, and `occurredAt` is not compared with stored
state. Deletes are physical.

**Decision:** Accept this limit for now and do not add ordering control. The
projections are applied in arrival order, relying on RabbitMQ preserving order within a
queue with a single consumer. The gap is tracked as R-016 in
`15-project-control/risks.md`.

**Consequences:**
- ✅ No schema change and no new moving parts while the service runs as one instance.
- ⚠️ Out-of-order events (DLQ replays, several consumers or replicas) can leave
  `removed_at` stale, resurrect a deleted row, or purge measurements by a late delete.
- ⚠️ `MeasurementAlertingService` skips evaluation, logging at `debug` only, when the
  installation has no projection or its environment has no type. The measurement is kept
  and is not re-evaluated when the projection arrives.
- ⚠️ The projections cannot be guaranteed rebuildable: `HistoricalBackfillService`
  copies from the monolith schemas, is disabled by default, and cannot work with
  separate databases per service (R-007). `inbox_message` makes redeliveries safe,
  but it does not recover a lost or misordered event.

**Revisit when:** the service runs with more than one replica or consumer per queue,
or an installation stops alerting without a configuration change. The first step is a
`last_event_at` column on both projections, applied only if the incoming event is newer.

---

## Correlations

- Global architecture ADRs → `05-architecture/decisions/records/`
  (ADR-002 boundaries, ADR-003 database, ADR-007 events, ADR-009 hexagonal,
  ADR-014 thresholds)
- Technical security rules → `00-governance/security-rules.md`
- Data model → [data-model.md](data-model.md)
- API contract → `07-api/contracts/openapi/ms-environment-monitoring.yaml`