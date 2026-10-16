# Layout Mockups

> Screen layouts for the EduAirControl applications.
> Organized by platform: desktop (web) and mobile.
>
> **Tokens:** all mockups share `mockups/shared/mockup.css`, whose variables are
> 1:1 with `ea-control-frontend/apps/web/src/index.css` (see
> `../../design-system.md`). These are *layout* mockups, not production code.

---

## Structure

```
mockups/
├── shared/mockup.css               ← design tokens + mockup components
├── exports/                        ← PNG captures (desktop/ + mobile/)
└── layout/
    ├── desktop/                    ← Web layouts (1280px)
    │   ├── landing-page/
    │   ├── authentication/
    │   ├── guide/
    │   ├── environmental-dashboard/
    │   ├── educational-environments/
    │   ├── saved-environments/
    │   ├── environment-administration/
    │   ├── super-admin/
    │   ├── alert-notifications/
    │   ├── user-profile/
    │   └── user-settings/
    └── mobile/                     ← Mobile layouts (375px frame)
        ├── authentication/
        ├── guide/
        ├── environmental-dashboard/
        ├── educational-environments/
        ├── saved-environments/
        ├── environment-administration/
        ├── super-admin/
        ├── alert-notifications/
        ├── user-profile/
        ├── user-settings/
        └── provisioning/
```

Each screen folder contains `index.html` (open in a browser) and `README.md`.

---

## Screen inventory (12 screens)

| # | Screen | Desktop (web) | Mobile | Route / navigation | Minimum role |
|---|--------|---------------|--------|--------------------|--------------|
| 01 | Landing Page | ✅ `landing-page/` | — (no landing on mobile) | `/landing` | Public |
| 02 | Authentication | ✅ `authentication/` | ✅ `authentication/` | `/login` (+ recovery flow) | Public (guest) |
| 03 | Product Guide | ✅ `guide/` | ✅ `guide/` | `/guide` | Public |
| 04 | Environmental Dashboard | ✅ `environmental-dashboard/` | ✅ `environmental-dashboard/` | `/dashboard` | USER |
| 05 | Educational Environments | ✅ `educational-environments/` | ✅ `educational-environments/` | `/all-environments`, `/environment/:id` | USER |
| 06 | Saved Environments | ✅ `saved-environments/` | ✅ `saved-environments/` | `/favorites` | USER |
| 07 | Environment Administration | ✅ `environment-administration/` | ✅ `environment-administration/` | `/management` | ADMIN |
| 08 | Super Admin Panel | ✅ `super-admin/` | ✅ `super-admin/` | `/admin/institutions` | SUPER_ADMIN |
| 09 | Alert Notifications | ✅ `alert-notifications/` (side panel) | ✅ `alert-notifications/` (screen) | panel / `NotificationsPanel` | USER |
| 10 | User Profile | ✅ `user-profile/` | ✅ `user-profile/` | `/profile` | USER |
| 11 | User Settings | ✅ `user-settings/` | ✅ `user-settings/` | `/settings` | USER |
| 12 | Device Provisioning (BLE) | — (mobile only) | ✅ `provisioning/` | `Provisioning` stack screen | ADMIN |

Total: **11 desktop + 11 mobile = 22 mockups** covering the 12 screens
(two screens are platform-specific: landing is web-only, provisioning is mobile-only).

---

## How to use

1. Open `index.html` in any screen folder (desktop mockups render at any width;
   mobile mockups render inside a 375 px device frame).
2. To change layout, edit the HTML; adjust tokens only in `shared/mockup.css`
   and mirror any change in the real `index.css` / `tokens.js`.
3. Captures for documentation go to `mockups/exports/` (see `exports/README.md`).

---

## Tech stack

- HTML5 + one shared CSS file (`shared/mockup.css`) with the product tokens.
- No build step, no CDN, no JavaScript — everything renders offline.

---

## Navigation flow

```
Landing Page ─▶ Authentication ─▶ Environmental Dashboard
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
Educational Environments      Saved Environments        Alert Notifications
        │                                                        │
        ▼                                                        ▼
Environment Detail ◀─────────────────────────────────────────────┘
        │
        ▼
Environment Administration (ADMIN) ─▶ Device Provisioning (mobile, ADMIN)
Super Admin Panel (SUPER_ADMIN): institutions + users/roles
User Profile ─▶ User Settings (theme, language, accessibility)
Product Guide: reachable from landing and from the auth stack (mobile)
```

---

## Correlations

- Domain contexts → `02-domain/domain-map.md`
- Navigation map → `12-ux-ui/navigation-map.md`
- Wireframes → `12-ux-ui/wireframes.md`
- Design system → `12-ux-ui/design-system.md`
