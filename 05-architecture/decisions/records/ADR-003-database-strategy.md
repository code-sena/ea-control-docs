## ADR-003 — Database Engine and Domain Data Ownership

- **ID:** ADR-003
- **Date:** 2026-09-09
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

The project documentation contains conflicting database decisions. 01-context/scope.md, 04-requirements/non-functional.md, and 06-data/models.md assume PostgreSQL, while 01-context/overview.md, 05-architecture/overview.md, and the service catalog describe MySQL. The documentation also alternates between database-per-service and one shared database infrastructure with logical domain separation.

This must be resolved before migrations, repositories, Docker Compose, and deployment configuration are implemented. A database decision that remains ambiguous will cause incompatible schemas and prevent reproducible environments.

**Known constraints:**
- The MVP requires relational persistence, UUID identifiers, timestamps with timezone, constraints, and historical environmental queries.
- Each service must own its data and must not directly manipulate another service's tables.
- The team has three developers and needs a low-operational-complexity MVP.

---

## Decision

**We decided:** Use PostgreSQL as the database engine for the MVP, with one logical database ownership boundary per microservice. The initial deployment may use one PostgreSQL instance, but each service must use its own schema or database namespace and credentials; cross-service data access occurs only through APIs or events.

**Justification:**
PostgreSQL matches the existing data model, migration examples, UUID and TIMESTAMPTZ conventions, relational constraints, and the NFR recovery requirements. A single managed instance reduces MVP operations while preserving ownership rules and a future path to physically separate databases.
This ADR supersedes the undocumented MySQL assumption. It does not require an immediate physical database server per service.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| PostgreSQL with logical ownership per service — chosen | Matches current models and NFRs; strong relational features; manageable operations | Isolation is weaker than separate physical instances | Chosen for MVP practicality |
| MySQL with logical ownership per service | Familiar relational model; already named in some architecture files | Conflicts with the data model, migrations, and scope assumptions | Discarded to remove existing documentation inconsistency |
| Separate physical database per service from day one | Strong isolation and independent scaling | Higher operational, backup, and local-development complexity | Deferred until scale or isolation requirements justify it |

---

## Consequences

**Positive:**
- The database technology and migration syntax become consistent across documents and environments.
- Services retain data ownership without requiring the MVP to operate many database servers.
- PostgreSQL supports the relational queries needed for historical analysis and dashboard views.

**Negative / Trade-offs:**
- A shared PostgreSQL instance remains a potential availability and resource-sharing boundary.
- Schema or database namespace isolation requires permissions to be configured correctly.
- A future physical split will require migration and operational planning.

**Impact on the system:**
- Affected services: all persistence-owning services, especially ms-security, ms-user-management, ms-classroom-management, ms-sensor-management, and ms-environment-monitoring.
- Documents that must be updated: 01-context/overview.md, 01-context/scope.md, 05-architecture/overview.md, 06-data/models.md, 04-requirements/non-functional.md, 04-requirements/traceability-matrix.md, 10-devops/local-setup.md.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| A service reads another service's tables directly | Medium | High | Separate database credentials and enforce access permissions in development and deployment |
| One PostgreSQL instance becomes a single point of failure | Medium | High | Backups, restoration tests, health checks, and documented migration to separate instances |
| Documentation remains inconsistent after acceptance | Medium | High | Update every affected document in the same pull request as ADR acceptance |

---

## References

- Data model and migration strategy → 06-data/models.md
- Scope assumptions and constraints → 01-context/scope.md
- Database recovery requirements → 04-requirements/non-functional.md
- Related to: ADR-002