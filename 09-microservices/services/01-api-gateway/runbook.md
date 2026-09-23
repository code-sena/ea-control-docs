# Runbook — API Gateway

> Operational procedures for whoever is on call.
> Each section is executable without extra context.

**Service:** api-gateway
**Local port:** 8080
**Version:** 1.0
**Last updated:** [YYYY-MM-DD]

---

## 1. Quick reference

| Field | Value |
|-------|-------|
| Local port | 8080 |
| Production URL | `https://api.[domain]/` |
| Staging URL | `https://staging.api.[domain]/` |
| Grafana dashboard | [gateway dashboard URL] |
| Alerts channel | [#alerts] |
| Escalation | [Tech Lead — contact] |
| Target RTO | 5 min (it is the entry point — immediate P0) |
| Target RPO | N/A (stateless) |

---

## 2. Health check

```bash
# Public health check (no authentication required)
curl https://api.[domain]/health

# Expected response:
# {"status": "ok", "timestamp": "2024-01-15T10:30:00Z"}

# If there are problems, check the upstreams:
curl -H "Authorization: Bearer [token-dev]" https://api.[domain]/api/v1/auth/health
```

---

## 3. Common alerts

### High rate of 502/503 errors (upstream not responding)

**Symptom:** Services behind the gateway return 502 or 503.

```bash
# See which service the errors belong to
kubectl logs -n [ns] -l app=api-gateway --tail=200 | grep '"status":50'

# Verify that the affected service pods are Running
kubectl get pods -n [ns] -l app=[affected-service]
```

**Decision tree:**
- Does the affected service have `Running` pods? → The problem may be an unhandled exception. Check the service logs.
- Are the pods in `CrashLoopBackOff`? → The service crashed. Escalate to the affected service runbook.
- Are all services down? → Network problem or the gateway itself. See section 3.3.

### High rate of 401 errors (invalid token)

**Symptom:** Many 401s. Could be an attack or a rotated JWT key.

```bash
# See IPs with the most 401s
kubectl logs -n [ns] -l app=api-gateway --tail=500 | \
  grep '"status":401' | jq '.ip' | sort | uniq -c | sort -rn | head
```

- Does a single IP generate all the 401s? → Possible attack. Add to denylist.
- Do many IPs generate 401s after a deploy? → The JWT public key may have changed. Check the gateway environment variables.

### Rate limit triggered globally

```bash
# See how many requests were blocked by rate limit
kubectl logs -n [ns] -l app=api-gateway --tail=200 | grep '"status":429'
```

If the rate limit is triggered under normal conditions, the limit may be too low.
Coordinate with the Tech Lead before changing it.

---

## 4. Rollback

The API Gateway is stateless — rollback is a redeploy of the previous version:

```bash
kubectl rollout history deployment/api-gateway -n [ns]
kubectl rollout undo deployment/api-gateway -n [ns]
kubectl rollout status deployment/api-gateway -n [ns]
```

---

## 5. Scale the gateway

```bash
# Scale horizontally (no downtime, stateless)
kubectl scale deployment/api-gateway -n [ns] --replicas=3
kubectl get pods -n [ns] -l app=api-gateway
```

---

## 6. Post-incident

- [ ] Gateway responding with P95 latency < 50ms
- [ ] Zero 5xx in the last 5 minutes
- [ ] Incident recorded in `13-operations/incident-management.md`
- [ ] If the incident caused an SLA breach: notify the Tech Lead
