# User Experience Service — Data Model

## 1. Service

**Service:** User Experience Service
**Domain:** User Experience
**Database Engine:** PostgreSQL 15

The User Experience Service manages user-specific preferences and interactions with classrooms and environmental information.

Its main responsibilities are:

* Managing user interface preferences.
* Managing favorite classrooms and environmental variables.
* Storing classroom ratings and user comments.
* Recording user searches and applied filters.
* Supporting personalization of the user experience.
* Providing interaction data that can be used by the frontend and future analytics services.

The service does not own users, classrooms, or environmental variables. It only stores the user's interaction with those resources.

---

## 2. PostgreSQL Configuration

The service uses PostgreSQL 15.

### UUID generation

The `pgcrypto` extension can be enabled for UUID generation:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

UUIDs are used as primary keys to avoid predictable sequential identifiers and to facilitate distributed architectures.

Example:

```sql
preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### Timestamp strategy

All timestamps should use:

```sql
TIMESTAMPTZ
```

This allows the service to store timestamps with timezone information.

---

# 3. Naming Convention

The database follows these conventions:

* Table names use plural `snake_case`.
* Column names use singular `snake_case`.
* Primary keys use the `<entity>_id` format.
* Boolean fields use descriptive names such as `notifications_enabled`.
* Timestamps use `_at` when representing an event or occurrence.
* All identifiers are written in English.

Examples:

```text
user_preferences
favorite_id
classroom_id
notifications_enabled
rated_at
searched_at
```

---

# 4. Tables

The User Experience Service contains four main tables:

| Table               | Responsibility                                         |
| ------------------- | ------------------------------------------------------ |
| `user_preferences`  | Stores personal interface and notification preferences |
| `favorites`         | Stores classrooms and variables marked as favorites    |
| `classroom_ratings` | Stores user ratings and comments for classrooms        |
| `searches`          | Stores user search history and applied filters         |

---

# 5. User Preferences

## Table: `user_preferences`

This table stores the preferences that customize the user experience.

```text
user_preferences
├── preference_id
├── user_id
├── language
├── color_theme
├── notifications_enabled
└── time_zone
```

### Data Dictionary

| Field                   | Type    | Constraints | Description                                 |
| ----------------------- | ------- | ----------- | ------------------------------------------- |
| `preference_id`         | UUID    | PK          | Unique preference identifier                |
| `user_id`               | UUID    | NOT NULL    | Logical reference to the user               |
| `language`              | VARCHAR | NULL        | User interface language                     |
| `color_theme`           | VARCHAR | NULL        | Preferred interface theme                   |
| `notifications_enabled` | BOOLEAN | NULL        | Indicates whether notifications are enabled |
| `time_zone`             | VARCHAR | NULL        | User's preferred timezone                   |

### Recommended constraints

Each user should normally have only one preference record.

```sql
UNIQUE (user_id)
```

Recommended values for `color_theme` could include:

```text
light
dark
system
```

Supported languages can be represented using standard language codes:

```text
en
es
fr
pt
```

---

# 6. Favorites

## Table: `favorites`

This table stores resources that a user has marked as favorites.

A favorite can refer to a classroom, a monitored environmental variable, or potentially both depending on the application's behavior.

```text
favorites
├── favorite_id
├── user_id
├── classroom_id
├── variable_id
└── added_at
```

### Data Dictionary

| Field          | Type        | Constraints | Description                                    |
| -------------- | ----------- | ----------- | ---------------------------------------------- |
| `favorite_id`  | UUID        | PK          | Unique favorite identifier                     |
| `user_id`      | UUID        | NOT NULL    | Logical reference to the user                  |
| `classroom_id` | UUID        | NULL        | Logical reference to a classroom               |
| `variable_id`  | UUID        | NULL        | Logical reference to an environmental variable |
| `added_at`     | TIMESTAMPTZ | NULL        | Date and time when the favorite was created    |

### Cross-domain references

`user_id`:

```text
user_id
→ IAM Service.users.user_id
```

`classroom_id`:

```text
classroom_id
→ Classroom Management Service.classrooms.classroom_id
```

`variable_id`:

```text
variable_id
→ Sensor Management Service.variable.variable_id
```

These references should remain logical references rather than physical PostgreSQL foreign keys because the referenced entities belong to other services.

### Recommended validation

At least one target should be provided:

```sql
CHECK (
    classroom_id IS NOT NULL
    OR variable_id IS NOT NULL
)
```

A future refinement could define whether a favorite is allowed to contain both a classroom and a variable.

---

# 7. Classroom Ratings

## Table: `classroom_ratings`

This table stores user evaluations of classrooms.

```text
classroom_ratings
├── rating_id
├── user_id
├── classroom_id
├── score
├── comment
└── rated_at
```

### Data Dictionary

| Field          | Type        | Constraints | Description                               |
| -------------- | ----------- | ----------- | ----------------------------------------- |
| `rating_id`    | UUID        | PK          | Unique rating identifier                  |
| `user_id`      | UUID        | NOT NULL    | Logical reference to the user             |
| `classroom_id` | UUID        | NOT NULL    | Logical reference to a classroom          |
| `score`        | INTEGER     | NULL        | User rating score                         |
| `comment`      | VARCHAR     | NULL        | Optional user comment                     |
| `rated_at`     | TIMESTAMPTZ | NULL        | Date and time when the rating was created |

### Recommended score validation

If the application uses a five-point rating system:

```sql
CHECK (score BETWEEN 1 AND 5)
```

### Cross-domain references

```text
user_id
→ IAM Service.users.user_id

