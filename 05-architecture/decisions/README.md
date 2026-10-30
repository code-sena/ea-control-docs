# ADRs — Architecture Decision Records

ADRs document important architectural decisions. Each file = one decision.

## How to create an ADR

1. Copy `_template-adr.md`
2. Name it `ADR-NNN-short-title.md` (e.g.: `ADR-001-message-broker.md`)
3. Fill it in completely — especially the evaluated alternatives
4. Once accepted, the status is **permanent** (it is not deleted, it is "Superseded" by another ADR)

## Possible statuses

- `Proposed` — under discussion
- `Accepted` — approved by the team
- `Rejected` — evaluated and discarded (document why)
- `Superseded` — superseded by ADR-NNN (indicate which one)

## ADR register

| # | Title | Status | Date |
|---|-------|--------|------|
| ADR-001 | Documentation Language | Accepted | 2026-09-08 |
| ADR-002 | Microservice Boundaries | Accepted (ms-alert folded by ADR-015) | 2026-09-09 |
| ADR-003 | Database Engine and Domain Data Ownership | Accepted (clarified 2026-10-28) | 2026-09-09 |
| ADR-004 | Communication Patterns Between Components | Accepted (ingestion path updated 2026-10-28) | 2026-09-09 |
| ADR-005 | API Gateway as the External Backend Entry Point | Accepted | 2026-09-09 |
| ADR-006 | JWT Authentication and Service-Level RBAC | Accepted | 2026-09-09 |
| ADR-007 | At-Least-Once Events with Transactional Outbox | Accepted (implementation status 2026-10-28) | 2026-09-09 |
| ADR-008 | Database Migration Tool | Accepted | 2026-09-17 |
| ADR-009 | Hexagonal Architecture | Accepted | 2026-09-17 |
| ADR-010 | Containerization Strategy | Accepted | 2026-09-17 |
| ADR-011 | Production Deployment Strategy | Accepted | 2026-09-17 |
| ADR-012 | Observability Stack | Accepted | 2026-09-17 |
| ADR-013 | Circuit Breaker Adoption | Accepted | 2026-09-17 |
| ADR-014 | Environmental Sensor Variables and Thresholds | Accepted | 2026-09-17 |
| ADR-015 | Fold Alert Management into ms-environment-monitoring | Accepted | 2026-10-06 |
| ADR-016 | Multi-Tenancy by Institution and Campus | Accepted | 2026-10-06 |
| ADR-017 | OAuth2/OIDC Authorization Server and Backend-for-Frontend | Accepted | 2026-10-06 |
| ADR-018 | JWT-Only Mesh Authentication | Accepted | 2026-10-17 |
| ADR-019 | Jenkins as the Official CI/CD (GHCR, auto-deploy on main) | Accepted | 2026-10-17 |
| ADR-021 | Offline Measurement Buffering and Device-Side `measuredAt` | Accepted | 2026-10-29 |

> Add rows here as you create ADRs in `records/`
