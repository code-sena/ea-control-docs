# ADR-022 — Capacity Target and Scaling Path to 1000 Environments

- **ID:** ADR-022
- **Date:** 2026-11-01
- **Status:** Accepted
- **Authors:** Jhon-Cortez
- **Related plan:** PLAN-001 (EduAirControl Delivery 2026-11-06)
- **Related:** ADR-020 (storage, retention, aggregations), ADR-021 (offline buffering), ADR-014 (thresholds)

---

## Context

The product must be able to grow to **1000 active environments**, each one a node that
measures 4 variables every 10 s, and the data must stay useful for years, not months. The
1000 figure is a **design target**: this delivery (2026-11-06) is not committed to reach it.

Where the system runs today: one Hostinger KVM 2 VPS (2 vCPU, 8 GB RAM) that hosts the whole
stack (~20 containers). `postgres-monitoring` is capped at **384 MB** (`docker-compose.cloud.yml`).
The disk size must be confirmed with `df -h` on the VPS; this ADR assumes a budget of
**40 GB** for the monitoring database.

Load model, one environment: 4 variables × 8,640 cycles/day = **34,560 readings/day**.

| Load at 1000 environments | Value |
|---|---|
| Readings per second | 400 |
| Readings per day | 34.56 M |
| HTTP requests per second, one POST per reading (today) | 400 |
| HTTP requests per second, one batch per node per minute | 16.7 |

ADR-020 sized the raw retention at 90 days from an estimate of 150 bytes/row for 50
environments. Measured row size is higher (below), and at 1000 environments the same policy
would need ~700 GB. The numbers have to be fixed before the system grows, not after.

---

## Evidence (measured)

PostgreSQL 15 in a container limited to **1 CPU and 384 MB**, synthetic data for 1000
installations × 4 variables, rows inserted in arrival order.

| Measure | Result |
|---|---|
| Current-style row (UUID keys, composite PK + time index) | **229 B/row** (111 heap + 107 indexes) |
| "Slim" row (`series_id int`, `measured_at`, `real`, `smallint` flag; PK + BRIN on time) | **92.9 B/row** (2.5× smaller) |
| Aggregate bucket row (`series_id`, bucket, avg/min/max `real`, count `smallint`) | **93.4 B/row** |
| Single-row `INSERT … ON CONFLICT DO NOTHING`, 8 clients, 5 M-row table | ~1,200 rows/s |
| Batch of 24 rows per statement, same setup | ~11,300 rows/s |
| Required at 1000 environments | 400 rows/s |

