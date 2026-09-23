# Data Model — API Gateway

> The API Gateway is **stateless**: it has no database of its own.
> Its configuration state (routes, rate limits, allowlists) is managed
> through environment variables and configuration files versioned in Git,
> not in database tables.

---

## Database engine

**Engine:** N/A — no persistent database.

**Rationale:** An API Gateway that requires its own database introduces an extra failure
point in the layer every request traverses. Routing state is managed
via configuration (YAML files or environment variables), and session state
(token blacklist, rate limits) is delegated to shared Redis.

---

## In-memory / Redis state

The API Gateway does keep ephemeral state:

| Data | Storage | TTL | Purpose |
|------|---------|-----|---------|
| Rate limit counters | Redis | 60 seconds | Request counting per IP |
| Token blacklist check | Redis (read-only) | Per token expiration | Verify revoked tokens |

The auth-service **owns** the token blacklist — the gateway only reads it.

---

## Route configuration files

Instead of tables, routes are defined in:

```
config/
├── routes.yaml          # Route map: path → service + port
├── rate-limits.yaml     # Limits per route and per role
└── cors.yaml            # CORS configuration per origin
```

These files are versioned in Git and reloaded on service startup.
A route change requires a redeploy (intentional: routing changes are infrastructure changes).

---

## Correlations

- Environment configuration → `10-devops/environments.md`
- Gateway runbook → `runbook.md`
- Available route catalog → `09-microservices/service-catalog.md`
