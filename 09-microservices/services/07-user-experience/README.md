# ms-user-experience

> User preferences and interaction data. Owns how users interact with the platform,
> not the resources they interact with.

## Service sheet

| Field | Value |
|-------|-------|
| Number in catalog | 07 |
| Local port | 3006 |
| Repository | `EduAirControl/-ms-user-experience` (standalone service repository) |
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

One sentence: **it stores what users prefer and how they interact with environments.**

### Responsibilities (what this service DOES)

- Store per-user interface and notification preferences (one record per user).
- Store favorites (environments and/or variables) per user.
- Store classroom ratings (1-5) with optional comments.
- Store search history with applied filters.
- Track notification read state per user and alert.
- Serve all of the above scoped by the authenticated user from the JWT.

### Out of scope

- Users, roles, authentication — owned by `ms-security` / `ms-user-management`.
- Educational environments — owned by `ms-classroom-management`.
- Sensors and variables — owned by `ms-sensor-management`.
- Measurements and alerts — owned by `ms-environment-monitoring`.

## Main endpoints

Base path `/api/v1`. Full contract: [ms-user-experience.yaml](../../../07-api/contracts/openapi/ms-user-experience.yaml).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/preferences` | Get my preferences (creates defaults on first read) |
| PUT | `/preferences` | Update my preferences |
| GET | `/favorites` | List my favorite environment IDs |
| POST | `/favorites/{id}/toggle` | Toggle favorite |
| DELETE | `/favorites/{id}` | Remove favorite |
| POST | `/classrooms/{id}/ratings` | Rate a classroom (1-5) |
| GET | `/ratings` | My ratings |
| GET | `/searches` | My search history (paginated) |
| POST | `/searches` | Record a search |
| DELETE | `/searches/{id}` | Delete a search |

## Identity

The user always comes from the JWT (`userId` claim). No endpoint accepts `userId`
in the body or query. Unauthenticated requests get `401`.

## Documents

| Document | Content |
|----------|---------|
| [data-model.md](data-model.md) | Tables owned by this service |
| [events.md](events.md) | Published and consumed events |
| [decisions.md](decisions.md) | Internal technical decisions |
