# Normalization Assessment

> Cross-cutting normalization review of the business models under `06-data/domain/`.
> It predates the retirement of UX ratings/search history and is not the runtime table inventory. See `guia-base-de-datos.md` for current tables and retained legacy tables.
> Source of truth for normalization verdicts, the entity-to-table crosswalk,
> registered denormalizations, and open items.

---

## Scope

| Domain file | Notation | Tables owned |
|---|---|---|
| `ms-iam.md` | SQL | 13 |
| `ms-classroom-management.md` | DBML | 3 |
| `ms-sensor-management.md` | DBML | 7 |
| `ms-environment-monitoring.md` | DBML | 11 |
| `ms-alert.md` | SQL | 2 |
| `ms-user-experience.md` | text-tree + SQL | 4 |
| **Total (unique)** | | **34** |

> Counts include the `severity` lookup table added for `variable_threshold.severity_id` (open item 5).
> Six names are defined in more than one domain file (referenced copies): `educational_environment`,
> `sensor`, `sensor_installation`, `variable`, `sensor_variable`, `environment_alert` —
> row-wise sum is 40, unique union is 34.

---

## Normalization verdict per domain

| Domain | 1NF | 2NF | 3NF | Notes |
|---|---|---|---|---|
| `ms-iam` | Pass (asserted) | Pass (asserted) | Pass (asserted) | Self-documented at `ms-iam.md:1390–1409`; associative tables use composite PKs. |
| `ms-classroom-management` | Pass | Pass | Pass | Status field is application-level text; candidate for a reference table (`ms-classroom-management.md:217`). |
| `ms-sensor-management` | Pass | Pass | Pass | `sensor_models` and `measurement_units` keep attributes out of `sensor`/`variable` (`ms-sensor-management.md:161,269,606`). |
| `ms-environment-monitoring` | Pass (asserted) | Pass | Pass | Explicit 1NF note at `ms-environment-monitoring.md:169–175`; threshold resolved by FK, not copied (`:190`). |
| `ms-alert` | Pass | Pass | Pass | Statuses in a separate table (`ms-alert.md:155`); `triggering_value` intentionally not stored (`:361`). |
| `ms-user-experience` | Pass | Pass | Pass | Four flat tables; cross-domain references are logical, not physical FKs. |

**Overall verdict:** all six domains are documented as conforming to 3NF.
No intentional denormalization (JSONB, materialized copies) was found.

---

## Entity → table crosswalk

Maps the 7 entities in `02-domain/entities-and-rules.md` to canonical tables.

| Entity (02) | Owning domain file | Canonical table(s) |
|---|---|---|
| `User` (`:76`) | `ms-iam.md` | `users` |
| `EducationalEnvironment` (`:154`) | `ms-classroom-management.md` | `educational_environment` |
| `EnvironmentalData` (`:198`) | `ms-environment-monitoring.md` | `environment_measurement` |
| `EnvironmentalDataAnalysis` (`:248`) | `ms-environment-monitoring.md` | `environmental_analysis` + `analysis_result` |
| `Sensor` (`:298`) | `ms-sensor-management.md` | `sensor` |
| `Variable` (`:330`) | `ms-sensor-management.md` | `variable` |
| `VariableThreshold` (`:361`) | `ms-environment-monitoring.md` | `variable_threshold` |

**Naming note:** the entity was previously named `EnvironmentData` in the heading and
`EnvironmentalData` in aggregates/summary. Aligned to `EnvironmentalData` in
`02-domain/entities-and-rules.md`; DB name remains `environment_measurement`.

---

## Registered denormalizations

| Location | What | Why it is acceptable |
|---|---|---|
| `ms-sensor-management.md:161` | `sensor_model` attributes shared across `sensor` | Normalization *into* `sensor_models`, not a denormalization. |
| `ms-sensor-management.md:269` | `measurement_unit_id` FK instead of unit text | Correct FK reference; no duplication. |
| `ms-environment-monitoring.md:190` | Threshold not copied into measurements | Resolved by FK at query time. |
| `ms-alert.md:361` | `triggering_value` not stored on `environment_alert` | Referenced via `triggering_measurement_id`. |
| `ms-alert.md:155` | Statuses stored in `alert_status`, not inline | Avoids repeating literal status strings. |
| `ms-iam.md:1419` | Status info kept in `user_statuses`/`session_statuses` | Avoids duplication in `users`/`user_sessions`. |

