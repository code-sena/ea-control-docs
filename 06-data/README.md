# 06 — Data

> **What is this?** How the system stores, structures, and migrates data.
> In microservices, data management is one of the most complex challenges.

## Fundamental principle in microservices

> **Each microservice owns its own data.**

No service should access another service's database directly. If it needs data from another
service, it requests it via API or receives it via event. This principle guarantees independence.

---

## What is here and how to fill it in

### `domain/` ⭐
Data models for each microservice, organized by service.

**Files:**
- `ms-iam.md` — Identity and Access Management data model
- `ms-alert.md` — Alert management data model
- `ms-sensor-management.md` — Sensor management data model
- `ms-environment-monitoring.md` — Environmental monitoring data model
- `ms-classroom-management.md` — Classroom management data model
- `ms-user-experience.md` — User experience data model

**Format per service:**
```markdown
## Service: [name]
**DB Engine:** [PostgreSQL / MongoDB / Redis / etc.]
**Justification:** [why this engine for this service]

### Table/Collection: [name]
| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | UUID | No | Unique identifier | PK |
| [field] | [type] | [Yes/No] | [description] | [FK/Unique/etc.] |

### Indexes
| Name | Fields | Type | Justification |
|------|--------|------|---------------|
```

---

## Correlations with other sections

| This section is fed by... | And feeds into... |
|---------------------------|-------------------|
| `02-domain/entities-and-rules.md` → domain entities | DB tables |
| `05-architecture/` → DB engine decisions | Engine choice in `models.md` |
| `models.md` | `07-api/contracts/` → what data each service exposes |
| `models.md` | `08-uml/` → ER diagrams |
| `models.md` | `09-microservices/[service]/data-model.md` |

---

## Important data decisions in microservices

### SQL or NoSQL?
There is no single answer. It depends on the service:
- **SQL** (PostgreSQL, MySQL): relational data, ACID transactions, fixed schema
- **Document** (MongoDB): hierarchical data, flexible schema, high variability
- **Key-value** (Redis): cache, sessions, high-speed temporary data
- **Time series** (InfluxDB, TimescaleDB): metrics, event logs

### How to handle consistency between services?
Without a shared database, consistency is **eventual**:
- Saga Pattern: chain of compensating transactions
- Outbox Pattern: guarantee that the event is published along with the transaction

---

## Questions this section must answer

- What data does each microservice handle?
- Why was that database engine chosen for each service?
- How is the schema updated without breaking the system?
- Who is the "owner" of each piece of data in the system?
