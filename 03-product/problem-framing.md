# Problem Framing — Problem Definition

## Purpose

This document defines the problem EduAirControl is intended to solve before detailing the implementation. It distinguishes the user need from the proposed platform and establishes the assumptions that must be validated through requirements, pilot use and operational evidence.
  
---

## 1. Problem statement

Users and administrators in educational institutions need to understand the environmental conditions of classrooms and other educational spaces. However, environmental information from sensors is not sufficiently centralized and analyzed in a single platform. This makes it difficult to consult current conditions, compare changes over time and use the information to support decisions about monitored spaces.

## Problem dimensions

| Dimension | Current problem | Product implication | 
|---------|-------------|---------------|
| Access | Users need a clear place to consult environmental information | Provide authenticated dashboard access |
| Centralization | Measurements from sensors must be associated with an educational environment rather than remaining isolated | Manage environments, sensors and measurement references |
| Understanding | Raw values are not enough to understand how conditions change | Provide time-based analysis by day, week, month and year |
| Traceability | A measurement is meaningful only when its source, environment and recorded time are known | Preserve sensor, environment and timestamp relationships |
| Governance | User and administrator access must be controlled | Use IAM roles, permissions, sessions and audit information |

---

## 2. Affected users

| Segment | Description | Main interaction | Priority |
|---------|-------------|---------------|---------|
| Educational environment users | Consult environmental conditions and historical information for relevant spaces | Authenticate, select an environment, use dashboard and analysis filters | High |
| Administrators | Manage access, campuses, educational environments and sensors | Create, update, activate or deactivate managed resources | High |
| Sensor or ingestion processes | Deliver measurements with the information needed for acceptance and persistence | Send environmental data associated with a sensor and environment | High |
| Authorized operators | Review security or environmental conditions that require attention when those capabilities are enabled | Consult audit records or alert information according to permissions | Medium |

### 3. Jobs-to-be-done (JTBD)

Primary job

**When** I need to understand the environmental conditions of an educational environment,

**I want** to consult temperature, humidity, CO₂, and noise information and analyze it over different time periods,

**so that** I can understand the current condition and its changes over time.

Administrative jobs

**When** I am responsible for the institution's monitored spaces,

**I want** to manage environments and sensors and control access,

**so that** measurements remain associated with the correct space and authorized users can consult them.

**When** I need to verify how the platform has been used or investigate a security-related situation, 
**I want** authorized audit and session information, 
**so that** access and security activity can be reviewed.

Supporting interaction jobs

**When** I frequently consult particular environments or variables, 
**I want** to save favorites and preferences, 
**so that** the dashboard reflects the information relevant to me.

---

## 4. Evidence and current knowledge

The current project documentation establishes the need, the product scope, the domain model and the data responsibilities. It does not include dated user interviews, support records or benchmark studies. Those sources must not be presented as completed evidence.

| Evidence source | Current status | How it should be used | 
|--------------|--------|------|------------|
| Product and context documentation | Available in 01-context/ and this section | Establishes the initial problem and product hypothesis |
| Domain model | Available in 02-domain/ | Confirms entities, boundaries and business rules |
| Data models | Available in 06-data/ | Confirms that the problem has concrete storage and ownership support |
| User interviews | Not documented in the current repository | Validate user language, priorities and dashboard usefulness |
| Direct observation or pilot | Not documented in the current repository. | Validate real consultation workflows and environmental interpretation |
| Usage and operations data | To be collected after an operational pilot | Establish adoption, availability and data-completeness baselines |

The absence of research records is an explicit validation gap, not a reason to invent quantitative baselines.

---

## 5. Current alternative and its limitations

The current problem framing identifies a fragmented or non-centralized way of consulting environmental information as the principal alternative. The documentation does not specify a particular existing product or manual process. EduAirControl therefore addresses the information problem without claiming that it replaces a named system.

| Alternative | Limitation relevant to the problem | Product response |
|-----------------|------------|--------------|
| Fragmented consultation of environmental information | Users may need to consult measurements in separate places or without consistent historical views | Centralize authenticated consultation and historical analysis |
| Raw sensor output without environment context | A value is difficult to interpret if its educational space and source are unclear | Associate measurements with environments, sensors and recorded time |
| Manual comparison of measurements | Manual comparison increases effort and makes time-based changes harder to understand | Provide day/week/month/year analysis |
| Uncontrolled access to platform information | Sensitive user and audit information requires protection | Apply IAM roles, permissions, sessions and audit controls |

