# ADR-014 — Environmental Sensor Variables and Thresholds

- **ID:** ADR-014
- **Date:** 2026-09-17
- **Status:** Accepted
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
- Measurements come from physical IoT sensors over HTTPS (ADR-004 note; no MQTT adapter exists)
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
| Temperature | `temperature` | Celsius | °C | Air temperature in the environment | -10 to 50 |
| Humidity | `humidity` | Percent | % | Relative humidity in the environment | 0 to 100 |
| Carbon Dioxide | `co2` | Parts Per Million | ppm | CO₂ concentration in the environment | 0 to 5000 |
| Noise Level | `noise` | Decibels | dB | Sound pressure level in the environment | 0 to 140 |

---

> **Note (2026-10-30):** the codes above are the ones stored by the service (seed
> `010-seed-reference`) and used by the API (`variableCode`); the first draft of this ADR used
> `TEMP`/`HUM`/`CO2`/`NOISE`. The stored unit symbol for temperature is `C` (displayed as °C).

## Threshold Configuration

Thresholds are defined per variable and environment type, with validity dates and severity levels.

> [!NOTE] AMENDMENT (2026-10-16) — Per-environment overrides
> A threshold row may additionally carry a nullable `educational_environment_id`
> (originally rejected in this ADR; amended after product requirements for
> per-environment configuration in the web UI). The effective threshold of an
> environment is: its own override for the variable/severity if one exists,
> otherwise the threshold of its environment type. Only the WARNING severity
> of temperature is exposed for per-environment editing (web environment
> management modal); overrides are created by ADMIN/SUPER_ADMIN via
> `PUT /api/v1/environments/{id}/thresholds/{variableCode}` and are never
> deleted — replaced rows are closed with `valid_to`. A partial unique index
> `ux_variable_threshold_env_var_sev` keeps one open override per
> (environment, variable, severity).

### Default Thresholds for Educational Environments

#### Classroom (environment type: `CLASSROOM`)

| Variable | Normal Range | Warning Range | Critical Range | Unit |
|----------|--------------|---------------|----------------|------|
| Temperature | 20 - 26 | 18-20 or 26-28 | <18 or >28 | °C |
| Humidity | 40 - 60 | 30-40 or 60-70 | <30 or >70 | % |
| CO₂ | 0 - 800 | 800 - 1000 | >1000 | ppm |
| Noise Level | 0 - 45 | 45 - 55 | >55 | dB |

#### Laboratory (environment type: `LABORATORY`)

| Variable | Normal Range | Warning Range | Critical Range | Unit |
|----------|--------------|---------------|----------------|------|
| Temperature | 18 - 24 | 16-18 or 24-26 | <16 or >26 | °C |
| Humidity | 30 - 60 | 25-30 or 60-75 | <25 or >75 | % |
| CO₂ | 0 - 600 | 600 - 800 | >800 | ppm |
| Noise Level | 0 - 50 | 50 - 60 | >60 | dB |

#### Library (environment type: `LIBRARY`)

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
| `educational_environment_id` | Optional per-environment override (nullable) | Ambiente A-101 |
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

1. **Threshold Uniqueness:** One threshold per variable, environment type, and severity combination during a given time period. Per-environment overrides are unique per variable and severity (one open row per environment, variable and severity).

2. **Override Precedence:** If a threshold with `educational_environment_id` set exists for a variable/severity, it wins over the threshold of the environment type; the type threshold remains the fallback for environments without an override.

3. **Validity Dates:** Thresholds must have a `valid_from` date. The `valid_to` date is optional (null means ongoing).

4. **Overlapping Prevention:** A new threshold cannot overlap with an existing threshold for the same variable, environment type, and severity.

5. **Alert Generation:** Alerts are generated when a measurement exceeds the threshold boundaries for the active threshold.

6. **Measurement Validation:** Each measurement must be validated against the active threshold for its variable and environment type.

7. **Historical Preservation:** Thresholds are never deleted; they are marked as invalid by setting `valid_to`.

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
- Affected services: ms-sensor-management, ms-environment-monitoring (alerts live here since ADR-015)
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
- Alert data model: `06-data/domain/ms-alert.md` (historical; alerts were folded into monitoring by ADR-015)
- Domain events: `02-domain/domain-events.md`
- Related to: ADR-002 (Microservice Boundaries), ADR-008 (Database Migration Tool)