classroom_id
→ Classroom Management Service.classrooms.classroom_id
```

No physical foreign keys should be created for these references.

---

# 8. Searches

## Table: `searches`

This table stores user searches performed through the application.

```text
searches
├── search_id
├── user_id
├── search_text
├── applied_filter
└── searched_at
```

### Data Dictionary

| Field            | Type        | Constraints | Description                   |
| ---------------- | ----------- | ----------- | ----------------------------- |
| `search_id`      | UUID        | PK          | Unique search identifier      |
| `user_id`        | UUID        | NOT NULL    | Logical reference to the user |
| `search_text`    | VARCHAR     | NULL        | Text entered by the user      |
| `applied_filter` | VARCHAR     | NULL        | Filter applied to the search  |
| `searched_at`    | TIMESTAMPTZ | NULL        | Date and time of the search   |

### Cross-domain reference

```text
user_id
→ IAM Service.users.user_id
```

The service should not create a foreign key to the IAM database.

---

# 9. Cross-Domain References

The User Experience Service interacts with several other domains.

```text
                    ┌─────────────────────────┐
                    │       IAM Service       │
                    │                         │
                    │         users           │
                    └────────────┬────────────┘
                                 │
                                 │ user_id
                                 ▼
                    ┌─────────────────────────┐
                    │   User Experience       │
                    │        Service          │
                    │                         │
                    │  user_preferences       │
                    │  favorites              │
                    │  classroom_ratings      │
                    │  searches               │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 │               │                │
                 ▼               ▼                ▼
       Classroom Management   Sensor Management
              Service              Service
                 │                  │
                 │ classroom_id     │ variable_id
                 ▼                  ▼
            classrooms          variables
```

### Reference matrix

| Local Field    | External Service             | External Entity           |
| -------------- | ---------------------------- | ------------------------- |
| `user_id`      | IAM Service                  | `users.user_id`           |
| `classroom_id` | Classroom Management Service | `classrooms.classroom_id` |
| `variable_id`  | Sensor Management Service    | `variable.variable_id`     |

These are **logical references**.

The User Experience Service should not directly access another service's database.

---

# 10. Domain Responsibilities

The service is responsible for **how users interact with the platform**, rather than owning the resources themselves.

### IAM Service

Responsible for:

* Users
* Roles
* Permissions
* Authentication
* Sessions
* Security

### Classroom Management Service

Responsible for:

* Classrooms
* Classroom information
* Classroom locations
* Classroom lifecycle

### Sensor Management Service

Responsible for:

* Sensors
* Environmental variables
* Variable configurations
* Sensor metadata

### Environmental Monitoring Service

Responsible for:

* Measurements
* Environmental history
* Environmental status
* Environmental statistics

### User Experience Service

Responsible for:

* User preferences
* Favorites
* Classroom ratings
* Search history

This separation prevents the User Experience Service from becoming the owner of information belonging to other domains.

---

# 11. Indexing Strategy

Indexes should be created for the most common queries.

Recommended indexes:

```sql
CREATE INDEX idx_user_preferences_user_id
ON user_preferences(user_id);

CREATE INDEX idx_favorites_user_id
ON favorites(user_id);

CREATE INDEX idx_favorites_classroom_id
ON favorites(classroom_id);

CREATE INDEX idx_favorites_variable_id
ON favorites(variable_id);

CREATE INDEX idx_classroom_ratings_user_id
ON classroom_ratings(user_id);

CREATE INDEX idx_classroom_ratings_classroom_id
ON classroom_ratings(classroom_id);

CREATE INDEX idx_searches_user_id
ON searches(user_id);

