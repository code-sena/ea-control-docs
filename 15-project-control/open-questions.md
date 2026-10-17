# Open Questions

> Questions nobody on the team can answer alone. When a question gets an answer,
> turn it into an ADR (if architectural) or close it here and say where the answer
> lives. An unanswered question is a risk with a deadline.

---

| # | Question | Context | Required for | Who answers | Deadline | Status |
|---|----------|---------|-------------|-------------|---------|--------|
| Q-001 | Which database topology is definitive: one shared PostgreSQL instance with a schema per service (ADR-003), or one server per service (what compose and k8s actually deploy)? | `HistoricalBackfillService` joins across schemas and cannot work with per-service databases. `config/env` and `infra/` describe different topologies. | Closing R-007 / TD-007 | Tech Lead | 2026-11-30 | 🔴 Unanswered |
| Q-002 | Should `EnvironmentalDataRecorded` exist as a broker event at all, given that `POST /api/v1/measurements` is now the single ingest path? | The consumer was removed on 2026-10-08 in favour of HTTP ingest. If a future sensor fleet cannot do HTTP, the event path has to come back and the idempotency story changes. | ADR-004 (Communication Patterns) review | Tech Lead | 2026-11-15 | 🔴 Unanswered |
| Q-003 | What credential do devices use to ingest measurements? | The header hole is closed (R-001, ADR-018: `esp32_sensor_sender.ino` now gets 401). Devices need a real credential — `infra/iot/esp32-node` already sketches the device-token flow (`roles:["DEVICE"]`), but it does not compile yet. | Closing R-009 | Security + IoT team | 2026-10-31 | 🟡 Partially answered |
| Q-004 | Where does the RSA private key of ms-security live in production? | The committed copy is gone from the repo (R-002, 2026-10-17): runtime keys come from gitignored `infra/secrets/*.pem`, dev keys from `scripts/generate-dev-keys.sh`, tests from `target/test-keys/`, with a rotation runbook (§3.3.2.1). Remaining question: move from file-based secrets to a secret manager (Vault/Sealed Secrets) for production. | Production hardening | DevOps | 2026-10-15 | 🟡 Deferred |
| Q-005 | Is the Circuit Breaker (ADR-013) still needed, or should the ADR be marked superseded? | It was accepted but never implemented, and today the gateway only validates tokens locally. | ADR-013 status | Tech Lead | 2026-12-15 | 🟡 Deferred |
| Q-006 | Do we adopt Jenkins or GitHub Actions as the official CI? | ADR-010/011 and `01-context/overview.md` say Jenkins; the only pipeline that exists is GitHub Actions. | `10-devops/ci-cd.md` | Tech Lead | 2026-11-15 | 🔴 Unanswered |
| Q-007 | What is the actual `user_management` data model? | `06-data/domain/` has a model for every other schema but not for `user_management`. The glossary claims `ms-iam.md` covers both IAM services, but `user_profile` does not appear in it. | Closing the 06-data gap | Backend team | 2026-11-15 | 🔴 Unanswered |
| Q-008 | Which UML diagrams are actually required? | `08-uml/diagram-index.md` registers 6 diagrams (C4, sequence, ER) and `diagrams/source/` is empty. Either produce the sources or drop the registry. | `08-uml/` | Whole team | 2026-11-30 | 🔴 Unanswered |
| Q-009 | Is `institution` / `campus` created by a SUPER_ADMIN only, or can an institution admin provision its own campuses? | `ms-security` exposes `/api/v1/institutions/**` for SUPER_ADMIN; `ms-classroom-management` exposes `/api/v1/campuses/**` for ADMIN. The onboarding flow is not defined anywhere. | Multi-tenancy onboarding (ADR-016) | Product owner | 2026-11-15 | 🔴 Unanswered |
| Q-010 | What is the retention policy for `environment_measurement` and `environment_alert`? | Nothing documents how long raw measurements are kept or when they are aggregated and dropped. | `13-operations/backup-and-recovery.md` | Product owner | 2026-12-01 | 🔴 Unanswered |

---

## Status legend

- 🔴 **Unanswered** — blocks or will block work.
- 🟡 **Deferred** — deliberately postponed, with a date to revisit.
- 🟢 **Answered** — moved to an ADR or to the relevant document; keep the row and
  say where the answer lives.

---

## Resolved

| # | Question | Answer | Where it lives |
|---|----------|--------|----------------|
| Q-011 | Do the five services share a JWT secret or validate against the issuer's JWKS? | Validate RS256 against the ms-security JWKS. | ADR-006, implemented 2026-10-08 |
| Q-012 | Are measurements ingested by HTTP or by broker events? | HTTP (`POST /api/v1/measurements`) is the single path; the event consumer was removed. | Closed in TD-018; revisit at Q-002 |
