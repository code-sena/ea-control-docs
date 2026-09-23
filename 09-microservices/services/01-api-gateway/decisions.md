# Technical Decisions — API Gateway

> Internal design decisions for this service that are not covered by the global
> architecture ADRs. Each decision documents the context, the choice, and the consequences.

---

## Decision: Authentication at the gateway vs. in each service

**Date:** [decision date]
**Context:** There are two strategies to verify JWT tokens: (A) the gateway verifies the
token and passes the user context as headers; (B) each microservice verifies its own token.

**Decision:** Strategy A — the gateway verifies the JWT (signature + expiration + blacklist)
and attaches `X-User-Id` and `X-User-Role` as internal headers. Microservices trust
these headers without re-verifying the token.

**Consequences:**
- Microservices are simpler (no JWT library needed)
- The gateway is the only component that needs access to the JWT public key
- If the gateway is compromised, all services are vulnerable — mitigated with internal TLS
- Internal headers must NOT be available from outside the gateway (nginx/proxy strips incoming X-User-* headers)

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
