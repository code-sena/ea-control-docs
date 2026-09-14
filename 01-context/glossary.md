# Project Glossary

> **Instructions:** Define here all technical and business terms used in the project.
> This is the official dictionary — if there is ambiguity, this document wins.
> Add terms throughout the project, not only at the start.

---

## Purpose and authority

This is the authoritative dictionary for EduAirControl. Definitions apply to requirements, domain models, architecture, data models, APIs and operational documentation unless a more specific approved definition is recorded in the relevant section.
A term must be added or clarified when it is used with a meaning that could be misunderstood. When a definition changes, review the documents that use the term and update them consistently.

---

## Domain terms

| Term | Definition | Notes / Synonyms |
|------|-----------|-----------------|
| Educational Environment | A physical space in an educational institution whose environmental information is managed or monitored by EduAirControl | Use this term for classrooms and other monitored educational spaces |
| Environmental variable | 	
A measurable physical characteristic of an educational environment | The initial variables are temperature, humidity, CO₂ and noise level |
| Temperature | Environmental variable that represents the degree of heat measured in an educational environment | Store and display the unit defined by the sensor and data model |
| Humidity | Environmental variable that represents the amount of moisture measured in an educational environment | Store and display the unit defined by the sensor and data model |
| Carbon dioxide (CO₂) | Concentration of carbon dioxide measured in an educational environment | Use CO₂ in user-facing text and carbon_dioxide where a technical identifier is required |
| Noise Level | Measurement that represents the sound level detected in an educational environment | The unit and measurement range depend on the sensor specification |
| Environmental Monitoring | The process of receiving, storing, presenting and consulting environmental measurements from educational environments | Includes current monitoring and historical consultation |
| Environmental measurement | A time-associated value produced by a sensor for one environmental variable in one educational environment | It is part of the historical environmental data |
| Environmental Data | Information generated from environmental measurements and their associated environment, sensor and time | Used for monitoring, dashboards and analysis |
| Historical data | Previously recorded environmental data consulted to identify changes or behavior over time | Supported analysis periods are day, week, month and year |
| Environmental Data Analysis | The process of examining environmental data across time periods to understand conditions and variations | The MVP supports daily, weekly, monthly and yearly analysis |
| Environmental dashboard | Visual interface that presents current or historical environmental information for one or more educational environments |
| Favorite | A user-specific association that allows an educational environment to be accessed quickly | The feature name is Favorites in user-facing documentation |
| Environment rating | A user-provided assessment of the comfort or conditions of an educational environment | It is a user-experience capability, not an environmental measurement |
| Sensor | IoT device that detects one or more environmental variables and sends measurements to the platform | Hardware development is outside the current scope |
| Sensor status | Operational state recorded for a sensor by the platform | The exact state values are defined by sensor-management requirements |

---

## Technical terms of the project

| Term | Definition |
|------|-----------|
| Microservice | Independently deployable software service with a defined responsibility and controlled ownership of its data |
| Bounded context | Boundary within which a domain model and its terms have a consistent meaning |
| Domain Event | Record of a business fact that has occurred and can be observed by other services. Event names use past tense |
| API Gateway | Backend entry point that routes external requests to the appropriate services and applies common controls |
| API | Application Programming Interface used by software components to communicate through defined operations and data contracts |
| IoT | Internet of Things; connected devices that collect or exchange data, such as environmental sensors |
| MQTT  | Lightweight messaging protocol suitable for communication between sensors and an ingestion service|
| RabbitMQ | Message broker used for asynchronous integration events when decoupling or buffering is required |
| Circuit Breaker | Resilience pattern that stops calls to a failing service for a period to reduce cascading failures |
| Saga | Sequence of local transactions across services with compensating actions when a later step fails |
| Dead Letter Queue | Queue that receives messages that cannot be processed after the configured retry policy |
| Idempotence | Property of an operation whose repeated execution has the same intended result as its single execution |
| UUID | Universally Unique Identifier used by the system when a stable non-sequential identifier is required |
| Dashboard | Interactive visual presentation of relevant data and indicators. In this project, the environmental dashboard is the domain-specific dashboard |

## Roles and access terms

| Term | Definition |
|---------|---------|
| User | Authenticated person who uses EduAirControl to consult or manage information according to assigned permissions |
| Administrator | User with permissions to manage platform information and administrative functions |
| Authentication | Process of verifying the identity of a person or system requesting access |
| Authorization | Process of determining which actions or resources an authenticated identity may access |
| Permission | Granted authorization that allows a user or service to perform a defined action |

---


## Acronyms

| Acronym | Meaning |
|---------|---------|
| ADR | Architecture Decision Record |
| API | Application Programming Interface |
| CI/CD | Continuous Integration / Continuous Delivery |
| CO₂ | Carbon dioxide |
| CRUD | Create, Read, Update, Delete |
| DTO | Data Transfer Object |
| DoD | Definition of Done |
| FR | Functional Requirement |
| IAM | Identity and Access Management |
| IoT | Internet of Things |
| JWT | JSON Web Token |
| MVP | Minimum Viable Product |
| NFR | Non-Functional Requirement |
| PR | Pull Request |
| SLA | Service Level Agreement |
| SLO | Service Level Objective |

---

## Naming rules

- Use educational environment as the general domain term; use classroom only when referring to a specifically defined classroom.
- Use environmental measurement for one time-associated sensor value and environmental data for the broader set of measurements and related information.
- Use authentication for identity verification and authorization for permission checks.
- Use the full term at first mention when an acronym may be unfamiliar; use the acronym afterward.
- Keep technical identifiers in the naming style defined by the affected section, while preserving the glossary meaning.