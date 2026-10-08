# Sensor Service — Data Model

## 1. Overview

The Sensor Service manages the physical sensors used by EduAirControl to collect environmental information from educational environments.

The service is responsible for:

* Physical sensor identification.
* Sensor models and manufacturers.
* Sensor operational status.
* Sensor installation history.
* Environmental variables that can be measured.
* The relationship between sensors and variables.
* Measurement units associated with environmental variables.

The service does **not** manage environmental measurements, threshold rules, alerts, or notifications.

Those responsibilities belong to other domains.

### Domain Responsibilities

```text
Sensor Service
├── Physical Sensors
├── Sensor Models
├── Sensor Statuses
├── Sensor Installations
├── Variables
├── Sensor Variables
└── Measurement Units
```

## 2. Database Technology

The service uses:

* PostgreSQL 15
* UUID identifiers
* `snake_case` naming convention
* `TIMESTAMPTZ` for temporal data
* `pgcrypto` for UUID generation
* Liquibase for database migrations

Each Sensor Service database is owned exclusively by the service.

References to entities owned by other services are logical references and must not be implemented as physical foreign keys across databases.

---

## 3. Database Model

```dbml
Project SensorService {
  database_type: 'PostgreSQL'
  Note: 'Physical sensor management, measurable variables and sensor installations'
}

Table sensor_models {
  sensor_model_id uuid [pk, default: `gen_random_uuid()`]
  manufacturer varchar(100) [not null]
  model varchar(100) [not null]
  description varchar(255)
  created_at timestamptz [not null, default: `now()`]

  indexes {
    (manufacturer, model) [unique]
  }

  Note: 'Technical model information shared by multiple physical sensors'
}

Table sensor_statuses {
  sensor_status_id uuid [pk, default: `gen_random_uuid()`]
  code varchar(30) [not null, unique]
  name varchar(80) [not null]
  description varchar(255)
}

Table sensor {
  sensor_id uuid [pk, default: `gen_random_uuid()`]
  serial_number varchar(60) [not null, unique]
  sensor_model_id uuid [not null]
  sensor_status_id uuid [not null]
  last_seen_at timestamptz
  created_at timestamptz [not null, default: `now()`]
  updated_at timestamptz

  Note: 'Physical sensor installed in an educational environment'
}

Table sensor_installation {
  sensor_installation_id uuid [pk, default: `gen_random_uuid()`]
  sensor_id uuid [not null]
  educational_environment_id uuid [not null]
  installed_at timestamptz [not null]
  removed_at timestamptz

  indexes {
    (sensor_id, installed_at)
    (educational_environment_id, installed_at)
  }

  Note: 'Historical record of sensor installation in an educational environment'
}

Table measurement_units {
  measurement_unit_id uuid [pk, default: `gen_random_uuid()`]
  code varchar(30) [not null, unique]
  name varchar(80) [not null]
  symbol varchar(20) [not null]
}

Table variable {
  variable_id uuid [pk, default: `gen_random_uuid()`]
  code varchar(30) [not null, unique]
  name varchar(80) [not null]
  measurement_unit_id uuid [not null]
  description varchar(255)
  created_at timestamptz [not null, default: `now()`]

  Note: 'Environmental variable that can be measured by a sensor'
}

Table sensor_variable {
  sensor_id uuid [not null]
  variable_id uuid [not null]

  indexes {
    (sensor_id, variable_id) [pk]
  }

  Note: 'Many-to-many relationship between physical sensors and measurable variables'
}

Ref: sensor.sensor_model_id > sensor_models.sensor_model_id
Ref: sensor.sensor_status_id > sensor_statuses.sensor_status_id
Ref: sensor_installation.sensor_id > sensor.sensor_id
Ref: variable.measurement_unit_id > measurement_units.measurement_unit_id
Ref: sensor_variable.sensor_id > sensor.sensor_id
Ref: sensor_variable.variable_id > variable.variable_id
```

---

## 4. Entity Description

### 4.1 Sensor Model

`sensor_models` stores technical information shared by multiple physical sensor units.

A model can represent a commercial or technical device specification.

Example:

```text
Manufacturer: Sensirion
Model: SCD30
```

The manufacturer and model are stored once instead of being duplicated in every physical sensor.

This follows normalization principles because these attributes describe the **model**, not the individual device.

---

### 4.2 Sensor

`sensor` represents an individual physical device.

Each physical sensor is identified by a unique serial number.

