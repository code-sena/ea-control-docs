# ADR-016 — Multi-Tenancy by Institution and Campus

- **ID:** ADR-016
- **Date:** 2026-10-06
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl is used by multiple educational institutions (for example `SEN-444`).
Each institution may operate several campuses (sedes), and each campus contains
educational environments and sensors. A user must only see and manage the data of the
institution (and campus) they belong to.

Today the platform only stores a `company_code` on the user and checks it at login
(`ms-security` does not model it at all). No service filters data by institution, so
there is **no real tenant isolation**. This decision is required before building the
monitoring and experience services, because it determines the identity model, the token
claims, the campus ownership, and the query scoping of every domain service.

**Known constraints:**
- One user belongs to exactly **one institution** and **one campus (sede)**.
- Admins are scoped to their **whole institution** (all its campuses).
- `company_code` is the institution code and keeps its name.
- Isolation must be **strict**: a user must never read another institution's data.
- Identity data is owned by `ms-security`; campuses are owned by `ms-classroom-management`
  (ADR-003: one schema per service; cross-domain references by UUID, no cross-schema FK).

---

## Decision

**We decided:** Model the **institution** as a tenant owned by `ms-security`, and treat
`company_code` as the institution code. Every user carries `institution_id` and
`campus_id` (campus nullable only for institution-wide admins). The access token includes
`institution_id` and `campus_id` claims; the gateway propagates them as
`X-Institution-Id` / `X-Campus-Id`; every domain service enforces isolation by filtering
its queries with the institution (and campus, for non-admin users) from the token.
`ms-classroom-management` stores `campus.institution_id` (reference by UUID) so
environments, sensors and measurements can be scoped transitively
(`environment → campus → institution`).

**Justification:**
Identity and access control already live in `ms-security`, and the tenant is part of the
token, so the institution model belongs there. Referencing the institution by UUID from
the campus preserves ADR-003 without cross-schema foreign keys. Enforcing isolation in
each service follows the existing defense-in-depth principle (ADR-006).

> **Note (2026-10-07):** `company_code` is required at **registration** (to join an
> institution) but **not at login**: `users.email` is globally unique, so the email already
> identifies the user and the institution is resolved from the account. This avoids the
> friction and the misleading "invalid credentials" errors caused by re-typing the code.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Institution owned by `ms-security`; campus references it by UUID — chosen | Single place for identity + tenant; token carries tenant; keeps ADR-003 | Campus needs the institution UUID (managed via admin) | — (chosen) |
| New `ms-organization` service | Clear organization domain | Extra deployment, contract, schema; overlaps identity | Not justified for the MVP team size |
| Institution owned by `ms-classroom-management` | Campuses already there | Login would depend on classroom; identity/tenant split | Couples authentication to a business service |
| One database per tenant (physical isolation) | Strongest isolation | Operationally heavy; overkill for the MVP | Deferred; revisit only with regulatory need |

---

## Consequences

**Positive:**
- Real tenant isolation with a single source of truth for institutions.
- Token-carried tenant enables stateless enforcement in every service.
- Transitive scoping through `campus → institution` avoids duplicating the institution id
  on every domain row.

**Negative / Trade-offs:**
- Every domain service must enforce scoping; a missed filter becomes a data leak.
- Cross-domain reference (`campus.institution_id`) needs an admin flow and a migration.
- Existing users have only `company_code`; a data migration is required.

**Impact on the system:**
- Affected services: `ms-security` (owner), `ms-classroom-management` (campus.institution_id),
  `ms-sensor-management`, `ms-environment-monitoring`, `ms-user-management`,
  `ms-user-experience`, `api-gateway` (header propagation).
- Documents to update: `06-data/domain/ms-iam.md`, `06-data/domain/ms-classroom-management.md`,
  `06-data/domain/ms-sensor-management.md`, `06-data/domain/ms-environment-monitoring.md`,
  `07-api/contracts/openapi/*`, `09-microservices/service-catalog.md`.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| A service forgets to filter by institution (data leak) | Medium | High | Mandatory isolation tests per service; review checklist |
| Migration loses the link between old users and institutions | Medium | High | Migration script + dry-run + verification queries |
| Admin scope ambiguity (institution vs campus) | Low | Medium | `campus_id` nullable = institution-wide admin; documented |
| Institution code reused/renamed | Low | Medium | `company_code` unique and immutable per institution |

---

## References

- Database strategy and ownership → `ADR-003`
- Authentication and RBAC → `ADR-006`
- OAuth2/OIDC token flow → `ADR-017`
- IAM data model → `06-data/domain/ms-iam.md`
