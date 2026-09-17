# ADR-010 — Containerization Strategy

- **ID:** ADR-010
- **Date:** 2026-09-17
- **Status:** Proposed
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl microservices require a containerization strategy for consistent development, testing, and deployment environments. The `05-architecture/overview.md` references Docker and Docker Compose but lacks a formal ADR documenting the decision.

A decision is required now because:
- Development environments need to be reproducible across team members
- CI/CD pipeline requires containerized builds
- Production deployment depends on container orchestration
- Local development should match production as closely as possible

**Known constraints:**
- The team of three needs simplicity and ease of use
- Cost should be minimal for MVP phase
- Integration with Jenkins CI/CD is required
- Future scalability to production clusters should be possible

---

## Decision

**We decided:** Adopt Docker and Docker Compose for containerization across all environments (development, testing, staging, production).

**Justification:**
Docker provides industry-standard containerization with excellent tooling and community support. Docker Compose simplifies multi-service orchestration for development and testing. This approach:
- Enables consistent environments across all stages
- Simplifies onboarding (new developers can start with `docker-compose up`)
- Integrates seamlessly with Jenkins CI/CD
- Allows future migration to Kubernetes without changing Dockerfiles

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Docker + Docker Compose — chosen | Industry standard, excellent tooling, simple orchestration, CI/CD integration | Docker Desktop licensing for enterprises, learning curve for beginners | Chosen for balance of simplicity and capability |
| Podman + Podman Compose | Rootless containers, daemonless, OCI-compatible | Less mature ecosystem, fewer integrations, smaller community | Rejected due to ecosystem maturity |
| Kubernetes (minikube/k3s) | Production-grade orchestration, auto-scaling, self-healing | Over-engineered for MVP, steep learning curve, operational overhead | Overkill for current team size and needs |
| Nix-based environments | Reproducible, declarative, immutable | Very steep learning curve, limited adoption, poor Docker integration | Too complex for current needs |

---

## Consequences

**Positive:**
- Consistent environments across development, testing, and production
- Simplified onboarding with `docker-compose up`
- Easy integration with Jenkins CI/CD pipeline
- Each service can be developed and tested independently
- Future migration path to Kubernetes if needed

**Negative / Trade-offs:**
- Docker Desktop requires license for enterprise use
- Additional layer of abstraction adds complexity
- Docker images need to be maintained and updated
- Container networking requires understanding

**Impact on the system:**
- Affected services: All microservices, api-gateway, frontend
- Documents that must be updated: `10-devops/local-setup.md`, `10-devops/environments.md`, Dockerfiles and docker-compose.yml files

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Docker image vulnerabilities | Medium | High | Use minimal base images, regular security scans, automated updates |
| Container performance overhead | Low | Low | Use multi-stage builds, optimize image size, monitor resource usage |
| Docker Desktop licensing issues | Medium | Medium | Evaluate Podman as alternative for enterprise environments |
| Inconsistent Docker versions across team | Low | Medium | Pin Docker versions in documentation, use .docker-version file |

---

## References

- Docker documentation: https://docs.docker.com
- Docker Compose specification: https://docs.docker.com/compose/
- Local setup guide: `10-devops/local-setup.md`
- Related to: ADR-009 (Hexagonal Architecture), ADR-011 (Deployment Strategy)