**No blocking denormalizations found.**

---

## Open items

| # | Issue | Location | Severity |
|---|---|---|---|
| ~~1~~ | ~~Broken FK: `REFERENCES app_user(user_id)`~~ **Resolved** — now `REFERENCES users(user_id)` | `ms-alert.md:194` | ~~High~~ Done |
| ~~2~~ | ~~Singular/plural mismatch: `educational_environments`~~ **Resolved** — all occurrences renamed to `educational_environment` per `00-governance/documentation-rules.md:54` | `ms-classroom-management.md`, `ms-sensor-management.md`, `ms-environment-monitoring.md`, ERs | ~~High~~ Done |
| ~~3~~ | ~~Monolith ↔ microservices contradiction~~ **Resolved** — reworded to microservices + shared PostgreSQL instance per ADR-002/ADR-003 | `ms-alert.md:5,13,15,30`; `ms-classroom-management.md:17,103,263,320,337,574,578`; `ms-environment-monitoring.md:579,605,841` | ~~High~~ Done |
| ~~4~~ | ~~Migration tool split: Flyway vs Liquibase~~ **Resolved** — Liquibase standardized in `ms-iam`, `ms-sensor-management`, `ms-user-experience`, and `10-devops/local-setup.md` | see plan lines | ~~High~~ Done |
| ~~5~~ | ~~Dangling column: `severity_id` with no referenced table~~ **Resolved** — `severity` lookup table + FK added to the DBML | `ms-environment-monitoring.md:82` | ~~Medium~~ Done |
| ~~6~~ | ~~Typo: `senor_models`~~ **Resolved** → `sensor_models` | `ms-sensor-management.md:150` | ~~Medium~~ Done |
| ~~7~~ | ~~ER/prose model `ENVIRONMENTAL_STATUS` / `ENVIRONMENTAL_STATISTICS` not in the DBML~~ **Resolved** — prose, indexes, events, domain boundary, ER, and domain-fit diagram realigned to `environmental_analysis` / `analysis_result` | `ms-environment-monitoring.md` §8–12, §14–16, §19, §21 | ~~Medium~~ Done |
| ~~8~~ | ~~Classroom `status` not normalized into a reference table~~ **Accepted** — kept as an app-level validated `varchar(30)` per source intent; revisit only if lifecycle management grows more complex | `ms-classroom-management.md:217` | ~~Low~~ Accepted |
| ~~9~~ | ~~Entity name mismatch in 02: `EnvironmentData` vs `EnvironmentalData`~~ **Resolved** — aligned to `EnvironmentalData` | `02-domain/entities-and-rules.md:198` | ~~Low~~ Done |
| ~~10~~ | ~~UX domain declares "Table names use plural `snake_case`", conflicting with the singular core-table rule~~ **Resolved (exemption)** — active UX tables `user_preferences` and `favorites` retain their service-local plural names; renamed `legacy_*` tables are archival, not active domain tables | `ms-user-experience.md` | ~~Low~~ Done |
| ~~11~~ | ~~Sensor FK column named `environment_id`~~ **Resolved** — renamed to `educational_environment_id` (DBML, indexes, prose, diagrams) | `ms-sensor-management.md` | ~~Low~~ Done |
| ~~12~~ | ~~Cross-domain duplicate tables with name/schema drift~~ **Resolved** — owning domain renamed to singular (`sensor`, `sensor_installation`, `variable`, `sensor_variable`), monitoring copies aligned (`measurement_unit_id` + audit columns), crosswalk/traceability/entities updated | `ms-sensor-management.md`, `ms-environment-monitoring.md:48–74`, `04-requirements/traceability-matrix.md:78–79` | ~~High~~ Done |
| ~~13~~ | ~~Residual Spanish outside the Phase 7 OpenAPI scope~~ **Resolved** — `09-microservices/services/01-api-gateway/{data-model,events,runbook,decisions}.md`, `02-ms-security/{data-model,events,runbook,decisions}.md`, and `.env.example` translated to English per ADR-001 | see listed files | ~~Medium~~ Done |

---

## Correlations

- Fed by: `02-domain/entities-and-rules.md` (entity inventory).
- Feeds: `04-requirements/traceability-matrix.md` (entity→table coverage), `07-api/contracts/` (exposed schemas).
- Governance: `00-governance/documentation-rules.md` (singular table names, canonical service names).
