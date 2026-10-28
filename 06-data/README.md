# 06 — Data

> How the system stores, structures, and migrates data.
> In microservices, data management is one of the most complex challenges.

---

## Documents in this section

| File | Purpose |
|------|---------|
| [domain/ms-iam.md](./domain/ms-iam.md) | Identity and Access Management data model |
| [domain/ms-alert.md](./domain/ms-alert.md) | Alert management data model (served by `ms-environment-monitoring`, ADR-015) |
| [domain/ms-sensor-management.md](./domain/ms-sensor-management.md) | Sensor management data model |
| [domain/ms-environment-monitoring.md](./domain/ms-environment-monitoring.md) | Environmental monitoring data model |
| [domain/ms-classroom-management.md](./domain/ms-classroom-management.md) | Classroom management data model |
| [domain/ms-user-experience.md](./domain/ms-user-experience.md) | User experience data model |
| [normalization-assessment.md](./normalization-assessment.md) | Cross-domain normalization verdicts, entity→table crosswalk, and open items |

---

## Domain split ↔ bounded contexts ↔ services

Physical organization of the business model (one schema per domain, per ADR-003):

| Schema | Bounded context | Microservice(s) | Tables |
|--------|-----------------|------------------|--------|
| `classrooms` | Classrooms | `ms-classroom-management` | `campuses`, `environment_types`, `educational_environment` |
| `sensors` | Sensors | `ms-sensor-management` | `sensor`, `sensor_installation`, `variable`, `sensor_variable` |
| `environment_monitoring` | Monitoring + Data Analysis | `ms-environment-monitoring` (owns alerts — `ms-alert` deprecated, ADR-015) | `severity`, `variable_threshold`, `environment_measurement`, `environmental_analysis`, `analysis_result`, `environment_alert` |
| `user_experience` | UX | `ms-user-experience` | `user_preferences`, `favorites`, `classroom_ratings`, `searches`, `notification_state` |
| `seguridad` | IAM | `ms-security` | 13 tables from `domain/ms-iam.md` (see `database/identidad-seguridad/`) |
| `user_management` | User Management | `ms-user-management` | `user_profile` |

Rules that hold across the split:

- **FKs**: physical *within* a domain; *logical UUID* (no FK) *across* domains — matching the
  `Ref:` pattern in `domain/*.md` and ADR-003 (cross-service access only via API/events).
- **Catalogs**: the implementation keeps `sensor_models`, `sensor_statuses`, `measurement_units`
  and `alert_status` as logical UUID references instead of tables (21 canonical business tables
  → 17 implemented); `severity` remains a physical table (open item #5).
- Implementation: `EduAirControl/database/negocio/` (Liquibase changelog, one folder per domain).

---

## Fundamental principle

> **Each microservice owns its own data.**

No service should access another service's database directly. If it needs data from another
service, it requests it via API or receives it via event. This principle guarantees independence.

---

## Correlations with other sections

| This section is fed by... | And feeds into... |
|---------------------------|-------------------|
| `02-domain/entities-and-rules.md` → domain entities | DB tables |
| `05-architecture/` → DB engine decisions | Engine choice in data models |
| `06-data/domain/` | `07-api/contracts/` → what data each service exposes |
| `06-data/domain/` | `09-microservices/[service]/data-model.md` |