**Reading of the evidence:** the database is not the first limit (3× headroom with single
inserts, ~28× with batches). The limits are the **HTTP/application path** (not measured here;
Issue #12 measures it on the real host) and **disk**.

**Limits of the evidence:** one machine; CPU quota emulating one vCPU on an 8-core PC; database
only (no Caddy, gateway, JWT validation or alert evaluation); the other containers of the VPS
were not running; synthetic keys.

### Storage consequences

| At 1000 environments | Per day | Per year |
|---|---|---|
| Raw, current row (229 B) | 7.9 GB | 2.9 TB |
| Raw, slim row (92.9 B) | 3.2 GB | 1.2 TB |
| 5-min buckets (288/day/series) | 108 MB | 39 GB |
| 1-hour buckets | 9 MB | 3.3 GB |
| 1-day buckets | 0.37 MB | 0.14 GB |

Raw days that fit in a 40 GB budget:

| Row / resolution | 50 env | 100 env | 1000 env |
|---|---|---|---|
| Current row, 10 s | 101 d | 50 d | **5 d** |
| Slim row, 10 s | 250 d | 125 d | **12 d** |
| Slim row, 1 reading per minute | — | — | **75 d** |

---

## Decision

**We decided:** keep 1000 environments as a design target, send readings in one batch per
minute from now on, size raw retention with a formula instead of a fixed number, and reach 1000
through phases that are started by measurable triggers.

### 1. Normal operation sends one batch per 60 s

- Every reading is appended to the node buffer first (ADR-021); a sender drains the buffer
  once per minute as **one batch** (≈ 24 readings). Online and offline are the same path: an
  outage only makes the batch bigger.
- Requests drop from 400/s to ~17/s at 1000 environments.
- **Accepted trade-off (decided 2026-11-01):** a reading reaches the backend up to ~60 s after
  it was taken, and threshold evaluation (ADR-014, done at write) is delayed by the same
  amount. This amends ADR-021 section 6.

### 2. Raw retention is sized, not fixed

```
raw_days = budget_GB × 1000 / (environments × 34,560 × bytes_per_row / 1e6)
```

- Floor: raw data must cover **at least 2 days**, because the ADR-020 job recomputes the last
  25 h (ADR-021 contract).
- Reference steady state at 1000 environments with the slim row and 10 s resolution:

| Tier | Retention | Size |
|---|---|---|
| Raw | 7 days | 22.5 GB |
| 5-min buckets | 90 days | 9.7 GB |
| 1-hour buckets | 2 years | 6.5 GB |
| 1-day buckets | indefinite | 0.14 GB/year |
| **Total** | | **≈ 38.7 GB** |

- This is a **proposed amendment to ADR-020** (which fixes raw retention at 90 days). It needs
  confirmation from the ADR-020 owners before ADR-020 is edited.

### 3. Scaling path

| Phase | Scale | What changes | Start when |
|---|---|---|---|
| 0 — delivery | up to ~100 environments | Batch per minute; current schema (229 B/row); raw retention from the formula (~14 days at 100 environments = 11 GB); drop the two redundant indexes (`measurement-idempotency.md`); ADR-020 partitions and aggregation job | Now |
| 1 | ~100 – 300 | **Slim schema**: series catalog, composite PK `(series_id, measured_at)`, `real` values, `smallint` flag, BRIN on time. Alert evaluation resolved once per batch (see below). Alerts reference `(series_id, measured_at)` instead of a measurement id | 100 active environments, or raw retention would fall under 14 days |
| 2 | ~300 – 1000 | Choose by measured need: (a) store 1 reading per minute (semantic change, needs product decision; the node buffer shrinks to 1,440 records); (b) evaluate compression (for example TimescaleDB) on a staging copy; (c) more disk or a dedicated database host; (d) several replicas of the stateless ingestion service behind the gateway | 300 active environments, or any trigger below |

Triggers (any one starts the next step):

| Metric | Threshold | Action |
|---|---|---|
| Active environments | 100 / 300 | Start phase 1 / phase 2 |
| Monitoring DB size | > 60 % of the budget | Shorten raw retention, then next phase |
| Ingestion p95 latency or error rate | To be set from the k6 results of Issue #12 | Phase 2 (d) |

### 4. Known cost to remove in phase 1: alert evaluation per reading

`MeasurementAlertingService.evaluate` runs at least three lookups per reading (environment of the
installation, environment type, thresholds) before it can compare the value. A batch of 24
readings repeats them 24 times; at 1000 environments that is ~400 evaluations/s. In phase 1
these lookups are resolved once per batch (or cached with a short TTL), and only values that can
change an alert state are evaluated. This cost was **not measured**; it is the first thing the
k6 run should expose.

### 5. What this ADR does *not* decide

| Topic | Owner |
|---|---|
| Batch payload, maximum batch size, HTTP codes | OpenAPI contract (Issue #3) |
| Partitioning, aggregation job, bucket definitions | ADR-020 |
| Firmware drain/sender implementation | Issues #7 and #8 |
| The real ceiling of the VPS | Issue #12 (k6) |

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|---|---|---|---|
| **Phased path with triggers — chosen** | No premature work; each step justified by a measurement | 1000 is not demonstrated in this delivery | — (chosen) |
| Keep ADR-020 as is (90 days raw) | No change | 90 days of raw data is ~710 GB at 1000 environments and ~71 GB at 100 | Does not fit the host or the target |
| Bigger or dedicated database host now | Removes the disk and memory limits | Cost, migration risk 6 days before delivery | Not needed at the demonstrated scale; kept as phase 2 (c) |
| Keep only aggregates, no raw data | Smallest storage | Late readings (up to 24 h) could not be folded into closed buckets | Breaks the ADR-021 / ADR-020 contract |
| One POST per reading (today) | No firmware change | 400 requests/s on 2 shared vCPU | Request volume is the likely first limit |

---

## Consequences

**Positive:**
- A clear, measured answer to "how does this reach 1000 environments and last for years".
- Request volume drops ~24× immediately, with no schema change.
- Each step has a trigger, so effort is spent only when the data asks for it.

**Negative / Trade-offs:**
- Alerts can be up to ~60 s late.
- 1000 environments is not demonstrated by this delivery.
- Phase 1 changes the schema and the alert reference; it needs a migration and code changes.
- Phase 2 (a) changes the data semantics and must be a product decision.

**Impact on the system:**
- Documents to update: ADR-021 (amended in the same change), ADR-020 (pending owner
  confirmation), `15-project-control/risks.md` (R-018, R-019 numbers).
- Issues: #7 and #8 (sender drains the buffer every 60 s), #12 (k6 scenario below).

**Suggested k6 scenario for Issue #12:** virtual nodes ramp 50 → 100 → 250 → 500 → 1000; each
node sends one batch of 24 readings per minute; record p95 latency, errors, CPU, memory and DB
size per step, and report the step where a threshold is crossed.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Disk is smaller than the 40 GB budget | Medium | High | Confirm with `df -h`; the formula in section 2 recomputes retention |
| The HTTP path or alert evaluation limits the system before the database | High | Medium | Batch per minute; k6 run (#12); phase 1 batch-level evaluation |
| Measurements are synthetic and from one machine | Medium | Medium | Re-measure on the VPS before changing retention in production |
| Compression or a dedicated host adds cost or lock-in | Low | Medium | Only evaluated in phase 2, on a staging copy |
| Late alerts are unacceptable for a customer | Low | Medium | Interval is configurable on the node; smaller batches cost more requests |

---

## References

- ADR-014 — Environmental Sensor Variables and Thresholds
- ADR-020 — Storage, Retention and Aggregations
- ADR-021 — Offline Measurement Buffering and Device-Side `measuredAt` (amended 2026-11-01)
- `09-microservices/services/05-ms-environment-monitoring/measurement-idempotency.md`
- `infra/docker-compose.cloud.yml` (memory limits of the VPS)
- PLAN-001, Issues #7, #8, #12
