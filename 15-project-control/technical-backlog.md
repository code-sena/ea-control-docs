# Technical Backlog

> Things that "work but not as they should". Clearly separated from product user
> stories — nothing here is a feature, everything here slows the features down.
> Add an entry the moment the team knowingly takes a shortcut.

---

| ID | Description | Impact if not resolved | Estimated effort | Priority | Sprint |
|----|-------------|------------------------|------------------|---------|--------|
| TD-001 | Add JaCoCo with a coverage threshold to the six services and enforce it in CI. `11-quality/testing-strategy.md` sets ≥80% lines / ≥90% domain but nothing measures it. | NFR-006 stays unverifiable; refactors are unguided. | 3 SP | High | Next |
| TD-004 | Restrict gateway CORS and wire up or delete the unused `CORS_ALLOWED_ORIGINS` (see R-003). | Cross-origin abuse with credentials. | 1 SP | High | Next |
| TD-005 | Add `ms-user-experience` to `deploy/k8s/` and to the `build-services.yml` matrix (see R-005). | The service cannot be deployed in production. | 2 SP | High | Next |
| TD-006 | Add actuator + micrometer to the six services so the Prometheus scrape config actually works (see R-006). | No metrics during incidents. | 3 SP | High | Next |
| TD-007 | Decide the database topology and align ADR-003, compose and k8s; then fix or retire `HistoricalBackfillService` (see R-007). | Cross-schema joins silently fail. | 3 SP | Medium | Later |
| TD-008 | Consolidate the two ESP32 firmwares into one that speaks the real ingest contract with a device credential (see R-009). | Hardware deployed against a broken or insecure path. | 5 SP | Medium | Later |
| TD-009 | Generate frontend API clients from the OpenAPI contracts and share them between web and mobile (see R-010). | Contract changes keep breaking the UI silently. | 8 SP | Medium | Later |
| TD-010 | Add smoke tests to `apps/web` and `apps/mobile` and ESLint to mobile. | No automated verification at all on the frontends. | 5 SP | Medium | Later |
| TD-011 | Remove the Jackson 2 / Jackson 3 mix in `ms-classroom-management/OutboxWriter` (it builds its own Jackson 2 mapper while a Jackson 3 `JsonMapper` is injected and unused). | Subtle serialization differences between producer and consumer. | 1 SP | Low | Later |
| TD-012 | Clean up `ms-environment-monitoring`: triplicated `app.messaging.classroom.*` was already consolidated, but `application.properties` still mixes section numbering and `SensorInstallationListener`/`ClassroomEnvironmentListener` carry duplicated fully-qualified annotations in older revisions. | Low readability. | 1 SP | Low | Later |
| TD-013 | Align test package layout with production (`src/test/.../infrastructure/inbound/web` vs `src/main/.../infrastructure/web` in ms-classroom-management and ms-sensor-management). | Navigation and IDE search are misleading. | 1 SP | Low | Later |
| TD-014 | Delete stale `target/` surefire reports referencing tests that no longer exist (they are not committed, but they mislead local audits). | False signal during code review. | 0.5 SP | Low | Later |
| TD-015 | Fix `ms-security/pom.xml` description: it still says "Sensor registration and management service (sensors domain)". | Misleading for anyone reading the POM. | 0.5 SP | Low | Later |

---

## How to use this

- **Estimated effort** is in story points relative to the team's own scale.
- **Priority** follows `15-project-control/risks.md`: anything that closes a
  *Critical* risk goes first, regardless of effort.
- When an item is done, move it to the "Resolved" table below and say what closed it.

---

## Resolved

| ID | Description | Resolved on | How |
|----|-------------|-------------|-----|
| TD-002 | Close the `X-User-*` header trust in the five services (see R-001). | 2026-10-17 | JWT-only authentication (ADR-018): filters ignore `X-User-*`; tenant comes from JWT claims; negative spoofing tests added per service. |
| TD-003 | Move the RSA private key out of `ms-security/src/main/resources/keys/` and rotate it; require `SUPERADMIN_PASSWORD` (see R-002). | 2026-10-17 | Keys deleted from the repo (gitignored), `SECURITY_RSA_*` and `SUPERADMIN_PASSWORD` required with no defaults, tests generate an ephemeral pair, compose/k8s/smoke enforce the password, rotation procedure in the runbook. |
| TD-016 | `ms-environment-monitoring` did not compile (duplicate `DLQ_ROUTING_KEY` field) and its 86 tests had never run. | 2026-10-08 | Fixed the duplicate field, added a surefire `api.version` for Docker Engine 29, disabled listener auto-startup outside consumer tests and set `spring.test.context.cache.pause=NEVER`. 89 tests green. |
| TD-017 | The `ms-classroom-management` outbox was inert: no `outbox_event` table in Liquibase, no `@EnableScheduling`, `@Scheduled` method with an argument, and `of()` emitting random UUIDs. | 2026-10-08 | Added the migration, enabled scheduling, made the method no-arg, fixed the payload mapping, and added a contract test. |
| TD-018 | The event pipeline had no producers, so `ms-environment-monitoring` consumers were idle and measurements were never visible. | 2026-10-08 | Installation outbox in `ms-sensor-management` and HTTP ingest as the single measurement path. |
| TD-019 | HS256 / RS256 split-brain: tokens from ms-security were rejected by every other service. | 2026-10-08 | All five services validate RS256 against the ms-security JWKS (ADR-006). |
