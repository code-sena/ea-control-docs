# Runbook — ms-sensor-management

**Service:** ms-sensor-management
**Repository:** local repo `ms-sensor-management/` (remote not created yet)
**Version:** 0.1.0-SNAPSHOT
**Last updated:** 2026-10-06

---

## 1. Quick service information

| Field | Value |
|-------|-------|
| Local port | 3004 |
| Database | PostgreSQL, database `eduaircontrol_sensors`, schema `sensors` |
| Local DB port | 5434 (compose) |
| Health endpoint | `GET http://localhost:3004/health` (public) |
| Swagger UI | `http://localhost:3004/swagger-ui.html` |
| API contract | `07-api/contracts/openapi/ms-sensor-management.yaml` |
| Logs (local) | stdout / `/tmp/mssensor-app.log` when started manually |
| Migration tool | Liquibase (runs automatically at startup) |

---

## 2. Verify the service is healthy

```bash
curl http://localhost:3004/health
# 200 → {"status":"ok","timestamp":"...","dependencies":{"database":"ok"}}
# 503 → {"status":"down",...,"dependencies":{"database":"down"}}  (DB unreachable)
```

Authenticated smoke (any admin JWT — reads only need a valid token):

```bash
curl -s http://localhost:3004/api/v1/sensors -H "Authorization: Bearer $TOKEN"
```

**Expected:** `200` with `{"data":[…],"meta":{…}}`.
**Without/invalid token:** `401` `{"error":"UNAUTHORIZED",…}`.

---

## 3. Start / stop

```bash
# Full stack (service + own PostgreSQL 15 on :5434)
docker compose up -d
docker compose down                    # stop (data persists in volume)
docker compose down -v                 # stop and wipe data

# Dev mode against any PostgreSQL
POSTGRES_URL=jdbc:postgresql://localhost:5432/eduaircontrol_sensors \
POSTGRES_USER=… POSTGRES_PASSWORD=… JWKS_URI=http://localhost:8081/api/v1/auth/jwks \
./mvnw spring-boot:run
```

Environment variables: `SERVER_PORT`, `POSTGRES_URL`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `JWKS_URI` (RS256 JWKS of ms-security; defaults to the local
`http://localhost:8081/api/v1/auth/jwks`), `JWT_EXPIRATION`, `CORS_ALLOWED_ORIGINS`.

---

## 4. Database migrations

```bash
# Applied automatically at startup (classpath:db/changelog/db.changelog-master.yaml)
# Verify applied changesets:
docker exec -it ms-sensor-management-db \
  psql -U sensor_user -d eduaircontrol_sensors \
  -c "SELECT id, author, dateexecuted FROM databasechangelog ORDER BY orderexecuted;"

# Full rollback (drops schema and all 7 changesets) — from the service root:
docker run --rm --network host \
  -e LIQUIBASE_SEARCH_PATH=file:/liquibase/changelog \
  -v "$PWD/src/main/resources":/liquibase/changelog \
  -v "$HOME/.m2/repository/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar":/drivers/postgresql.jar \
  liquibase/liquibase rollbackCount --count=7 \
  --changelog-file=db/changelog/db.changelog-master.yaml \
  --classpath=/drivers/postgresql.jar \
  --url=jdbc:postgresql://localhost:5434/eduaircontrol_sensors \
  --username=sensor_user --password=sensor_pass
```

**New changeset rule:** add `NNN-description.yaml`, include it in the master,
always declare `rollback`, and mirror the change in `EduAirControl/database/negocio/`
(global reference — see decisions.md DEC-003).

---

## 5. Frequent problems

### Symptom: `401` for a token that works elsewhere

- The token must be **RS256-signed** and validate against the ms-security JWKS
  (`JWKS_URI`, DEC-002 superseded / ADR-018 JWT-only). Identity headers (`X-User-*`)
  are ignored — check the `Authorization: Bearer` header instead.

### Symptom: `409 CONFLICT` on sensor/variable create

- Duplicate `serialNumber` or duplicate variable `code`. Variable codes are
  uppercased before the check; serial numbers are compared case-insensitively.

### Symptom: `409 CONFLICT` "Sensor already has an overlapping installation"

- The sensor has an open installation, or an existing period that overlaps the
  requested `installedAt` (DEC-008). Close the active installation first
  (`POST /api/v1/sensor-installations/{id}/remove`).

### Symptom: `409` on `DELETE /sensors/{id}` or `DELETE /variables/{id}`

- The sensor has installation history (by design — history is immutable, DEC-006)
  or the variable is referenced by `sensor_variable`. Dissociate the pairs
  first; sensors cannot be deleted once installed (deactivate instead).

### Symptom: `400 VALIDATION_ERROR` on remove with `installedAt is in the future`

- The installation starts in the future; it cannot be closed before it begins.

### Symptom: startup fails with Liquibase error

- Read the changeset id in the exception; fix the YAML (colons inside unquoted
  scalars are the usual culprit), rebuild, and restart. If a changeset was
  partially applied, roll it back (section 4) before retrying.

### Symptom: `503` on `/health`

- Database down or wrong `POSTGRES_URL`; check `docker compose ps` and logs.

---

## 6. Tests

```bash
./mvnw verify          # 34 tests: domain unit (16) + controllers (18) on H2
```

Controller tests cover: 401/403, CRUD happy paths, 409 duplicates/overlaps,
400 validation, pagination meta, filters, physical delete guards, install →
close → 409 on second close, associate → dissociate → 404.

**PostgreSQL smoke (manual):** apply migrations on a disposable PostgreSQL 15,
run the HTTP checks above, then `rollbackCount 7` and assert the `sensors`
schema is gone (performed 2026-10-06: 4 tables / 9 constraints / 2 indexes,
22/22 checks, rollback total).

---

## 7. Production deployment

> Not deployed yet. Planned per ADR-011 — fill in URL, dashboards, alert
> channel, RTO/RPO, and rollout/rollback commands when the environment exists.
