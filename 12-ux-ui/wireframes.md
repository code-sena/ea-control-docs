# Wireframes

> Low-fidelity designs of the main screens: structure, not colors.
> The visual language lives in `design-system.md`; the navigation rules in
> `navigation-map.md`. Wireframes here describe **layout regions and content
> blocks** validated against the implemented screens (`apps/web`, `apps/mobile`).
>
> Conventions: `[ Button ]` actions · `#` headings · `···` text blocks ·
> `┌─ ─┐` regions · `▤` tables/lists · `◔` charts · `⚙` widgets.

---

## 01 — Landing Page (web, `/landing`)

```
┌──────────────────────────────────────────────────────────────┐
│ Navbar:  Logo · ¿Por qué? · Guía · Precios · [ Iniciar sesión ]│
├──────────────────────────────────────────────────────────────┤
│  # Aire limpio para aprender mejor                           │
│  ··· propuesta de valor (2 líneas)                           │
│  [ Comenzar ]  [ Ver guía ]                                  │
│  ◔ hero visual (aula + métricas)                             │
├──────────────────────────────────────────────────────────────┤
│  # ¿Por qué EduAirControl?                                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                        │
│  │tarifa│ │tarifa│ │tarifa│ │tarifa│  (features)            │
│  └──────┘ └──────┘ └──────┘ └──────┘                        │
├──────────────────────────────────────────────────────────────┤
│  # Diseñado para                                            │
│  ┌──────┐ ┌──────┐ ┌──────┐   (perfiles: docente,          │
│  │persona│ │persona│ │persona│    coordinador, estudiante)  │
│  └──────┘ └──────┘ └──────┘                                 │
├──────────────────────────────────────────────────────────────┤
│  CTA final:  # Empieza hoy  [ Crear cuenta ]                │
├──────────────────────────────────────────────────────────────┤
│  Footer: logo · links · redes · © EduAirControl             │
│  ⚙ AccessibilityWidget (font size · theme · color themes)   │
└──────────────────────────────────────────────────────────────┘
```

---

## 02 — Authentication (web `/login` + recovery · mobile auth stack)

```
┌─────────────────────────────┐   Mobile: same blocks stacked,
│  Logo                       │   one panel per screen
│  ┌─────────┐ ┌─────────┐    │   (Login · SignUp · ForgotPassword
│  │ Ingresar│ │Registro │    │    · VerifyCode · ChangePassword
│  └─────────┘ └─────────┘    │    · Terms)
│  # Bienvenido de nuevo      │
│  Correo     [____________]  │
│  Contraseña [____________]  │
│  ☐ Recordarme  ¿Olvidaste?  │
│  [ Iniciar sesión ]         │
│  ── o continúa con ──       │
│  ( G ) ( f )                │   Google / Facebook → one-time code
│  ¿No tienes cuenta? Regístrate│
└─────────────────────────────┘
```

Recovery flow screens: `forgot-password` (email) → `verify-code` (6-digit) →
`change-password` (new + confirm) → back to login.

---

## 03 — Product Guide (web `/guide` · mobile `Guide`)

```
┌──────────────────────────────────────────────────────────────┐
│  ← Volver        # Guía de producto                          │
├──────────────────────────────────────────────────────────────┤
│  [ 1. Qué es ] [ 2. Sensores ] [ 3. Cómo funciona ] [ 4. FAQ]│
├──────────────────────────────────────────────────────────────┤
│  # Sección activa                                           │
│  ··· explicación breve                                      │
│  ┌────────────────────────────┐                             │
│  │   ilustración / captura    │                             │
│  └────────────────────────────┘                             │
│  ··· pasos numerados                                        │
│  [ Siguiente sección ]                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 04 — Environmental Dashboard (`/dashboard` · `DashboardHome`)

```
┌──────────────────────────────────────────────────────────────┐
│ Navbar: Logo · Dashboard · Ambientes · ⚙mgto · 🔔(panel) · 👤│
├──────────────────────────────────────────────────────────────┤
│  # Panel ambiental            [ periodo: hoy ▾ ]  [ 🌙 ]     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                │
│  │ Calidad│ │  CO₂   │ │  Temp  │ │  Hum   │  stat cards    │
│  │  87    │ │ 612ppm │ │ 22.4°  │ │  48%   │  + badge estado│
│  └────────┘ └────────┘ └────────┘ └────────┘                │
│  ┌───────────────────────────────┐ ┌───────────────────────┐ │
│  │ ◔ Serie temporal (24 h)      │ │ # Recomendaciones      │ │
│  │   temp · CO₂ · humedad       │ │ ··· ··· ···            │ │
│  └───────────────────────────────┘ └───────────────────────┘ │
│  # Ambientes monitorizados      [ Ver todos ]                │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                        │
│  │ card │ │ card │ │ card │ │ card │  (top 4)               │
│  └──────┘ └──────┘ └──────┘ └──────┘                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 05 — Educational Environments (`/all-environments` · `/environment/:id`)

