# Entities, Value Objects, and Business Rules

> **What to fill in here:** The building blocks of the domain following the DDD tactical model.
> This document translates domain knowledge (obtained in Event Storming) into code models.

> **Stack note:** The concepts of Entity, Value Object, and Aggregate are language-independent.
> Code examples (classes, interfaces, decorators) are written in pseudo-TypeScript
> to illustrate the idea. To see the implementation in your technology:
> [`_stacks/node-typescript.md`](../_stacks/node-typescript.md) ·
> [`_stacks/java-spring.md`](../_stacks/java-spring.md) ·
> [`_stacks/python-fastapi.md`](../_stacks/python-fastapi.md) ·
> [`_stacks/go.md`](../_stacks/go.md)

---

## Tactical DDD concepts

### Entity
An **Entity** is an object defined by its identity, not its attributes.
Two entities are equal if they have the same ID, even if all their other attributes differ.

```
✓ Entity: User — identified by a unique user ID

✓ Entity: Educational Environment — identified by its unique environment ID

✓ Entity: Environmental Data — identified by its unique data record ID

✗ Not an entity: Temperature — it is an environmental measurement

✗ Not an entity: Humidity — it is an environmental measurement

✗ Not an entity: CO₂ — it is an environmental measurement

✗ Not an entity: Noise Level — it is an environmental measurement
```

### Value Object (VO)
A **Value Object** is an object defined by its attributes; it has no identity of its own.
It is immutable — if an attribute changes, it is a new VO.

```
✓ Value Object: Email — identifies an email value, not an independent entity
✓ Value Object: AnalysisPeriod — represents day, week, month, or year
✓ Value Object: EnvironmentalMeasurements — represents environmental
  measurement values when treated as a value rather than an entity
```

### Aggregate
An **Aggregate** is a cluster of entities and VOs treated as a unit.
It has an **Aggregate Root** which is the entry point — internal objects can only be
accessed through the root.

For EduAirControl, the exact aggregate boundaries have not yet been formally validated through Event Storming.

```
Educational Environment (Aggregate Root)

 └── Environmental Data[]
```
The final aggregate structure should be refined after formal Event Storming and detailed domain modeling.

**Golden rule of the Aggregate:** Transactions do not cross aggregate boundaries.
If you need to modify two aggregates in one operation, use a Domain Event and a Saga.

### Business Rules
**Business Rules** (invariants) are the constraints the domain must always satisfy.
They live in the Aggregate Root and are validated on every operation.

For EduAirControl, the rules below represent the currently identified domain constraints. Rules that have not been formally defined by the project are marked Not defined.

---

## System entities

### Entity: User

**Context:** User Management

**Description:** Represents a user who registers and accesses the EduAirControl platform.

**Attributes:**

| Attribute | Type | Description | Required | Rules |
|-----------|------|-------------|---------|-------|
| id | UUID | Unique identifier | Yes | Auto-generated on creation |
| email | String | User email address | Yes | Must have a valid email format |
| name | String | User name | Yes | Not defined |
| password | String | User authentication | Yes | Must satisfy authentication requirements |
| createdAt | DateTime | Creation date | Yes | Immutable, set on creation |
| updatedAt | DateTime | Last modification | Yes | Updated automatically |

**Lifecycle / States:**

```
[REGISTERED] ──(authenticate)──▶ [AUTHENTICATED]
                                      │
                                      │ (logout)
                                      ▼
                                 [REGISTERED]
```

| State | Description | Allowed transitions |
|-------|-------------|---------------------|
| REGISTERED | User has completed registration | → AUTHENTICATED |
| AUTHENTICATED | User has succesfully authenticated | → REGISTERED |


**Invariants (Business rules that MUST ALWAYS hold):**

```
INV-001: Valid User Email

 - Rule: A user's email must have a valid email format.
 - Violation: A user with an invalid email cannot be registered.
 - Implementation: Validate the email during user creation.

INV-002: User Identity

 - Rule: Every user must have a unique identifier.
 - Violation: A user cannot be created without an ID.
 - Implementation: Generate the identifier when the user is created.
```

**Code example (TypeScript/Java):**

```typescript
// TypeScript — Entity with invariants
class User {

  private constructor(
    private readonly id: UserId,
    private email: Email,
    private name: string,
    private password: string,
  ) {}

  static create(
    email: Email,
    name: string,
    password: string
  ): User {

    return new User(
      UserId.new(),
      email,
      name,
      password
    );
  }
}
```

### Entity: EducationalEnvironment

**Context:** Environmental Monitoring

**Description:** Represents an educational environment whose environmental conditions are monitored.

**Attributes:**

