# Risk Register

> Unmitigated risks become problems. This register allows the team to
> anticipate, not just react.
> Review and update at each retrospective or when there is a significant project change.

---

## Probability × impact matrix

```
IMPACT
  │
  │ HIGH  │  [Mitigate]    │  [Avoid]       │
  │       │  Low           │  High          │
  │       │  Probability   │  Probability   │
  │───────────────────────────────────────
  │ MEDIUM│  [Accept]      │  [Mitigate]    │
  │       │  with monitoring│              │
  │───────────────────────────────────────
  │ LOW   │  [Accept]      │  [Accept]      │
  │       │                │               │
  └───────────────────────────────────────
              LOW              HIGH
                      PROBABILITY
```

**Response strategies:**
- **Avoid:** Change the plan so the risk cannot materialize
- **Mitigate:** Reduce the probability or impact
- **Transfer:** Pass the risk to another party (insurance, provider, contract)
- **Accept:** Acknowledge the risk and have a contingency plan

---

## Active risk register

> Filled in from the 2026-10-08 source-code audit. Risks closed during that work
> are listed under «Closed risks» at the end.

### R-001 — Identity spoofing via `X-User-*` headers

| Field | Value |
|-------|-------|
| **ID** | R-001 |
| **Category** | Technical / Security |
| **Description** | All five services accept `X-User-Id` and `X-User-Role` without checking where they come from. Anyone reaching a service port directly can impersonate ADMIN and pick the tenant (`X-Institution-Id`, `X-Campus-Id`). The `esp32_sensor_sender.ino` firmware relies on this on purpose. |
| **Probability** | High |
| **Impact** | High |
| **Risk level** | Critical |
| **Strategy** | Mitigate |
| **Mitigation plan** | Enforce a gateway-only network path (network policy / mTLS) or a shared header secret validated by every service; in parallel have services validate the real JWT and treat gateway headers as a fallback only. |
| **Contingency plan** | If abuse is detected, close internal mesh access and force all traffic through the gateway. |
| **Trigger** | Access logs hitting internal ports directly, or tokens whose roles do not match the real user. |
| **Owner** | Backend team |
| **Review date** | 2026-10-31 |
| **Status** | Active |

---

### R-002 — RSA private key committed in the ms-security repository

| Field | Value |
|-------|-------|
| **ID** | R-002 |
| **Category** | Technical / Security |
| **Description** | `ms-security/src/main/resources/keys/dev-private.pem` is versioned and is the default key (`security.rsa.*-key-path`) any deployment would use. The superadmin account is seeded with the default password `EduAirControl1!`. |
| **Probability** | High |
| **Impact** | High |
| **Risk level** | Critical |
| **Strategy** | Mitigate |
| **Mitigation plan** | Remove the key from the repository and the classpath: load it from an environment variable or a secret manager. Require `SUPERADMIN_PASSWORD` and `JWT_SECRET` with `:?` in every compose file. Rotate the exposed key. |
| **Contingency plan** | Immediate key and superadmin password rotation; audit tokens issued with the compromised key. |
| **Trigger** | The repository becomes reachable outside the team or appears in a public fork. |
| **Owner** | Backend team |
| **Review date** | 2026-10-15 |
| **Status** | Active |

---

### R-003 — Open CORS with credentials on the gateway

| Field | Value |
|-------|-------|
| **ID** | R-003 |
| **Category** | Technical / Security |
| **Description** | `BffSecurityConfig` allows `setAllowedOriginPatterns("*")` with `allowCredentials(true)`. The `CORS_ALLOWED_ORIGINS` variable exists in compose and configmap but **no code reads it**: it is dead configuration. |
| **Probability** | Medium |
| **Impact** | High |
| **Risk level** | High |
| **Strategy** | Mitigate |
| **Mitigation plan** | Restrict the allowed origins from real configuration and either wire the variable up or delete it. |
| **Contingency plan** | If CSRF or data leakage is detected, narrow the origins manually. |
| **Trigger** | Requests arriving from origins other than the application. |
| **Owner** | Backend team |
| **Review date** | 2026-10-31 |
| **Status** | Active |

---

### R-004 — Coverage is unenforced despite NFR-006

| Field | Value |
|-------|-------|
| **ID** | R-004 |
| **Category** | Technical |
| **Description** | `11-quality/testing-strategy.md` sets ≥80% lines (≥90% in domain) and a "coverage may not decrease" rule, but no `pom.xml` has JaCoCo and there is no coverage gate. Contract, E2E and performance tests do not exist. Both frontends have zero tests. |
| **Probability** | High |
| **Impact** | Medium |
| **Risk level** | High |
| **Strategy** | Mitigate |
| **Mitigation plan** | Add JaCoCo with a threshold to the six services and enforce it in the pipeline. Add at least smoke tests to web and mobile. |
| **Contingency plan** | Freeze new features until coverage is back on target. |
| **Trigger** | NFR-006 remains «Pending» in the traceability matrix. |
| **Owner** | QA team |
| **Review date** | 2026-11-15 |
| **Status** | Active |

