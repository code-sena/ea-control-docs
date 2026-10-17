# Design Patterns and Microservices Guide

> This document is the project's pattern catalog.
> For each pattern: when to use it, when NOT to, and an implementation example.
> Patterns are not recipes — they are tools. Use them when the problem requires it.

> **Stack note:** Descriptions and diagrams are technology-agnostic.
> Illustrative code snippets use pseudo-TypeScript as a reference language
> for its proximity to pseudocode syntax. To see the concrete implementation in your stack:
> [`_stacks/node-typescript.md`](../_stacks/node-typescript.md) ·
> [`_stacks/java-spring.md`](../_stacks/java-spring.md) ·
> [`_stacks/python-fastapi.md`](../_stacks/python-fastapi.md) ·
> [`_stacks/go.md`](../_stacks/go.md)

---

## Index

**Design patterns (GoF and SOLID)**
1. [Creational patterns](#creational)
2. [Structural patterns](#structural)
3. [Behavioral patterns](#behavioral)

**Microservices patterns**
4. [System decomposition](#decomposition)
5. [Inter-service communication](#communication)
6. [Resilience](#resilience)
7. [Data and consistency](#data)
8. [Observability](#observability)

---

## Design patterns (GoF) {#creational}

### 1. Factory Method

**Problem:** You want to create objects without exposing the creation logic or coupling code to the concrete type.

**When to use it:**
- When the exact type of object to create is not known until runtime
- When creation has complex logic (validations, configuration)

**Domain example:**

```typescript
// Factory Method — inside the Aggregate Root
class Order {
  // Instead of new Order(...), we use a factory method
  static create(customerId: CustomerId, items: OrderItem[]): Order {
    if (items.length === 0) throw new DomainException('INV-001');
    return new Order(OrderId.new(), customerId, items, OrderStatus.PENDING);
  }

  static reconstitute(data: OrderData): Order {
    // To reconstruct from the database
    return new Order(new OrderId(data.id), new CustomerId(data.customerId), ...);
  }
}
```

---

### 2. Builder

**Problem:** An object has many optional parameters and construction becomes unreadable.

**When to use it:** Complex configuration objects, test data builders.

```typescript
// Builder — especially useful for tests
const order = new OrderBuilder()
  .withCustomer('customer-id-123')
  .withItem(product1, quantity: 2)
  .withItem(product2, quantity: 1)
  .withAddress('5th Street #10-20, Neiva')
  .inStatus(OrderStatus.CONFIRMED)
  .build();
```

---

### 3. Singleton (with caution)

**Problem:** A class must have exactly one instance.

**When to use it:** DB connections, configuration registries.

**WARNING:** Singleton makes testing difficult. Prefer dependency injection.

```typescript
// ✓ Better: Singleton managed by the DI container, not by the class itself
// In the container (NestJS, tsyringe, etc.):
container.registerSingleton(DatabaseConnection, DatabaseConnectionImpl);
```

---

### 4. Adapter (Structural pattern) {#structural}

**Problem:** You want to use an existing class but its interface does not match the one you need.

**When to use it:** Integration with external APIs, third-party libraries.

```typescript
// The domain defines the interface it needs
interface PaymentGatewayPort {
  charge(amount: Money, card: TokenData): Promise<ChargeResult>;
}

// The adapter translates to the external API
class StripePaymentAdapter implements PaymentGatewayPort {
  constructor(private stripe: Stripe) {}

  async charge(amount: Money, card: TokenData): Promise<ChargeResult> {
    // Translate domain model → Stripe model
    const charge = await this.stripe.charges.create({
      amount: amount.toCents(),
      currency: amount.currency,
      source: card.token,
    });
    // Translate Stripe result → domain model
    return new ChargeResult(charge.id, charge.status === 'succeeded');
  }
}
```

---

### 5. Decorator

**Problem:** You want to add behavior to an object without modifying it or inheriting from it.

**When to use it:** Logging, caching, validation, rate limiting around use cases.

```typescript
// Cache decorator around the repository
class CachedOrderRepository implements OrderRepositoryPort {
  constructor(
    private readonly repo: OrderRepositoryPort,
    private readonly cache: CachePort,
  ) {}

  async findById(id: OrderId): Promise<Order | null> {
    const cached = await this.cache.get(`order:${id.value}`);
    if (cached) return OrderMapper.toDomain(cached);

    const order = await this.repo.findById(id);
    if (order) await this.cache.set(`order:${id.value}`, order, TTL_5_MINUTES);
    return order;
  }
}
```

---

### 6. Observer / Internal Event Bus {#behavioral}

**Problem:** An object needs to notify others without knowing them directly.

**When to use it:** To publish domain events after persisting the aggregate.

```typescript
// The Aggregate accumulates events — the UseCase publishes them
class Order {
  private readonly _events: DomainEvent[] = [];

  confirm(): void {
    // ... business logic ...
    this._events.push(new OrderConfirmed(this.id));
  }

  get domainEvents(): DomainEvent[] {
    return [...this._events];
  }

  clearEvents(): void {
    this._events.length = 0;
  }
}
```

---

### 7. Strategy

**Problem:** You want to swap algorithms at runtime.

**When to use it:** Discount strategies, calculation algorithms, payment methods.

```typescript
interface DiscountStrategy {
  calculate(subtotal: Money, user: User): Money;
}

class StudentDiscount implements DiscountStrategy {
  calculate(subtotal: Money, user: User): Money {
    return subtotal.multiply(0.15); // 15% discount
  }
}

class CorporateDiscount implements DiscountStrategy {
  calculate(subtotal: Money, user: User): Money {
    return subtotal.multiply(0.20); // 20% discount
  }
}
```

---

### 8. Template Method

**Problem:** An algorithm has a fixed structure but some steps vary.

**When to use it:** Process flows with variations (export to CSV, Excel, PDF).

```typescript
abstract class ReportExporter {
  // Template Method — fixed structure
  async export(data: ReportData): Promise<Buffer> {
    const validated = await this.validate(data);
    const transformed = await this.transform(validated);
    const buffer = await this.generate(transformed);
    await this.recordExport(data.userId);
    return buffer;
  }

  protected abstract transform(data: ReportData): Promise<TransformedData>;
  protected abstract generate(data: TransformedData): Promise<Buffer>;
  
  // Steps with default implementation (can be overridden)
  protected async validate(data: ReportData): Promise<ReportData> { return data; }
  protected async recordExport(userId: UserId): Promise<void> {}
}
```

---

## Microservices Patterns

### Decomposition {#decomposition}

#### API Gateway

**Problem:** Clients need to call multiple services to get a response.

```
                    ┌─────────────────┐
Mobile ──────────▶  │                 │ ──▶ [Service A]
Web ────────────▶  │   API Gateway   │ ──▶ [Service B]
IoT ────────────▶  │                 │ ──▶ [Service C]
                    └─────────────────┘
                         Does:
                    - Routing
                    - Auth/AuthZ
                    - Rate limiting
                    - SSL termination
                    - Request aggregation
```

**When to use it:** Always, in microservices architectures it is essential.

**Tools:** Kong, AWS API Gateway, NGINX, Traefik, Spring Cloud Gateway.

---

#### Backend for Frontend (BFF)

**Problem:** Mobile and web need data in very different formats but share the same API.

```
Mobile ──▶ [BFF Mobile]  ──▶ Internal services
Web    ──▶ [BFF Web]     ──▶ Internal services
Alexa  ──▶ [BFF Voice]   ──▶ Internal services
```

**When to use it:** When clients have very different needs. Use sparingly — each BFF is an API to maintain.

---

#### Strangler Fig (Incremental migration)

**Problem:** You need to migrate a monolith to microservices without rewriting it all at once.

```
Phase 1:  Client → Monolith (100% traffic)
Phase 2:  Client → API Gateway → Monolith (70%) + New Service (30%)
Phase 3:  Client → API Gateway → New Service (100%) — monolith retired
```

**How:** The API Gateway gradually routes traffic to the new service while the monolith keeps running.

---

### Inter-service communication {#communication}

#### Synchronous: REST / gRPC

| Aspect | REST | gRPC |
|--------|------|------|
| Protocol | HTTP/1.1 or HTTP/2 | HTTP/2 |
| Serialization | JSON (human-readable) | Protocol Buffers (efficient) |
| Typing | Manual with OpenAPI | Automatic with .proto |
| Streaming | Not native | Yes (unidirectional and bidirectional) |
| Recommended use | Public APIs, external communication | Internal service-to-service communication |

**When to use synchronous communication:**
- When you need the response immediately (queries, UI)
- Low-latency operations the user is waiting for

---

#### Asynchronous: Message Broker (Kafka / RabbitMQ)

```
[Service A] ──publishes──▶ [Topic/Queue] ──consumes──▶ [Service B]
                                                        [Service C]
```

**When to use asynchronous communication:**
- When the operation does not require an immediate response
- When you want to decouple producers from consumers
- For background processing (emails, notifications, reports)
- To guarantee delivery (the broker's DB is durable)

---

### Resilience {#resilience}

#### Circuit Breaker

**Problem:** A slow or failing service causes yours to fail too (failure cascade).

```
CLOSED state (normal):
  Calls pass through → if N consecutive failures → switch to OPEN

OPEN state (circuit breaker):
  Calls blocked immediately (fail fast) → after T seconds → HALF-OPEN

HALF-OPEN state (testing):
  Allows 1 call → if it fails: back to OPEN | if it passes: back to CLOSED
```

```typescript
// With opossum or resilience4j
const circuit = new CircuitBreaker(externalService.call, {
  timeout: 3000,                    // Timeout per call
  errorThresholdPercentage: 50,     // % of errors to open
  resetTimeout: 30000,              // Time in OPEN before trying HALF-OPEN
});

circuit.fallback(() => ({ cached: true, data: lastReliableCache }));
```

---

#### Retry with Exponential Backoff

**Problem:** Transient failures (unstable network, service restarting).

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  options = { attempts: 3, backoffBase: 1000 }
): Promise<T> {
  for (let attempt = 1; attempt <= options.attempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === options.attempts) throw err;
      const delay = options.backoffBase * Math.pow(2, attempt - 1); // 1s, 2s, 4s
      await sleep(delay + Math.random() * 100); // Jitter to avoid thundering herd
    }
  }
}
```

---

### Data and consistency {#data}

#### Database per Service

**Rule:** Each microservice has its own database. No service directly accesses another service's database.

```
✓ Correct:
  Service A → Database A
  Service B → Database B

✗ Incorrect:
  Service A → Database B (direct JOIN)
```

**How do I share data then?** With APIs or events, never with direct SQL.

---

#### Saga (Distributed transactions)

**Problem:** A business transaction spans multiple services and you cannot use a distributed ACID transaction.

```
Choreographed Saga (via events):

  [Orders]                  [Inventory]            [Payments]
     │ OrderCreated              │                     │
     │ ─────────────────────▶   │                     │
     │                     StockReserved              │
     │ ◀─────────────────────   │                     │
     │ OrderStockConfirmed                            │
     │ ─────────────────────────────────────────▶    │
     │                                          PaymentApproved
     │ ◀─────────────────────────────────────────    │
```

**Compensations:** If a step fails, execute compensating transactions in reverse order.

```
Step 1: Reserve stock         → Compensation: Release stock
Step 2: Debit payment         → Compensation: Refund
Step 3: Confirm order         → Compensation: Cancel order
```

---

#### CQRS (Command Query Responsibility Segregation)

**Problem:** The logic for writing data is very different from the logic for reading it.
A single model forces suboptimal compromises for both.

```
Write (Commands):                        Read (Queries):
  POST /orders                             GET /orders?customerId=X
       │                                         │
       ▼                                         ▼
  [Command Handler]                       [Query Handler]
       │                                         │
       ▼                                         ▼
  [Aggregate]                            [Read Model / Projection]
       │                                 (denormalized, optimized for reading)
       ▼
  [Event Store / Write DB]
       │
       ▼ (updates the read side via events)
  [Read DB]
```

**When to use it:** When read volume is much higher than write volume, or when queries are very complex to perform on the write model.

**Caution:** Increases complexity. Not always worth it.

---

#### Outbox Pattern (Transactional)

**Problem:** You need to guarantee that when you save to the database, you also publish the event — without risk of publishing it twice or not publishing it if there is a failure.

```
❌ Without Outbox (may lose events):
  BEGIN TRANSACTION
    INSERT INTO orders ...
  COMMIT
  // If the system crashes here, the event is lost
  publishEvent(OrderCreated)

✓ With Outbox (atomic):
  BEGIN TRANSACTION
    INSERT INTO orders ...
    INSERT INTO outbox (event_type, payload, published) VALUES ('OrderCreated', '...', false)
  COMMIT
  // Separate process reads outbox and publishes
  // If publishing fails, the outbox still has the event
```

```sql
-- Outbox table
CREATE TABLE outbox (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type  VARCHAR(100) NOT NULL,
  payload     JSONB NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  published_at TIMESTAMPTZ,
  published   BOOLEAN DEFAULT false
);

-- Index for the Relay (process that publishes pending events)
CREATE INDEX idx_outbox_unpublished ON outbox (created_at) WHERE published = false;
```

---

#### Event Sourcing

**Problem:** You need full audit, reproducing system state at any point in time, or rebuilding projections.

```
Traditional:    DB stores current state → "An order is worth $150"
Event Sourcing: DB stores events        → "OrderCreated($100) + DiscountApplied($-30) + ItemAdded($80)"

To know the current state: you replay all events in order.
```

**When to use it:** Financial auditing, advanced debugging, systems where history matters.

**When NOT to use it:** Most cases. It adds significant complexity. It is not the default solution.

---

### Observability {#observability}

#### Sidecar Pattern

**Problem:** You want to add observability, configuration, or network capabilities to a service without modifying its code.

```
Kubernetes Pod:
  ┌──────────────────────────────┐
  │  [Service A]                │
  │  [Sidecar: Envoy/Istio]    │  ← Handles TLS, metrics, service mesh
  │  [Sidecar: Filebeat]       │  ← Collects logs
  └──────────────────────────────┘
```

---

## When NOT to use each pattern

| Pattern | Do not use it when... |
|---------|----------------------|
| CQRS | The read and write models are similar. It only adds complexity. |
| Event Sourcing | You do not need complete history. It is hard to implement and maintain. |
| Saga | The transaction fits in a single service. Use a simple ACID transaction. |
| Circuit Breaker | The call is internal to the same service. The overhead is not worth it. |
| BFF | Clients have similar needs. A standard API Gateway is sufficient. |

---

## Patterns adopted in this project

> Current state as of October 2026. Where an ADR justifies the decision it is cited;
> a status of "not used" means the pattern is not implemented in the codebase.

| Pattern | Status | Justification / where |
|---------|---------|---------------------|
| API Gateway | **Adopted** — ADR-005 | `api-gateway`: path predicates, JWKS verify, Redis rate limit, correlation IDs, OAuth2 client (BFF) |
| BFF (OAuth2 login) | **Adopted** — ADR-017 | Gateway holds the OAuth2 client + Redis sessions for the web app |
| Database per service | **Adopted in `infra`** (mixed) — ADR-003 | 6 PostgreSQL containers, one per service; 2 services still use shared `eduaircontrol` DB by schema |
| Transactional Outbox | **Adopted** — ADR-007 | `ms-sensor-management` / monolith: `OutboxWriter` → `OutboxRelay` → `OutboxPublisher` → RabbitMQ |
| Inbox (consumer idempotency) | **Adopted** — ADR-007 | `ms-environment-monitoring`: `InboxRepository.claim` (`ON CONFLICT DO NOTHING`) |
| Event-Driven Communication | **Adopted** — ADR-004, ADR-007 | RabbitMQ topic exchange `eduaircontrol.environmental-data`, durable queue, DLQ (7-day retention) |
| CQRS | **Adopted (monitoring only)** | `ms-environment-monitoring`: read model (`environment_measurement`, `installation_projection`, dashboard) vs command side |
| Hexagonal Architecture | **Adopted** — ADR-009 | All `ms-*` services; see `hexagonal-architecture.md` |
| Retry with Exponential Backoff | **Adopted** | Consumer retries 1s → 2s → 4s → 8s (4 attempts) then DLQ (`RejectAndDontRequeueRecoverer`) |
| Circuit Breaker | **Not implemented** — ADR-013 documented | No resilience4j dependency in any service |
| Saga (choreographed) | Not used | No distributed transactions across services |
| Event Sourcing | Not used | Full event history not required |
| Repository | **Adopted** | Domain port + Spring Data JPA adapter per service |
| Aggregate Root + State Machine | **Adopted** | `EnvironmentalAnalysis` (PENDING → RUNNING → COMPLETED | FAILED) |
| Factory Method | **Adopted** | `EnvironmentalAnalysis.request(...)`, event statics (`EnvironmentalDataRecorded.at(...)`) |
| Builder | **Adopted** | Lombok `@Builder` (`OutboxEvent`), Spring `QueueBuilder`/`RegisteredClient.builder()` |
| Adapter / Mapper | **Adopted** | `EnvironmentalReadingMapper`, `AnalysisResultLoader`, `MeasurementAggregationAdapter`, `UserIdentityAdapter` |
| Value Objects / Records | **Adopted** | `PageResult<T>`, `AnalysisPeriod.Window`, event `Payload`/`Metadata` |
| Anti-Corruption Layer / ports | **Adopted (monitoring)** | `shared/contract/` ports (`EnvironmentLookupPort`, `ThresholdPort`, `MeasurementAggregationPort`, `UserIdentityPort`, `VariableCatalogPort`) |
| Token deny-list / refresh rotation | **Adopted** | `RedisTokenBlacklist` (TTL = remaining token lifetime); `AuthService.refresh` rotates |

---

## Patterns in use in the codebase (concrete references)

The catalog above is generic; this is where each pattern is actually applied today.

### Decomposition & communication

- **API Gateway + BFF** — `api-gateway` (`com.eduaircontrol.apigateway`):
  - `JwtAuthenticationFilter` validates RS256 tokens against `ms-security` JWKS and forwards
    the resolved `Authorization` header plus `X-User-Id`, `X-User-Role`, `X-Institution-Id`
    headers — the headers are informational since ADR-018; services authenticate the JWT
    itself and ignores them.
  - `RateLimitFilter` enforces 100 req/60s using Redis (`app.rate-limit`).
  - `CorrelationIdFilter` propagates a correlation ID for tracing.
  - Routes are declared by path predicate in `application.yml`; OAuth2 authorization-code
    client + Redis session for the web BFF (ADR-017).

- **Sync (REST, via gateway only)** — versioned `/api/v1/*` contracts; service-to-service
  calls are prevented (services never call each other over HTTP).

- **Async (RabbitMQ)** — producers:
  - `ms-sensor-management` publishes `SensorInstalled` / `SensorRemoved` via a transactional
    outbox to the topic exchange `eduaircontrol.sensor`.
  - The legacy monolith publishes `EnvironmentalDataRecorded` (measurements) to the topic
    exchange `eduaircontrol.environmental-data`.
  - `ms-environment-monitoring` consumes both (`MeasurementEventListener`,
    `SensorInstallationListener`):
  - Topology declared from the consumer: topic exchanges `eduaircontrol.environmental-data`
    and `eduaircontrol.sensor`, bindings `environmental.data.*` and
    `sensor.installation.*`, durable work queues, DLX/DLQ with 7-day TTL.
  - At-least-once delivery + idempotency: inbox claim in the same transaction plus natural
    key `ON CONFLICT (sensor_installation_id, variable_id, measured_at) DO NOTHING`.
  - Retries: statutory 4 attempts, exponential backoff from 1s (max 10s), then DLQ
    (`RejectAndDontRequeueRecoverer`).
  - `SensorInstalled` / `SensorRemoved` maintain the local `installation_projection`.

### Data & consistency

- **Transactional Outbox** — `OutboxWriter` appends an `outbox_event` row inside the
  business transaction; `OutboxRelay` (`@Scheduled`, 1s) polls the pending rows and
  `OutboxPublisher` sends each in `REQUIRES_NEW` with the `eventId` as message id.
- **Inbox / idempotent consumer** — `InboxRepository.claim` inserts with
  `ON CONFLICT (message_id) DO NOTHING` in the same transaction that applies the effect
  (measurements or projections).
- **CQRS read model** — `ms-environment-monitoring` writes atomic
  `environment_measurement` rows and reads aggregated summary/series through the dashboard;
  `environmental_analysis` holds completed analysis results.

### Domain modeling

- **Aggregate Root + state machine** — `EnvironmentalAnalysis` with factory
  `request(...)` and guarded transitions.
- **Domain services** — `PeriodResolver` resolves `DAY/WEEK/MONTH/YEAR` into `[start, end)`
  windows using an injected `Clock` (pure, deterministic, testable).
- **Value objects** — `PageResult<T>`, `AnalysisPeriod.Window`, `Severity`, composite key
  `SensorVariableId`, event `Payload`/`Metadata` records.

### Security

- **OAuth2 / OIDC authorization server** — `ms-security` (`OAuth2ServerConfig`,
  Spring Authorization Server): clients `ea-control-web` (authorization_code + PKCE),
  `ea-control-mobile`, `ea-control-device` (client_credentials, scope `sensors.write`).
  `OAuth2TokenCustomizer` adds `roles`, `userId`, `permissions` claims.
- **RS256 JWT + JWKS** — `JwtService` signs with an RSA private key,
  `JwksController` exposes `/api/v1/auth/jwks`; `kid` derived from key material.
- **Refresh rotation + revocation** — `AuthService.refresh` rotates (revokes + issues);
  logout blacklists the access-token `jti` in Redis with TTL = remaining lifetime.
- **IoT API key** — monolith `DeviceApiKeyFilter` authenticates ESP32 ingest via `X-API-Key`
  (`DeviceAuthService` resolves the device per API key).
- **Lockout** — `login` locks the account after `lockoutMaxAttempts` (default 5) for
  `lockoutDurationMinutes` (default 15).

### Cross-cutting

- **Repository pattern** — port interface + Spring Data JPA + adapter (`*RepositoryAdapter`).
- **Global exception handler** — every service returns
  `{ status, message }` via `@RestControllerAdvice`; 400/401/403/404/409/500 mapping.
- **Pagination** — `page`/`limit` clamped; `PageResult<T>` keeps ports framework-free.
- **Factory / Builder** — domain factories and Lombok builders across all services.

---

## When NOT to use each pattern

| Pattern | Do not use it when... |
|---------|----------------------|
| CQRS | The read and write models are similar. It only adds complexity. |
| Event Sourcing | You do not need complete history. It is hard to implement and maintain. |
| Saga | The transaction fits in a single service. Use a simple ACID transaction. |
| Circuit Breaker | The call is internal to the same service. The overhead is not worth it. |
| BFF | Clients have similar needs. A standard API Gateway is sufficient. |
| Outbox | You publish within the same request and can tolerate loss. Not for fire-and-forget UX. |

---

## Correlations

- Hexagonal Architecture → `05-architecture/hexagonal-architecture.md`
- ADR for pattern decisions → `05-architecture/decisions/`
- Event delivery and consistency → ADR-007 + `02-domain/domain-events.md`
- Saga implementation → `09-microservices/services/XX/events.md`
- Circuit Breaker runbook → `09-microservices/services/XX/runbook.md`
- Outbox in the data model → `06-data/normalization-assessment.md`
