# ms-user-experience

> Owns user interface preferences and favorites. Search history and classroom ratings have been retired from the active product and API.

## Service sheet

| Field | Value |
|-------|-------|
| Number in catalog | 07 |
| Local port | 3006 |
| Repository | `ms-user-experience` (standalone service repository) |
| Owner team | Development Team |
| DB engine | PostgreSQL 15 (`user_experience` schema) |
| Status | In development |

## Responsibility

`ms-user-experience` is the authoritative owner of current user preferences and favorites. It does not own users, classrooms, or variables; it references them by UUID and maintains an environment projection for institution checks.

### Responsibilities

- Manage user interface preferences (language, theme, timezone, notifications).
- Manage favorite classrooms and variables per user.
- Maintain the local classroom-to-institution projection and event inbox.

### Retired capabilities

- Search history endpoints and ratings endpoints have been removed from the service and gateway.
- Existing rows are preserved as `legacy_searches` and `legacy_classroom_ratings` by Liquibase changeset `005-deprecate-ratings-and-search-history`; the application does not read or write those tables.

### Out of scope

- Users and authentication — owned by `ms-security`.
- Educational environments — owned by `ms-classroom-management`.
- Sensors and variables — owned by `ms-sensor-management`.
- Environmental measurements and alerts — owned by `ms-environment-monitoring`.
- User profiles — owned by `ms-user-management`.

## Main endpoints

Base path `/api/v1`. Full contract: [ms-user-experience.yaml](../../../07-api/contracts/openapi/ms-user-experience.yaml).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/preferences` | Get current user preferences |
| PUT | `/preferences` | Update current user preferences |
| GET | `/favorites` | List current user's favorite IDs |
| POST | `/favorites/{environmentId}/toggle` | Toggle favorite for an environment |
| DELETE | `/favorites/{environmentId}` | Remove a favorite |

## Frontend behavior

- Environment search and filtering are performed by the client; search history is not persisted by the backend.
- Alert notifications are generated only for environments marked as favorite.
- A `SUPER_ADMIN` without `institutionId` cannot access institution-scoped environment data.

## Documents

| Document | Content |
|----------|---------|
| [data-model.md](data-model.md) | Active tables and retained legacy data |
| [decisions.md](decisions.md) | Internal technical decisions of the service |
