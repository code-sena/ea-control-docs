# ADR-018 — JWT-Only Mesh Authentication

- **ID:** ADR-018
- **Date:** 2026-10-17
- **Status:** Accepted
- **Authors:** Backend team
- **Closes:** R-001, TD-002

---

## Context

The five internal services authenticated in two ways: gateway identity headers
(`X-User-Id`, `X-User-Role`, `X-User-Roles`, `X-Institution-Id`, `X-Campus-Id`) trusted
first, and the RS256 Bearer token as a fallback. The headers were accepted without
checking their origin, so anyone reaching a service port directly could impersonate
ADMIN and pick the tenant (R-001, critical).

The header path no longer had a legitimate consumer:

- The gateway re-injects the resolved `Authorization` header on every proxied request,
  including the BFF cookie flow (see `JwtAuthenticationFilter.forward`).
- The ESP32 firmware authenticates with a device token (`roles:["DEVICE"]`), not headers.
- Both frontends send `Bearer` tokens; there are no direct service-to-service HTTP calls.

## Decision

**We decided:** every service authenticates **exclusively** with a Bearer JWT RS256
validated against the ms-security JWKS. `X-User-*` and `X-Institution-Id`/`X-Campus-Id`
headers are never read as identity or tenant. Tenant claims (`institutionId`,
`campusId`) are taken from the validated token (via request attributes published by
`JwtAuthFilter` where a `TenantFilter` exists).

The api-gateway **keeps propagating** the headers (they remain an internal observability
convention), but their content is informational only — no service trusts them.

**Justification:** the JWT path was already end-to-end (gateway always forwards the
token; RS256/JWKS since ADR-006/TD-019). Removing the header path eliminates the entire
spoofing class with no secrets to distribute and one auth path to reason about.

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| **Option A — JWT-only (chosen)** | Single auth path; no shared secrets; closes R-001 completely; aligns with ADR-006 | Every caller must carry a token (already true) | — (chosen) |
| Option B — shared `X-Internal-Secret` header | Keeps header identity | Two auth paths; secret distribution and rotation; headers still forgeable if the secret leaks | More moving parts for the same guarantee |
| Option C — JWT-first with header fallback | Smallest diff | Spoofing still works on any request without `Authorization`; keeps the trap for later | Does not close the risk |

## Consequences

- Forged `X-User-*` headers now yield **401** (no authentication) in all five services.
- Each service has a negative regression test: headers alone → 401; USER token + forged
  ADMIN headers → only USER privileges apply.
- `ROLE_HEADER` / `!hasRole('HEADER')` guards in `ms-environment-monitoring` were removed
  (no longer meaningful).
- `TenantFilter` (classroom, sensor, user-management) now runs **after** the security
  chain (order −100) and reads the attributes published by `JwtAuthFilter`; the tenant
  scoping tests mint tokens carrying `institutionId` claims.
- Developers calling a service directly (e.g. Swagger) must use a real token; the
  `X-User-*` shortcut is gone.
- Hardening the network path (mTLS / network policies between gateway and services) is
  still desirable defense in depth, but is no longer what stands between the mesh and
  privilege escalation.

## Related

- ADR-006 (JWT RS256 + JWKS), ADR-016 (multi-tenancy; tenant now from claims),
  ADR-017 (BFF; gateway re-injects the token).
