# Data Models for EduAirControl

> This document is the canonical data-model reference for the project.
> It is not a template. It reflects the actual domain model defined in 02 and the work carried out in 06.

---

## 1. Design principles

### 1.1 Naming and vocabulary

All data model names use English and `snake_case`.

```text
✓ educational_environment
✓ environment_measurement
✓ variable_threshold
✓ analysis_result
✓ app_user

✗ ambiente_educativo
✗ EnvironmentMeasurement
✗ ms-enviroment-monitoring
```

### 1.2 Normalization

The project follows 3NF for transactional domain data.

- One fact per row.
- No repeated columns for variables or measurements.
- Thresholds are referenced by foreign key with validity dates instead of duplicated into each measurement.
- Measurements are stored as time-series facts, not as a wide row per variable.

### 1.3 Audit and traceability

Every persistent table should include the same audit block:

```sql
created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
created_by      BIGINT NULL,
updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_by      BIGINT NULL,
deleted_at      TIMESTAMPTZ NULL,
deleted_by      BIGINT NULL,
row_version     INTEGER NOT NULL DEFAULT 0
```

The exact audit fields may be implemented according to the identity and audit service conventions, but the concept is mandatory in all domain tables.

---

## 2. Shared catalog and identity tables

These tables are shared in the project and are not specific to environmental monitoring.

### Identity

- `identity.app_user`
- `identity.person`
- `identity.role`
- `identity.permission`
- `identity.role_permission`
- `identity.user_role`
- `identity.user_session`

### Audit

- `audit.audit_log`

### Catalogs

- `city`
- `environment_type`
- `sensor_model`
- `sensor_status`
- `measurement_unit`
- `quality_flag`
- `severity`
- `analysis_status`

---

## 3. Environment domain

### `campus`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `campus_id` | SERIAL / BIGSERIAL | PK | Unique campus identifier |
| `code` | VARCHAR(30) | NOT NULL, UNIQUE | Stable internal code |
| `name` | VARCHAR(150) | NOT NULL | Campus name |
| `city_id` | INTEGER | NOT NULL, FK | City reference |

### `educational_environment`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `educational_environment_id` | SERIAL / BIGSERIAL | PK | Unique educational environment identifier |
| `campus_id` | INTEGER | NOT NULL, FK | Campus owner |
| `code` | VARCHAR(30) | NOT NULL | Environment code within campus |
| `name` | VARCHAR(120) | NOT NULL | Friendly environment name |
| `environment_type_id` | SMALLINT | NOT NULL, FK | Classroom, lab, etc. |
| `floor_area_m2` | NUMERIC(8,2) | NULL | Usable area |
| `occupancy_capacity` | SMALLINT | NULL | Maximum occupancy |

### `environment_type`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `environment_type_id` | SMALLINT | PK | Type catalog |
| `code` | VARCHAR(30) | UNIQUE, NOT NULL | Internal code |
| `name` | VARCHAR(80) | UNIQUE, NOT NULL | Human readable type |

---

## 4. Sensor domain

### `sensor`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `sensor_id` | BIGSERIAL | PK | Unique sensor identifier |
| `serial_number` | VARCHAR(60) | NOT NULL, UNIQUE | Physical device serial |
| `sensor_model_id` | SMALLINT | NOT NULL, FK | Sensor catalog model |
| `sensor_status_id` | SMALLINT | NOT NULL, FK | Current operational status |
| `last_seen_at` | TIMESTAMPTZ | NULL | Last communication timestamp |

### `sensor_installation`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `sensor_installation_id` | BIGSERIAL | PK | Installation record |
| `sensor_id` | BIGINT | NOT NULL, FK | Sensor being installed |
| `educational_environment_id` | INTEGER | NOT NULL, FK | Environment where it is located |
| `installed_at` | TIMESTAMPTZ | NOT NULL | Initial install timestamp |
| `removed_at` | TIMESTAMPTZ | NULL | End of installation time |

### `variable`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `variable_id` | SMALLSERIAL | PK | Unique variable identifier |
| `code` | VARCHAR(30) | NOT NULL, UNIQUE | Variable code such as CO2 |
| `name` | VARCHAR(80) | NOT NULL | Variable name |
| `unit_id` | SMALLINT | NOT NULL, FK | Measurement unit |

### `sensor_variable`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `sensor_id` | BIGINT | PK/FK | Sensor |
| `variable_id` | SMALLINT | PK/FK | Measured variable |

