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
| ADR-002 | Microservice Boundaries | Proposed | 2026-09-09 |
| ADR-003 | Database Engine and Domain Data Ownership | Accepted | 2026-09-09 |
| ADR-004 | Communication Patterns Between Components | Proposed | 2026-09-09 |
| ADR-005 | API Gateway as the External Backend Entry Point | Proposed | 2026-09-09 |
| ADR-006 | JWT Authentication and Service-Level RBAC | Proposed | 2026-09-09 |
| ADR-007 | At-Least-Once Events with Transactional Outbox | Proposed | 2026-09-09 |

> Add rows here as you create ADRs in `records/`
