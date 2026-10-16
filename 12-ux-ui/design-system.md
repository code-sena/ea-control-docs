# Design System

> The design system is the shared visual language between design and development.
> It prevents inconsistencies, accelerates design, and reduces rework.
> **Rule:** Before creating a new component, check here if it already exists.
>
> **Source of truth:** the values below are extracted from the real code:
> `ea-control-frontend/apps/web/src/index.css` (CSS custom properties),
> `apps/web/src/shared/styles/design-system.css` (component classes `.ds-*`) and
> `apps/mobile/.../src/shared/styles/tokens.js` (mobile tokens, kept 1:1 with the web).
> When code and this file disagree, **trust the code** and update this file.

---

## Design tokens

Tokens are the design system's variables. Changing a token changes the entire system.

### Colors — accent (light theme)

The product accent is a green that evokes clean air. It is the default theme.

```css
--accent:          #01805b;   /* Primary buttons, links, active nav */
--accent-rgb:      1 128 91;  /* For alpha derivations: rgb(var(--accent-rgb) / 0.22) */
--accent-hover:    #016d4d;
--accent-light:    #e8faf5;   /* Tinted surfaces, soft backgrounds */
--accent-dark:     #00513d;
--border-nav:      var(--accent);
```

### Colors — semantic

```css
--color-success:   #368139;   /* Green — success, confirmed */
--color-warning:   #9d6602;   /* Amber — caution, pending */
--color-danger:    #d63030;   /* Red — error, cancelled */
--color-info:      #3376b0;   /* Blue — neutral information */
```

### Colors — text and surfaces (light theme)

```css
/* Text */
--text-primary:    #111827;
--text-secondary:  #374151;
--text-muted:      #4b5563;
--text-nav:        #1f2937;

/* Backgrounds */
--bg-body:         #f0fafa;
--bg-card:         #ffffff;
--bg-input:        #ffffff;
--bg-field-icon:   #f0fafa;
--bg-subtle:       #f3f6f6;
--bg-nav:          #ffffff;

/* Borders */
--border-color:    #d1d5db;
--border-card:     #e5e7eb;
--border-nav:      var(--accent);
```

### Dark mode (`body.dark-mode`)

Dark mode is a first-class theme, not an inversion. It also follows the
`prefers-color-scheme` media query when the user has not chosen explicitly.

```css
--bg-body:         #0a0f1e;
--bg-card:         #040f23;
--bg-input:        #1a2540;
--bg-field-icon:   #1a2540;
--bg-subtle:       #162035;
--bg-nav:          #060c1a;

--text-primary:    #f1f5f9;
--text-secondary:  #cbd5e1;
--text-muted:      #94a3b8;
--text-nav:        #e2e8f0;

--border-color:    #2d3f5c;
--border-card:     #1e2d45;

--color-success:   #4ca649;
--color-warning:   #ffc107;
--color-danger:    #f23838;
--color-info:      #5aa9e6;
```

### Color accessibility themes (color blindness)

Only the **accent** changes; glass surfaces derive from `--accent-rgb`, so they
adapt automatically in light and dark modes.

| Theme (`body` class) | Light accent | Dark accent | Condition |
|----------------------|--------------|-------------|-----------|
| *(default)* | `#01805b` | `#3cc99a` | — |
| `theme-protanopia` | `#007aa7` | `#2aa5d1` | Red–green (protan) |
| `theme-deuteranopia` | `#4f7e00` | `#7fbf3f` | Red–green (deutan) |
| `theme-tritanopia` | `#5b4b8a` | `#a99bf0` | Blue–yellow (tritan) |

### Glass surfaces (cards, side panels)

```css
--lb-glass-bg:          rgba(255, 255, 255, 0.78);
--lb-glass-bg-hover:    rgba(255, 255, 255, 0.94);
--lb-glass-border:      rgb(var(--accent-rgb) / 0.22);
--lb-glass-border-hover:rgb(var(--accent-rgb) / 0.52);
--lb-glass-blur:        blur(16px);
--lb-glass-shadow:      0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.06);
--lb-text-primary:      #0f172a;
--lb-text-muted:        #64748b;
--lb-text-pill:         #334155;
--lb-surface:           rgb(var(--accent-rgb) / 0.08);   /* pills, tracks */
--lb-track-bg:          rgba(0, 0, 0, 0.06);
```