---

### R-005 — `ms-user-experience` missing from k8s and from CI

| Field | Value |
|-------|-------|
| **ID** | R-005 |
| **Category** | Technical / Operations |
| **Description** | The service exists and runs under `docker compose`, but `deploy/k8s/` has neither a Deployment nor a Postgres for it and `build-services.yml` leaves it out of the matrix. `wait-for-services.sh` only waits for 4 services. |
| **Probability** | High |
| **Impact** | Medium |
| **Risk level** | High |
| **Strategy** | Avoid |
| **Mitigation plan** | Complete `apps.yaml`, `postgres.yaml` and the CI matrix; extend the wait script. |
| **Contingency plan** | Do not promote to production until it is deployable. |
| **Trigger** | A k8s deployment leaves the frontend without favourites or preferences. |
| **Owner** | DevOps team |
| **Review date** | 2026-10-31 |
| **Status** | Active |

---

### R-006 — Observability is decorative

| Field | Value |
|-------|-------|
| **ID** | R-006 |
| **Category** | Technical / Operations |
| **Description** | `observability/prometheus.yml` scrapes `/actuator/prometheus` on 4 services, but no `pom.xml` includes actuator or micrometer: every target fails. Three services are missing from the scrape config, the OTel collector exports only to `debug`, and Grafana has no datasources or dashboards. |
| **Probability** | High |
| **Impact** | Medium |
| **Risk level** | High |
| **Strategy** | Mitigate |
| **Mitigation plan** | Add `spring-boot-starter-actuator` and `micrometer-registry-prometheus` to the six services, complete the scrape list, and give the collector a real backend. |
| **Contingency plan** | Until then, diagnose with logs and the smoke script. |
| **Trigger** | An incident needs diagnosing and there are no metrics. |
| **Owner** | DevOps team |
| **Review date** | 2026-11-15 |
| **Status** | Active |

---

### R-007 — Drift between ADR-003 and the actual deployment

| Field | Value |
|-------|-------|
| **ID** | R-007 |
| **Category** | Technical |
| **Description** | ADR-003 mandates one shared PostgreSQL instance with a schema per service, but compose and k8s run six independent Postgres servers. `HistoricalBackfillService` joins across schemas (`sensors`, `classrooms`) that live in different databases under that topology, so it cannot work. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk level** | Medium |
| **Strategy** | Avoid |
| **Mitigation plan** | Decide the definitive topology, update ADR-003, and fix the backfill (or retire it if it is no longer needed). |
| **Contingency plan** | Keep the backfill disabled, which is already the default. |
| **Trigger** | Someone enables `BACKFILL_ENABLED=true` and it fails. |
| **Owner** | Backend team |
| **Review date** | 2026-11-30 |
| **Status** | Active |

---

### R-008 — Circuit Breaker documented but not implemented

| Field | Value |
|-------|-------|
| **ID** | R-008 |
| **Category** | Technical |
| **Description** | ADR-013 is Accepted but `05-architecture/overview.md` acknowledges it is not implemented. Without it, an ms-security outage leaves the gateway with no way to degrade gracefully. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk level** | Medium |
| **Strategy** | Accept |
| **Mitigation plan** | Implement it once there are synchronous inter-service calls with an SLA; today the gateway only validates tokens locally. |
| **Contingency plan** | Explicit timeouts and retries in HTTP clients. |
| **Trigger** | Synchronous REST calls between services are introduced. |
| **Owner** | Backend team |
| **Review date** | 2026-12-15 |
| **Status** | Accepted |

---

### R-009 — Device firmware off-contract

| Field | Value |
|-------|-------|
| **ID** | R-009 |
| **Category** | Technical / External |
| **Description** | Two unconsolidated firmwares exist: `esp32_sensor_sender.ino` posts over plain HTTP to :3003 while forging ADMIN headers (it depends on R-001), and `infra/iot/esp32-node` does not compile, targets the wrong service and port, and uses the wrong JSON body and auth header. |
| **Probability** | High |
| **Impact** | Medium |
| **Risk level** | Medium |
| **Strategy** | Mitigate |
| **Mitigation plan** | A single firmware, using a device credential (not headers) against the real ingest contract. Document the chosen ingest channel in ADR-004. |
| **Contingency plan** | Keep the working `.ino` as the reference until the definitive one exists. |
| **Trigger** | Real hardware is deployed with the broken firmware. |
| **Owner** | IoT team |
| **Review date** | 2026-11-15 |
| **Status** | Active |

---

### R-010 — Frontend has no tests and no shared contracts

