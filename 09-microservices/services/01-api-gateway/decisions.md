# Technical Decisions — API Gateway

> Internal design decisions for this service that are not covered by the global
> architecture ADRs. Each decision documents the context, the choice, and the consequences.

---

## Decision: Authentication at the gateway vs. in each service

**Date:** 2026-10-17 (supersedes the interim strategy A)
**Context:** There are two strategies to verify JWT tokens: (A) the gateway verifies the
token and passes the user context as headers; (B) each microservice verifies its own token.

**Decision:** Strategy **B** — JWT-only (ADR-018). The gateway still validates the token
(signature + expiration + blacklist) and still attaches `X-User-Id`/`X-User-Role` headers
for logs and traces, but **no microservice trusts them**: every service re-validates the
RS256 Bearer token against the ms-security JWKS. The interim Strategy A ("microservices
trust headers without re-verifying") was **rejected** on 2026-10-17 because it allowed
identity spoofing from any caller reaching a service port (R-001).

**Consequences:**
- One auth path to reason about; no shared secrets between gateway and services
- If the gateway is compromised it can no longer impersonate users inside the mesh
  (it can still act with any token it sees)
- The gateway must always forward the resolved `Authorization` header — including the
  BFF cookie flow (`JwtAuthenticationFilter.forward`)
- Internal headers must NOT be available from outside the gateway (nginx/proxy strips
  incoming X-User-* headers) — kept as defense in depth for logs/traces

---

## Decision: Rate limiting per IP vs. per user

**Date:** [decision date]
**Context:** Rate limiting can be applied to the source IP or to the authenticated user.

**Decision:** Rate limiting per IP for public endpoints (login, register), per user-id for
authenticated endpoints.

**Consequences:**
- Per-IP rate limiting does not penalize users on the same network (corporate NAT)
- Per-user-id rate limiting requires the token to be verified before applying the limit
- Implementation: Redis bucket with key `rate:{ip}:{path}` or `rate:{userId}:{path}`

---

## Decision: Gateway implementation

**Date:** [decision date]
**Context:** Options: (A) Kong/NGINX Plus (managed solution), (B) Express/Fastify custom,
(C) Envoy as sidecar.

**Decision:** [A / B / C] — [reason]

**Consequences:** [trade-offs of the decision]

---

## Correlations

- Global architecture ADRs → `05-architecture/decisions/records/`
- Gateway runbook → `runbook.md`
