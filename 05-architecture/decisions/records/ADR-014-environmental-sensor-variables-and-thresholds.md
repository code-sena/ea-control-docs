# ADR-014 — Environmental Sensor Variables and Thresholds

- **ID:** ADR-014
- **Date:** 2026-09-17
- **Status:** Proposed
- **Authors:** EduAirControl Development Team

---

## Context

EduAirControl monitors environmental conditions in educational spaces using IoT sensors. The system needs to define which environmental variables are measured, their units, and the threshold values that trigger alerts when conditions fall outside acceptable ranges.

A decision is required now because:
- Sensors must be configured to measure specific variables
- Alert generation requires defined thresholds per variable and environment type
- Users need to understand what the system monitors and when alerts are triggered
- Historical analysis requires consistent variable definitions and units

**Known constraints:**
- The MVP focuses on four primary environmental variables
- Thresholds must be configurable per environment type (classroom, lab, library, etc.)
- Measurements come from physical IoT sensors via MQTT/HTTP
- The system must support different threshold severity levels

---

## Decision

**We decided:** Define four primary environmental variables with standard units and configurable thresholds per environment type, using a severity-based alerting system.

**Justification:**
The four variables (CO₂, humidity, noise level, temperature) are the most critical indicators of environmental quality in educational spaces. They directly impact student health, comfort, and learning performance. Configurable thresholds allow different environment types (classrooms, laboratories, libraries) to have different acceptable ranges.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| Four variables with configurable thresholds — chosen | Covers critical environmental factors, flexible per environment type, industry-standard metrics | Requires threshold configuration per environment | Chosen for comprehensive coverage |
| Fixed thresholds for all environments | Simpler implementation, less configuration | Doesn't account for different environment needs (e.g., labs vs libraries) | Rejected due to inflexibility |
| More variables (PM2.5, occupancy, light) | More comprehensive monitoring | Higher sensor costs, increased complexity, not critical for MVP | Deferred to future versions |

---

## Environmental Variables

| Variable | Code | Unit | Symbol | Description | Valid Range |
|----------|------|------|--------|-------------|-------------|
| Temperature | `TEMP` | Celsius | °C | Air temperature in the environment | -10 to 50 |
| Humidity | `HUM` | Percent | % | Relative humidity in the environment | 0 to 100 |
| Carbon Dioxide | `CO2` | Parts Per Million | ppm | CO₂ concentration in the environment | 0 to 5000 |
| Noise Level | `NOISE` | Decibels | dB | Sound pressure level in the environment | 0 to 140 |

---

## Threshold Configuration

Thresholds are defined per variable and environment type, with validity dates and severity levels.

### Default Thresholds for Educational Environments

#### Classroom (环境类型: `CLASSROOM`)

| Variable | Normal Range | Warning Range | Critical Range | Unit |
|----------|--------------|---------------|----------------|------|
| Temperature | 20 - 26 | 18-20 or 26-28 | <18 or >28 | °C |
| Humidity | 40 - 60 | 30-40 or 60-70 | <30 or >70 | % |
| CO₂ | 0 - 800 | 800 - 1000 | >1000 | ppm |
| Noise Level | 0 - 45 | 45 - 55 | >55 | dB |

#### Laboratory (环境类型: `LABORATORY`)

| Variable | Normal Range | Warning Range | Critical Range | Unit |
|----------|--------------|---------------|----------------|------|
| Temperature | 18 - 24 | 16-18 or 24-26 | <16 or >26 | °C |
| Humidity | 30 - 60 | 25-30 or 60-75 | <25 or >75 | % |
| CO₂ | 0 - 600 | 600 - 800 | >800 | ppm |
| Noise Level | 0 - 50 | 50 - 60 | >60 | dB |

#### Library (环境类型: `LIBRARY`)

| Variable | Normal Range | Warning Range | Critical Range | Unit |
|----------|--------------|---------------|----------------|------|
| Temperature | 20 - 24 | 18-20 or 24-26 | <18 or >26 | °C |
| Humidity | 40 - 55 | 35-40 or 55-65 | <35 or >65 | % |
| CO₂ | 0 - 600 | 600 - 800 | >800 | ppm |
| Noise Level | 0 - 40 | 40 - 50 | >50 | dB |

---

## Threshold Structure

Each threshold is defined with:

| Field | Description | Example |
|-------|-------------|---------|
| `variable_id` | Environmental variable | Temperature |
| `environment_type_id` | Type of environment | Classroom |
| `min_value` | Minimum acceptable value | 20 |
| `max_value` | Maximum acceptable value | 26 |
| `severity_id` | Alert severity level | Warning |
| `valid_from` | Start date for this threshold | 2026-09-01 |
| `valid_to` | End date for this threshold (nullable) | null |

### Severity Levels

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Info** | Normal operating conditions | No action required |
| **Warning** | Conditions approaching limits | Monitor and investigate |
| **Critical** | Conditions outside acceptable range | Immediate action required |

---

## Business Rules

1. **Threshold Uniqueness:** One threshold per variable, environment type, and severity combination during a given time period.

2. **Validity Dates:** Thresholds must have a `valid_from` date. The `valid_to` date is optional (null means ongoing).

3. **Overlapping Prevention:** A new threshold cannot overlap with an existing threshold for the same variable, environment type, and severity.

4. **Alert Generation:** Alerts are generated when a measurement exceeds the threshold boundaries for the active threshold.

5. **Measurement Validation:** Each measurement must be validated against the active threshold for its variable and environment type.

6. **Historical Preservation:** Thresholds are never deleted; they are marked as invalid by setting `valid_to`.

---

## Consequences

**Positive:**
- Clear definition of what the system monitors
- Flexible threshold configuration per environment type
- Severity-based alerting for appropriate response
- Historical threshold tracking with validity dates
- Standard units for consistent data analysis

**Negative / Trade-offs:**
- Requires initial threshold configuration for each environment type
- Threshold maintenance overhead as new environment types are added
- May need tuning based on real-world observations

**Impact on the system:**
- Affected services: ms-sensor-management, ms-environment-monitoring, ms-alert
- Documents that must be updated: `06-data/domain/ms-environment-monitoring.md`, `06-data/domain/ms-sensor-management.md`

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Thresholds too sensitive causing alert fatigue | Medium | Medium | Start with conservative thresholds, tune based on data |
| Thresholds too loose missing real issues | Low | High | Validate thresholds with environmental experts |
| Different regions have different comfort standards | Low | Low | Make thresholds configurable, allow regional overrides |

---

## References

- Environmental monitoring data model: `06-data/domain/ms-environment-monitoring.md`
- Sensor management data model: `06-data/domain/ms-sensor-management.md`
- Alert data model: `06-data/domain/ms-alert.md`
- Domain events: `02-domain/domain-events.md`
- Related to: ADR-002 (Microservice Boundaries), ADR-008 (Database Migration Tool)
