# Unit Tests Report

> Summary of the backend unit-tests status. The full report (ES + EN, PDF) is
> Deliverable 07 in the documentation repository:
> `EduAirControl/ea-control-documentation/07_unit-tests-report/`
> (`07_Informe_Pruebas_Unitarias_ES.md` / `07_Unit_Tests_Report_EN.md` + PDFs).

**Run:** 2026-10-11 · `./mvnw -B clean verify` on `develop` · JDK 21 (`--release 17`)
· Docker 29.7.2 for Testcontainers.

## Headline numbers

| Metric | Value |
|--------|-------|
| Automated tests (all types) | **294** — 0 errors, 0 failures |
| **Pure unit tests** | **100 tests in 15 classes** (34 % of total) |
| Slice tests (`@SpringBootTest` + MockMvc + H2) | 89 in 9 classes |
| Spring tests with mocks (services, listeners, filters) | 40 in 9 classes |
| Container-based integration (Testcontainers) | 65 in 11 classes |
| Test classes total | 44 across 7 services |
| Accumulated test time | ≈167 s |

## Per service (tests / errors / failures)

| Service | Tests | Pure unit |
|---------|-------|-----------|
| api-gateway | 27 | 6 |
| ms-security | 57 | 12 |
| ms-classroom-management | 33 | 10 |
| ms-sensor-management | 55 | 36 |
| ms-user-management | 20 | 8 |
| ms-environment-monitoring | 92 | 28 |
| ms-user-experience | 10 | 0 (Testcontainers only) |
| **Total** | **294** | **100** |

## What a unit test means here

JUnit 5 + Mockito + AssertJ in full isolation: no Spring context, no database,
no network. Covers domain aggregates (`EnvironmentalAnalysisTest` state machine),
application services (`SensorServiceTest`, `InstitutionServiceTest`,
`UserProfileServiceTest`), domain services (`PeriodResolverTest`), and the
asynchronous event contracts (`*EventTest`).

**Not unit:** `@SpringBootTest` slice tests over H2, Testcontainers tests against
real PostgreSQL/RabbitMQ, and `infra/scripts/smoke.sh` — the last one is a manual
**E2E smoke check** of the identity flow (health → login → institution → register
→ logout → revoked token = 401), not a unit test and not in CI.

## Findings (2026-10-11)

| # | Finding | Target |
|---|---------|--------|
| H1 | No JaCoCo configured — RNF6 (≥ 80 % lines) not measurable | Add JaCoCo + failing gate |
| H2 | CI runs `verify` without `clean` (64 spurious errors today) | `./mvnw -B clean verify` |
| H3 | `ms-user-experience` missing from CI matrix | Add to matrix |
| H4 | `smoke.sh` runs only manually | Staging pipeline / manual job |
| H5 | `api-gateway` working copy broken by uncommitted edit | Finish or revert (suite vs HEAD is 27/27 green) |
| H6 | `MICROSERVICIOS.md` says «139 tests» and marks two services pending | Update to 294 |

## Correlations

- Full strategy (tiers, coverage thresholds, CI) → `11-quality/testing-strategy.md`
- TDD process → `11-quality/tdd-guide.md`
- RNF6 coverage requirement → `04-requirements/`
- Deliverable 02 (RF/CU numbering used in the report) → `03_Analisis_Software` catalogue
