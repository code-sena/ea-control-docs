# Data Model — ms-user-management

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables directly.

---

## Database engine

**Engine:** PostgreSQL 15
**Schema:** `user_management`. Cross-domain references (`institution_id`) are logical UUIDs without a foreign key, per ADR-003.

---

## Schema

### Table: user_profile

**Purpose:** Stores user profile information linked to an authenticated user.

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| user_profile_id | UUID | No | Unique identifier | PK, `gen_random_uuid()` |
| user_id | UUID | No | Authenticated user reference | Logical ref to `ms-security` |
| institution_id | UUID | No | Owning institution | Logical ref to `ms-security` |
| first_name | VARCHAR(100) | No | First name | |
| last_name | VARCHAR(100) | No | Last name | |
| phone | VARCHAR(20) | Yes | Contact phone | |
| avatar_url | VARCHAR(500) | Yes | Profile picture URL | |
| status | VARCHAR(30) | No | Record status | `ACTIVE` / `INACTIVE` |
| created_at | TIMESTAMPTZ | No | Creation timestamp | Default `now()` |
| updated_at | TIMESTAMPTZ | No | Last update timestamp | |
| deleted_at | TIMESTAMPTZ | Yes | Soft-delete timestamp | |

**Relationships:**
- `user_id` → logical reference to `ms-security`
- `institution_id` → logical reference to `ms-security`

### Indexes

| Name | Fields | Type | Justification |
|------|--------|------|---------------|
| uq_user_profile_user | (user_id) | UNIQUE | One profile per user |
| idx_user_profile_institution | (institution_id) | BTREE | Multi-tenant filtering |

---

## Schema migration

**Tool:** Liquibase (ADR-008)
**Script location:** `ms-user-management/src/main/resources/db/changelog/`
