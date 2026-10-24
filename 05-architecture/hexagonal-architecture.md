# Hexagonal Architecture (Ports & Adapters) — as implemented in EduAirControl

> Hexagonal architecture, proposed by Alistair Cockburn, organizes a service so that the
> **business domain is completely independent** of the surrounding technology.
> The database, the web framework, the message broker — all are interchangeable details.
> What matters is the business logic, which lives at the center.
>
> This document describes how the `ms-*` Spring Boot services implement the pattern.
> For the generic concept guide, see the stack notes below.

> **Stack note:** The generic concepts are valid for any language.
> - Java + Spring Boot → [`_stacks/java-spring.md`](../_stacks/java-spring.md)
> - Node.js + TypeScript → [`_stacks/node-typescript.md`](../_stacks/node-typescript.md)

---

## 1. The problem it solves

```
❌ Traditional layered architecture:

  [HTTP Controller]
       ↓
  [Service]
       ↓
  [Repository]
       ↓
  [Database]

Problem: The "Service" mixes business logic with framework calls.
If you change the framework, you break the business. If you want to test the business,
you need to simulate the database.
```

```
✓ Hexagonal Architecture in EduAirControl:

[REST Controller]  [@RabbitListener]  [Tests]
        │                 │             │
        └─────────────────┼─────────────┘
                          │
                  [Inbound port / use case]
                          │
                   ┌───────────────┐
                   │    DOMAIN     │
                   │  (model, VOs, │
                   │   services)   │
                   └───────────────┘
                          │
                  [Outbound port (repository interface)]
                          │
              ┌───────────┴───────────┐
              │                       │
       [JPA Adapter]            [Messaging Adapter]
```

---

## 2. Standard package structure (all services)

All six `ms-*` services use the same base layout, with the base package
`com.eduaircontrol.<service>` and packages `domain` / `application` / `infrastructure`:

```
src/main/java/com/eduaircontrol/<service>/
├── domain/                          # The hexagon — business rules
│   ├── model/                       # Aggregate roots, entities, value objects, enums
│   ├── port/
│   │   ├── in/                      # Driving ports: use case contracts (monitoring)
│   │   └── out/                     # Driven ports: repository interfaces
│   ├── service/                     # Pure domain services (e.g. PeriodResolver)
│   ├── event/                       # Domain events
│   └── exception/                   # Domain exceptions (NotFoundException, Conflict…)
├── application/                     # Use cases / application services (orchestrators)
├── infrastructure/                  # Everything external to the hexagon
│   ├── inbound/web/                 # Primary adapters: REST controllers + DTOs
│   ├── outbound/persistence/        # Secondary adapters: JPA repos + adapters
│   ├── messaging/                   # RabbitMQ listener/config or outbox (sensor)
│   ├── security/                    # JWT filters, SecurityConfig
│   └── (shared/…)                   # Cross-cutting per service
└── <Service>Application.java        # Bootstrap
```

> **Note on layout naming:** actual service code varies. For example,
> `ms-environment-monitoring` models the domain inside a deeper structure
> (`analysis/…`), and `ms-security` places repository ports under
> `application/port/` instead of `domain/port/out/`. The `domain → application →
> infrastructure` dependency rule is the invariant that matters.

---

## 3. The Ports (interfaces defined by the domain)

The domain defines interfaces (ports); infrastructure provides the implementations.

### Driven port — repository interface

```java
// domain/port/out/ — no Spring Data in the interface
public interface EducationalEnvironmentRepository {
    Optional<EducationalEnvironment> findById(UUID id);
    PageResult<EducationalEnvironment> search(...);
}
```

### Driving port — use case interface (ms-environment-monitoring)

```java
// domain/port/in/
public interface RequestAnalysisUseCase {
    CommandResult execute(Command command);   // record Command { ... }
}
```

---

## 4. The Adapters (infrastructure implementations)

### Primary adapter — REST controller

The controller translates the HTTP request to the domain/application call and never
contains business rules.

```java
// infrastructure/inbound/web/
@RestController
@RequestMapping("/api/v1/classrooms")
public class EducationalEnvironmentController {
    private final EducationalEnvironmentService service;   // use case
    // maps DTO <-> request and delegates
}
```

### Secondary adapter — JPA repository

The domain port is implemented by a JPA repository + an adapter class.

```java
// infrastructure/outbound/persistence/
@Repository
public class EducationalEnvironmentRepositoryAdapter
        implements EducationalEnvironmentRepository {   // the domain contract
    private final EducationalEnvironmentJpaRepository jpa;   // Spring Data
    // translates entity <-> domain and enforces pagination bounds
}
```

---

## 5. The Use Case (application layer)

The application service orchestrates the domain through ports and contains no framework
logic.

```java
// application/
@RequiredArgsConstructor
@Service
public class EducationalEnvironmentService {
    private final EducationalEnvironmentRepository repo;
    // business flow: validate -> mutate domain -> persist through the port
}
```

---

## 6. The Dependency Rule

> Dependencies always point inward.
> `domain/` imports nothing from `application/` or `infrastructure/`.
> `infrastructure/` imports from `domain/`.

```
infrastructure/ → application/ → domain/
                                    ↑
                         CANNOT import from application/ or infrastructure/
```

---

## 7. How each service adheres (consistency matrix)

