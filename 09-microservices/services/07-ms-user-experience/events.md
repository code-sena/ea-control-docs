# Events — ms-user-experience

> Events published and consumed by this service.

## Published events

**None currently.** The service is purely request/response in v1.

Potential future events (per `06-data/domain/ms-user-experience.md`):

| Event | Trigger | Consumers |
|---|---|---|
| `UserPreferencesUpdated` | Preferences saved | Analytics, recommendations |
| `FavoriteAdded` / `FavoriteRemoved` | Favorite toggled | Analytics, recommendations |
| `ClassroomRated` | Rating saved | Analytics, classroom management |
| `SearchPerformed` | Search recorded | Analytics |

## Consumed events

**None currently.** The service does not react to events from other services.

The `notification_state` table references alerts from `ms-environment-monitoring`
by ID, but the alert lifecycle is queried synchronously, not via events.

---

## Retries, dead letters and alerts

Not applicable: no broker consumption in v1.
