# Technical Decisions — Auth Service

> Authentication service design decisions that complement the global ADRs.

---

## Decision: JWT signing algorithm — RS256 vs HS256

**Date:** [date]
**Context:** JWT can be signed with HMAC-SHA256 (HS256, shared symmetric key) or
RSA-SHA256 (RS256, public/private key pair).

**Decision:** RS256 — private key only in auth-service, public key available at
`GET /api/v1/auth/jwks` so any service can verify tokens without calling auth-service.

**Consequences:**
- Each service can verify tokens independently (no network latency)
- Key rotation is operationally more complex (the new public key must be distributed)
- The JWKS endpoint allows gradual rotation with multiple active keys simultaneously

---

## Decision: Refresh tokens in database vs. stateless

**Date:** [date]
**Context:** Refresh tokens can be stateless (long JWT) or stateful (ID in DB).

**Decision:** Stateful — the refresh token is a UUID stored in the `refresh_tokens` table.
Only the SHA-256 hash is persisted (never the real value).

**Consequences:**
- Immediate revocation possible (specific device logout, account suspension)
- Requires a PostgreSQL lookup on every refresh token use
- The refresh_tokens DB can become a bottleneck if there are millions of active sessions

---

## Decision: Where resource-level permission checks live

**Date:** [date]
**Context:** Granular permissions (e.g., "can only see their own appointments") can live
in auth-service or in each business service.

**Decision:** Auth-service manages roles (ADMIN, USER, VIEWER). Granular resource
permissions are the responsibility of each business microservice.

**Rationale:** Auth-service does not know each service's domain. Centralizing granular permissions
would create bidirectional coupling and make auth-service dependent on all others.

---

## Decision: Account lockout policy

**Date:** [date]
**Decision:** [N] failed attempts → lock for [M] minutes. The counter resets
on successful login. The lock is stored in Redis (TTL = M minutes, self-cleaning).

**Consequences:**
- An attacker can DoS a specific user by forcing lockouts
- Mitigation: gradual lockout (5 min → 30 min → 24 hours) reduces the impact

---

## Correlations

- Global architecture ADRs → `05-architecture/decisions/records/`
- Technical security rules → `00-governance/security-rules.md`
- Data model → `data-model.md`
