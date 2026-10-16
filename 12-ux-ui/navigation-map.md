# Navigation Map

> Defines the screen structure of the system, how screens connect to each other, and what routes
> exist. It is the reference when frontend and backend discuss what endpoints exist
> or how to reach a feature.
>
> **Source of truth:** extracted from the real code —
> `apps/web/src/App.jsx` (React Router) and
> `apps/mobile/.../App.js` + `src/navigation/AppNavigator.jsx` (React Navigation).
> Last reviewed against `develop` (commits through `fc8c9f2`).

---

## Platforms

| Platform | Router | Entry |
|----------|--------|-------|
| Web | `react-router-dom` `<Routes>` in `App.jsx` | `main.jsx` → `App` |
| Mobile | `@react-navigation` native stack + bottom tabs in `App.js` | `App.js` → `AppNavigator` |

**Roles in code:** `USER` (default), `ADMIN`, `SUPER_ADMIN`.
Route guards: `GuestRoute` (only unauthenticated), `ProtectedRoute` (any authenticated),
`AdminRoute` (`ADMIN` or `SUPER_ADMIN`), `SuperAdminRoute` (`SUPER_ADMIN` only).

> **Doc drift:** documents (SRS, test plan) also mention a `VIEWER` role. It is
> **not implemented** in the frontend — treat it as pending, not as a screen permission.

---

## Web route structure

```
/                           → redirect → /landing

Public (no authentication)
├── /landing                → Landing page (hero, value proposition, CTA)
├── /guide                  → Product guide (GuideScreen)
├── /login                  → Login / registration (panels: login | register)
│                              Social login: Google / Facebook (one-time code flow)
├── /signup                 → redirect → /login?panel=register
├── /forgot-password        → Request recovery code
├── /verify-code            → Enter recovery code
├── /change-password        → Set new password
└── /terms                  → Terms and conditions

Authenticated (ProtectedRoute)
├── /dashboard              → Environmental analysis dashboard
│                              + NotificationPanel (side panel, not a route)
├── /ranking                → redirect → /dashboard
├── /all-environments       → Educational environments list (filters, search)
├── /environment/:id        → Environment detail (metrics, sensors, recommendations)
├── /favorites              → Saved environments
├── /profile                → User profile
└── /settings               → User settings (preferences, accessibility, language)

Administration
├── /management             → Environment administration (AdminRoute)
│                              CRUD environments · campuses · sensors/variables · unlink device
└── /admin/institutions     → Super admin panel (SuperAdminRoute)
                               Institutions + users/roles management (merged screen)
    /admin/users            → redirect → /admin/institutions

Errors
└── *                       → NotFoundScreen (404)
```

## Mobile route structure

```
Auth stack (unauthenticated)
├── Login                   → Email + password (no company-code field)
├── SignUp                  → Registration
├── ForgotPassword          → Request recovery code
├── VerifyCode              → Enter recovery code
├── ChangePassword          → Set new password
├── Terms                   → Terms and conditions
└── Guide                   → Product guide

App (bottom tab navigator)
├── Tab: Dashboard
│   └── Stack: DashboardHome → EnvironmentDetail
│                            → NotificationsPanel (screen on mobile)
├── Tab: Favorites
│   └── Stack: FavoritesHome → EnvironmentDetail
│                            → NotificationsPanel
├── Tab: Management          [visible: ADMIN / SUPER_ADMIN]
│   └── Stack: ManagementHome → EnvironmentDetail
│                             → Provisioning (BLE device setup)
├── Tab: SuperAdmin          [visible: SUPER_ADMIN]
│   └── SuperAdminScreen (institutions + users/roles)
├── Tab: Environments
│   └── Stack: EnvironmentsHome → EnvironmentDetail
│                               → NotificationsPanel
└── Tab: Profile
    └── Stack: ProfileHome → Settings (preferences, language, theme, accessibility)
```

> **Asymmetry worth documenting:** on the web, notifications are a **side panel**
> (`NotificationPanel` component over any authenticated screen); on mobile they are
> a **pushed screen** (`NotificationsPanel`). Same feature, two navigation patterns.

---

## Screen map

