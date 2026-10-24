# Runbook — Auth Service

> Operational procedures for whoever is on call.
> This service is critical — a P0 in auth-service prevents ALL users from accessing the system.

**Service:** auth-service
**Local port:** 8081
**Version:** 1.0
**Last updated:** [YYYY-MM-DD]

---

## 1. Quick reference

| Field | Value |
|-------|-------|
| Local port | 8081 |
| Production URL | `https://api.[domain]/api/v1/auth` |
| Staging URL | `https://staging.api.[domain]/api/v1/auth` |
| Grafana dashboard | [auth-service dashboard URL] |
| Alerts channel | [#alerts] |
| Escalation | [Tech Lead — contact — URGENT if auth is down] |
| Target RTO | 5 min (authentication blocked = system inoperable) |
| Target RPO | 0 (PostgreSQL with real-time replica) |

---

## 2. Health check

```bash
# Health check
curl https://api.[domain]/api/v1/auth/health

# Expected response:
# {"status": "ok", "db": "connected", "redis": "connected"}

# If there are problems, check the dependencies:

# Check PostgreSQL
kubectl exec -n [ns] [postgres-pod] -- pg_isready -U [user]

# Check Redis
kubectl exec -n [ns] [redis-pod] -- redis-cli ping
# Expected response: PONG
```

---

## 3. Common alerts

### High rate of 401 errors on login

**Symptom:** Many failed login attempts in a short time (possible attack).

```bash
# See IPs with the most attempts
kubectl logs -n [ns] -l app=auth-service --tail=500 | \
  grep '"eventType":"user.login_failed"' | jq '.payload.ipAddress' | \
  sort | uniq -c | sort -rn | head -10
```

**Action:** If one IP exceeds [N] attempts in 5 minutes, add it to the gateway denylist.

### Refresh tokens not working (users with active sessions cannot renew)

**Likely cause:** Redis is down or the JWT key was rotated without updating all services.

```bash
# Check Redis
kubectl exec -n [ns] [redis-pod] -- redis-cli ping

# Verify the public key in the gateway matches the one in auth-service
kubectl exec -n [ns] [auth-pod] -- curl localhost:8081/api/v1/auth/jwks
```

### Mass account lockouts

**Symptom:** Many users report "account locked" simultaneously.

**Likely cause:** (A) coordinated attack, (B) counter bug incrementing incorrectly.

```bash
# Count currently locked accounts
kubectl exec -n [ns] [redis-pod] -- redis-cli keys "locked:*" | wc -l

# Unlock a specific account (emergencies only, Tech Lead approval)
kubectl exec -n [ns] [redis-pod] -- redis-cli del "locked:user@example.com"
```

---

## 4. JWT key rotation

> Only run with Tech Lead approval. Impacts all services.

```bash
# 1. Generate a new key pair
openssl genrsa -out new-private.pem 2048
openssl rsa -in new-private.pem -pubout -out new-public.pem

# 2. Update the secret in the environment vault
# (follow your infrastructure's vault process)

# 3. The JWKS endpoint supports multiple keys — add the new one without removing the old one
# This allows existing tokens (signed with the old key) to remain valid
# until they expire (max 1 hour)

# 4. After 1 hour: remove the old key from JWKS

# 5. Verify the gateway can use the new public key
curl https://api.[domain]/api/v1/auth/jwks
```

---

## 5. Rollback

```bash
kubectl rollout history deployment/auth-service -n [ns]
kubectl rollout undo deployment/auth-service -n [ns]
kubectl rollout status deployment/auth-service -n [ns]
```

**If there are DB migrations in the deploy being rolled back:**
Contact the Tech Lead before rolling back — a rollback migration may be required.

---

## 6. Maintenance operations

### Clean up expired refresh tokens

```bash
# If the automatic cleanup job fails:
kubectl exec -n [ns] [postgres-pod] -- psql -U [user] -d [db] \
  -c "DELETE FROM refresh_tokens WHERE expires_at < NOW() AND revoked_at IS NOT NULL;"
```

### Revoke all sessions for a user (emergency)

```bash
kubectl exec -n [ns] [postgres-pod] -- psql -U [user] -d [db] \
  -c "UPDATE refresh_tokens SET revoked_at = NOW() WHERE user_id = '[user-uuid]';"
```

---

## 7. Post-incident

- [ ] Login and refresh working normally
- [ ] Zero 5xx in the last 5 minutes
- [ ] Incorrectly locked accounts unlocked (if applicable)
- [ ] Incident recorded in `13-operations/incident-management.md`
- [ ] If there was a credential breach: escalate to the security protocol