### `variable_threshold`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `variable_threshold_id` | SERIAL | PK | Threshold definition |
| `variable_id` | SMALLINT | NOT NULL, FK | Related variable |
| `environment_type_id` | SMALLINT | NOT NULL, FK | Applies to environment type |
| `min_value` | NUMERIC(12,4) | NULL | Lower threshold |
| `max_value` | NUMERIC(12,4) | NULL | Upper threshold |
| `severity_id` | SMALLINT | NOT NULL, FK | Criticality |
| `valid_from` | DATE | NOT NULL | Start of validity |
| `valid_to` | DATE | NULL | End of validity |

---

## 5. Measurement and analysis domain

### `environment_measurement`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `environment_measurement_id` | BIGSERIAL | PK | Unique measurement record |
| `sensor_installation_id` | BIGINT | NOT NULL, FK | Installation that generated the reading |
| `variable_id` | SMALLINT | NOT NULL, FK | Measured variable |
| `measured_value` | NUMERIC(12,4) | NOT NULL | Raw value |
| `measured_at` | TIMESTAMPTZ | NOT NULL | Original observation timestamp |
| `quality_flag_id` | SMALLINT | NOT NULL, FK | Validity or quality state |

> This is the core time-series table of the project. One row = one measurement, one sensor installation, one variable, one instant.

### `environmental_analysis`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `environmental_analysis_id` | BIGSERIAL | PK | Unique analysis batch |
| `educational_environment_id` | INTEGER | NOT NULL, FK | Environment analyzed |
| `period_start` | TIMESTAMPTZ | NOT NULL | Analysis start |
| `period_end` | TIMESTAMPTZ | NOT NULL | Analysis end |
| `analysis_status_id` | SMALLINT | NOT NULL, FK | Current status |
| `requested_by` | BIGINT | NULL, FK | Who requested it |
| `computed_at` | TIMESTAMPTZ | NULL | When processed |

### `analysis_result`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `analysis_result_id` | BIGSERIAL | PK | Unique result record |
| `environmental_analysis_id` | BIGINT | NOT NULL, FK | Parent analysis |
| `variable_id` | SMALLINT | NOT NULL, FK | Evaluated variable |
| `min_value` | NUMERIC(12,4) | NOT NULL | Minimum observed |
| `max_value` | NUMERIC(12,4) | NOT NULL | Maximum observed |
| `avg_value` | NUMERIC(12,4) | NOT NULL | Average observed |
| `sample_count` | INTEGER | NOT NULL | Number of readings |
| `exceedance_count` | INTEGER | NOT NULL | Number of threshold breaches |

---

## 6. Alert domain

### `environment_alert`

| Column | Type | Constraints | Purpose |
|--------|------|------------|---------|
| `environment_alert_id` | BIGSERIAL | PK | Unique alert identifier |
| `educational_environment_id` | INTEGER | NOT NULL, FK | Affected environment |
| `variable_id` | SMALLINT | NOT NULL, FK | Triggering variable |
| `variable_threshold_id` | INTEGER | NOT NULL, FK | Threshold used |
| `triggering_measurement_id` | BIGINT | NOT NULL, FK | Measurement that triggered the alert |
| `raised_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Alert creation time |
| `acknowledged_at` | TIMESTAMPTZ | NULL | Acknowledgement time |
| `acknowledged_by` | BIGINT | NULL, FK | Responsible user |

> An alert must keep the threshold and the triggering measurement as traceable evidence. It does not duplicate the entire measurement payload.

---

## 7. Recommended integrity rules

- `environment_measurement` stores one value per installation, variable and instant.
- `educational_environment` is the nucleus of the monitoring domain and must exist as a first-class table.
- `environmental_analysis` and `environment_alert` must not be represented as unstructured text or JSON blobs when the project already has a relational model.
- Thresholds are stored by validity window and referenced by foreign key, not copied into each record.
- A sensor may move between environments over time through `sensor_installation` without breaking measurement history.

---

## 8. Data ownership

| Domain | Owns |
|--------|-------|
| Identity & Access | `app_user`, sessions, permissions |
| Environment | `campus`, `educational_environment`, `environment_type` |
| Sensor | `sensor`, `sensor_installation`, `variable`, `sensor_variable` |
| Measurement | `environment_measurement` |
| Analysis | `environmental_analysis`, `analysis_result` |
| Alert | `environment_alert` |

---

## 9. Migration notes

The data model must be implemented with versioned migrations, always using English names and without modifying already-executed migrations. The final target is a normalized relational model aligned with the domain definitions in 02 and the monitoring requirements in 03 and 06.
