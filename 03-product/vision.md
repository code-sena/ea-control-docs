# Product Vision

## Purpose

The product vision defines the long-term direction against which scope, priorities and trade-offs are evaluated. It is intentionally broader than the first release, but every future capability must remain connected to the central value of understanding environmental conditions in educational environments.

---

## Vision statement

**For** users and administrators in educational institutions 
**who** need to monitor, manage and understand environmental conditions in classrooms and other educational spaces, 
**EduAirControl** is a web-based IoT environmental monitoring and analysis platform 
**that** centralizes temperature, humidity, CO₂ and noise information and presents it through current dashboards and historical analysis by day, week, month and year. 
**Unlike** fragmented or non-centralized consultation of sensor information, 
**EduAirControl** connects users, educational environments, sensors, measurements and time-based analysis in one protected platform.

---

## Team mission

The team exists to develop a reliable platform that makes environmental information from educational environments accessible, traceable and understandable. The team does this by connecting sensor data with the spaces where it was produced, presenting it clearly to authorized users and preserving the historical information needed to understand change over time.

## Product promise

EduAirControl promises four things:
1. Centralization: environmental information is available through a common platform rather than isolated consultation points.
2. Context: measurements are associated with an educational environment, sensor and recorded time.
3. Understanding: users can consult current information and analyze supported historical periods.
4. Protection: registration, authentication, permissions, sessions and audit controls protect access to the platform.

The product does not promise automatic physical control, predictive environmental management or a ranking of spaces in the current scope.

---

## Strategic pillars

| Pillar | Product meaning | Capabilities supported | Evidence of progress |
|--------|-------------|----------------|--------------------------|
| Environmental Monitoring | Make current environmental information available for educational environments | Measurement ingestion, persistence, environment selection and dashboard consultation | Environments with valid sensor references and usable measurement records |
| Historical understanding | Help users understand how environmental conditions change over time | Analysis by day, week, month and year, with clear variable and period selection | Successful analysis requests and user completion of historical consultation |
| Managed foundation | Keep users, spaces and sensors organized so measurements remain trustworthy | IAM, campuses, environment types, educational environments, sensors, models, variables and installations | Administrators can maintain valid references and lifecycle states |
| Clear user experience | Reduce the effort required to find and interpret relevant information | Dashboard, favorites, preferences, searches, filters, ratings and comments when enabled | Successful consultation and meaningful repeated interaction |
| Reliability and protection | Preserve availability, integrity and controlled access to product information | PostgreSQL-backed persistence, sessions, permissions, audit, migrations and service ownership | Successful authenticated operations, accepted measurements and traceable activity |

---

## Product architecture from the user's perspective

```text
User or administrator
        │
        ▼
Protected web interface
        │
        ▼
Product capabilities
  ├── Identity and access
  ├── Environment and campus management
  ├── Sensor management
  ├── Environmental monitoring
  ├── Historical analysis
  └── User experience
        │
        ▼
Owned data and service contracts
        │
        ▼
Environmental sensors and institutional information
```
This is a product view. 05-architecture/ defines the technical deployment and service interactions, while 06-data/ defines the persistence structures.

## Capability-to-data traceability

| Product capability | Data service or model | Key documented data | Product implication |
|--------|-------------|----------------|--------------------------|
| Identity and access | ms-iam.md | Users, user statuses, roles, permissions, sessions, password policies, security configurations, audit actions, audit logs and error logs | Protected screens and actions can be tied to an authenticated identity and audited activity |
| Campus and environment management | ms-classroom-management.md | Campuses, environment types and educational environments | The dashboard can organize information by institution and monitored space |
| Sensor management | ms-sensor-management.md | Sensor models, manufacturers, sensors, statuses, installations, variables, sensor-variable associations and measurement units | Measurement values can be interpreted in relation to a registered source and supported variable |
| Environmental monitoring | ms-environment-monitoring.md | Environmental measurements, recorded time, environment references, variables and analysis support | Current and historical data can be persisted and queried |
| User experience | ms-user-experience.md | Preferences, favorites, ratings, comments, searches and filters | The product can support personalized consultation without transferring ownership of core entities |
| Environmental alerts | ms-alert.md | Alert status, environment, variable, threshold, measurement and user references | Threshold-related workflows are data-ready but require explicit product scope and contracts |

---

 ## Main product journeys

Journey A — Authorized consultation