Example:

```text
sensor_id: 7e4c...
serial_number: EA-CO2-00042
sensor_model_id: ...
sensor_status_id: ...
last_seen_at: 2026-09-09T10:35:00
```

The sensor itself does not store its current educational environment.

Its location is managed through `sensor_installation`.

This allows the system to preserve installation history.

---

### 4.3 Sensor Status

`sensor_statuses` is a reference catalog for the operational state of a sensor.

Possible values include:

```text
ACTIVE
INACTIVE
MAINTENANCE
OFFLINE
DECOMMISSIONED
```

Using a catalog avoids storing inconsistent free-text values in `sensor`.

---

### 4.4 Sensor Installation

`sensor_installation` represents the relationship between a physical sensor and an educational environment over a period of time.

Example:

```text
Sensor S001
│
├── Installation 1
│   Environment: LAB-01
│   Installed: 2026-01-15
│   Removed:   2026-04-20
│
└── Installation 2
    Environment: ROOM-204
    Installed: 2026-04-21
    Removed:   NULL
```

This provides historical traceability.

The `educational_environment_id` is a logical reference to:

```text
Environment Service
└── educational_environment.educational_environment_id
```

There must be no physical foreign key to the Environment Service database.

---

## 5. Variable

A `variable` represents an environmental value that can be measured.

Examples:

```text
TEMPERATURE
HUMIDITY
CO2
NOISE
PM25
OCCUPANCY
```

Each variable has a measurement unit.

For example:

```text
TEMPERATURE → CELSIUS → °C
HUMIDITY    → PERCENT  → %
CO2         → PPM      → ppm
NOISE       → DECIBEL  → dB
PM25        → MICROGRAM_PER_M3 → µg/m³
```

The unit is referenced through `measurement_unit_id` rather than duplicated as text.

---

## 6. Sensor Variable

A sensor may measure multiple variables, and a variable may be measured by multiple sensor models or physical sensors.

Therefore, the relationship is many-to-many:

```text
Sensor N ───────── N Variable
```

This relationship is represented by:

```text
sensor_variable
```

Example:

```text
Sensor S001
├── Temperature
├── Humidity
└── CO2
```

Another sensor may measure:

```text
Sensor S002
├── Temperature
└── Humidity
```

The composite primary key prevents the same variable from being associated with the same sensor more than once.

---

## 7. Measurement Unit

`measurement_units` is a normalized catalog of units used by environmental `variable` rows.

Examples:

```text
Code: CELSIUS
Name: Celsius
Symbol: °C
```

```text
Code: PPM
Name: Parts per million
Symbol: ppm
```

```text
Code: PERCENT
Name: Percentage
Symbol: %
```

```text
Code: DECIBEL
Name: Decibel
Symbol: dB
```

This avoids repeating unit information throughout the database.

---

## 8. Relationships

The internal relationships of the Sensor Service are:

```text
Sensor Model 1 ─────── N Sensor

Sensor Status 1 ─────── N Sensor

Sensor 1 ─────── N Sensor Installation

Sensor N ─────── N Variable

Measurement Unit 1 ─────── N Variable
```

The external relationship is:

```text
Sensor Installation
        │
        │ educational_environment_id
        ▼
Environment Service
        │
        └── educational_environment
```

---

## 9. Microservice Boundaries

The Sensor Service owns:

```text
sensor_models
sensor_statuses
sensor
sensor_installation
measurement_units
variable
sensor_variable
```

The Environment Service owns:

```text
campuses
educational_environment
environment_types
```

The Measurement Service owns environmental measurements.

The Alert Service owns threshold rules and alerts.

The Notification Service owns user notifications.

Therefore:

```text
Environment
     │
     │ educational_environment_id
     ▼
Sensor
     │
     │ sensor_id / variable_id
     ▼
Measurement
     │
     ▼
Analysis
     │
     ▼
Alert
     │
     ▼
Notification
```

---

## 10. What Does Not Belong to Sensor Service

The following entities are intentionally excluded.

### Measurements

A sensor identifies what can measure, but actual readings belong to the Measurement Service.

```text
Sensor
     │
     └── can measure CO2

Measurement
     │
     └── CO2 = 850 ppm at 10:35
```

### Thresholds

Thresholds are business/environmental rules and belong to the Alert domain.

For example:

```text
CO2
Environment Type: CLASSROOM
Maximum: 1000 ppm
Severity: WARNING
```