### 5a — List

```
┌──────────────────────────────────────────────────────────────┐
│  # Ambientes educativos                                      │
│  [ 🔍 buscar________ ]  [ sede ▾ ] [ estado ▾ ] [ orden ▾ ]  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│  │ card │ │ card │ │ card │ │ card │ │ card │ │ card │ grid │
│  │ ★    │ │      │ │ ★    │ │      │ │      │ │ ★    │      │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘      │
│  [ Cargar más ]                          EmptyState si 0     │
└──────────────────────────────────────────────────────────────┘
```

### 5b — Detail

```
┌──────────────────────────────────────────────────────────────┐
│  ← Ambientes   # Aula 204 · Sede Norte   [ ★ favorito ]      │
│  badge: ● Calidad buena          [ 🔔 alertas ]              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                │
│  │ score  │ │  CO₂   │ │  Temp  │ │  Hum   │                │
│  └────────┘ └────────┘ └────────┘ └────────┘                │
│  ┌───────────────────────────────┐ ┌───────────────────────┐ │
│  │ ◔ Histórico [24h|7d|30d]     │ │ # Sensores instalados │ │
│  └───────────────────────────────┘ │ ▤ DHT11 · KY-038 ···  │ │
│                                    │ # Recomendaciones      │ │
│                                    └───────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 06 — Saved Environments (`/favorites` · `FavoritesHome`)

```
┌──────────────────────────────────────────────────────────────┐
│  # Mis favoritos                                             │
│  ┌──────┐ ┌──────┐ ┌──────┐                                  │
│  │ card │ │ card │ │ card │  (mismas EnvironmentCard)        │
│  │ ★    │ │ ★    │ │ ★    │                                  │
│  └──────┘ └──────┘ └──────┘                                  │
│  EmptyState: "Aún no tienes favoritos" [ Explorar ambientes ] │
└──────────────────────────────────────────────────────────────┘
```

---

## 07 — Environment Administration (`/management` · `ManagementHome`, ADMIN)

```
┌──────────────────────────────────────────────────────────────┐
│  # Administración de ambientes                               │
│  [ + Nuevo ambiente ]   [ Sedes ]  [ Sensores ]               │
│  ┌─────────────────────────────┐ ┌─────────────────────────┐ │
│  │ ▤ Lista de ambientes        │ │ Panel contextual        │ │
│  │   Aula 204    [✎] [🗑]     │ │ (según pestaña)         │ │
│  │   Lab 2       [✎] [🗑]     │ │ · CampusManagementPanel │ │
│  │   Biblioteca  [✎] [🗑]     │ │ · SensorVariablePanel   │ │
│  └─────────────────────────────┘ │ · desvincular dispositivo│ │
│  Modales: Add · Edit · Delete    └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

Mobile adds the **Provisioning** screen from here (see 12).

---

## 08 — Super Admin Panel (`/admin/institutions` · `SuperAdmin` tab)