| Field | Value |
|-------|-------|
| **ID** | R-010 |
| **Category** | Technical |
| **Description** | `apps/web` and `apps/mobile` have no tests at all and mobile has no ESLint. The API layer is duplicated between the two and diverging, with no shared contract package against the backend. The mobile app was written against an API that does not exist. |
| **Probability** | High |
| **Impact** | Medium |
| **Risk level** | Medium |
| **Strategy** | Mitigate |
| **Mitigation plan** | Generate the contracts from OpenAPI and share them; smoke tests per app; ESLint for mobile. |
| **Contingency plan** | Manual review of the critical flow before each release. |
| **Trigger** | A contract change breaks the frontend with no test catching it. |
| **Owner** | Frontend team |
| **Review date** | 2026-11-30 |
| **Status** | Active |

---

### R-011 — Documentation that describes things that do not exist

| Field | Value |
|-------|-------|
| **ID** | R-011 |
| **Category** | Team |
| **Description** | The docs declare Jenkins as CI (the real one is GitHub Actions), list 6 UML diagrams with no source file, `local-setup.md` has the wrong auth-service port (3001 instead of 8081), and about 18 referenced files do not exist. The workspace `AGENTS.md` files claimed `ms-environment-monitoring` was a copy of `ms-sensor-management`, which was already false. |
| **Probability** | High |
| **Impact** | Low |
| **Risk level** | Medium |
| **Strategy** | Mitigate |
| **Mitigation plan** | Review cross-references at every delivery and keep the service catalogue as the single place for service facts. |
| **Contingency plan** | Standing rule: trust the executable source and flag the drift. |
| **Trigger** | Someone follows a document instead of the code. |
| **Owner** | Whole team |
| **Review date** | 2026-10-31 |
| **Status** | Active |

---
## Common technical risks in microservices

These risks apply to almost all microservices projects. Evaluate which ones apply:

| Risk | Typical probability | Standard mitigation |
|------|--------------------|--------------------|
| Failure cascade (one service down brings everything down) | Medium | Circuit Breaker, timeout, fallback |
| Data inconsistency between services | High | Saga, Outbox, idempotent events |
| Network latency in synchronous calls | High | gRPC, cache, async where possible |
| Lost messages in the broker | Medium | At-least-once + idempotent consumers |
| Schema evolution breaks consumers | High | Version events, compatible changes first |
| Technical debt accumulation | High | DoD with minimum coverage, regular reviews |
| Premature over-engineering | Medium | Start simple, YAGNI, measure before optimizing |
| Sensitive data exposure in logs | Medium | Logging policy, PII masking, SAST |
| Configuration drift between environments | High | Infrastructure as Code, environment variables |

---

## Closed risks / Lessons learned

| ID | Risk | Outcome | Lesson |
|----|------|---------|--------|
| R-012 | Los tokens de ms-security no interoperaban con el resto de servicios (HS256 con secreto compartido vs RS256) | Occurred | Cerrado el 2026-10-08: los cinco servicios validan RS256 contra el JWKS de ms-security (ADR-006). Lección: un ADR «Accepted» no significa que esté implementado; hay que referenciarlo en la Definition of Done. |
| ID | Risk | Outcome | Lesson |
|----|------|---------|--------|
| R-012 | Tokens issued by ms-security did not interoperate with the other services (HS256 with a shared secret vs RS256) | Occurred | Closed 2026-10-08: the five services validate RS256 against the ms-security JWKS (ADR-006). Lesson: an «Accepted» ADR does not mean it is implemented; reference it in the Definition of Done. |
| R-013 | The `ms-classroom-management` outbox never published (missing table, missing `@EnableScheduling`, and events carrying random UUIDs) | Occurred | Closed 2026-10-08. Lesson: a feature with no integration test against a real broker can look finished and never deliver a single message. |
| R-014 | The event pipeline had no producers: `ms-environment-monitoring` consumed `sensor.installation.*` and `EnvironmentalDataRecorded` that nobody published | Occurred | Closed 2026-10-08: installation outbox in ms-sensor-management and HTTP ingest as the single measurement path. Lesson: consuming something untested keeps the debt invisible. |
| R-015 | Live metrics never reached the frontend (score always 100, temperature `undefined`) | Occurred | Closed 2026-10-08 with `GET /api/v1/environments/current`. Lesson: the UI must not assume fields no endpoint returns; the contract is the source of truth. |
## Template for adding a new risk

```markdown
### R-00X — [Name]

| Field | Value |
|-------|-------|
| **ID** | R-00X |
| **Category** | |
| **Description** | |
| **Probability** | |
| **Impact** | |
| **Risk level** | |
| **Strategy** | |
| **Mitigation plan** | |
| **Contingency plan** | |
| **Trigger** | |
| **Owner** | |
| **Review date** | |
| **Status** | Active |
```

---

## Correlations

- External dependencies → `15-project-control/dependencies.md`
- Related open questions → `15-project-control/open-questions.md`
- Architectural decisions that mitigated risks → `05-architecture/decisions/`
