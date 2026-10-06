# ADR-015 — Fold Alert Management into ms-environment-monitoring

- **ID:** ADR-015
- **Date:** 2026-10-06
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

ADR-002 originally listed `ms-alert` as a separate domain service responsible for alert generation and management, and the service catalog kept it as service #06 (`:3005`). However, the database implementation approved in the data mapping work placed all alert-related tables (`severity`, `variable_threshold`, `environment_alert`) inside the `monitoring` schema, which is owned by `ms-environment-monitoring` (ADR-003: one schema or namespace ownership boundary per service).

This creates an inconsistency:
- Two deployable services (`ms-environment-monitoring`, `ms-alert`) would claim ownership of the same schema `monitoring`.
- The alerts lifecycle (threshold evaluation → alert creation) is driven by data that `ms-environment-monitoring` already owns (measurements and analysis results).
- The MVP is built by a three-person team; ADR-002's own risk register anticipated this case: *"ms-alert and ms-user-experience become unnecessary overhead → merge into existing services if not justified by domain complexity"*.

A decision is required before `ms-environment-monitoring` is implemented, because it determines service boundaries, API ownership, schema ownership, and catalog documentation.

**Known constraints:**
- Alert tables are already defined in the `monitoring` schema of `database/negocio` and will not be moved.
- Alert evaluation consumes measurements and thresholds that live in the same schema.
- Event-driven communication between monitoring and alerting would be internal once both capabilities live in one deployable.
- The MVP team size does not justify an extra deployment, contract, and operational surface for alerts alone.

---

## Decision

**We decided:** Fold alert generation and management into `ms-environment-monitoring`. The service owns the full environmental data pipeline: measurements, analysis, thresholds, and alerts. `ms-alert` is deprecated as a separate deployable; its service catalog entry is marked ⏸ Deprecated and no new repository, contract, or schema will be created for it.

**Justification:**
- Alerts are a direct downstream effect of measurements and threshold evaluation, which `ms-environment-monitoring` already owns in the same schema.
- Folding them in preserves ADR-003 (single ownership per schema) without moving tables.
- It exercises the merge option explicitly anticipated by ADR-002's risk table.
- It removes one deployment, one API surface, and one event link from the MVP without changing the external product scope (alerts remain available to users).

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Fold alerts into `ms-environment-monitoring` — chosen | Single schema ownership; no table moves; fewer deployments; keeps ADR-003 intact | `ms-environment-monitoring` keeps a broad responsibility (already flagged in ADR-002) | Chosen for the MVP |
| Keep `ms-alert` as a separate service sharing the `monitoring` schema | Clear separation of alerting logic; matches original catalog | Two services over one schema violates ADR-003; requires cross-service access to measurements/thresholds or duplicated data | Violates the database ownership rule |
| Give `ms-alert` its own `alerts` schema (move tables) | Restores 1 service : 1 schema | Refactors `database/negocio`, all data docs, and DDL references for no product gain; alerts stay logically coupled to monitoring data | Cost without justifying benefit for MVP |

---

## Consequences

**Positive:**
- One owner for the whole environmental data pipeline: `ms-environment-monitoring` (measurements → analysis → thresholds → alerts).
- ADR-003 ownership rule remains satisfied; no schema or table changes.
- One fewer service to deploy, secure, test, and observe.
- The `EnvironmentalDataRecorded` event link monitoring → alert disappears (it becomes an internal call).

**Negative / Trade-offs:**
- `ms-environment-monitoring` must keep alerting as an internally separated module (ports, use cases, contracts), consistent with the ADR-002 risk "second monolith".
- Alert endpoints will be published under the `ms-environment-monitoring` contract instead of a dedicated `ms-alert` contract.
- Catalog and architecture docs must be updated to reflect the deprecation (this ADR records it).

**Impact on the system:**
- Affected services: `ms-environment-monitoring` (gains alert ownership), `ms-alert` (deprecated).
- Documents that must be updated: `09-microservices/service-catalog.md`, `05-architecture/overview.md`, `01-context/glossary.md`, `02-domain/domain-map.md`, `06-data/README.md`, `06-data/domain/ms-alert.md`.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| `ms-environment-monitoring` grows into a second monolith | Medium | High | Keep measurements, analysis, and alerts as explicit internal modules with separate ports and contracts (extends ADR-002 mitigation) |
| Residual references to `ms-alert` confuse contributors | Medium | Low | Mark the catalog entry ⏸ Deprecated and the glossary name deprecated instead of deleting history |
| Future need for independent alert scaling | Low | Medium | Re-evaluate a split only with an `alerts` schema of its own, via a superseding ADR |

---

## References

- Bounded contexts and service boundaries → `05-architecture/decisions/records/ADR-002-microservice-boundaries.md`
- Database strategy (one ownership boundary per service) → `05-architecture/decisions/records/ADR-003-database-strategy.md`
- Service catalog → `09-microservices/service-catalog.md`
- Alert data model → `06-data/domain/ms-alert.md`
- Alert tables in the monitoring schema → `database/negocio/changelog/01_ddl/03_tables/03_monitoring/`
