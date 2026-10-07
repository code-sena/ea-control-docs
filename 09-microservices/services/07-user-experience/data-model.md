# Data Model — ms-user-experience

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables directly.

---

## Database engine

**Engine:** PostgreSQL 15
**Schema:** `user_experience`. Cross-domain references (`user_id`, `classroom_id`,
`variable_id`) are logical UUIDs without foreign keys, per ADR-003.

---

## Schema

### Table: user_preferences

**Purpose:** Per-user interface and notification preferences. One record per user.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| preference_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User | Logical ref to IAM, UNIQUE |
| language | VARCHAR(10) | Yes | UI language | |
| color_theme | VARCHAR(20) | Yes | Preferred theme | |
| notifications_enabled | BOOLEAN | No | Notifications on/off | Default TRUE |
| time_zone | VARCHAR(100) | Yes | Preferred timezone | |
| date_format | VARCHAR(20) | Yes | Date display format | |
| reminders | JSONB | No | Reminder flags | Default `'{}'` |
| dark_mode | BOOLEAN | No | Dark mode | Default FALSE |
| auto_time_zone | BOOLEAN | No | Auto timezone | Default TRUE |

### Table: favorites

**Purpose:** Environments and/or variables marked as favorite by a user.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| favorite_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User | Logical ref to IAM |
| classroom_id | UUID | Yes | Environment | Logical ref to `ms-classroom-management` |
| variable_id | UUID | Yes | Variable | Logical ref to `ms-sensor-management` |
| added_at | TIMESTAMPTZ | No | Creation time | Default now |

**Constraint:** `CHECK (classroom_id IS NOT NULL OR variable_id IS NOT NULL)`.

### Table: classroom_ratings

**Purpose:** User ratings of environments (1-5 scale).

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| rating_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User | Logical ref to IAM |
| classroom_id | UUID | No | Environment | Logical ref to `ms-classroom-management` |
| score | INTEGER | No | Rating 1-5 | `CHECK (score BETWEEN 1 AND 5)` |
| comment | VARCHAR(1000) | Yes | Optional comment | |
| rated_at | TIMESTAMPTZ | No | Creation time | Default now |

### Table: searches

**Purpose:** User search history with applied filters.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| search_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User | Logical ref to IAM |
| search_text | VARCHAR(500) | Yes | Search text | |
| applied_filter | VARCHAR(500) | Yes | Applied filter | |
| searched_at | TIMESTAMPTZ | No | Search time | Default now |

### Table: notification_state

**Purpose:** Read state of notifications per user and alert. The alert lives in
`ms-environment-monitoring`; only the user interaction is stored here.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| user_id | UUID | No | User | Part of composite PK |
| alert_id | UUID | No | Alert | Part of composite PK, logical ref |
| read_at | TIMESTAMPTZ | No | Read time | Default now |

---

## Schema migration

**Tool:** Liquibase (ADR-008)
**Script location:** `ms-user-experience/src/main/resources/db/changelog/`
