# Functional Requirements

> **What is this?** List of all the system's functional requirements.
>
> Each FR is numbered, with the module/service it belongs to, source (originating HU), and priority.

---

## User and Access Management (ms-security)

| ID | Module | Description | Source (HU) | Priority |
|----|--------|-------------|-------------|----------|
| FR-001 | ms-security | The system allows user registration. | HU-IAM-001 | High |
| FR-002 | ms-security | The system allows user authentication through login. | HU-IAM-002 | High |
| FR-015 | ms-security | The system controls access to protected functionalities according to user roles. | HU-IAM-003 | High |

---

## User Management (ms-usuarios)

| ID | Module | Description | Source (HU) | Priority |
|----|--------|-------------|-------------|----------|
| FR-003 | ms-usuarios | The system allows administrators to manage users and their information. | HU-USER-001 | Medium |

---

## Educational Environment Management (ms-aulas)

| ID | Module | Description | Source (HU) | Priority |
|----|--------|-------------|-------------|----------|
| FR-004 | ms-aulas | The system allows authorized users to manage educational classrooms or environments. | HU-CLASS-001 | Medium |

---

## Environmental Sensor Management (ms-sensores)

| ID | Module | Description | Source (HU) | Priority |
|----|--------|-------------|-------------|----------|
| FR-005 | ms-sensores | The system allows the registration and management of environmental sensors. | HU-SENS-001 | Medium |
| FR-017 | ms-sensores | The system allows environmental data to be transmitted from sensors using the defined communication mechanisms. | HU-SENS-002 | Medium |

---

## Environmental Monitoring (ms-monitoreo)

| ID | Module | Description | Source (HU) | Priority |
|----|--------|-------------|-------------|----------|
| FR-006 | ms-monitoreo | The system receives environmental measurements from sensors. | HU-MON-001 | High |
| FR-007 | ms-monitoreo | The system stores environmental measurements for historical consultation. | HU-MON-002 | High |
| FR-008 | ms-monitoreo | The system allows users to consult current environmental conditions. | HU-MON-003 | Medium |
| FR-014 | ms-monitoreo | The system provides information about temperature, humidity, CO₂ and noise levels. | HU-MON-004 | Medium |
| FR-009 | ms-monitoreo | The system allows users to consult historical environmental information by day. | HU-ANA-001 | Medium |
| FR-010 | ms-monitoreo | The system allows users to consult historical environmental information by week. | HU-ANA-002 | Medium |
| FR-011 | ms-monitoreo | The system allows users to consult historical environmental information by month. | HU-ANA-003 | Medium |
| FR-012 | ms-monitoreo | The system allows users to consult historical environmental information by year. | HU-ANA-004 | Medium |
| FR-013 | ms-monitoreo | The system displays environmental information through a dashboard. | HU-ANA-005 | Medium |

---

## API Gateway

| ID | Module | Description | Source (HU) | Priority |
|----|--------|-------------|-------------|----------|
| FR-016 | API Gateway | The system communicates between the frontend and backend services through the API Gateway. | HU-ARCH-001 | High |

---

## Summary

| Module | FR Count | High | Medium |
|--------|----------|------|--------|
| ms-security | 3 | 3 | 0 |
| ms-usuarios | 1 | 0 | 1 |
| ms-aulas | 1 | 0 | 1 |
| ms-sensores | 2 | 0 | 2 |
| ms-monitoreo | 9 | 2 | 7 |
| API Gateway | 1 | 1 | 0 |
| **Total** | **17** | **6** | **11** |

---

## Correlations

- Traceability matrix → `04-requirements/traceability-matrix.md`
- User stories → `04-requirements/user-stories.md`
- Non-functional requirements → `04-requirements/non-functional.md`
