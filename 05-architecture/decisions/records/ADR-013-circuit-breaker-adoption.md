# ADR-013 — Circuit Breaker Adoption

- **ID:** ADR-013
- **Date:** 2026-09-17
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl microservices communicate synchronously via REST APIs, creating dependencies between services. The `05-architecture/overview.md` references Circuit Breaker with Resilience4j but lacks a formal ADR documenting the decision.

A decision is required now because:
- Inter-service communication can fail and cause cascading failures
- User experience degrades when dependent services are unavailable
- The system needs resilience mechanisms for production reliability
- The team needs guidelines for implementing circuit breakers

**Known constraints:**
- The project uses Spring Boot microservices
- Synchronous REST communication between services
- The team of three needs simplicity and ease of implementation
- Integration with Spring Boot ecosystem is preferred

---

## Decision

**We decided:** Adopt Resilience4j as the Circuit Breaker implementation for critical inter-service communication.

**Justification:**
Resilience4j provides a lightweight, functional approach to circuit breaking with:
- Excellent Spring Boot integration via `spring-boot-starter-resilience4j`
- Circuit Breaker, Rate Limiter, Retry, and Bulkhead patterns
- Functional programming approach with decorators
- Minimal overhead and footprint
- Active community and comprehensive documentation

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Resilience4j — chosen | Lightweight, functional, Spring Boot integration, multiple patterns | Learning curve for functional approach | Chosen for simplicity and comprehensiveness |
| Hystrix (Netflix) | Battle-tested, mature | Deprecated, maintenance mode, heavier footprint | Rejected due to deprecation |
| Sentinel (Alibaba) | Rich flow control, dashboard included | Less Spring Boot integration, heavier | Over-engineered for current needs |
| Custom implementation | Full control, no dependencies | High maintenance, error-prone, reinventing the wheel | Not sustainable for production systems |

---

## Consequences

**Positive:**
- Prevents cascading failures between services
- Improves system resilience and fault tolerance
- Provides fallback mechanisms for degraded functionality
- Integrates seamlessly with Spring Boot via starter
- Supports multiple resilience patterns (Circuit Breaker, Rate Limiter, Retry)

**Negative / Trade-offs:**
- Adds complexity to inter-service communication
- Requires configuration tuning for each service
- May mask underlying issues if not monitored properly
- Fallback logic needs to be designed for each use case

**Impact on the system:**
- Affected services: All services with synchronous inter-service communication
- Documents that must be updated: `05-architecture/overview.md`, `05-architecture/pattern-guide.md`, service-specific documentation

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Incorrect circuit breaker configuration | Medium | Medium | Start with sensible defaults, tune based on monitoring |
| Fallback logic introduces bugs | Medium | Medium | Test fallback scenarios thoroughly, keep fallbacks simple |
| Circuit breaker masks underlying issues | Low | High | Monitor circuit breaker state changes, alert on频繁 trips |
| Performance overhead from decorators | Low | Low | Benchmark critical paths, minimize unnecessary decorators |

---

## References

- Resilience4j documentation: https://resilience4j.readme.io/
- Spring Boot Resilience4j integration: https://docs.spring.io/spring-cloud-circuitbreaker/docs/current/reference/html/
- Pattern guide: `05-architecture/pattern-guide.md`
- Related to: ADR-004 (Communication Patterns), ADR-012 (Observability Stack)