| # | Screen | Web route | Mobile screen | Component | Minimum role | Backend service(s) |
|---|--------|-----------|---------------|-----------|--------------|--------------------|
| 01 | Landing Page | `/landing` | — (auth stack has `Guide`, not landing) | `Landing` | Public | — |
| 02 | Authentication | `/login`, `/forgot-password`, `/verify-code`, `/change-password`, `/terms` | `Login`, `SignUp`, `ForgotPassword`, `VerifyCode`, `ChangePassword`, `Terms` | `LoginScreen`, forms | Public (guest) | `authService` → `ms-security` via gateway |
| 03 | Product Guide | `/guide` | `Guide` | `GuideScreen` | Public | — |
| 04 | Environmental Dashboard | `/dashboard` | `DashboardHome` | `DashboardScreen` | USER | `environmentService`, `alertService` → monitoring |
| 05 | Educational Environments | `/all-environments`, `/environment/:id` | `EnvironmentsHome`, `EnvironmentDetail` | `AllEnvironmentsScreen`, `EnvironmentDetailScreen` | USER | `environmentService`, `sensorService`, `catalogService` |
| 06 | Saved Environments | `/favorites` | `FavoritesHome` | `FavoritesScreen` | USER | favorites → `ms-user-experience` |
| 07 | Environment Administration | `/management` | `ManagementHome` (+ `Provisioning`) | `EnvironmentManagement` | ADMIN | `environmentService`, `sensorService`, `catalogService` (+ BLE on mobile) |
| 08 | Super Admin Panel | `/admin/institutions` | `SuperAdmin` tab | `SuperAdminScreen` | SUPER_ADMIN | `adminService`, `institutionService` → `ms-user-management` |
| 09 | Alert Notifications | `NotificationPanel` (overlay) | `NotificationsPanel` (screen) | `NotificationPanel` / `NotificationsScreen` | USER | `alertService` → monitoring |
| 10 | User Profile | `/profile` | `ProfileHome` | `ProfileScreen` | USER | `profileService` → `ms-user-management` |
| 11 | User Settings | `/settings` | `Settings` | `SettingsScreen` | USER | `preferencesService` → `ms-user-experience` |
| 12 | Device Provisioning | — (mobile only) | `Provisioning` | `ProvisioningScreen` | ADMIN | BLE → ESP32, then `sensorService` |
| — | Not Found | `*` | — | `NotFoundScreen` | — | — |

---

## Access matrix

| Screen | Guest | USER | ADMIN | SUPER_ADMIN |
|--------|-------|------|-------|-------------|
| Landing, Guide, Terms | ✅ | ✅ | ✅ | ✅ |
| Login / recovery / register | ✅ | ↩ redirect to `/dashboard` | ↩ | ↩ |
| Environmental Dashboard | ❌ | ✅ | ✅ | ✅ |
| Educational Environments (list + detail) | ❌ | ✅ | ✅ | ✅ |
| Saved Environments | ❌ | ✅ | ✅ | ✅ |
| Alert Notifications | ❌ | ✅ | ✅ | ✅ |
| User Profile / Settings | ❌ | ✅ | ✅ | ✅ |
| Environment Administration | ❌ | ❌ | ✅ | ✅ |
| Super Admin Panel (institutions, users, roles) | ❌ | ❌ | ❌ | ✅ |
| Device Provisioning (BLE, mobile) | ❌ | ❌ | ✅ | ✅ |

---

## Main user flows

### F1 — Sign up and first login
```
Landing → /login (panel=register) → SignUpForm → verify email (out of band)
       → /login → LoginForm → /dashboard
```
Social variant: `/login` → Google/Facebook → backend OAuth2 (one-time code) → `/dashboard`.

### F2 — Password recovery
```
/login → /forgot-password → /verify-code → /change-password → /login
```

### F3 — Explore an environment
```
/dashboard → /all-environments → /environment/:id
     ↳ from detail: add to /favorites, open notifications panel
```

### F4 — Manage environments (ADMIN)
```
/nav → /management
  ├─ CRUD environments (Add/Edit/Delete modals)
  ├─ Campus management panel
  ├─ Sensor variables panel / unlink device
  └─ (mobile) Provisioning: BLE scan → configure ESP32 → attach to environment
```

### F5 — Super admin
```
/nav → /admin/institutions
  ├─ Institutions CRUD
  └─ Users + role assignment (USER / ADMIN / SUPER_ADMIN)
```

### F6 — Notification triage
```
Web:     any screen → NotificationPanel (side overlay) → /environment/:id
Mobile:  Dashboard/Favorites/Environments → NotificationsPanel → EnvironmentDetail
```

### F7 — Preferences and accessibility
```
/profile → /settings (web) · ProfileHome → Settings (mobile)
  ├─ Language (es / en / pt / fr)
  ├─ Theme (light / dark / system)
  ├─ Color accessibility (protanopia / deuteranopia / tritanopia)
  └─ Font size (16 / 18 / 20 px)
```

---

## Redirects and aliases

| From | To | Why |
|------|----|-----|
| `/` | `/landing` | Landing is the public entry point |
| `/signup` | `/login?panel=register` | Register is a panel inside the auth screen |
| `/ranking` | `/dashboard` | Legacy URL kept for old links |
| `/admin/users` | `/admin/institutions` | User management merged into the super admin panel |

---

## Correlations

- Design system → `12-ux-ui/design-system.md`
- Wireframes → `12-ux-ui/wireframes.md`
- Mockups → `12-ux-ui/mockups/layout/`
- Domain contexts → `02-domain/domain-map.md`
- User stories → `04-requirements/user-stories.md`
