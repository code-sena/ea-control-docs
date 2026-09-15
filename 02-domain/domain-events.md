# Domain Events

> **What to fill in here:** A domain event is a fact that occurred in the business.
> They are the backbone of asynchronous communication between bounded contexts.
> The name is ALWAYS in past tense and in the ubiquitous language of the domain.

---

## What is a domain event?

A **Domain Event** communicates that something important occurred in the business.
It is an immutable message that describes the fact in past tense.

```
✓ OrderCreated
✓ PaymentRejected
✓ UserRegistered
✓ StockDepleted

✗ CreateOrder (this is a command, not an event)
✗ OrderUpdated (too generic — what changed?)
✗ OrderEvent (does not indicate what occurred)
```

### Difference between Command and Event

| Concept | Intent | Tense | Can fail? |
|---------|--------|-------|-----------|
| **Command** | Instruction to do something | Present | Yes |
| **Event** | Notification of something that occurred | Past | No (it already happened) |

```
User → [RegisterUser] → System → [UserRegistered]
          (Command)                    (Event)
```

---

## Event catalog

### Event: UserRegistered

| Field | Value |
|-------|-------|
| **Name** | `UserRegistered` |
| **Bounded Context** | User Management |
| **Aggregate** | User |
| **Trigger** | A user completes the registration process |
| **Consumers** | Not defined |
| **Channel (topic)** | Not defined |
| **Schema version** | `v1` |
| **Delivery guarantee** | Not defined |

**Payload (JSON schema):**

```json
{
  "eventId": "UUID",
  "eventType": "UserRegistered",
  "aggregateId": "UUID",
  "aggregateType": "User",
  "occurredAt": "ISO 8601",
  "version": 1,
  "payload": {
    "userId": "UUID",
    "email": "string"
  },
  "metadata": {
    "correlationId": "UUID",
    "causationId": "UUID",
    "userId": "UUID"
  }
}
```

**Real payload example:**

```json
{
  "eventId": "generated-uuid",
  "eventType": "UserRegistered",
  "aggregateId": "user-uuid",
  "aggregateType": "User",
  "occurredAt": "2026-09-04T10:30:00Z",
  "version": 1,
  "payload": {
    "userId": "user-uuid",
    "email": "user@example.com"
  }
}
```

**What do consumers do with this event?**

| Consuming service | Action | Idempotent? |
|------------------|--------|-------------|
| [Service A] | Not defined | Not defined — Not defined |

---


### Event: EnvironmentalDataRecorded

| Field | Value |
|-------|-------|
| **Name** | `EnvironmentalDataRecorded` |
| **Bounded Context** | Environmental Monitoring |
| **Aggregate** | Environmental Data |
| **Trigger** | Environmental measurements are recorded for an educational environment |
| **Consumers** | Environmental Data Analysis |
| **Channel (topic)** | Not defined |
| **Schema version** | `v1` |
| **Delivery guarantee** | Not defined |

**Payload (JSON schema):**

```json
{
  "eventId": "UUID",
  "eventType": "EnvironmentalDataRecorded",
  "aggregateId": "UUID",
  "aggregateType": "EnvironmentalData",
  "occurredAt": "ISO 8601",
  "version": 1,
  "payload": {
    "environmentId": "UUID",
    "temperature": "number",
    "humidity": "number",
    "co2": "number",
    "noiseLevel": "number"
  },
  "metadata": {
    "correlationId": "UUID",
    "causationId": "UUID",
    "userId": "UUID"
  }
}
```

**Real payload example:**

```json
{
  "eventId": "generated-uuid",
  "eventType": "EnvironmentalDataRecorded",
  "aggregateId": "environmental-data-uuid",
  "aggregateType": "EnvironmentalData",
  "occurredAt": "2026-09-04T10:30:00Z",
  "version": 1,
  "payload": {
    "environmentId": "environment-uuid",
    "temperature": 23.5,
    "humidity": 58.2,
    "co2": 650,
    "noiseLevel": 42.5
  }
}
```

---

**What do consumers do with this event?**

| Consuming service | Action | Idempotent? |
|------------------|--------|-------------|
| Environmental Data Analysis | Uses environmental data for historical analysis | Not defined |

---

### Event: EnvironmentalDataAnalyzed

| Field | Value |
|-------|-------|
| **Name** | `EnvironmentalDataAnalyzed` |
| **Bounded Context** | Environmental Data Analysis |
| **Aggregate** | Environmental Data Analysis |
| **Trigger** | Environmental data is analyzed according to a selected time period |
| **Consumers** | Environmental Dashboard |
| **Channel (topic)** | Not defined |
| **Schema version** | `v1` |
| **Delivery guarantee** | Not defined |

**Payload (JSON schema):**

```json
{
  "eventId": "UUID",
  "eventType": "EnvironmentalDataAnalyzed",
  "aggregateId": "UUID",
  "aggregateType": "EnvironmentalDataAnalysis",
  "occurredAt": "ISO 8601",
  "version": 1,
  "payload": {
    "environmentId": "UUID",
    "period": "day | week | month | year",
    "temperature": "number",
    "humidity": "number",
    "co2": "number",
    "noiseLevel": "number"
  },
  "metadata": {
    "correlationId": "UUID",
    "causationId": "UUID",
    "userId": "UUID"
  }
}
```

**Real payload example:**

