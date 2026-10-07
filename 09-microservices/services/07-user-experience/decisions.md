# Decisions — ms-user-experience

> Internal technical decisions of the service that complement the global ADRs.

---

## [DEC-001] User identity always comes from the JWT

**Date:** 2026-10-07
**Status:** Active

**Context:** All endpoints are user-scoped. Accepting `userId` in the body or query
would let any authenticated user read or modify another user's data.

**Decision:** The user ID is resolved exclusively from the JWT (`userId` claim) via
`UserIdentityPort`. No endpoint accepts `userId` as input. Missing or invalid tokens
return `401` through the shared security filter chain.

**Consequences:**
- ✅ Users can only access their own data by construction.
- ⚠️ Tokens issued before the `userId` claim existed leave `requested_by` empty;
  those tokens must be re-issued.

---

## [DEC-002] Default preferences on first read

**Date:** 2026-10-07
**Status:** Active

**Context:** Every user needs a preference record, but requiring explicit creation
adds friction and a failure mode to onboarding.

**Decision:** `GET /preferences` creates the record with defaults (`es`,
`America/Lima`, notifications on) if it does not exist. The operation is
idempotent per `user_id` (UNIQUE constraint).

---

## [DEC-003] Ratings validated in the domain

**Date:** 2026-10-07
**Status:** Active

**Context:** The score range (1-5) is a business rule, not just a database constraint.

**Decision:** `ClassroomRating.rate()` validates the range and throws
`IllegalArgumentException` (mapped to `400`) before persistence. The database
`CHECK` remains as a second line of defense.

---

## Correlations

- Global architecture ADRs → `05-architecture/decisions/records/`
- Data model → [data-model.md](data-model.md)
- API contract → `07-api/contracts/openapi/ms-user-experience.yaml`
