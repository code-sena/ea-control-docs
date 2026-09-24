# ADR-008 — Database Migration Tool

- **ID:** ADR-008
- **Date:** 2026-09-17
- **Status:** Proposed
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl requires a database migration tool to manage schema changes across multiple microservices sharing a PostgreSQL 15 infrastructure. Currently, there is an inconsistency in the documentation: `05-architecture/overview.md` references Liquibase while `06-data/domain/ms-iam.md` recommends Flyway.

A decision is required now because:
- Multiple microservices will need consistent schema management
- The team must agree on a single tool before implementation begins
- Inconsistent documentation creates confusion for developers

**Known constraints:**
- The project uses Spring Boot microservices
- PostgreSQL 15 is the chosen database
- The team of three needs robust features for schema management
- Integration with Spring Boot ecosystem is preferred

---

## Decision

**We decided:** Adopt Liquibase as the database migration tool for all microservices.

**Justification:**
Liquibase provides comprehensive schema management with support for XML, YAML, JSON, and SQL formats. Its rollback capabilities, diff tools, and multi-database support make it ideal for microservice architectures. Liquibase integrates seamlessly with Spring Boot through `spring-boot-starter-data-liquibase` and provides better control over complex schema transformations compared to simpler alternatives.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Liquibase — chosen | Rollback support, multiple formats (XML/YAML/JSON/SQL), diff tools, multi-DB support, commercial features available | Steeper learning curve, more complex configuration | Chosen for comprehensive features and rollback capabilities |
| Flyway | Simple SQL migrations, lightweight, version-based ordering | Limited rollback, less flexible for complex changesets, commercial features require paid license | Lacks rollback capabilities needed for production safety |
| Manual SQL scripts | No additional dependency, full control | Error-prone, no rollback tracking, difficult to coordinate across services | Not sustainable for production systems |

---

## Consequences

**Positive:**
- Consistent migration approach across all microservices
- Rollback capabilities for safe schema changes
- Multiple format support (XML, YAML, JSON, SQL) for different use cases
- Built-in diff tools for comparing environments
- Clear version tracking in `DATABASECHANGELOG` table
- Seamless integration with Spring Boot via `spring-boot-starter-data-liquibase`

**Negative / Trade-offs:**
- More complex configuration than simpler alternatives
- Steeper learning curve for developers new to Liquibase
- XML-heavy approach may feel verbose for simple changes
- Commercial features (Pro, Enterprise) require paid license

**Impact on the system:**
- Affected services: All microservices (ms-security, ms-classroom-management, ms-sensor-management, ms-environment-monitoring, ms-alert, ms-user-experience)
- Documents that must be updated: `05-architecture/overview.md`, `06-data/domain/ms-iam.md`, service-specific documentation

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Migration conflicts between services | Low | Medium | Each service has its own schema; no shared tables |
| Failed migrations in production | Medium | High | Test migrations in staging environment; use rollback capabilities |
| Schema drift between environments | Low | Medium | Use Liquibase diff tools to validate schema consistency |
| Complex XML configurations | Medium | Low | Provide templates and examples; prefer SQL formats when possible |

---

## References

- Liquibase documentation: https://docs.liquibase.com
- Spring Boot Liquibase integration: https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.liquibase
- Related to: ADR-003 (Database Strategy)