```json
{
  "eventId": "generated-uuid",
  "eventType": "EnvironmentalDataAnalyzed",
  "aggregateId": "analysis-uuid",
  "aggregateType": "EnvironmentalDataAnalysis",
  "occurredAt": "2026-09-04T10:30:00Z",
  "version": 1,
  "payload": {
    "environmentId": "environment-uuid",
    "period": "week",
    "temperature": 23.8,
    "humidity": 57.4,
    "co2": 640,
    "noiseLevel": 43.1
  }
}

---

**What do consumers do with this event?**

| Consuming service | Action | Idempotent? |
|------------------|--------|-------------|
| Environmental Dashboard | Displays the analyzed environmental information | Not defined |

---

## Standard fields for all events

All events must include these fields in the envelope:

| Field | Type | Description |
|-------|------|-------------|
| `eventId` | UUID | Unique event ID (for idempotency) |
| `eventType` | string | Event name in PascalCase |
| `aggregateId` | UUID | ID of the aggregate that generated the event |
| `aggregateType` | string | Aggregate type |
| `occurredAt` | ISO 8601 | When the business fact occurred |
| `version` | integer | Schema version (for evolution) |
| `payload` | object | Event data (specific per type) |
| `metadata.correlationId` | UUID | For tracing a transaction across services |
| `metadata.causationId` | UUID | ID of the event or command that caused this event |
| `metadata.userId` | UUID | User who initiated the chain (if applicable) |

---
## Event flow: Environmental Monitoring and Data Analysis

> Document here the event flows for the main business processes.
> Use the Event Storming format: orange=event, blue=command, green=view/policy, yellow=aggregate.

```
User
  │
  │ RegisterUser (command)
  ▼
[Aggregate: User]
  │
  │ UserRegistered (event)
  ▼
[User Management]


Environmental Data Source
  │
  │ RecordEnvironmentalData (command)
  ▼
[Aggregate: Environmental Data]
  │
  │ EnvironmentalDataRecorded (event)
  ▼
[Environmental Data Analysis]
  │
  │ AnalyzeEnvironmentalData (command)
  ▼
[Aggregate: Environmental Data Analysis]
  │
  │ EnvironmentalDataAnalyzed (event)
  ▼
[Environmental Dashboard]

Analysis periods:
Day → Week → Month → Year

```

### Example: Order creation flow

```
Customer
  │
  │ CreateOrder (command)
  ▼
[Aggregate: Order]
  │
  │ OrderCreated (event)
  ├──────────────────────────────────┐
  │                                  ▼
  │                         [Service: Inventory]
  │                         Decrements stock
  │                         StockReserved (event)
  │
  │ OrderCreated (event)
  └──────────────────────────────────┐
                                     ▼
                           [Service: Notifications]
                           Sends email to customer
```

---

## Schema evolution strategy

Events are contracts. Changing them in an incompatible way breaks consumers.

### What is a compatible change (does not break)?

```
✓ Add a new optional field to the payload
✓ Add a new event type
✓ Change a required field → optional
```

### What is an incompatible change (breaks)?

```
✗ Remove a field from the payload
✗ Change the type of a field (string → number)
✗ Change an optional field → required
✗ Change the event name
```

### How to evolve a schema without breaking consumers

**Strategy: Version the event**

```
Step 1: Publish EventV2 (new type with incompatible changes)
Step 2: Publish both EventV1 and EventV2 during the migration period
Step 3: Migrate consumers to V2 one by one
Step 4: Deprecate EventV1 (announce 1 sprint in advance)
Step 5: Stop publishing EventV1
```

---

## Event summary table

| Event | Origin context | Topic | Consumers | Version |
|-------|---------------|-------|-----------|---------|
| UserRegistered | User Management | `Not defined` | Not defined | v1 |
| EnvironmentalDataRecorded | Environmental Monitoring | `Not defined` | Environmental Data Analysis | v1 |
| EnvironmentalDataAnalyzed | Environmental Data Analysis | `Not defined` | Environmental Dashboard | v1 |

---

## Policies — Reactions to events

A **Policy** (or Saga step) describes what happens automatically when an event arrives.
It is the logic of "whenever X occurs, do Y".

```
Event: EnvironmentalDataRecorded

Policy: Whenever environmental data is recorded,
        use it for historical environmental analysis
```

| Trigger event | Policy | Emitted command | Service |
|--------------|--------|----------------|---------|
| EnvironmentalDataRecorded | Whenever environmental data is recorded, use it for historical analysis | AnalyzeEnvironmentalData | Environmental Data Analysis |
| EnvironmentalDataAnalyzed | Whenever environmental data is analyzed, display the results according to the selected period | Not defined | Environmental Dashboard |

---

## Resilience patterns for events

### At-least-once delivery + Idempotency

The message broker guarantees the event is delivered **at least once** but it may be
delivered more than once (in case of retries). Consumers must be **idempotent**.

```typescript
// Idempotent consumer — stores the processed eventId

async function processEnvironmentalDataRecordedEvent(
  event: EnvironmentalDataRecorded
): Promise<void> {

  // 1. Check if already processed
  if (await isEventAlreadyProcessed(event.eventId)) {
    logger.info(`Event ${event.eventId} already processed, ignoring`);
    return;
  }

  // 2. Process the event
  await updateModel(event.payload);

  // 3. Mark as processed (in the same transaction)
  await markEventProcessed(event.eventId);
}
```

### Dead Letter Queue (DLQ)

When an event fails after N retries, it goes to the DLQ.

| Configuration | Recommended value |
|--------------|------------------|
| Retries before DLQ | 3-5 |
| Backoff | Exponential (1s → 2s → 4s → 8s) |
| DLQ retention | 7 days |
| Alert | When DLQ has > 0 messages |

> See DLQ runbook in `09-microservices/services/XX-service/runbook.md`
