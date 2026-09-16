# Alert Notifications
> Alert history and active notifications.
## Files
- `index.html` — Screen layout
## Components
- Active alerts list with severity
- Alert history
- Alert detail (variable, threshold, value)
- Mark as read button
- Filter by severity/date
## Navigation
- Back → `../environmental-dashboard/`
- To environment → `../educational-environments/`
## Bounded Context
Environmental Monitoring
## Correlations
- Alert entity → `06-data/domain/ms-alert.md`
- EnvironmentalDataRecorded event → `02-domain/domain-events.md`
