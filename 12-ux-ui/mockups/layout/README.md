# Layout Mockups

> Screen layouts for EduAirControl application.
> Organized by platform: desktop and mobile.

---

## Structure

```
mockups/layout/
├── desktop/                    ← Desktop layouts (1280px+)
│   ├── landing-page/
│   ├── authentication/
│   ├── environmental-dashboard/
│   ├── educational-environments/
│   ├── saved-environments/
│   ├── environment-administration/
│   ├── alert-notifications/
│   ├── user-profile/
│   └── user-settings/
│
└── mobile/                     ← Mobile layouts (375px)
    ├── landing-page/
    ├── authentication/
    ├── environmental-dashboard/
    ├── educational-environments/
    ├── saved-environments/
    ├── environment-administration/
    ├── alert-notifications/
    ├── user-profile/
    └── user-settings/
```

---

## Screen inventory

| # | Screen | Bounded Context | Description |
|---|--------|-----------------|-------------|
| 01 | Landing Page | — | Public entry point, value proposition |
| 02 | Authentication | User Management | Login, registration, password recovery |
| 03 | Environmental Dashboard | Environmental Data Analysis | Current conditions and charts |
| 04 | Educational Environments | Environmental Monitoring | List and detail of spaces |
| 05 | Saved Environments | Environmental Monitoring | User's favorites |
| 06 | Environment Administration | Environmental Monitoring | CRUD environments/sensors |
| 07 | Alert Notifications | Environmental Monitoring | Active alerts and history |
| 08 | User Profile | User Management | Personal information |
| 09 | User Settings | User Management | Preferences and security |

---

## How to use

1. Open `index.html` in any screen folder
2. Modify HTML/Tailwind classes to change layout
3. Changes are reflected immediately in browser

---

## Tech stack

- HTML5
- Tailwind CSS (via CDN)
- No build step required

---

## Navigation flow

```
Landing Page
    │
    ├──▶ Authentication
    │         │
    │         ▼
    │    Environmental Dashboard
    │         │
    │         ├──▶ Educational Environments
    │         ├──▶ Saved Environments
    │         ├──▶ Alert Notifications
    │         ├──▶ User Profile
    │         └──▶ User Settings
```

---

## Correlations

- Domain contexts → `02-domain/domain-map.md`
- Navigation map → `12-ux-ui/navigation-map.md`
- Design system → `12-ux-ui/design-system.md`
