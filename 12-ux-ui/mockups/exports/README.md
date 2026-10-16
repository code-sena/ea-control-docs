# Mockup exports (PNG)

Captures of the layout mockups in `../layout/`, used as figures in the project
documentation (`05_Diseno_Software`, "Graphical interfaces" section).

```
exports/
├── desktop/   ← 1280 px viewport, 2× scale
└── mobile/    ← 375 px device frame, 2× scale
```

Regenerate after changing any mockup:

```bash
python3 -m venv /tmp/shotvenv && /tmp/shotvenv/bin/pip install playwright
/tmp/shotvenv/bin/python -m playwright install chromium
/tmp/shotvenv/bin/python shoot_mockups.py   # script: renders every index.html
```

Rules:
- A capture must never show real personal data — mockups use illustrative values.
- File name = screen slug (same as its `layout/<platform>/<slug>/` folder).
- Keep the capture set complete: one PNG per mockup (11 desktop + 11 mobile).