### Typography

```css
/* Family (web) */
font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;

/* Accessibility base size (user-scalable: 16 / 18 / 20 px) */
--a11y-font-size: 16px;

/* Relative sizes in components */
page title:      calc(var(--a11y-font-size) * 1.25)   /* ~20px */
section title:   calc(var(--a11y-font-size) * 1)      /* 16px */
label / helper:  calc(var(--a11y-font-size) * 0.8125) /* ~13px */
stat number:     28px                                  /* dashboard cards */
card title:      18px
```

Weights in use: `400` (regular), `600` (labels, nav), `700` (titles).

### Spacing (4px-ish system)

```css
--space-xs:  6px;
--space-sm:  12px;
--space-md:  20px;
--space-lg:  32px;
--space-xl:  48px;
```

Mobile mirrors the same scale in `tokens.js`: `SPACE = { xs: 6, sm: 12, md: 20, lg: 32, xl: 48 }`.

### Borders, radii and shadows

```css
/* Radius — mobile RADII is 1:1 */
--radius-sm:   10px;
--radius-md:   16px;
--radius-lg:   20px;
--radius-xl:   28px;
--radius-full: 999px;    /* pill */

/* Shadows */
--shadow-card: 0 2px 10px rgba(0, 0, 0, 0.08);
--shadow-nav:  0 2px 5px rgba(0, 0, 0, 0.1);
--shadow-sm:   0 2px 8px rgba(0, 0, 0, 0.07);
--shadow-md:   0 6px 20px rgba(0, 0, 0, 0.1);
--shadow-lg:   0 12px 40px rgba(0, 0, 0, 0.14);
--shadow-xl:   0 20px 60px rgba(0, 0, 0, 0.18);
```

### Stacking order (z-index)

Fixed so panels, modals and toasts never fight each other.

```css
--z-panel:   100;   /* side panels: notifications, filters */
--z-modal:   200;   /* modals and dialogs */
--z-tooltip: 300;   /* tooltips, above the modal that contains them */
--z-toast:   400;   /* transient messages, always visible */
--z-loading: 500;   /* loading overlay, just below toasts */
```

---

## Components

Implemented as the `.ds-*` class family in `design-system.css` (web) and styled
components in `tokens.js`/`*.styles.js` (mobile). Reuse them before creating new ones.

### Buttons

| Class / variant | Use | Mobile token |
|-----------------|-----|--------------|
| `.ds-btn--primary` | Main action on the page | `accentButton` |
| `.ds-btn--outline` | Secondary actions | border + accent text |
| `.ds-btn--danger` | Destructive actions (delete) | `errorButton` (`#b42318`) |
| `.ds-btn--ghost` | Tertiary actions, links | transparent |
| `.ds-btn--sm` / `.ds-btn--lg` | Density variants | — |
| `.ds-btn-icon` | Icon-only actions (close, edit) | — |

**Usage rules:**
- Only one Primary action per view.
- Danger only with modal confirmation ("Are you sure?").
- Buttons have a loading state for async operations.

### Forms

| Class | When to use |
|-------|-------------|
| `.ds-field` + `.ds-field__label` | Field wrapper with label |
| `.ds-input` | Single-line text / select |
| `.ds-input--error` + `.ds-field__error` | Invalid field + inline message |
| `Checkbox`, `Input`, `Modal` (shared components) | Binary option, text entry, dialogs |

**Error messages in forms:**
- The message appears below the field, in `--color-danger`.
- The field border turns red.
- The message says how to fix the error, not just that it is an error.

```
✓ "The email must have the format user@domain.com"
✗ "Invalid email"
```

### Feedback

