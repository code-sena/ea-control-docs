## ADR-005 — API Gateway as the External Backend Entry Point

- **ID:** ADR-005
- **Date:** 2026-09-09
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

The architecture defines Spring Cloud Gateway as the entry point between the React frontend and the backend microservices. The requirements also trace a dedicated gateway user story, but routing, authentication validation, correlation identifiers, and service exposure rules are not recorded as one decision.
Without an explicit gateway boundary, the frontend could become coupled to service locations and each service could implement inconsistent cross-cutting controls.

**Known constraints:**
- The frontend communicates through HTTP/HTTPS.
- Private endpoints require JWT authentication and RBAC.
- The gateway must not own business data or domain rules.

---

## Decision

**We decided:** Use Spring Cloud Gateway as the single external backend entry point. It will terminate external TLS where applicable, route requests to internal services, propagate correlation IDs, apply coarse-grained authentication checks, and enforce common request controls. Fine-grained authorization remains the responsibility of each target service.
The gateway will not contain domain business logic, persist domain data, or replace service-level authorization.

**Justification:**
Centralized routing reduces frontend coupling and provides one place for common edge concerns. Keeping domain authorization in each service follows least privilege and prevents a gateway configuration error from becoming the only security boundary.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Spring Cloud Gateway as single entry point — chosen | Central routing, TLS, correlation, and edge controls; fits existing stack| Gateway is a critical infrastructure component | Chosen for consistency and controlled exposure |
| Frontend calls every microservice directly | Simple initial routing | Exposes topology; duplicates auth and CORS concerns; increases coupling | Discarded because it conflicts with the gateway requirement |
| Custom gateway service with business aggregation | Flexible custom behavior | Higher maintenance and risk of business logic leaking into the edge | Discarded in favor of a standard gateway |


---

## Consequences

**Positive:**
- The frontend depends on stable gateway routes rather than internal service addresses.
- Correlation IDs and common edge policies can be standardized.
- Internal services can remain private to the platform network.

**Negative / Trade-offs:**
- The gateway can become a bottleneck or single point of failure.
- Route configuration must be versioned and tested.
- Authorization logic exists at both the edge and service layers at different levels of responsibility.

**Impact on the system:**
- Affected services: api-gateway, React frontend, and all backend microservices.
- Documents that must be updated: 05-architecture/overview.md, 04-requirements/traceability-matrix.md, 00-governance/security-policy.md, 07-api/README.md, 10-devops/environments.md, 13-operations/observability.md.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Gateway failure blocks all frontend traffic | Medium | High | Health/readiness checks, restart policy, replicated deployment when available |
| Gateway becomes a business-logic layer | Medium | High | Enforce the no-domain-logic rule in reviews and keep aggregation out of the MVP |
| Incorrect route exposes an internal service | Low | High | Private network controls, route tests, and security review before release |

---

## References

- Gateway requirement → 04-requirements/user-stories.md (HU-ARCH-001)
- Security policy → 00-governance/security-policy.md
- System architecture → 05-architecture/overview.md
- Related to: ADR-002, ADR-004, ADR-006