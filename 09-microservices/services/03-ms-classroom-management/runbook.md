# Runbook — ms-classroom-management

**Service:** ms-classroom-management
**Repository:** local repo `ms-classroom-management/` (remote not created yet)
**Version:** 0.1.0-SNAPSHOT
**Last updated:** 2026-09-29

---

## 1. Quick service information

| Field | Value |
|-------|-------|
| Local port | 3002 |
| Database | PostgreSQL, database `eduaircontrol_classrooms`, schema `classrooms` |
| Local DB port | 5433 (compose) |
| Health endpoint | `GET http://localhost:3002/health` (public) |
| Swagger UI | `http://localhost:3002/swagger-ui.html` |
| API contract | `07-api/contracts/openapi/ms-classroom-management.yaml` |
| Logs (local) | stdout / `/tmp/opencode/msclassroom.log` when started manually |
| Migration tool | Liquibase (runs automatically at startup) |

---

## 2. Verify the service is healthy

```bash
curl http://localhost:3002/health
# 200 → {"status":"ok","timestamp":"...","dependencies":{"database":"ok"}}
# 503 → {"status":"down",...,"dependencies":{"database":"down"}}  (DB unreachable)
```

Authenticated smoke (any admin JWT — reads only need a valid token):

```bash
curl -s http://localhost:3002/api/v1/campuses -H "Authorization: Bearer $TOKEN"
```

**Expected:** `200` with `{"data":[…],"meta":{…}}`.
**Without/invalid token:** `401` `{"error":"UNAUTHORIZED",…}`.

---

## 3. Start / stop

```bash
# Full stack (service + own PostgreSQL 15 on :5433)
docker compose up -d
docker compose down                    # stop (data persists in volume)
docker compose down -v                 # stop and wipe data

# Dev mode against any PostgreSQL
POSTGRES_URL=jdbc:postgresql://localhost:5432/eduaircontrol_classrooms \
POSTGRES_USER=… POSTGRES_PASSWORD=… JWT_SECRET=… \
./mvnw spring-boot:run
```

Environment variables: `SERVER_PORT`, `POSTGRES_URL`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `JWT_SECRET` (required), `JWT_EXPIRATION`, `CORS_ALLOWED_ORIGINS`.

---

## 4. Database migrations

```bash
# Applied automatically at startup (classpath:db/changelog/db.changelog-master.yaml)
# Verify applied changesets:
docker exec -it ms-classroom-management-db \
  psql -U classroom_user -d eduaircontrol_classrooms \
  -c "SELECT id, author, dateexecuted FROM databasechangelog ORDER BY orderexecuted;"

# Full rollback (drops schema and all 6 changesets) — from the service root:
docker run --rm --network host \
  -e LIQUIBASE_SEARCH_PATH=file:/liquibase/changelog \
  -v "$PWD/src/main/resources":/liquibase/changelog \
  -v "$HOME/.m2/repository/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar":/drivers/postgresql.jar \
  liquibase/liquibase rollbackCount --count=6 \
  --changelog-file=db/changelog/db.changelog-master.yaml \
  --classpath=/drivers/postgresql.jar \
  --url=jdbc:postgresql://localhost:5433/eduaircontrol_classrooms \
  --username=classroom_user --password=classroom_pass
```

**New changeset rule:** add `NNN-description.yaml`, include it in the master,
always declare `rollback`, and mirror the change in `EduAirControl/database/negocio/`
(global reference — see decisions.md DEC-003).

---

## 5. Frequent problems

### Symptom: `401` for a token that works elsewhere

- The token must be HMAC-signed with the same `JWT_SECRET` as the issuer
  (interim scheme, DEC-002). Check the env var matches the issuing app.

### Symptom: `409 CONFLICT` on create

- Duplicate `code` (campus/env type) or duplicate `(campusId, code)` (environment).
  Codes are uppercased before the check; soft-deleted rows still consume the code.

### Symptom: `400 VALIDATION_ERROR` "campusId does not reference an existing campus"

- FK check: the referenced campus is missing **or soft-deleted**. List campuses
  (`GET /api/v1/campuses`) and create/restore it first.

### Symptom: startup fails with Liquibase error

- Read the changeset id in the exception; fix the YAML (colons inside unquoted
  scalars are the usual culprit), rebuild, and restart. If a changeset was
  partially applied, roll it back (section 4) before retrying.

### Symptom: `503` on `/health`

- Database down or wrong `POSTGRES_URL`; check `docker compose ps` and logs.

---

## 6. Tests

```bash
./mvnw verify          # 25 tests: domain unit + controller (H2)
```

Controller tests cover: 401/403, CRUD happy paths, 409 duplicates, 400
validation, pagination meta, filters, soft delete → 404.

---

## 7. Production deployment

> Not deployed yet. Planned per ADR-011 — fill in URL, dashboards, alert
> channel, RTO/RPO, and rollout/rollback commands when the environment exists.
