# ADR-011 — Production Deployment Strategy

- **ID:** ADR-011
- **Date:** 2026-09-17
- **Status:** Proposed
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl requires a production deployment strategy to ensure safe, reliable, and zero-downtime deployments. The `10-devops/environments.md` documents various deployment strategies (canary, blue-green, rolling) but lacks a formal ADR documenting the decision.

A decision is required now because:
- Production deployments must be safe and reversible
- The team needs clear guidelines for deployment procedures
- CI/CD pipeline requires a defined deployment strategy
- Zero-downtime deployments are required for user-facing services

**Known constraints:**
- The team of three needs simplicity and ease of management
- Infrastructure costs should be minimal for MVP
- Integration with Jenkins CI/CD is required
- Future scalability should be possible

---

## Decision

**We decided:** Adopt Rolling Deployment strategy for production environments, with automatic rollback capabilities.

**Justification:**
Rolling Deployment provides a balance between safety and resource efficiency. It gradually replaces old instances with new ones, allowing for:
- Zero-downtime deployments
- Lower infrastructure costs compared to blue-green
- Simpler implementation than canary deployments
- Automatic rollback if health checks fail

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Rolling Deployment — chosen | Zero-downtime, lower cost, simpler than canary, automatic rollback | Slower than blue-green, requires careful health checks | Chosen for balance of safety and simplicity |
| Blue-Green Deployment | Instant rollback, zero-downtime, clear separation | Double infrastructure cost, more complex setup, resource-intensive | Rejected due to infrastructure costs for MVP |
| Canary Deployment | Gradual rollout, minimal risk, feature flags | Complex implementation, requires traffic splitting, monitoring overhead | Over-engineered for current team size |
| Recreate Deployment | Simple, no additional infrastructure | Downtime during deployment, higher risk | Rejected due to downtime requirements |

---

## Consequences

**Positive:**
- Zero-downtime deployments for user-facing services
- Lower infrastructure costs compared to blue-green
- Automatic rollback capabilities on health check failures
- Gradual rollout reduces risk of full system failure
- Clear deployment process for CI/CD integration

**Negative / Trade-offs:**
- Slower deployment compared to blue-green
- Requires robust health checks and monitoring
- Rollback is gradual, not instant
- May have mixed versions running temporarily

**Impact on the system:**
- Affected services: All microservices, api-gateway, frontend
- Documents that must be updated: `10-devops/environments.md`, `10-devops/local-setup.md`, CI/CD pipeline configuration

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Failed deployment causes service degradation | Medium | High | Implement health checks and automatic rollback |
| Mixed version compatibility issues | Low | Medium | Ensure backward compatibility in API contracts |
| Rollback takes too long | Low | Medium | Set aggressive health check timeouts, monitor deployment progress |
| Resource constraints during deployment | Medium | Low | Monitor resource usage, scale up if needed |

---

## References

- Environments documentation: `10-devops/environments.md`
- Local setup guide: `10-devops/local-setup.md`
- Related to: ADR-010 (Containerization Strategy), ADR-012 (Observability Stack)
