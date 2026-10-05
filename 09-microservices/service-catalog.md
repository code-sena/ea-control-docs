# Microservices Catalog

> Complete inventory of EduAirControl services. For detail per service,
> go to `09-microservices/services/NN-service-name/`.

---

## Services map

```
                          ┌─────────────────┐
  External clients        │   API Gateway   │
  (Web, Mobile)      ──▶ │   :8080         │
                          └────────┬────────┘
                                   │ routes by path
          ┌────────────┬───────────┴───────────┬─────────────────┐
          ▼            ▼                       ▼                 ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────┐
  │ ms-security  │ │  ms-aulas    │ │   ms-monitoreo   │ │ ms-sensores  │
  │    :3001     │ │    :3002     │ │      :3003       │ │    :3004     │
  └──────────────┘ └──────────────┘ └────────┬─────────┘ └──────────────┘
                                             │
                                    ┌────────┴────────┐
                                    │  Message Broker  │
                                    │  (RabbitMQ)      │
                                    └─────────────────┘
```

---

## Service registry

| # | Service | Main responsibility | Port | DB | Status |
|---|---------|-------------------|------|-----|--------|
| 01 | `api-gateway` | Routing, authentication, rate limiting | 8080 | Redis | 🟢 Active |
| 02 | `ms-security` | Registration, login, JWT tokens, RBAC | 3001 | PostgreSQL | 🟢 Active |
| 03 | `ms-aulas` | Educational environment management | 3002 | PostgreSQL | 🟢 Active |
| 04 | `ms-sensores` | Sensor registration and management | 3004 | PostgreSQL | 🟢 Active |
| 05 | `ms-monitoreo` | Environmental data collection and analysis | 3003 | PostgreSQL | 🟡 In development |
| 06 | `ms-alert` | Alert generation and management | 3005 | PostgreSQL | 🟢 Active |
| 07 | `ms-user-experience` | User preferences and experience | 3006 | PostgreSQL | 🟢 Active |

**Statuses:** 🟢 Active | 🟡 In development | 🔴 Planned | ⏸ Deprecated

---

## Service communication matrix

| Source service | Destination service | Channel | Type | Description |
|----------------|--------------------|---------|------|-------------|
| api-gateway | ms-security | HTTP/REST | Synchronous | Validate JWT on each request |
| api-gateway | ms-aulas | HTTP/REST | Synchronous | CRUD educational environments |
| api-gateway | ms-sensores | HTTP/REST | Synchronous | CRUD sensors |
| api-gateway | ms-monitoreo | HTTP/REST | Synchronous | Query environmental data |
| ms-sensores | ms-monitoreo | Event | Asynchronous | Sensor data measurements |
| ms-monitoreo | ms-alert | Event | Asynchronous | EnvironmentalDataRecorded |
| ms-monitoreo | ms-user-experience | Event | Asynchronous | EnvironmentalDataAnalyzed |

---

## Data ownership matrix

| Entity / Data | Owner service | How other services access |
|---------------|---------------|--------------------------|
| User / Identity | ms-security | REST API (`GET /users/:id`) |
| Educational Environment | ms-aulas | REST API (`GET /aulas/:id`) |
| Sensor | ms-sensores | REST API (`GET /sensores/:id`) |
| Environmental Data | ms-monitoreo | Event `EnvironmentalDataRecorded` |
| Alert | ms-alert | REST API (`GET /alertas/:id`) |
| User Preferences | ms-user-experience | REST API (`GET /preferences/:userId`) |

---

## Correlations

- Architecture → `05-architecture/overview.md`
- ADRs → `05-architecture/decisions/`
- Service documentation → `09-microservices/services/`
- API contracts → `07-api/contracts/openapi/`

### Documented services

| Service | Service documentation | API contract |
|---------|----------------------|--------------|
| `api-gateway` | [services/01-api-gateway](services/01-api-gateway/README.md) | [api-gateway.yaml](../07-api/contracts/openapi/api-gateway.yaml) |
| `ms-security` | [services/02-auth-service](services/02-auth-service/README.md) | [auth-service.yaml](../07-api/contracts/openapi/auth-service.yaml) |
| `ms-monitoreo` | [services/05-monitoreo](services/05-monitoreo/README.md) | [ms-monitoreo.yaml](../07-api/contracts/openapi/ms-monitoreo.yaml) |
- API contracts → `07-api/contracts/openapi/`
- Domain events → `02-domain/domain-events.md`
- Data models → `06-data/domain/`
