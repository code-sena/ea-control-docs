## ADR-006 — JWT Authentication and Service-Level RBAC

- **ID:** ADR-006
- **Date:** 2026-09-09
- **Status:** Accepted — token flow partially superseded by ADR-017
- **Authors:** EduAirControl Development Team

> **Note (2026-10-06):** The **token issuance/exchange flow** of this ADR (custom
> `/auth/login` + manual refresh) is superseded by **ADR-017** (OAuth2/OIDC Authorization
> Server + BFF). The remaining decisions here stay in force: **RS256 + JWKS**, rotating
> refresh tokens, BCrypt password hashing, and **service-level RBAC** (defense in depth).

---

## Context

Authentication and authorization are MVP capabilities. The requirements define JWT access tokens, refresh tokens, and role-based access control, while the security policy adds token rotation, asymmetric signing as the preferred option, secure client storage, gateway validation, and service-level permission checks.
The current documents contain different access-token lifetimes: one NFR states one hour, while the security policy states fifteen minutes. A single decision is needed before implementing ms-security, the gateway, and protected services.

**Known constraints:**
- Private endpoints require authentication.
- Roles include SUPER_ADMIN, ADMIN, and USER.
- Passwords must be hashed and secrets must not be committed to source control.
- The platform is a web application.

---

## Decision

**We decided:** Use short-lived JWT access tokens with a 15-minute expiration and rotating, persisted refresh tokens valid for 7 days. Prefer RS256 signing so services can validate access tokens with a public key without sharing the signing secret. Use RBAC: the gateway validates token integrity and expiration, while every target service validates permissions for its operation.
For the web frontend, refresh tokens are stored in httpOnly, Secure, SameSite cookies; access tokens must not be persisted in browser local storage. Passwords are hashed with BCrypt or an approved equivalent.

**Justification:**
Short-lived access tokens reduce the impact of token leakage. Rotation and revocation provide control over sessions. Asymmetric signing limits secret distribution. Repeating authorization in each service follows defense in depth and least privilege.
This decision resolves the current one-hour versus fifteen-minute inconsistency in favor of the security policy's stricter value.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| JWT access tokens + rotating refresh tokens + service-level RBAC — chosen | Stateless request validation; bounded token exposure; defense in depth | Revocation and key rotation require operational support | Chosen because it matches the security policy and MVP requirements |
| Server-side sessions | Straightforward revocation | Requires shared session storage and introduces stateful scaling concerns | Discarded because the NFR requires stateless horizontal scaling |
| Long-lived JWTs without refresh rotation | Simple implementation | Larger compromise window; weak revocation | Discarded for security reasons |
| Gateway-only authorization | Centralized configuration | A compromised or misconfigured gateway becomes the sole authorization boundary | Discarded because each service must enforce its own permissions |


---

## Consequences

**Positive:**
- Authentication behavior is consistent across frontend, gateway, and services.
- Token exposure is limited and revoked refresh tokens can invalidate sessions.
- Services remain independently scalable without server-side session affinity.

**Negative / Trade-offs:**
- Key publication, rotation, refresh-token storage, and logout invalidation add implementation work.
- Users may need refresh operations more often.
- Service teams must maintain permission checks consistently.

**Impact on the system:**
- Affected services: ms-security, api-gateway, ms-user-management, ms-classroom-management, ms-sensor-management, ms-environment-monitoring, and React frontend.
- Documents that must be updated: 00-governance/security-policy.md, 04-requirements/non-functional.md, 04-requirements/user-stories.md, 05-architecture/overview.md, 09-microservices/service-catalog.md.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Refresh-token theft | Medium | High | Hash refresh tokens, rotate on use, revoke on logout/password change, invalidate all on reuse detection |
| Inconsistent permissions between services | Medium | High | Central permission vocabulary, shared security guidance, integration tests, and service-level review |
| Signing-key rotation breaks validation | Low | High | Publish key identifiers and overlapping key validity with a documented rotation procedure |

---

## References

- Security policy → 00-governance/security-policy.md
- Authentication and RBAC stories → 04-requirements/user-stories.md (HU-IAM-001 to HU-IAM-003 )
- Security NFR → 04-requirements/non-functional.md
- Related to: ADR-005