# Testing Strategy

> Defines what, how much, and with which tools to test at each layer.
> Complements the TDD guide (`tdd-guide.md`) that explains the process.
> This document is the project's quality contract.
>
> **Status (2026-10-11):** the pyramids below describe the strategy the team
> commits to. Items marked **[gap]** are not yet in place; they come from the
> unit-tests report (`unit-tests-report.md`) and are tracked as findings.

---

## Project testing pyramid

Current distribution of the 294 automated backend tests (run of 2026-10-11):

```
                 /\
                /  \
               /    \
              /  E2E  \     ← 0 automated today (manual smoke.sh)  [gap H4]
             /────────────\
            /  Integration  \
           /    [22%]        \  ← 65 tests: Testcontainers vs real PostgreSQL/RabbitMQ
          /──────────────────\
         /   Slice (@SpringBootTest + H2)
        /       [30%]         \  ← 89 tests: controllers with MockMvc over in-memory H2
       /──────────────────────\
      /      Unit Tests        \
     /         [34%]            \  ← 100 tests: JUnit 5 + Mockito, full isolation
    /────────────────────────────\
```

**Rule:** More tests at the bottom = more maintainable system at lower cost.
Inverting the pyramid (more E2E than unit tests) makes CI slow and fragile.

---

## Tier 1: Unit Tests

**Objective:** Test business logic in complete isolation.

| Aspect | Value |
|--------|-------|
| **What they test** | Aggregates, value objects, domain services, application services, event builders |
| **Isolation** | Complete — no Spring context, no database, no network |
| **Speed** | < 5 ms per test |
| **Target coverage** | ≥ 80% of lines, ≥ 90% in `src/main/java/**/domain/` (RNF6) |
| **Tools** | JUnit 5, Mockito, AssertJ |
| **Doubles** | Mockito mocks and stubs, manual fakes built with constructors |
| **When they run** | On every `./mvnw verify` (CI and pre-merge) |
| **Current state** | 100 tests in 15 classes across all 7 services — **no coverage metric yet** [gap H1] |

**Folder structure (hexagonal layout):**

```
src/test/java/.../
├── domain/                  # pure domain tests
│   ├── model/               #   aggregates: EnvironmentalAnalysisTest
│   ├── service/             #   domain services: PeriodResolverTest
│   └── event/               #   event contracts: SensorInstallationEventTest
├── application/             # application services with mocked ports
└── infrastructure/          # controllers (slice tests), listeners, persistence
```

**Unit test example:**

```java
@Test
void createRejectsDuplicatedCode() {
    when(repository.existsByCode("ABC")).thenReturn(true);

    assertThatThrownBy(() -> service.create(new CreateInstitution("ABC", "Name")))
        .isInstanceOf(DuplicateCodeException.class);

    verify(repository, never()).save(any());
}
```

---

## Tier 2: Slice Tests (`@SpringBootTest` + MockMvc + H2)

**Objective:** Verify controllers and their security configuration without a real database.

| Aspect | Value |
|--------|-------|
| **What they test** | HTTP routing, request/response mapping, security (JWT), validation |
| **Isolation** | Medium — full Spring context, in-memory H2, Liquibase disabled |
| **Speed** | 50 ms – 2 s per test |
| **Tools** | `@SpringBootTest`, MockMvc, H2 (`src/test/resources/application-test.properties`) |
| **When they run** | On every `./mvnw verify` |
| **Current state** | 89 tests in 9 classes (auth, classroom, sensor, user-management, gateway) |

```java
@Test
@WithMockUser(authorities = "ADMIN")
void createCampusReturns201() throws Exception {
    mockMvc.perform(post("/api/v1/campuses")
            .contentType(MediaType.APPLICATION_JSON)
            .content(payload))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.code").value("BOGOTA"));
}
```

---

## Tier 3: Integration Tests (Testcontainers)

**Objective:** Verify that adapters work against real systems.

| Aspect | Value |
|--------|-------|
| **What they test** | Repositories vs real PostgreSQL, RabbitMQ listeners vs real broker |
| **Isolation** | Low — real services in Docker |
| **Speed** | 1 – 30 s per test |
| **Tools** | Testcontainers (PostgreSQL 15, RabbitMQ 3) + JUnit 5 |
| **When they run** | On every `./mvnw verify` where Docker is available (CI runners) |
| **Current state** | 65 tests in 11 classes (`ms-environment-monitoring`, `ms-user-experience`) |

Base class pattern used by those two services:

```java
@SpringBootTest
@Testcontainers
abstract class PostgresTestBase {
    @Container
    static PostgreSQLContainer<?> PG = new PostgreSQLContainer<>("postgres:15");
    // datasource properties bound from PG.getJdbcUrl() before the context loads
}
```

Services with H2 slice tests (`ms-security`, `ms-classroom-management`,
`ms-sensor-management`, `ms-user-management`) may migrate to this pattern later;
until then H2 is the agreed compromise for speed.

---

## Tier 4: Contract Tests

**Objective:** Verify that what a service publishes (HTTP contract or event) is what
consumers expect.

