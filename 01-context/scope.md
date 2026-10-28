# System Scope

> **Why this document exists:** Scope prevents scope creep and aligns expectations.
> It is equally important to define what the system does NOT do as what it does.
> Review this document at the start of each planning cycle.

---

## Purpose and scope baseline

This document defines the boundaries of the EduAirControl MVP. It is the baseline for prioritization, requirements, architecture and delivery planning. A proposed change must be evaluated against this baseline before entering the product backlog.

### MVP Features - product capabilities

| # | Capability | Description | Responsible service |
|---|---------|-------------|---------------------|
| 1 | User Authentication and Registration | Allows users to register,sign up and access the platform securely. | ms-security |
| 2 | Educational Environment management | Allows authorized users to manage and consult information about educational environments | ms-classroom-management |
| 3 | Sensor management | Allows the registration, configuration and status management of environmental sensors | ms-sensor-management |
| 4 | Environmental monitoring |Allows users to view temperature, humidity, CO₂ and noise measurements for educational environments | ms-environment-monitoring |
| 5 | Environmental dashboard | Presents current and historical environmental information in an organized visual interface | ms-environment-monitoring and frontend |
| 6 | Historical analysis | Allows consultation of environmental data by day, week, month and year | ms-environment-monitoring |
| 7 | Environment Favorites | Allows users to add and remove educational environments from a personal favorites list | ms-user-experience |
| 8 | Environment Rating | Allows users to rate the comfort or conditions of an educational environment | ms-user-experience |

### Included integrations and environments

| External system | Integration type | Purpose |
|----------------|------------------|---------|
| GitHub | Source-control platform | Stores source code and supports version control |
| Jenkins | CI/CD platform | Automates integration and project delivery tasks |
| Docker | Containerization technology | Provides consistent execution environments |
| MQTT or HTTPS | Sensor-ingestion mechanism | Receives measurements from environmental sensors |
| Local | Development environment | Supports development on a team member's machine |
| Development (dev) | Integration environment | Supports continuous integration and development testing |
| Staging | Pre-production environment | Supports validation before production |
| Production | Delivery environment | Hosts the released system when the MVP is deployed |

---

## Excluded from the MVP

| # | Excluded capability | Reason | Future consideration |
|---|---------------------|--------|----------------|
| 1 | Environmental ranking | The current scope focuses on monitoring, visualization and analysis rather than ranking environments | No current commitment |
| 2 | Advanced predictive environmental analysis | Predictive analysis is not part of the current MVP | To be evaluated in a future version |
| 3 | Automated control of environmental equipment | The current system monitors and analyzes conditions but does not control equipment | To be evaluated in a future version |
| 4 | Integration with external environmental control systems | No such external integration has been defined for the current version | To be evaluated in a future version  |

### Responsibilities outside EduAirControl

| Responsability | owner | Boundary |
|---------|--------------|-----------|
| Environmental sensor hardware development | External hardware provider or institution | EduAirControl consumes sensor data; it does not develop the physical hardware |
| External infrastructure services | Infrastructure provider or institution | EduAirControl documents and uses required integrations but does not own external provider infrastructure |

---

## Scope assumptions

> These assumptions are taken to be true. If they change, the scope must be renegotiated.

| # | Assumption | Consequence if false |
|---|-----------|---------------------|
| 1 | Environmental measurements are available through the defined ingestion mechanisms | 	
Environmental measurements are available through the defined ingestion mechanisms |
| 2 | Users access the system through a web interface | Frontend and user-experience requirements must be revisited |
| 3 | PostgreSQL is available for the platform's relational persistence | The data and architecture decisions must be reviewed |
| 4 | Environmental data can be analyzed by day, week, month and year | Dashboard queries and analysis requirements must be adjusted |
| 5 | The initial delivery is performed by the currently assigned development team | Scope, sequencing and sprint capacity may need adjustment |

---

## Constraints

| Type | Description |
|------|-------------|
| **Time** | Work is organized in one-week Sprints. |
| **Budget** | No specific budget or cost limit has been defined in the available project documentation |
| **Technology** | The current baseline uses React, Spring Boot and PostgreSQL 15, with Docker, Jenkins and GitHub in the delivery toolchain |
| **Regulatory** | No specific regulation or certification has been defined in the available project documentation |
| **Team** | The available project documentation identifies two developers and a Teach Lead responsability |

---

## External dependencies

| Dependency | Team / Provider | Required date | Status |
|-----------|----------------|--------------|--------|
| GitHub repository | Development team | Not defined | 🟢 Available |
| Jenkins | Development team | 2026-10-17 | 🟢 Available (ADR-019: on the VPS, auto-deploy on `main`) |
| Docker environment | Development team | Not defined | 🟡 In progress |
| Environmental data source and sensor connectivity | Not defined | Not defined | 🟡 In progress |

---

## Scope-change process

- Record the proposed change and its reason in the backlog.
- Evaluate its impact on product value, requirements, architecture, data, schedule and delivery risk.
- Obtain Product Owner approval for scope and value.
- Obtain Tech Lead approval for technical and cross-section impacts.
- Update this document and the affected documents in 03-product/, 04-requirements/, 05-architecture/ and 06-data/.
- Add or update user stories and traceability in 04-requirements/.
- Record an ADR when the change alters an architectural decision.

---

## Correlations

- Product vision and roadmap: `03-product/vision.md`
- System overview: `overview.md`
- Project glossary: `glossary.md`
- Scope-related risks: `15-project-control/risks.md`
- Governance for scope changes: `00-governance/README.md`