| Attribute | Type | Description | Required | Rules |
|-----------|------|-------------|---------|-------|
| id | UUID | Unique identifier | Yes | Auto-generated on creation |
| name | String | Environment name | Yes | Not defined |
| createdAt | DateTime | Creation date | Yes | Immutable, set on creation |
| updatedAt | DateTime | Last modification | Yes | Updated automatically |

**Lifecycle / States:**

```
[ACTIVE] ──(deactivate)──▶ [INACTIVE]
    ▲                          │
    └────────(activate)────────┘
```

| State | Description | Allowed transitions |
|-------|-------------|---------------------|
| ACTIVE | Educational environment is available for monitoring | → INACTIVE |
| INACTIVE | Educational environment is not currently active | → ACTIVE |


**Invariants (Business rules that MUST ALWAYS hold):**

```
INV-003: Environment Identity

 - Rule: Every educational environment must have a unique identifier.
 - Violation: An environment cannot be created without an ID.
 - Implementation: Generate the identifier during creation.

INV-004: Environment Name

 - Rule: An educational environment must have a name.
 - Violation: An environment cannot be created without a name.
 - Implementation: Validate the name during creation.
```
### Entity: EnvironmentData

**Context:** Environmental Monitoring

**Description:** Represents environmental measurements collected from an educational environment.

**Attributes:**

| Attribute | Type | Description | Required | Rules |
|-----------|------|-------------|---------|-------|
| id | UUID | Unique identifier | Yes | Auto-generated on creation |
| environmentId | UUID | Educational environment identifier | Yes | Must reference an existing environment |
| temperature | Decimal | Temperature measurement | Yes | Valid range not defined |
| humidity | Decimal | Humidity measurement | Yes | Valid range not defined |
| co2 | Decimal | CO₂ measurement | Yes | Valid range not defined |
| noiseLevel | Decimal | Noise level measurement | Yes | Valid range not defined |
| recordedAt | DateTime | Measurement date and time | Yes | Represents when the data was recorded |
| createdAt | DateTime | Creation date | Yes | Immutable, set on creation |
| updatedAt | DateTime | Last modification | Yes | Updated automatically |

**Lifecycle / States:**

```
[RECORDED]
```

| State | Description | Allowed transitions |
|-------|-------------|---------------------|
| RECORDED | Environmental measurements have been recorded | Not defined |



**Invariants (Business rules that MUST ALWAYS hold):**

```
INV-005: Environment Association

 - Rule: Environmental data must belong to an educational environment.
 - Violation: Environmental data without an environment cannot be recorded.
 - Implementation: Validate environmentId when creating the data record.

INV-006: Required Environmental Measurements

 - Rule: Environmental data must contain temperature, humidity, CO₂,
   and noise level measurements.
 - Violation: A record missing a required environmental measurement
   cannot be recorded.
 - Implementation: Validate the required measurements during creation.
```

### Entity: EnvironmentalDataAnalysis

**Context:** Environmental Data Analysis

**Description:** Represents the analysis of environmental data for a selected time period.

**Attributes:**

| Attribute | Type | Description | Required | Rules |
|-----------|------|-------------|---------|-------|
| id | UUID | Unique identifier | Yes | Auto-generated on creation |
| environmentId | UUID | Educational environment identifier | Yes | Must reference an existing environment |
| period | AnalysisPeriod | Selected analysis period | Yes | Day, week, month, or year |
| temperature | Decimal | Analyzed temperature information | Yes | not defined |
| humidity | Decimal | Analyzed humidity information | Yes | not defined |
| co2 | Decimal | Analyzed CO₂ information | Yes | not defined |
| noiseLevel | Decimal | Analyzed noise information | Yes | not defined |
| createdAt | DateTime | Creation date | Yes | Immutable, set on creation |
| updatedAt | DateTime | Last modification | Yes | Updated 

**Lifecycle / States:**

```
[CREATED] ──(analyze)──▶ [ANALYZED]
```

| State | Description | Allowed transitions |
|-------|-------------|---------------------|
| CREATED | Analysis has been created | → ANALYZED |
| ANALYZED | Environmental data has been analyzed | → Not defined |


**Invariants (Business rules that MUST ALWAYS hold):**

```
INV-007: Valid Analysis Period

 - Rule: An analysis must use one of the supported periods:
   day, week, month, or year.
 - Violation: An analysis with an unsupported period cannot be created.
 - Implementation: Validate the AnalysisPeriod value.

INV-008: Environment Association

 - Rule: An environmental analysis must be associated with an
   educational environment.
 - Violation: An analysis without an environment cannot be created.
 - Implementation: Validate environmentId during creation.
```

---

## System Value Objects

### Value Object: Email

**Description:** Represents the email address associated with a user.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| value | String | User's email address |

**Validation rules:**

```
- Email must have a valid format.
- Email should be normalized consistently.
- Email cannot be empty.
```

**Example:**

