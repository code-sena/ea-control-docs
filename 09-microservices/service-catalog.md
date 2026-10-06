# Microservices Catalog

> Complete inventory of EduAirControl services. For detail per service,
> go to `09-microservices/services/NN-service-name/`.

---

## Services map

```
                         ┌──────────────────┐
  External clients       │    API Gateway   │
  (Web, Mobile)     ──▶ │       :8080      │
                         └────────┬─────────┘
                                  │ routes by path
          ┌───────────┬───────────┴────────────┬──────────────────┐
          ▼           ▼                        ▼                  ▼
 ┌────────────────┐ ┌────────────────────┐ ┌─────────────────────────┐ ┌────────────────────┐
 │  ms-security   │ │ms-user-management  │ │ ms-environment-monitoring│ │ms-sensor-management│
 │     :8081      │ │       :3007        │ │          :3003           │ │       :3004        │
 └────────────────┘ └────────────────────┘ └────────────┬────────────┘ └────────────────────┘
                                                        │
 ┌────────────────────┐ ┌────────────────────┐          │
 │ms-classroom-mgmt   │ │ ms-alert ⏸ (dep.)  │          │
 │       :3002        │ │  folded into #05   │          │
 └────────────────────┘ └────────────────────┘          │
                                          ┌─────────────┴──────────────┐
                                          │       Message Broker       │
                                          │         (RabbitMQ)         │
                                          └────────────────────────────┘
```

---

## Service registry

| # | Service | Main responsibility | Port | DB | Status |
|---|---------|-------------------|------|-----|--------|
| 01 | `api-gateway` | Routing, authentication, rate limiting | 8080 | Redis | 🟢 Active |
| 02 | `ms-security` | Registration, login, JWT tokens, RBAC | 8081 | PostgreSQL | 🟢 Active |
| 03 | `ms-classroom-management` | Educational environment management | 3002 | PostgreSQL | 🟡 In development |
| 04 | `ms-sensor-management` | Sensor registration and management | 3004 | PostgreSQL | 🟢 Active |
| 05 | `ms-environment-monitoring` | Environmental data collection and analysis | 3003 | PostgreSQL | 🟢 Active |
| 06 | `ms-alert` ⏸ | Deprecated — alert generation folded into `ms-environment-monitoring` (ADR-015) | — (was 3005) | — | ⏸ Deprecated |
| 07 | `ms-user-experience` | User preferences and experience | 3006 | PostgreSQL | 🟢 Active |
| 08 | `ms-user-management` | User information management | 3007 | PostgreSQL | 🟢 Active |

**Statuses:** 🟢 Active | 🟡 In development | 🔴 Planned | ⏸ Deprecated

> Canonical names per `01-context/glossary.md` → Canonical service names.

---

## Service communication matrix

| Source service | Destination service | Channel | Type | Description |
|----------------|--------------------|---------|------|-------------|
| api-gateway | ms-security | HTTP/REST | Synchronous | Validate JWT on each request |
| api-gateway | ms-classroom-management | HTTP/REST | Synchronous | CRUD educational environments |
| api-gateway | ms-sensor-management | HTTP/REST | Synchronous | CRUD sensors |
| api-gateway | ms-environment-monitoring | HTTP/REST | Synchronous | Query environmental data |
| api-gateway | ms-user-management | HTTP/REST | Synchronous | CRUD users |
| ms-sensor-management | ms-environment-monitoring | Event | Asynchronous | Sensor data measurements |
| ms-environment-monitoring | ms-user-experience | Event | Asynchronous | EnvironmentalDataAnalyzed |

> The former `ms-environment-monitoring → ms-alert` event link (`EnvironmentalDataRecorded`) is now an **internal** concern of `ms-environment-monitoring` (ADR-015).

---

## Data ownership matrix

| Entity / Data | Owner service | How other services access |
|---------------|---------------|--------------------------|
| User / Identity | ms-security | REST API (`GET /users/:id`) |
| User information | ms-user-management | REST API (`GET /users/:id`) |
| Educational Environment | ms-classroom-management | REST API (`GET /api/v1/educational-environments/{id}`) |
| Sensor | ms-sensor-management | REST API (`GET /sensors/:id`) |
| Environmental Data | ms-environment-monitoring | Event `EnvironmentalDataRecorded` |
| Alert | ms-environment-monitoring | REST API (published in the `ms-environment-monitoring` contract, ADR-015) |
| User Preferences | ms-user-experience | REST API (`GET /preferences/:userId`) |

---

## Correlations

- Architecture → `05-architecture/overview.md`
- ADRs → `05-architecture/decisions/`
- API contracts → `07-api/contracts/openapi/`
- Domain events → `02-domain/domain-events.md`
- Data models → `06-data/domain/`
- Canonical names → `01-context/glossary.md`