---

## 6. Solution hypothesis

**We believe that**  a platform that centralizes environmental monitoring and analysis for educational environments, including temperature, humidity, CO₂ and noise information,

**for** users who need to consult and understand environmental conditions,

**will achieve** easier access to environmental information and better understanding of changes over time.

**We will know we succeeded when** an authorized user can complete the full path from login to environment selection, dashboard consultation and historical analysis, while administrators can maintain the environment and sensor references required for trustworthy measurements.

---

## 7. Functional outcomes

The solution is successful only when it produces observable outcomes:

| Outcome | Observable behavior |
|-------------|---------|
| Accessible information | An authorized user can find a monitored environment and view its available variables |
| Traceable measurements | A stored measurement identifies its environment, sensor and recorded time |
| Understandable history | A user can select a supported period and interpret the resulting environmental information |
| Managed resources | An administrator can maintain the entities required for monitoring |
| Protected operation | Authentication and authorization restrict protected actions and data |
| Sustainable data ownership | Services own their data and expose it through defined APIs or events rather than uncontrolled direct access |

## 8. Success measurement plan

The repository does not yet provide production baselines or dated targets. The following metrics define what must be measured rather than inventing current values.

| Metric | Definition | Initial measurement source | Product signal |
|--------|----------------|---------------|-------------------|
| Measurement availability | Proportion of expected measurement records available for consultation in the selected period | Monitoring data and ingestion logs | Data is sufficiently complete for analysis |
| Dashboard completion | Proportion of authorized sessions that reach an environment view successfully | Application telemetry and access logs | Users can reach the main value |
| Historical analysis completion | Proportion of analysis requests for supported periods that return usable results | API and monitoring logs | Historical analysis is operationally useful |
| Environment coverage  | Number and proportion of active educational environments with valid sensor associations and data | Environment, sensor and measurement data | The monitored institution is represented consistently |
| Authentication success | Proportion of valid authentication attempts that create a usable session | IAM sessions and audit records | Protected access works without unnecessary friction |
| User interaction | Use of favorites, filters, ratings or comments when those features are enabled | User Experience data | The product supports repeated, relevant consultation |

**North Star metric:** For the initial product stage, the North Star is successful authorized environmental consultations with a usable current or historical result. It connects the product's central promise with real use without assuming a baseline that has not yet been collected.

---

## 9. Risks and validation actions

| Risk | Impact | Validation or mitigation |
|------|--------|--------------------------|
| Users do not adopt the dashboard. | High. The platform may centralize data without creating value| Pilot the dashboard with representative users and observe whether they complete the main consultation job |
| Measurements are incomplete or poorly associated | High. Historical analysis becomes unreliable | Validate ingestion completeness, sensor status, environment references and recorded timestamps |
| The selected variables do not answer users' needs | Medium/High. The dashboard may be technically correct but not useful | Validate the usefulness of temperature, humidity, CO₂ and noise information with representative users |
| Historical periods do not match the way users reason about conditions | Medium. Analysis may be difficult to interpret | Test day, week, month and year views and record which comparisons users actually perform |
| Access rules create excessive friction or insufficient protection | High. Security or adoption may be affected | Test registration, authentication, roles, permissions, sessions and audit behavior |
| Alert data is mistaken for an enabled alert product | Medium. Stakeholders may expect notifications or control actions not in scope | Keep alert activation tied to explicit requirements, APIs and service behavior |


---

## 10. Out of scope for the current product definition

- Environmental ranking.
- Predictive or advanced forecasting analysis.
- Automatic control of air conditioning, ventilation or lighting.
- Integration with external systems for physical environmental control.
- Manufacture, repair or physical installation of sensor hardware.
- Claims about user research findings that are not documented in the repository.
- Notifications or alert workflows unless they are explicitly activated through requirements and contracts.

## Correlations

- Product vision and principles: `03-product/vision.md`
- Domain language and boundaries: `02-domain/`
- Formal user stories and acceptance criteria: `04-requirements/`
- Data ownership and persistence: `06-data/`
- API behavior: `07-api/contracts/`
- Operational measurement: `13-operations/`