1. The user registers or receives an authorized account.
2. The user authenticates and obtains a valid session.
3. The user selects an educational environment.
4. The product retrieves available environmental information.
5. The dashboard presents temperature, humidity, CO₂ and noise values when available.
6. The user selects a supported historical period when a comparison over time is needed.
7. The product presents the result with enough context to identify the environment and period.

Journey B — Administrative readiness

1. An administrator authenticates with the required permissions.
2. The administrator creates or maintains the campus and environment type references.
3. The administrator registers the educational environment and lifecycle status.
4. The administrator registers the sensor model and physical sensor.
5. The administrator associates the sensor with the supported variables and installation environment.
6. The monitoring capability can accept measurements with valid source and environment references.

Journey C — Measurement to decision support

1. A sensor produces a measurement.
2. The ingestion path associates the measurement with the sensor and educational environment.
3. The monitoring service persists the values and recorded timestamp.
4. The dashboard retrieves current information.
5. Historical analysis groups the accepted records by day, week, month or year.
6. An authorized user uses the result to understand the condition or change of the environment.

## High-level roadmap

The roadmap is expressed as product horizons. It does not replace the prioritized requirements backlog.

| Horizon | Focus | Product content | Exit condition |
|--------|-------------|----------------|--------------------------|
| H1 — Now | Core MVP | Registration and authentication; environment management; sensor management; measurement ingestion; environmental dashboard; historical analysis by day, week, month and year; core favorites or ratings when prioritized | A representative user can complete the authorized consultation journey with valid data |
| H2 — Next | Validated iteration | Improve dashboard clarity, filters, preferences, searches and interaction flows based on pilot evidence; strengthen data completeness and operational visibility | Usage evidence identifies concrete improvements and the product remains within its domain boundary |
| H3 — Later | Controlled expansion | Consider alert workflows, richer operational analysis or additional integrations only after product value, ownership, contracts and operational impact are approved | Each expansion has explicit requirements, data ownership, API behavior and architecture review |


## Product principles

1. Value before volume
A new table, endpoint or screen is not automatically a product improvement. Prioritize the user outcome and the decision it enables.
2. Context before interpretation
Environmental values must retain their relationship to the environment, sensor, variable and recorded time. A dashboard without context can display data without making it useful.
3. Clarity before complexity
The product must expose the information needed for the selected use case without requiring users to understand service boundaries, database tables or IoT transport details.
4. Evidence before expansion
The roadmap should grow from validated user needs, data quality and operational evidence. Do not present future capabilities as current commitments.
5. Ownership before integration
Every capability must have an owner for its data and behavior. Cross-service interaction uses APIs or events rather than direct database access.
6. Protection by default
Authentication, authorization, session handling, audit and security-related data are product requirements, not optional technical extras.

---

## Product Definition of Done

The product is ready for an MVP release when the following outcomes are demonstrated in the approved environment:

| Outcome | Acceptance condition | 
|------------|---------|
| Protected access | A user can register or be provisioned, authenticate and access only permitted functionality |
| Managed environments | An administrator can manage campuses, environment types and educational environments with valid lifecycle states |
| Managed sensors | An administrator can register a sensor and its model, status, installation and supported variables |
| Trustworthy monitoring | Accepted measurements retain sensor, environment, variables and recorded time |
| Useful dashboard | An authorized user can consult available environmental information for a selected environment |
| Historical analysis | The user can request day, week, month and year views and receive a coherent result |
| Data alignment | Product behavior corresponds to the ownership and structures documented in 06-data/. |
| Operational readiness | Errors, authentication activity and relevant processing can be investigated through the documented security and operational data |
| Scope integrity | No release claim includes automatic equipment control, prediction, ranking or another excluded capability without an explicit decision |


---

## Success indicators
The initial baseline is to be collected during pilot operation. The product should track:

- Successful authenticated environmental consultations.
- Availability and completeness of measurements for active environments.
- Successful historical analysis requests by supported period.
- Coverage of active environments with valid sensor associations.
- Authentication and session success for valid users.
- Data-quality or ingestion errors that prevent dashboard consultation.
- Use of favorites, filters, searches, ratings and comments when enabled.

## Correlations

- Problem and validation hypothesis: `03-product/problem-framing.md`
- Domain model and bounded contexts: `02-domain/`
- Formal product requirements: `04-requirements/`
- Technical realization: `05-architecture/`
- Data structures and ownership: `06-data/`
- Service and integration contracts: `07-api/ and 09-microservices/`
- Operational follow-up: `13-operations/`