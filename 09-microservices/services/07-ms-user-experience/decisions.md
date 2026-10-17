# Decisions — ms-user-experience

## DEC-001: Hexagonal architecture

**Status:** Accepted

ADR-009 mandates hexagonal architecture for all microservices. This service follows the canonical structure:

- `domain/model/` — entities with JPA annotations
- `application/` — use case services
- `infrastructure/persistence/` — JPA adapters
- `infrastructure/web/` — controllers and DTOs
- `shared/` — exceptions, security, contracts, global exception handler

## DEC-002: User identity from JWT token

**Status:** Accepted

The service does not own users. The `userId` claim from the JWT is the single source of truth for the authenticated user. No endpoint accepts `userId` in the request body.

## DEC-003: Schema name `user_experience`

**Status:** Accepted

ADR-003 requires one schema per service. The schema is `user_experience` (not `ux`). Cross-domain references (`user_id`, `classroom_id`, `variable_id`) are logical UUIDs without foreign keys.

## DEC-004: JWT validation (superseded interim: HS256 shared secret)

**Status:** Superseded (2026-10-17)

The interim HS256/`jwt.secret` scheme was replaced by RS256 validation against the
ms-security JWKS (ADR-006), and the service is **JWT-only** since ADR-018: identity
headers (`X-User-*`, `X-User-Id`) are ignored, so no request can impersonate another
user without a valid token.

## DEC-005: Notification state table

**Status:** Accepted

The `notification_state` table tracks read/acknowledged state per user per notification. This is an extension beyond the original 4-table data model, added to support the notification UI.