This information must not be stored directly inside `sensor` or `variable`.

### Notifications

The Sensor Service may publish sensor-related events, such as `SensorStatusChanged`, but it does not manage user notifications.

---

## 11. Domain Events

The Sensor Service publishes events such as:

```text
SensorRegistered        (contract only)
SensorUpdated           (contract only)
SensorStatusChanged     (contract only)
SensorInstalled         IMPLEMENTED - sensor.installation.created
SensorRemoved           IMPLEMENTED - sensor.installation.closed
VariableRegistered      (contract only)
SensorVariableAssociated(contract only)
SensorVariableRemoved   (contract only)
```

It may consume events from the Environment Service, such as:

```text
EducationalEnvironmentCreated
EducationalEnvironmentUpdated
EducationalEnvironmentStatusChanged
```

These events allow services to remain decoupled.

### 11.1 Outbox table

`sensors.outbox_event` (migration `009-create-outbox-event.yaml`) is
infrastructure, not domain: it is the transactional outbox of ADR-007. It lives in
this schema because only this service publishes events, and ADR-003 gives one
schema per service.

| Column | Purpose |
|--------|---------|
| `event_id` | PK, also the idempotency key the consumer deduplicates on |
| `event_type`, `aggregate_type`, `aggregate_id`, `routing_key` | Event envelope |
| `payload` | JSON body as TEXT; the relay forwards it verbatim and never queries it |
| `occurred_at` | When the business change happened |
| `published_at` | NULL while pending. `idx_outbox_event_pending` is partial on this |
| `attempts`, `last_error` | Failure accounting for retry and alerting |

The row is written in the same transaction as the business change, so an
installation that rolls back leaves no event. See
`09-microservices/services/04-ms-sensor-management/events.md`.

---

## 12. Data Integrity Rules

Recommended rules include:

### Sensor

```text
serial_number IS NOT NULL
serial_number must be UNIQUE
sensor_model_id IS NOT NULL
sensor_status_id IS NOT NULL
```

### Sensor Installation

```text
installed_at IS NOT NULL
removed_at IS NULL OR removed_at > installed_at
```

A sensor should not have overlapping active installations.

Conceptually:

```text
One sensor
    └── maximum one active installation
```

Historical installations may exist as long as their validity periods do not overlap.

### Variable

```text
code must be UNIQUE
name must not be empty
measurement_unit_id must exist
```

### Sensor Variable

```text
(sensor_id, variable_id) must be UNIQUE
```

The composite primary key already enforces this rule.

---

## 13. PostgreSQL Configuration

The database should enable UUID generation through `pgcrypto`:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

UUIDs should be generated using:

```sql
gen_random_uuid()
```

Temporal fields should use:

```sql
TIMESTAMPTZ
```

Database changes should be managed through Liquibase changesets.

---

## 14. Normalization

The model follows normalization principles by separating information according to its responsibility.

For example:

```text
Sensor
├── serial number
├── model
└── status
```

is separated into:

```text
Sensor
    │
    ├── Sensor Model
    └── Sensor Status
```

Likewise:

```text
Variable
    │
    └── Measurement Unit
```

And:

```text
Sensor
    │
    └── Sensor Installation
          │
          └── Educational Environment
```

This prevents duplicated manufacturer, unit, location, and status information.

---

## 15. Future Extensibility

The model can later support additional sensor capabilities without changing the fundamental architecture.

Potential future attributes or entities include:

* Calibration records
* Sensor communication protocols
* Sensor connectivity information
* Battery information
* Firmware versions
* Maintenance records
* Sensor health metrics
* Measurement accuracy

These should only be introduced when the project requires them.

The current model intentionally focuses on the core Sensor domain.

---

## 16. Summary

The Sensor Service answers four fundamental questions:

1. **What physical sensors exist?**
2. **What model and status does each sensor have?**
3. **Where has each sensor been installed over time?**
4. **What environmental variables can each sensor measure?**

It does not answer:

* What value was measured?
* Is the value outside an acceptable range?
* Should an alert be generated?
* How should the user be notified?

Those responsibilities belong to Measurement, Analysis, Alert, and Notification respectively.

The resulting separation is:

```text
Sensor
  ↓
What can be measured?

Measurement
  ↓
What was measured?

Analysis
  ↓
What does it mean?

Alert
  ↓
Does it violate a rule?

Notification
  ↓
Who should be informed?
```
