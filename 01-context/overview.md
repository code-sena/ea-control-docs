# System Overview

> **Instructions:** Replace this content with your project's description.
> This is the first page someone new reads. They must be able to understand the system in 5 minutes.
> Remove these instructions when the document is complete.

---

## What is EduAirControl?

EduAirControl is a web platform for managing, monitoring and controlling information about educational environments through IoT data. It centralizes measurements from environmental sensors and presents them through dashboards and historical analysis so that users can supervise conditions and support decisions about educational spaces.

## Problem it solves

**Before the system:** Environmental conditions are monitored in a fragmented way, which makes it difficult to centralize measurements and identify changes over time.

**With the system:** EduAirControl centralizes environmental information and presents it through a controlled dashboard so that users and administrators can monitor conditions and make informed decisions.

**Scope Note (MVP):** EduAirControl is an analytical and monitoring platform. It does not automatically operate or control external environmental equipment in the current release.

## Main users

| Role | Description | What they do in the system |
|------|-------------|--------------------------|
| User | Authenticated person who consults environmental information according to assigned permissions | Accesses the platform, views educational environments, consults current conditions and reviews historical analysis |
| Administrator | Authenticated person responsible for platform administration | administration.
Manages users, educational environments and sensors according to assigned permissions |

## Information managed

EduAirControl manages educational environments, environmental sensors, sensor configuration and status, user access, current measurements and historical measurements. The initial environmental variables identified in the project are temperature, humidity, carbon dioxide (CO₂) and noise level.

## Technology stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Frontend | React | Modular web interface for management, consultation and dashboards |
| Backend | Spring Boot | Domain services and application APIs |
| API entry point | External backend entry point, routing, correlation identifiers and common request controls |
| Database | Relational persistence, constraints, UUIDs, migrations and historical queries |
| Messaging | RabbitMQ | Asynchronous integration events when decoupling or buffering is required |
| Sensor ingestion | MQTT or HTTPS | Receiving measurements from heterogeneous environmental sensors |
| Infrastructure | Docker + Jenkins + GitHub | Reproducible execution, CI/CD, and source control |

>The MVP uses a shared PostgreSQL instance with logical ownership boundaries per service. A service may access only its own tables or schema; cross-service information is exchanged through APIs or events. This context is consistent with ADR-003 in 05-architecture/decisions/.

## Main architecture

The system is organized around the following deployable components:

| Component | Responsibility |
|-------|-----------|---------------|
| api-gateway | Provides the single external backend entry point and routes requests to the corresponding services |
| Security service (ms-security) | Handles registration, authentication, refresh tokens and access control |
| User service (ms-usuarios) | Manages user information |
| Classroom service (ms-aulas) | Manages educational environments |
| Sensor service (ms-sensores) | Registers sensors and normalizes incoming measurements |
| Monitoring service (ms-monitoreo) | Persists environmental measurements and supports current monitoring, historical analysis and MVP dashboard queries |
| User experience service (ms-user-experience) | Supports user-facing functions such as environment favorites and ratings |
| React frontend | Presents management screens, dashboards and historical information |

>At a high level, the data flow is user → frontend → backend/API → database and services → IoT sensors. Measurements originate in sensors, enter through the supported ingestion mechanisms, and become information available for monitoring and analysis.

## Current status

- **Phase:** MVP development
- **Current version:** Not released
- **Last release:** Not applicable
- **Next milestone:** Complete authentication, environment and sensor management, environmental ingestion, and historical dashboard slices.

Project contacts
| Role                  | Name   | Contact   |
| --------------------- | ------ | --------- |
| Developer / Tech Lead | Jhon Cortez | cortezvargasjhon01@gmail.com |
| Developer             | Maria Olaya | mariadelosangelesolayagar@gmail.com |

## Related documents
Product vision: 03-product/vision.md.
Domain model and rules: 02-domain/.
Requirements and traceability: 04-requirements/.
Architecture overview: 05-architecture/overview.md.
Data models: 06-data/models.md.