# Data Model — [Service Name]

> This service is the **authoritative owner** of the data described here.
> No other service should read these tables/collections directly.

---

## Database engine

**Engine:** [PostgreSQL / MongoDB / Redis / etc.]
**Justification:** [why this engine is appropriate for this service]

---

## Schema

### Table/Collection: [table_name]

**Purpose:** [what this table represents]

| Field | Type | Nullable | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | UUID | No | Unique identifier | PK, auto-generated |
| [field] | [VARCHAR(255) / INT / BOOL / etc.] | [Yes/No] | [description] | [FK/Unique/Check/etc.] |
| created_at | TIMESTAMP | No | Creation date | Default: NOW() |
| updated_at | TIMESTAMP | No | Last modification | Update on each UPDATE |
| deleted_at | TIMESTAMP | Yes | Soft delete | NULL = active |

**Relationships:**
- `[field_id]` → FK to `[table].[field]` in [this service / service X via event]

### Indexes

| Name | Fields | Type | Justification |
|------|--------|------|---------------|
| idx_[table]_[field] | [field] | BTREE | Frequent searches by [field] |

---

## Modeling decisions

> Document here decisions that are not obvious — denormalizations, fields that seem redundant, etc.

- **[Decision]:** [why it was done this way]

---

## Schema migration

**Tool:** Liquibase
**Script location:** `src/main/resources/db/changelog/`
**Naming convention:** `changelog-<version>.xml` (or .yaml, .json, .sql)

**Rollback policy:**
- Liquibase supports rollback for most change types
- Use `<rollback>` tag within changesets for explicit rollback SQL