| Aspect | Value |
|--------|-------|
| **What they test** | OpenAPI contracts (`docs-ea-control/07-api/`) and RabbitMQ event envelopes |
| **Tools (events)** | Plain JUnit event-contract tests: payload, routing key, `eventId` |
| **Tools (HTTP)** | Spring Cloud Contract **[gap — planned]** |
| **When they run** | On every `./mvnw verify` |
| **Current state** | Event contracts covered: `SensorInstallationEventTest`, `EducationalEnvironmentCreatedEventTest`, `EnvironmentalDataAnalyzedTest` |

```java
@Test
void serializedEnvelopeMatchesWhatTheConsumerReads() {
    var json = mapper.writeValueAsString(envelope);
    assertThat(json).contains("\"routingKey\":\"sensor.installation.installed\"");
    // consumer side reads the same fields — see ms-environment-monitoring listener
}
```

---

## Tier 5: End-to-End Tests (E2E)

**Objective:** Verify complete flows as the end user experiences them.

| Aspect | Value |
|--------|-------|
| **What they test** | Critical business flows through the API Gateway with the full stack |
| **Isolation** | None — real deployed environment (`docker compose up -d`) |
| **Speed** | 5 s – 60 s per flow |
| **Tools** | `infra/scripts/smoke.sh` (bash + curl + jq), k6 for load **[gap — planned]** |
| **When they run** | Manually today; target: staging pipeline / `workflow_dispatch` [gap H4] |

**Priority E2E flows:**

| # | Flow | Services involved |
|---|------|------------------|
| 1 | health → superadmin login → create institution → register user → login → logout → revoked token rejected | api-gateway, ms-security, ms-user-management (**implemented** in `smoke.sh`) |
| 2 | Create classroom → create sensor → install → publish measurement | classroom, sensor, monitoring **[gap]** |
| 3 | Login → rate limit exceeded → 429 | api-gateway **[gap]** |

**The `smoke.sh` is not a unit test** — it is the E2E layer. Do not add it to
`./mvnw verify` or treat its result as unit coverage.

---

## Performance Tests

**Objective:** Verify that NFR performance requirements are met under load.

| Aspect | Value |
|--------|-------|
| **Tool** | k6 **[gap — planned]** |
| **When they run** | In the staging pipeline (not on every PR) |
| **Failure criterion** | If P95 > 300 ms or error rate > 1% |

---

## CI configuration (actual pipeline)

The live pipeline is `infra/.github/workflows/build-services.yml`: for each
`EduAirControl/ea-control-*` repository it sets up JDK 17 and runs Maven verify.

```yaml
# infra/.github/workflows/build-services.yml (simplified)
jobs:
  verify:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repo: [api-gateway, ms-security, ms-classroom-management,
               ms-sensor-management, ms-user-management,
               ms-environment-monitoring]   # ms-user-experience missing [gap H3]
    steps:
      - uses: actions/checkout@v4          # of the ea-control-* repo
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - run: ./mvnw -B clean verify        # `clean` required [gap H2]
```

Required changes (from `unit-tests-report.md`):

1. Use `clean verify` — stale `target/` classes caused 64 spurious errors today.
2. Add `ms-user-experience` to the matrix.
3. Add a JaCoCo coverage gate (see thresholds below).

---

## Code coverage — thresholds per layer

**[gap H1]** JaCoCo is not configured in any `pom.xml` yet. Target once added:

```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <executions>
    <execution>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>report</id><phase>verify</phase>
      <goals><goal>report</goal></goals>
    </execution>
    <execution>
      <id>check</id><phase>verify</phase>
      <goals><goal>check</goal></goals>
      <configuration>
        <rules>
          <rule>
            <element>BUNDLE</element>
            <limits>
              <limit><counter>LINE</counter><value>COVEREDRATIO</value><minimum>0.80</minimum></limit>
              <limit><counter>BRANCH</counter><value>COVEREDRATIO</value><minimum>0.70</minimum></limit>
            </limits>
          </rule>
          <rule>
            <element>BUNDLE</element>
            <includes><include>**/domain/**</include></includes>
            <limits>
              <limit><counter>LINE</counter><value>COVEREDRATIO</value><minimum>0.90</minimum></limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

**Coverage rule:** if a PR lowers the global coverage, CI fails.
Coverage cannot go down — if there is uncovered code, tests must be added in the same PR.

---

## Test data and secrets in tests

```
src/test/resources/
└── application-test.properties   # H2, Liquibase off, ddl-auto=create-drop
target/test-keys/                 # ephemeral RSA pair, NEVER committed
```

- Tests generate their own RSA key pair **in memory** and publish only the public
  key under `target/test-keys/` so JWT validation can load a JWKS. **Never commit
  a `.pem`** — see the `ms-*` AGENTS.md notes.
- Test users are created by the tests themselves (or seeded by
  `SuperAdminBootstrapTest`); there is no shared seed database.
- Event-contract tests build their own payloads; no external fixtures.

---

## Correlations

- Complete TDD guide → `11-quality/tdd-guide.md`
- Unit-tests report (run of 2026-10-11) → `11-quality/unit-tests-report.md`
- Definition of Done (required coverage) → `00-governance/definition-of-done.md`
- OpenAPI contracts to validate → `07-api/contracts/openapi/`
- Hexagonal architecture (facilitates testing) → `05-architecture/`
- CI/CD pipeline → `10-devops/` and `infra/.github/workflows/`
- Requirement RNF6 (coverage ≥ 80%) → `04-requirements/`