| Concern | ms-security | ms-classroom | ms-sensor | ms-env-monitoring | ms-user-mgmt | ms-user-exp |
|---------|-------------|--------------|-----------|-------------------|--------------|-------------|
| `domain` / `application` / `infrastructure` split | Yes | Yes | Yes | Yes | Yes | Partial |
| Repository port in `domain/port/out/` | No (in `application/port/`) | Yes | Yes | Yes | Yes | No |
| Use-case ports (`domain/port/in/`) | No | No | No | Yes | No | No |
| JPA adapter implements domain port | Yes | Yes | Yes | Yes | Yes | No |
| Domain events | No | No | Outbox events | Yes (`EnvironmentalDataAnalyzed`) | No | No |
| CQRS read model | No | No | No | Yes | No | No |
| RabbitMQ (pub/sub) | No (Redis only) | No | Producer (outbox) | Consumer (inbox) | No | No |
| Global exception handler | Yes | Yes | Yes | Yes | Yes | Yes |
| JWT auth filter | Yes (RS256) | Yes (HS256/headers) | Yes | Yes | Yes | Yes |
| Tenant isolation | Yes | Yes | Yes | Yes | Yes | No |

Summary:
- **`ms-environment-monitoring`** is the most mature: full ports & adapters, explicit
  inbound use-case ports, CQRS read models, domain events, idempotent messaging.
- **`ms-security`** relocates repository ports under `application/port/` and adds
  OAuth2/Redis outbound adapters.
- **`ms-user-experience`** only partially follows the layout (simple entities used directly
  by application services), while still providing controllers and global exceptions.
- All services keep Service/Repository layers and unified error handling; none leak
  framework types into the domain contracts through pagination (`PageResult<T>`).

---

## 8. Concrete examples per service

| Service | Domain aggregates | Ports (out) | Adapters |
|---------|-------------------|-------------|----------|
| ms-security | `User`, `Institution`, `Role`, `RefreshToken` | `UserRepository`, `RoleRepository`, `InstitutionRepository`, `RefreshTokenRepository`, `PasswordResetTokenRepository` | JPA adapters, `RedisTokenBlacklist`, `DeviceProvisioner` |
| ms-classroom-management | `EducationalEnvironment`, `Campus`, `EnvironmentType` | `EducationalEnvironmentRepository`, `CampusRepository`, `EnvironmentTypeRepository` | `*JpaRepository` + `*RepositoryAdapter` |
| ms-sensor-management | `Sensor`, `SensorInstallation`, `SensorVariable`, `Device`, `Variable` | `SensorRepository`, `SensorInstallationRepository`, `SensorVariableRepository`, `DeviceRepository`, `VariableRepository` | JPA adapters + outbox (`OutboxWriter`, `OutboxRelay`, `OutboxPublisher`) |
| ms-environment-monitoring | `EnvironmentalAnalysis` (state machine), `AnalysisResult`, `EnvironmentAlert` | `AnalysisRepository`, `AnalysisStatusRepository`, `MeasurementRepository`, `AlertRepository` (+ `MeasurementAggregationPort`, `ThresholdPort`, `EnvironmentLookupPort`, `UserIdentityPort`) | JPA adapters, `AnalysisResultLoader`, `MeasurementAggregationDao` (JdbcTemplate), RabbitMQ listeners |
| ms-user-management | `UserProfile` | `UserProfileRepository` | JPA adapter |
| ms-user-experience | `Favorite`, `UserPreference` | — | Controllers + services; environment projection and event inbox |

---

## 9. Advantages for TDD (how the codebase uses them)

1. **Domain is testable without framework mocks.** `PeriodResolver` (monitoring) is pure
   logic with an injected `Clock`.
2. **Driven ports can be faked.** Services are tested with fake/in-memory repositories or
   H2 and Testcontainers.
3. **Invariants are explicit.** `EnvironmentalAnalysis` guards state transitions
   (`PENDING → RUNNING → COMPLETED | FAILED`) with `requireStatus(...)`.

> See full TDD guide in `11-quality/tdd-guide.md` and the test strategy in
> `11-quality/testing-strategy.md`.

---

## 10. Hexagonal Architecture checklist

When reviewing a PR or a new service, verify:

- [ ] `domain/` has no imports from `infrastructure/` or `application/`
- [ ] `domain/` has no imports from Spring/Jakarta frameworks
- [ ] Every repository interface lives in `domain/port/out/` (or `application/port/` in ms-security)
- [ ] Every use case interface lives in `domain/port/in/`
- [ ] Mappers (`toDomain` / `toPersistence`) live in `infrastructure/`, not in `domain/`
- [ ] HTTP API DTOs live in `infrastructure/inbound/web/`, not in `domain/`
- [ ] There is a unit test for each Aggregate invariant

---

## 11. Common mistakes (anti-patterns)

| Anti-pattern | Why it is bad | Solution |
|-------------|--------------|---------|
| `import javax.persistence.*` in the domain | Couples the domain to JPA | Define your own port interface |
| Business logic in the Controller | If you change the endpoint, you change the business | Move to the service/aggregate |
| Repository returning DTOs instead of domain objects | The domain cannot validate invariants | Use a mapper to reconstruct the aggregate |
| Use case with many dependencies | It probably does too much | Split into smaller use cases |
| Leaking Spring Data types (Page/Pageable) into ports | Couples the contract to the framework | Use `PageResult<T>` |

---

## References and correlations

- Generic concept (any language) → `_stacks/*` guides
- Bounded Contexts → `02-domain/domain-map.md`
- Entities and invariants → `02-domain/entities-and-rules.md`
- Domain events → `02-domain/domain-events.md`
- Complementary patterns (CQRS, Event Sourcing, Saga) → `05-architecture/pattern-guide.md`
- TDD applied to hexagonal architecture → `11-quality/tdd-guide.md`
- Service template → `09-microservices/_template/service/`