| Component | When | Notes |
|-----------|------|-------|
| `Toast` (shared) | Action confirmations / errors | z-index 400, ~4 s |
| `.ds-overlay` + `.ds-modal` (+ `--sm`/`--lg`) | Destructive confirmations, forms | `.ds-modal__close`, z-index 200 |
| `.ds-overlay--side` + `.ds-panel` | Notification center, filters | z-index 100 |
| `Spinner` / `LoadingScreen` | Operations > 200 ms | z-index 500 |
| `EmptyState` | Empty lists / no results | illustration + message + CTA |

### Cards and layout

| Class | Use |
|-------|-----|
| `.ds-card` (+ `--sm`/`--lg`/`--hero`/`--section`/`--hoverable`) | Content containers |
| `.ds-card--stat` | Dashboard metric cards (28px number) |
| `.ds-container` (+ `--narrow`/`--wide`) | Page width wrappers |
| `.ds-page` / `.ds-page-bg` / `.ds-page-header` | Page shell with title, subtitle, icon |
| `.ds-grid-2` / `-3` / `-4`, `.ds-flex*` | Layout helpers |
| `.ds-badge` (`--normal`/`--warning`/`--alert`/`--accent`) | Status pills (air quality) |
| `.ds-dot` (same modifiers) | Status dots |
| `.ds-divider`, `.ds-truncate` | Visual helpers |

Animations: `.ds-anim-fade`, `.ds-anim-rise` (`-1..-4` stagger), `.ds-anim-scale`.

### Accessibility widget

Standalone control (landing and app) that switches: font size (16/18/20 px),
dark mode and color-blindness theme. Persisted in `localStorage` under
`a11y-font-size`, `darkMode`, `a11y-color-theme` (see
`shared/accessibility/accessibilitySettings.js`).

---

## UX patterns

### Principles

1. **Confirm before destroying:** Any action that permanently deletes or modifies data requires a confirmation modal.
2. **Immediate feedback:** Every action must have a visual response in < 100 ms (even if it is just the loading state).
3. **Prevent rather than correct:** Validate in real time in the form, not only on submit.
4. **Empty state as a feature:** The screen without data is the new user's first impression — guide them to the first action.

### Error handling

| Scenario | What to show |
|----------|-------------|
| Network error | Toast "No connection. Retrying..." with automatic retry |
| 401 error | Redirect to login with message "Your session expired" |
| 403 error | Screen "You do not have permission to view this" with link to support |
| 404 error | 404 screen with back navigation (`NotFoundScreen`) |
| 500 error | Error toast + "Retry" button |
| Timeout | Toast "This is taking longer than normal" with cancel option |

---

## Accessibility guide (minimums)

| Aspect | Minimum required |
|--------|-----------------|
| Text contrast | WCAG AA (4.5:1 for normal text, 3:1 for large text) — enforced by the theme refactor |
| Keyboard navigation | All interactive elements accessible with Tab |
| Form labels | All fields with associated label (`for` / `aria-label`) |
| Images | Descriptive alt text on all non-decorative images |
| Visible focus | Visible focus indicator on all interactive elements |
| Font scaling | All text derived from `--a11y-font-size` (16/18/20 px) |
| Color independence | Status never by color alone: pair with badge text / dot + label |

---

## Platform notes

- **Web** (`apps/web`): CSS custom properties + `.ds-*` classes + shared components
  (`Button`, `Input`, `Modal`, `Toast`, `Spinner`, `EmptyState`, `Checkbox`).
- **Mobile** (`apps/mobile`): `tokens.js` keeps colors, radii, spacing and shadows
  **1:1 with the web tokens**; components are styled-components (`Button.styles.js`,
  `Input.styles.js`, …). Dark/light comes from `ThemeContext`, not from CSS.
- **Mockups** (`12-ux-ui/mockups/`): static HTML + Tailwind CDN that replicate these
  tokens for layout validation. They are *not* production code.

---

## Correlations

- Navigation map → `12-ux-ui/navigation-map.md`
- Wireframes → `12-ux-ui/wireframes.md`
- Mockups → `12-ux-ui/mockups/layout/`
- UX non-functional requirements → `04-requirements/non-functional.md`
