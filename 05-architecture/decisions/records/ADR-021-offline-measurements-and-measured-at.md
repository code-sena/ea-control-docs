# ADR-021 — Offline Measurement Buffering and Device-Side `measuredAt`

- **ID:** ADR-021
- **Date:** 2026-10-29
- **Status:** Accepted — amended 2026-11-01 (normal-operation batching, see ADR-022)
- **Authors:** Jhon-Cortez
- **Related plan:** PLAN-001 (EduAirControl Delivery 2026-11-06), Issue #2

---

## Context

The ESP32 node posts each reading over HTTPS to `POST /api/v1/measurements` of
`ms-environment-monitoring` (ADR-004, ingestion path updated 2026-10-28). Today:

- The firmware **omits `measuredAt` on purpose** and the backend falls back to its own
  clock (`MeasurementService.record`). A reading that is retried later gets a *different*
  timestamp, so the natural key `(sensor_installation_id, variable_id, measured_at)` cannot
  deduplicate it.
- A reading taken while Wi-Fi is down is **lost**: there is no local storage and no retry.
- There is no batch endpoint, so recovering after an outage would mean replaying hundreds of
  single requests.
- The node has no RTC; its only clock is `millis()` until it syncs over NTP.

If this is not decided now, the firmware (Issues #5, #7, #8), the batch endpoint (#3, #6) and
the integration tests (#13) each invent their own rules for timestamps, retries and
duplicates.

**Known constraints:**
- No new hardware (no RTC, no SD card) — out of scope for this delivery.
- Delivery date 2026-11-06; the decision must not block parallel work.
- The node measures 4 variables every 10 s (`SENSOR_READ_INTERVAL_MS`), i.e. 8,640 cycles per
  24 h.
- The backend already rejects `measuredAt` older than 24 h or more than 5 min in the future
  (`MeasurementController.requireMeasuredAtInRange`).
- Flash is 4 MB; the current `min_spiffs.csv` leaves only 128 KB for data, and the second OTA
  slot is unused (firmware is flashed over USB).

---

## Decision

**We decided:** the node stamps every reading with the UTC instant at which it was taken
(`measuredAt`), keeps unsent readings in a circular binary buffer in internal flash for up to
24 h, re-sends them with retries that the backend treats as idempotent, and **keeps
measuring while offline**; BLE re-provisioning is opened on demand with the BOOT button
instead of automatically after a Wi-Fi drop.

### 1. `measuredAt` is set by the device, at read time

- `measuredAt` is the UTC instant of the **reading**, never of the HTTP request.
- Format: ISO-8601 UTC with `Z`, **whole seconds** (the 10 s cycle needs no more). The backend
  stores it as received and never replaces it.
- It is **mandatory** for the batch endpoint. The single-reading endpoint keeps accepting a
  missing value (server-clock fallback) only until the new firmware is deployed, so nothing
  that works today breaks; after that it becomes mandatory too.

### 2. Clock source and the "no time" case

- The node syncs its clock over **NTP**.
- A reading taken **before the first NTP sync** is stored with an *unsynced* flag and its
  `millis()` offset from boot. When NTP succeeds, the node rebuilds
  `measuredAt = now_utc − (millis_now − millis_at_read)`.
- If the node **reboots before ever syncing**, the offset is gone: those readings are
  **discarded**, never sent with an invented time.
- A node that has not synced does not send anything with a guessed timestamp.

### 3. Idempotency key

- A reading is identified by `(sensor_installation_id, variable_id, measured_at)`, the same
  natural key already in the schema and in `pattern-guide.md`.
- Re-sending an already stored reading is a **successful no-op**, not an error. This is what
  makes retries safe.

### 4. Offline buffer

- Storage: **LittleFS on internal flash**, fixed-size binary records (one record per cycle:
  UTC epoch seconds, the four values, a flags byte; ≈ 24 bytes).
- Retention target: **24 h** = 8,640 records ≈ 207 KB of payload. To fit it, the firmware
  uses a **custom partition table without the OTA slots** and a data partition of at least
  512 KB (final size set in Issue #7). No extra hardware.
- When full, the **oldest records are overwritten** (circular). The node always keeps the most
  recent data.
- The 24 h figure matches the backend acceptance window (section 5). If the partition is ever
  smaller, the effective window is the smaller of the two.

### 5. Acceptance window

- The backend accepts `measuredAt` in `[now − 24 h, now + 5 min]`. Both bounds are
  configuration, not contract.
- A reading outside the window is rejected **individually**; it does not fail the rest of a
  batch.

### 6. Delivery and retry rules for the node

- **Normal operation uses the same path (amended 2026-11-01, ADR-022).** Every reading is
  appended to the buffer first; a sender drains the buffer once per minute as one batch
  (about 6 cycles × 4 variables = 24 readings). Online and offline are one code path: an
  outage only makes the batch bigger. A reading reaches the backend up to ~60 s after it was
  taken, and threshold evaluation (ADR-014) is delayed by the same amount.
- Records are sent **oldest first**, in batches, at a controlled rate.
- A record is deleted from the buffer **only after the backend confirms it** (created or
  already-stored duplicate).
- `429`: wait and retry honoring `Retry-After` if present. `5xx` / network errors: exponential
  backoff. Nothing is deleted on these.
- Per-reading validation rejection (including out-of-window): the record is dropped, because
  retrying can never succeed.
- `410` (installation retired): stop sending for that installation, as the firmware already
  does.

### 7. Re-provisioning (BLE) while offline

Measuring and offering BLE are **independent**. Today, after 60 s without Wi-Fi the firmware
opens BLE and stops measuring (`loop()` returns before reading sensors while `bleRunning`),
and the 5 min BLE timeout in `config.h` is never applied. That behaviour is replaced:

- **The node never stops measuring or buffering because of BLE.** Only *sending* is paused
  while a provisioning payload is being written, to avoid using half-written credentials.
- **No automatic BLE when Wi-Fi drops** (the 60 s re-offer rule is removed). This also applies
  at boot when stored credentials fail to connect. The node keeps measuring into the buffer
  and retrying Wi-Fi.
- BLE is opened **on demand by holding the BOOT button (GPIO0) for 3 s**, after the node has
  booted. It stays open for **5 min** (`BLE_PROVISION_TIMEOUT_MS`, now actually enforced) and
  then closes by itself; measuring continues the whole time.
- BLE still opens **automatically** in the two cases where there is nothing to protect:
  the node has **no credentials** (first provisioning) or the backend answered `410`
  (installation retired, nothing valid to send).
- **Buffer vs. new provisioning:** records do not carry an installation id. If provisioning
  delivers the *same* `installationId` (e.g. only the Wi-Fi password changed), the buffer is
  kept and drained afterwards. If the `installationId` differs, the buffer is **erased**,
  because those readings belong to another installation.

### 8. Boundaries — what this ADR does *not* decide

So that it blocks nobody, these are owned elsewhere and may change without touching this ADR:

| Topic | Owner |
|-------|-------|
| Batch payload shape, max batch size, HTTP status codes, per-reading error format, rate limits | OpenAPI contract (Issue #3) |
| Storage engine, retention of stored data, partitioning, aggregations (5 min / 1 h / 1 day) | ADR-020 (Issue #1) |
| Firmware implementation details (task structure, record layout bytes, button debounce) | Issues #5, #7, #8 |
| Authentication or pairing for the BLE characteristic | Not planned for this delivery |

**Contract with ADR-020:** readings can arrive up to 24 h late (section 5), so the ADR-020
aggregation job must recompute the buckets of the last 25 h (24 h window plus margin) from raw
data on every run, using its existing idempotent upsert, instead of only the latest closed
bucket. Otherwise averages are wrong right after every outage. This is the only expectation
ADR-021 places on ADR-020.

ADR-020 is otherwise independent: if it partitions `environment_measurement` by `measured_at`, the
unique key above already contains `measured_at`, so both decisions hold.

**Justification:**
A timestamp assigned by the device at read time is the only value that stays identical
across retries, which is what makes idempotency possible. Internal flash with a binary
circular buffer gives the longest outage coverage without hardware, and reusing the existing
natural key avoids a schema change.

---

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| **Device `measuredAt` + circular binary buffer in flash + idempotent retries — chosen** | Stable key across retries; survives reboot; up to 24 h; no new hardware or schema | Needs NTP, a custom partition table and a one-time reflash | — (chosen) |
| Keep the server clock (current behaviour) | No firmware change | Retries get new timestamps, so duplicates; outage data is lost or mis-dated | Breaks idempotency and historical accuracy |
| RTC module and/or SD card | Accurate time without Wi-Fi; huge capacity | New hardware, wiring, cost and delivery risk | Out of scope for this delivery (PLAN-001); can come later |
| RAM-only buffer | Trivial | Lost on any reset or power cut | Does not meet the outage requirement |
| JSON text buffer on LittleFS | Easy to debug | ~110 bytes/cycle: only ~2.5 h fit in the 128 KB partition | Binary records give ~5× the capacity |

---

## Consequences

**Positive:**
- A Wi-Fi outage of up to 24 h loses no confirmed-pending readings.
- Retries and duplicate sends cannot create duplicate rows.
- Historical timestamps reflect when the reading happened, which the averages in ADR-020 rely on.
- The firmware, backend and OpenAPI work can proceed in parallel.

**Negative / Trade-offs:**
- No OTA updates (the second app slot is removed); firmware is updated over USB, as today.
- A node that reboots and cannot reach NTP loses the unsynced readings.
- Changing the Wi-Fi network of a node that is already provisioned now needs **physical access**
  (BOOT button); it can no longer be done from the app alone after a Wi-Fi drop.
- The BLE characteristic is still unauthenticated while open; this ADR only shortens and
  gates the exposure window, it does not add pairing or authentication.
- Records overwritten after 24 h offline are lost by design.
- Alerts can be up to ~60 s late because readings are sent in one batch per minute (ADR-022).
- Flash write wear: one ~24-byte append per 10 s cycle. LittleFS wear levelling makes this
  acceptable for the project lifetime, but it is measured in Issue #7.

**Impact on the system:**
- Affected services: `ms-environment-monitoring` (ingest and batch, validation),
  `api-gateway` (route for the batch endpoint), ESP32 firmware (`infra/iot/esp32-node`).
- Documents that must be updated:
  - `07-api/contracts/openapi/ms-environment-monitoring.yaml` — `measuredAt` required, batch endpoint (Issue #3).
  - `09-microservices/services/05-ms-environment-monitoring/` — ingestion behaviour.
  - `05-architecture/pattern-guide.md` — device-side timestamp and offline buffer.
  - `15-project-control/risks.md` — clock reference and buffer sizing risks (below).
  - `infra/iot/esp32-node/README.md` and `GUIA-PROVISIONAMIENTO.md` — partition table, reflash step, BOOT-button re-provisioning.
  - `guia_configuracion_esp32_react_native_ble.md` — the app no longer finds the node advertising after a Wi-Fi drop unless BOOT was held.

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Node loses its time reference (no RTC) and stamps wrong dates | Medium | High | NTP, unsynced flag, discard instead of guessing, acceptance window |
| Buffer smaller than the target outage | Medium | High | Size from 8,640 records/24 h; real test of 15, 30 and 60 min outages (Issue #13) |
| Retries create duplicates | Medium | High | Natural-key idempotency; duplicate = success |
| A burst of buffered data overloads the backend after an outage | Medium | Medium | Oldest-first controlled rate, `429` backoff |
| Custom partition table bricks a flash/update | Low | Medium | Documented one-time USB reflash procedure; `GUIA-PROVISIONAMIENTO.md` |
| Holding BOOT during a reset puts the ESP32 in download mode (GPIO0 is a strapping pin) | Low | Low | Long press is only read after boot completes; documented in the README |
| Node stuck offline with a wrong Wi-Fi and nobody on site | Medium | Medium | It keeps buffering up to 24 h; document the BOOT procedure for the operator |

---

## References

- ADR-004 — Communication Patterns (ingestion path updated 2026-10-28)
- ADR-007 — At-Least-Once Events with Transactional Outbox (natural-key idempotency)
- ADR-018 — JWT-Only Mesh Authentication (device token used by the node)
- Related to: ADR-020 (storage, retention and aggregations), PLAN-001
- `ms-environment-monitoring`: `MeasurementController.requireMeasuredAtInRange`, `MeasurementService.record`
- `infra/iot/esp32-node/platformio.ini`, `include/config.h`
