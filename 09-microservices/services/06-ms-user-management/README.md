# ms-user-management

> User information management. Owns user profiles and their lifecycle.

## Service sheet

| Field | Value |
|-------|-------|
| Number in catalog | 08 |
| Local port | 3007 |
| Repository | `ms-user-management` (standalone service repository) |
| Owner team | Development Team |
| DB engine | PostgreSQL 15 (`user_management` schema) |
| Status | In development |

## Responsibility

`ms-user-management` is the authoritative owner of:

```text
user_profile
```

One sentence: **it manages user profiles, preferences and personal information beyond authentication.**

### Responsibilities (what this service DOES)

- CRUD of user profiles linked to authenticated users.
- Soft-delete lifecycle for user records.
- Multi-tenant filtering by institution.

### Out of scope

- Authentication, login, JWT tokens — owned by `ms-security`.
- User preferences and experience — owned by `ms-user-experience`.
- Educational environments — owned by `ms-classroom-management`.

## Main endpoints

Base path `/api/v1`. Full contract: [ms-user-management.yaml](../../../07-api/contracts/openapi/ms-user-management.yaml).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users` | List user profiles with filters and pagination |
| GET | `/users/{id}` | Get one user profile |
| POST | `/users` | Create a user profile |
| PATCH | `/users/{id}` | Update a user profile |
| DELETE | `/users/{id}` | Soft-delete a user profile |

## Documents

| Document | Content |
|----------|---------|
| [data-model.md](data-model.md) | Tables owned by this service and modeling decisions |
| [decisions.md](decisions.md) | Internal technical decisions of the service |
