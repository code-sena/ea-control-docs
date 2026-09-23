# 06 — Data

> How the system stores, structures, and migrates data.
> In microservices, data management is one of the most complex challenges.

---

## Documents in this section

| File | Purpose |
|------|---------|
| [domain/ms-iam.md](./domain/ms-iam.md) | Identity and Access Management data model |
| [domain/ms-alert.md](./domain/ms-alert.md) | Alert management data model |
| [domain/ms-sensor-management.md](./domain/ms-sensor-management.md) | Sensor management data model |
| [domain/ms-environment-monitoring.md](./domain/ms-environment-monitoring.md) | Environmental monitoring data model |
| [domain/ms-classroom-management.md](./domain/ms-classroom-management.md) | Classroom management data model |
| [domain/ms-user-experience.md](./domain/ms-user-experience.md) | User experience data model |
| [normalization-assessment.md](./normalization-assessment.md) | Cross-domain normalization verdicts, entity→table crosswalk, and open items |

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
