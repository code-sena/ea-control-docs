# ADR-012 — Observability Stack

- **ID:** ADR-012
- **Date:** 2026-09-17
- **Status:** Accepted
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl requires a comprehensive observability stack to monitor, trace, and debug microservices. The `05-architecture/overview.md` references Prometheus, Grafana, and OpenTelemetry but lacks a formal ADR documenting the decision.

A decision is required now because:
- Production services need monitoring for performance and availability
- Debugging distributed microservices requires distributed tracing
- Alerting on service health issues is critical for reliability
- The team needs visibility into system behavior

**Known constraints:**
- The team of three needs simplicity and ease of management
- Infrastructure costs should be minimal for MVP
- Integration with Spring Boot ecosystem is required
- Open-source tools are preferred

---

## Decision

**We decided:** Adopt Prometheus for metrics, Grafana for visualization, and OpenTelemetry for distributed tracing.

**Justification:**
This combination provides comprehensive observability:
- **Prometheus:** Industry-standard metrics collection with excellent Spring Boot integration via Micrometer
- **Grafana:** Powerful visualization and alerting with pre-built dashboards
- **OpenTelemetry:** Vendor-neutral distributed tracing with automatic instrumentation

Together, they cover the three pillars of observability: metrics, logs, and traces.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Prometheus + Grafana + OpenTelemetry — chosen | Industry standard, excellent Spring Boot integration, open-source, comprehensive coverage | Requires setup and configuration | Chosen for completeness and community support |
| Datadog / New Relic | Managed service, less operational overhead, advanced features | Expensive, vendor lock-in, less control | Rejected due to cost and vendor lock-in |
| ELK Stack (Elasticsearch, Logstash, Kibana) | Powerful log analysis, full-text search | Heavyweight, complex setup, resource-intensive | Over-engineered for current needs |
| Jaeger alone | Excellent distributed tracing | No metrics or visualization, requires additional tools | Incomplete observability solution |

---

## Consequences

**Positive:**
- Comprehensive observability covering metrics, logs, and traces
- Excellent Spring Boot integration via Micrometer
- Open-source with strong community support
- Vendor-neutral with OpenTelemetry
- Pre-built dashboards and alerting rules available
- Scales from development to production

**Negative / Trade-offs:**
- Requires initial setup and configuration
- Storage requirements for metrics and traces
- Learning curve for Prometheus query language (PromQL)
- Additional infrastructure to maintain
- **Estado (2026-10):** Prometheus y Grafana corren en el overlay de observabilidad; OpenTelemetry aún no está cableado a los servicios (pendiente).

**Impact on the system:**
- Affected services: All microservices, infrastructure components
- Documents that must be updated: `05-architecture/overview.md`, `13-operations/observability.md`, service-specific documentation

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Storage overflow from metrics/traces | Medium | Medium | Implement retention policies, monitor storage usage |
| Performance overhead from instrumentation | Low | Low | Use sampling for traces, monitor resource usage |
| Configuration complexity | Medium | Medium | Start with defaults, provide templates and documentation |
| Alert fatigue from too many alerts | Medium | Medium | Define clear alerting thresholds, categorize alerts by severity |

---

## References

- Prometheus documentation: https://prometheus.io/docs/
- Grafana documentation: https://grafana.com/docs/
- OpenTelemetry documentation: https://opentelemetry.io/docs/
- Observability guide: `13-operations/observability.md`
- Related to: ADR-010 (Containerization Strategy), ADR-011 (Deployment Strategy)
