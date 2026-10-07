# Decisions — ms-user-management

## DEC-001: Hexagonal architecture

**Status:** Accepted

ADR-009 mandates hexagonal architecture for all microservices. This service follows the canonical structure:

- `domain/model/` — entities with JPA annotations
- `domain/port/out/` — repository interfaces
- `application/` — use case services
- `infrastructure/persistence/` — JPA adapters
- `infrastructure/web/` — controllers and DTOs
- `shared/` — exceptions, security, global exception handler

## DEC-002: Soft-delete lifecycle

**Status:** Accepted

User profiles use soft-delete (`deleted_at`) instead of hard delete to preserve referential integrity and audit trails. The `RecordStatus` enum (`ACTIVE`/`INACTIVE`) is independent of the soft-delete flag.

## DEC-003: Multi-tenancy via TenantContext

**Status:** Accepted

Institution filtering uses `TenantContext` populated by `TenantFilter` from the `X-Institution-Id` header added by the API gateway (ADR-016).