```typescript
// Value Object — Immutable, validated in the constructor
class Email {

  private readonly value: string;

  constructor(email: string) {

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      throw new DomainException(`Invalid email: ${email}`);
    }

    this.value = email.toLowerCase();
  }

  toString(): string {
    return this.value;
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}
```
### Value Object: AnalysisPeriod

**Description:** Represents the time period used to analyze environmental data.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| value | String | Select analysis period |

**Validation rules:**

```
- The value must be one of:
  day
  week
  month
  year
- Other values are not allowed.
```

**Example:**

```typescript
// Value Object — Immutable, validated in the constructor
class AnalysisPeriod {

  private readonly value: string;

  constructor(value: string) {

    const validPeriods = [
      'day',
      'week',
      'month',
      'year'
    ];

    if (!validPeriods.includes(value)) {
      throw new DomainException(
        `Invalid analysis period: ${value}`
      );
    }

    this.value = value;
  }

  toString(): string {
    return this.value;
  }

  equals(other: AnalysisPeriod): boolean {
    return this.value === other.value;
  }
}
```

---

## System Aggregates

### Aggregate: Educational Environment 

**Aggregate Root:** EducationalEnvironment

**Internal entities:**
- EnvironmentalData — environmental measurements are associated with the educational environment.

**Value Objects:**
- Not defined

**Aggregate invariants:**

```
AGGR-INV-001: Environmental data must be associated with an educational environment.

AGGR-INV-002: An educational environment must have a unique identifier.

AGGR-INV-003: Required environmental measurements must be present when
environmental data is recorded.
```

**Why do these objects form an aggregate?**
The Educational Environment represents the monitored environment and its associated environmental data. Keeping the relationship consistent ensures that environmental measurements are always associated with the correct educational environment.

### Aggregate: User

**Aggregate Root:** User

**Internal entities:**
- Not defined

**Value Objects:**
- Email

**Aggregate invariants:**

```
AGGR-INV-004: A User must have a valid email.

AGGR-INV-005: A User must have a unique identifier.
```

**Why do these objects form an aggregate?**
User is the aggregate root because registration and authentication information belong to the user. The Email value object is part of the User because it represents one of the user's validated domain values.

### Aggregate: Environmental Data Analysis

**Aggregate Root:** EnvironmentalDataAnalysis

**Internal entities:**
- Not defined

**Value Objects:**
- AnalysisPeriod

**Aggregate invariants:**

```
AGGR-INV-006: The analysis must be associated with an educational environment.

AGGR-INV-007: The analysis period must be day, week, month, or year.

AGGR-INV-008: Environmental analysis must contain the environmental
variables required by the domain.
```

**Why do these objects form an aggregate?**
EnvironmentalDataAnalysis represents the analysis of environmental information for a specific educational environment and selected time period. The analysis period is part of the aggregate because it determines the temporal scope of the analysis.

---

## Summary table of tactical building blocks

| Name | Type | Bounded Context | Aggregate Root? |
|------|------|----------------|----------------|
| User | Entity | User Management | Yes |
| EducationalEnvironment | Entity | Environmental Monitoring | Yes |
| EnvironmentalData  | Entity | Environmental Monitoring | Yes |
| EnvironmentalDataAnalysis | Entity |Environmental Data Analysis | Yes |
| Email | Value Object | Shared | User Management |
| AnalysisPeriod | Value Object | Environmental Data Analysis | N/A |
| Domain Service | value Object | Not defined | N/A |

---

## Domain Services

A **Domain Service** is business logic that does not naturally belong to any entity.

For EduAirControl, no Domain Service has been formally defined yet.

Domain Service: Not defined

Potential domain logic such as environmental data analysis should remain associated with the Environmental Data Analysis domain until the team determines that the logic does not naturally belong to an entity or aggregate.

No additional Domain Service is introduced because the current project documentation does not formally define one.
```

---

## Correlation with code

| Domain artifact | Package / folder in code | File |
| ------------------------------------------ | ------------------------ | ------------- |
| Aggregate Root `User`                      | `Not defined`            | `Not defined` |
| Value Object `Email`                       | `Not defined`            | `Not defined` |
| Aggregate Root `EducationalEnvironment`    | `Not defined`            | `Not defined` |
| Entity `EnvironmentalData`                 | `Not defined`            | `Not defined` |
| Aggregate Root `EnvironmentalDataAnalysis` | `Not defined`            | `Not defined` |
| Value Object `AnalysisPeriod`              | `Not defined`            | `Not defined` |
| Domain Service                             | `Not defined`            | `Not defined` |
| Repository                                 | `Not defined`            | `Not defined` |

The exact package/folder structure and filenames for these domain artifacts have not been formally defined in the current DDD documentation.

> See hexagonal structure in `05-architecture/hexagonal-architecture.md`