```
┌──────────────────────────────────────────────────────────────┐
│  # Panel super administrador                                 │
│  [ Instituciones ] [ Usuarios y roles ]                      │
│  ┌─────────────────────────────┐ ┌─────────────────────────┐ │
│  │ ▤ Instituciones             │ │ ▤ Usuarios              │ │
│  │   SENA Neiva   [✎] [🗑]    │ │  correo · rol ▾ · sede  │ │
│  │   I.E. San José [✎] [🗑]   │ │  rol: USER|ADMIN|S_ADMIN│ │
│  └─────────────────────────────┘ └─────────────────────────┘ │
│  [ + Institución ]  [ + Usuario ]                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 09 — Alert Notifications (web side panel · mobile screen)

```
Web overlay (right side panel)            Mobile (full screen)
┌─────────────────────┐                 ┌──────────────────────────┐
│ ✕ Notificaciones    │                 │  ←  # Notificaciones     │
│ [ Todas | No leídas ]│                 │  [ Todas | No leídas ]   │
│ ┌─────────────────┐ │                 │  ┌────────────────────┐  │
│  │ ● CO₂ alto      │ │                 │  │ ● CO₂ alto Aula 204│  │
│  │   Aula 204 · 10:32│ │               │  │   10:32  [ marcar ] │  │
│  ├─────────────────┤ │                 │  ├────────────────────┤  │
│  │ ● Calidad mejora│ │                 │  │ ● Calidad mejora   │  │
│  │   Lab 2 · 09:15 │ │                 │  │   Lab 2 · 09:15    │  │
│  └─────────────────┘ │                 │  └────────────────────┘  │
│  [ Ver todas ]       │                 │  tap → EnvironmentDetail │
└─────────────────────┘                 └──────────────────────────┘
```

---

## 10 — User Profile (`/profile` · `ProfileHome`)

```
┌──────────────────────────────────────────────────────────────┐
│  # Mi perfil                                                │
│  ┌──────┐   Nombre     [________________]                   │
│  │ avatar│  Correo     (no editable)                         │
│  └──────┘   Institución (no editable)                        │
│             Sede        (no editable)                        │
│             [ Guardar cambios ]                              │
│  # Seguridad                                                │
│  [ Cambiar contraseña ]  [ Cerrar sesiones ]                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 11 — User Settings (`/settings` · `Settings`)

```
┌──────────────────────────────────────────────────────────────┐
│  # Configuración                                            │
│  # Apariencia                                               │
│   Tema        ( ○ Claro  ○ Oscuro  ○ Sistema )               │
│   Idioma      [ Español ▾ ]  (es · en · pt · fr)             │
│  # Accesibilidad                                            │
│   Texto       ( ○ 16px  ○ 18px  ○ 20px )                     │
│   Color       ( ○ Normal  ○ Protanopia  ○ Deuteranopia       │
│                  ○ Tritanopia )                              │
│  # Preferencias                                             │
│   Notificaciones  [🔔 on/off]  Zona horaria [ América/Bogotá ▾ ]│
│  [ Guardar ]                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 12 — Device Provisioning (mobile `Provisioning`, ADMIN)

```
┌──────────────────────────────────────┐
│  ←  # Vincular sensor (ESP32)        │
│  1. Escaneo BLE                      │
│     ┌────────────────────────────┐   │
│     │ ▤ dispositivos cercanos    │   │
│     │   EA-Sensor-01   [conectar]│   │
│     │   EA-Sensor-02   [conectar]│   │
│     └────────────────────────────┘   │
│  2. Configuración                    │
│     Wi-Fi   [____________]           │
│     Clave   [____________]           │
│  3. Asociar                          │
│     Ambiente [ Aula 204 ▾ ]          │
│     [ Enviar configuración ]         │
│  ● estado: escaneando | enviando |   │
│            vinculado | error         │
└──────────────────────────────────────┘
```

---

## Shared patterns

- **Navbar (web)** on all authenticated screens: logo · nav links · notifications
  icon (panel) · user menu. **Bottom tabs (mobile)** per the access matrix.
- **EnvironmentCard** is reused in screens 04, 05a, 06 (list) — one component,
  three contexts.
- **EmptyState / Spinner / Toast** appear in every list screen.
- **Modals** (`Add/Edit/Delete`) belong to screens 07 and 08.

---

## Correlations

- Navigation map → `12-ux-ui/navigation-map.md`
- Design system → `12-ux-ui/design-system.md`
- High-fidelity mockups → `12-ux-ui/mockups/layout/`
