# ADR-017 — OAuth2/OIDC Authorization Server and Backend-for-Frontend

- **ID:** ADR-017
- **Date:** 2026-10-06
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

ADR-006 defined a custom JWT scheme (RS256, rotating refresh tokens, service-level RBAC)
and required that browser tokens are **not** persisted in `localStorage`. The product now
requires a **standard OAuth2/OIDC** authorization server (mandatory) and secure token
handling for a web SPA and a mobile app.

The current frontend stores the access token in `localStorage` and talks to a custom
`/auth/login` endpoint, which violates ADR-006 and is not standards-based. A decision is
needed before building the frontend, because it defines the authorization flows, the token
endpoints, and where tokens are stored.

**Known constraints:**
- Web (React SPA) and mobile (Expo) are public clients → **PKCE** is required.
- Tokens must not be readable by JavaScript (no `localStorage`).
- `ms-security` already owns identity and RSA keys; `api-gateway` is the only entry point.
- Spring Boot 4.0.5 ships Spring Security 7.0.x, which now includes Spring Authorization
  Server (SAS 7) under `org.springframework.security:spring-security-oauth2-authorization-server`.

---

## Decision

**We decided:** Adopt **Spring Authorization Server 7** inside `ms-security` as the
OAuth2/OIDC authorization server, using **Authorization Code + PKCE** for web and mobile
clients (plus client credentials for service-to-service). The **`api-gateway` acts as a
Backend-for-Frontend (BFF)**: it is an OAuth2 client that completes the code exchange,
stores tokens **server-side in a Redis-backed session**, and exposes only an **httpOnly,
Secure, SameSite cookie** to the browser. The gateway relays the access token to services
and propagates `X-User-Id`, `X-User-Role`, `X-Institution-Id` and `X-Campus-Id` — purely
informational since ADR-018 (services authenticate the JWT only). JWKS is
published at `/oauth2/jwks` (replacing `/api/v1/auth/jwks`).

**Justification:**
SAS is the standard, first-party Spring option and ships with Spring Security 7, so it
fits the stack without a separate IdP. PKCE is mandatory in SAS 7 by default. The BFF
pattern removes tokens from JavaScript entirely, satisfying ADR-006's security intent, and
reuses the Redis already used for rate limiting and the token blacklist.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| SAS 7 in `ms-security` + gateway BFF — chosen | Standard OAuth2/OIDC; no separate IdP; tokens out of JS | Gateway becomes stateful (Redis session); more moving parts | — (chosen) |
| Keep custom JWT (ADR-006) | Already built and tested | Not standard; no SSO/interop | Discarded: OAuth2 is a mandatory requirement |
| Keycloak as external IdP | MFA, admin UI, SSO out of the box | Separate infra/DB/user store; another system to operate | Deferred; revisit if MFA/SSO become hard requirements |
| SPA stores tokens in memory + refresh cookie | No extra BFF | Access token still in JS; more client complexity | Discarded in favor of the BFF |

---

## Consequences

**Positive:**
- Standards-based auth: OAuth2/OIDC, PKCE, discovery, userinfo, JWKS.
- Tokens are never exposed to JavaScript (httpOnly cookies).
- Enables future SSO and third-party integrations.

**Negative / Trade-offs:**
- Supersedes the token flow of ADR-006 (RS256 and service-level RBAC remain valid).
- The gateway changes from stateless to session-based (Redis) as a BFF.
- Adds OAuth2 tables (`oauth2_registered_client`, `oauth2_authorization`,
  `oauth2_authorization_consent`) and a login page.
- Requires a coordinated frontend/mobile migration.

**Impact on the system:**
- Affected services: `ms-security` (authorization server), `api-gateway` (BFF),
  frontend web and mobile.
- Documents to update: `ADR-006` (mark the flow as superseded), `07-api/contracts/openapi/ms-security.yaml`,
  `09-microservices/services/02-ms-security/*`, `10-devops/environments.md`.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| PKCE mandatory breaks misconfigured clients | Medium | Medium | Document client configuration; integration tests |
| Session store (Redis) becomes a single point of failure | Low | High | Redis persistence/HA; session timeout tuning |
| Gateway BFF complexity delays delivery | Medium | Medium | Phase it: multi-tenant first, then OAuth2 |
| Key rotation and consent add operational load | Low | Medium | Documented rotation runbook; first-party consent disabled |

---

## References

- Authentication and RBAC (superseded flow) → `ADR-006`
- Multi-tenancy claims → `ADR-016`
- API Gateway → `ADR-005`
- Spring Authorization Server (Spring Security 7) → https://docs.spring.io/spring-authorization-server/reference/
