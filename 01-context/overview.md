# System Overview

## What is EduAirControl?

EduAirControl is a web platform for managing and monitoring educational environments. It allows users to visualize temperature, humidity, CO₂, and noise measurements and to consult historical analysis by day, week, month, and year.

## Problem it solves

**Before the system:** Environmental conditions are monitored in a fragmented way, which makes it difficult to centralize measurements and identify changes over time.

**With the system:** EduAirControl centralizes environmental information and presents it through a controlled dashboard so that users and administrators can monitor conditions and make informed decisions.

## Main users

| Role | Description | What they do in the system |
|------|-------------|--------------------------|
| User | Person who accesses the platform to consult environmental information | Authenticates, views environments, consults current conditions, and reviews historical analysis |
| Administrator | Person responsible for managing platform information | Manages users, educational environments, and sensors according to assigned permissions |

## Technology stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Frontend | React | Allows the development of a modular and interactive web interface for visualizing and managing environments |
| Backend | Spring Boot | Domain services and application APIs |
| API entry point | Spring Cloud Gateway | Routing, edge authentication checks, correlation IDs, and common request controls |
| Database | PostgreSQL 15 | Relational persistence, UUIDs, constraints, migrations, and historical queries |
| Messaging | RabbitMQ | Asynchronous integration events when decoupling or buffering is required |
| Sensor ingestion | MQTT or HTTPS | Receiving measurements from heterogeneous environmental sensors |
| Infrastructure | Docker + Jenkins + GitHub | Reproducible execution, CI/CD, and source control |

>The MVP uses a shared PostgreSQL instance with logical ownership boundaries per service. A service may only access its own tables or schema; cross-service data is exchanged through APIs or events. See ADR-003.

## Main architecture

The system is organized around the following deployable components:

| Component | Responsibility |
|-------|-----------|---------------|
| api-gateway | Single external backend entry point |
| ms-security | Registration, authentication, refresh tokens, and access control |
| ms-usuarios | User information management |
| ms-aulas | Educational environment management |
| ms-sensores | Sensor registration and measurement ingestion normalization |
| ms-monitoreo | Environmental measurement persistence, current monitoring, historical analysis, and dashboard queries for the MVP |
| ms-user-experience | User experience features such as environment favorites and ratings |
| React frontend | User interface and visualization |

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
