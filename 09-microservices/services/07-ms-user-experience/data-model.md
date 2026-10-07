# Data Model — ms-user-experience

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables directly.

---

## Database engine

**Engine:** PostgreSQL 15
**Schema:** `user_experience`. Cross-domain references (`user_id`, `classroom_id`, `variable_id`) are logical UUIDs without a foreign key, per ADR-003.

---

## Schema

### Table: user_preferences

**Purpose:** Stores personal interface and notification preferences per user.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| preference_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | Authenticated user reference | Logical ref to `ms-security`, UNIQUE |
| language | VARCHAR(10) | Yes | UI language (`es`, `en`, `fr`, `pt`) | |
| color_theme | VARCHAR(20) | Yes | Theme preference (`light`, `dark`, `system`) | |
| notifications_enabled | BOOLEAN | No | Whether notifications are on | Default `true` |
| time_zone | VARCHAR(100) | Yes | User timezone | |
| date_format | VARCHAR(20) | Yes | Date display format | |
| dark_mode | BOOLEAN | Yes | Dark mode toggle | |
| auto_timezone | BOOLEAN | Yes | Auto-detect timezone | |
| reminders | JSONB | Yes | Reminder toggles | |
| created_at | TIMESTAMPTZ | No | Creation timestamp | Default `now()` |
| updated_at | TIMESTAMPTZ | No | Last update timestamp | |

### Table: favorites

**Purpose:** Stores classrooms and variables marked as favorites.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| favorite_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User reference | Logical ref to `ms-security` |
| classroom_id | UUID | Yes | Classroom reference | Logical ref to `ms-classroom-management` |
| variable_id | UUID | Yes | Variable reference | Logical ref to `ms-sensor-management` |
| added_at | TIMESTAMPTZ | No | When added | Default `now()` |

**Constraints:** `CHECK (classroom_id IS NOT NULL OR variable_id IS NOT NULL)`

### Table: classroom_ratings

**Purpose:** Stores user evaluations of classrooms.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| rating_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User reference | Logical ref to `ms-security` |
| classroom_id | UUID | No | Classroom reference | Logical ref to `ms-classroom-management` |
| score | INTEGER | No | Rating score | `CHECK (score BETWEEN 1 AND 5)` |
| comment | VARCHAR(1000) | Yes | Optional comment | |
| rated_at | TIMESTAMPTZ | No | When rated | Default `now()` |

### Table: searches

**Purpose:** Stores user search history and applied filters.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| search_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User reference | Logical ref to `ms-security` |
| search_text | VARCHAR(500) | Yes | Search text | |
| applied_filter | VARCHAR(500) | Yes | Applied filter | |
| searched_at | TIMESTAMPTZ | No | When searched | Default `now()` |

### Table: notification_state

**Purpose:** Tracks read/acknowledged state of notifications per user.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| notification_state_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | User reference | Logical ref to `ms-security` |
| notification_id | UUID | No | Notification reference | Logical ref to `ms-environment-monitoring` |
| read_at | TIMESTAMPTZ | Yes | When read | |
| acknowledged_at | TIMESTAMPTZ | Yes | When acknowledged | |

### Indexes

| Name | Fields | Type | Justification |
|------|--------|------|---------------|
| ix_user_preferences_user_id | (user_id) | BTREE | Lookup by user |
| ix_favorites_user_id | (user_id) | BTREE | List user favorites |
| ix_favorites_classroom_id | (classroom_id) | BTREE | Lookup by classroom |
| ix_classroom_ratings_user_id | (user_id) | BTREE | List user ratings |
| ix_classroom_ratings_classroom_id | (classroom_id) | BTREE | Classroom average |
| ix_searches_user_id | (user_id) | BTREE | User search history |
| ix_searches_searched_at | (searched_at) | BTREE | Time-based queries |

---

## Schema migration

**Tool:** Liquibase (ADR-008)
**Script location:** `ms-user-experience/src/main/resources/db/changelog/`