CREATE INDEX idx_searches_searched_at
ON searches(searched_at);
```

The `searches` table may grow rapidly because every search can generate a new record. Therefore, its indexes and retention policy should be reviewed as the system grows.

---

# 12. Recommended PostgreSQL Schema

A possible PostgreSQL implementation is:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE user_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    language VARCHAR(10),
    color_theme VARCHAR(20),
    notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    time_zone VARCHAR(100)
);

CREATE TABLE favorites (
    favorite_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    classroom_id UUID,
    variable_id UUID,
    added_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_favorite_target
        CHECK (
            classroom_id IS NOT NULL
            OR variable_id IS NOT NULL
        )
);

CREATE TABLE classroom_ratings (
    rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    classroom_id UUID NOT NULL,
    score INTEGER NOT NULL,

    comment VARCHAR(1000),

    rated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_classroom_rating_score
        CHECK (score BETWEEN 1 AND 5)
);

CREATE TABLE searches (
    search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    search_text VARCHAR(500),
    applied_filter VARCHAR(500),
    searched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

# 13. Migration Strategy

Database changes should be managed using **Liquibase**, the migration tool standardized for the project.

Example:

```text
db/changelog/changes/001-create-user-preferences.yaml
db/changelog/changes/002-create-favorites.yaml
db/changelog/changes/003-create-classroom-ratings.yaml
db/changelog/changes/004-create-searches.yaml
db/changelog/changes/005-add-indexes.yaml
```

Each changeset should have a unique ID and be committed to version control. Once executed in a shared environment, changesets should not be modified.

---

# 14. Security Considerations

The User Experience Service stores user-related interaction data.

Therefore:

* Users must only access their own preferences.
* Users must only modify their own preferences.
* Users must only manage their own favorites.
* Search history should be accessible only to the corresponding user or authorized administrative/analytics processes.
* Classroom ratings should be validated through authenticated requests.
* Authorization should be performed using the IAM Service.
* The service should validate the `user_id` obtained from the authenticated token rather than trusting arbitrary user identifiers supplied by the client.

For example:

```text
JWT
 │
 ▼
IAM Authentication
 │
 ▼
User Experience Service
 │
 ▼
Extract authenticated user_id
 │
 ▼
Query user-specific data
```

---

# 15. API Interaction

The frontend can communicate with the User Experience Service through endpoints such as:

```text
GET    /api/preferences
PUT    /api/preferences

GET    /api/favorites
POST   /api/favorites
DELETE /api/favorites/{favoriteId}

GET    /api/ratings
POST   /api/classrooms/{classroomId}/ratings

GET    /api/searches
POST   /api/searches
DELETE /api/searches/{searchId}
```

The exact endpoints should be defined during API design.

The service should use DTOs rather than exposing database entities directly.

---

# 16. Domain Events

The service can publish domain events when relevant user interactions occur.

Potential events include:

```text
UserPreferencesUpdated
FavoriteAdded
FavoriteRemoved
ClassroomRated
SearchPerformed
```

These events could later be consumed by other services such as:

* Analytics Service
* Notification Service
* Recommendation Service
* Dashboard Service

For example:

```text
User Experience Service
        │
        │ FavoriteAdded
        ▼
   Message Broker
        │
        ├──► Analytics Service
        │
        └──► Recommendation Service
```

If MQTT is used in the overall architecture, it should be evaluated carefully for these application-level events versus other messaging requirements. The communication technology should be chosen according to the characteristics of each interaction.

---

# 17. Data Retention

Not all data has the same retention requirements.

### User preferences

Long-term data.

Should remain available while the user account is active.

### Favorites

Long-term data.

Should remain until the user removes them or the referenced resource becomes unavailable.

### Classroom ratings

Long-term data.

May be retained for classroom analysis and user feedback.

### Search history

Potentially short- or medium-term data.

Because searches can grow rapidly, the service may eventually implement a retention policy such as:

```text
Recent searches → retained
Old searches → archived or deleted
```

The exact retention period should be defined according to project requirements and privacy policies.

---

# 18. Future Improvements

The current model can be extended if the application requires more advanced personalization.

Possible future entities include:

```text
notification_preferences
dashboard_preferences
favorite_types
search_filters
user_interactions
recommendations
```

However, these should only be introduced when they represent actual business requirements.

The current four-table model is sufficient for the initial User Experience domain.

---

# 19. Domain Architecture

The User Experience Service fits into the overall EduAirControl architecture as follows:

```text
                         ┌─────────────────────┐
                         │     IAM Service     │
                         │                     │
                         │ Users / Roles /     │
                         │ Permissions / Auth  │
                         └──────────┬──────────┘
                                    │
                                    │ user_id
                                    ▼
┌────────────────────────────────────────────────────────┐
│                User Experience Service                  │
│                                                        │
│  ┌────────────────┐   ┌─────────────────────────────┐ │
│  │ User           │   │ Interaction                │ │
│  │ Preferences    │   │ Management                 │ │
│  │                │   │                             │ │
│  │ preferences    │   │ favorites                   │ │
│  └────────────────┘   │ classroom_ratings           │ │
│                       │ searches                    │ │
│                       └─────────────────────────────┘ │
└───────────────┬──────────────────────┬─────────────────┘
                │                      │
                │ classroom_id         │ variable_id
                ▼                      ▼
┌────────────────────────┐  ┌──────────────────────────┐
│ Classroom Management   │  │ Sensor Management        │
│ Service                │  │ Service                  │
│                        │  │                          │
│ classrooms             │  │ variables                │
└────────────────────────┘  └──────────────────────────┘
```

The main architectural principle is:

> **The User Experience Service owns user interaction data, while other services remain responsible for the resources being interacted with.**

This maintains clear domain boundaries and supports the future migration toward a microservices architecture.
