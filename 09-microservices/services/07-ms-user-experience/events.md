# Events — ms-user-experience

> Events published and consumed by this service.

## Published events

**None currently.** The service is purely request/response in v1.

Potential future events, if event-driven integrations are introduced later:

| Event | Trigger | Consumers |
|---|---|---|
| `UserPreferencesUpdated` | Preferences saved | Analytics, recommendations |
| `FavoriteAdded` / `FavoriteRemoved` | Favorite toggled | Analytics, recommendations |

## Consumed events

**None currently.** The service does not react to events from other services.

The `notification_state` table references alerts from `ms-environment-monitoring`
by ID, but the alert lifecycle is queried synchronously, not via events.

---

## Retries, dead letters and alerts

Not applicable: no broker consumption in v1.
