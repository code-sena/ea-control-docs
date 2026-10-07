# ms-user-experience

> User preferences and interaction management. Owns user preferences, favorites,
> classroom ratings, search history and notification state.

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

`ms-user-experience` is the authoritative owner of:

```text
user_preferences
favorites
classroom_ratings
searches
notification_state
```

One sentence: **it manages how users interact with the platform — preferences, favorites, ratings, searches and notification state.**

### Responsibilities (what this service DOES)

- Manage user UI preferences (language, theme, timezone, notifications).
- Manage favorite classrooms and variables per user.
- Store classroom ratings and comments.
- Record search history and applied filters.
- Track notification read/acknowledged state per user.

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
| POST | `/classrooms/{id}/ratings` | Rate a classroom |
| GET | `/ratings` | List current user's ratings |
| GET | `/searches` | List current user's search history |
| POST | `/searches` | Record a search |
| DELETE | `/searches/{id}` | Delete a search record |

## Documents

| Document | Content |
|----------|---------|
| [data-model.md](data-model.md) | Tables owned by this service and modeling decisions |
| [decisions.md](decisions.md) | Internal technical decisions of the service |
