"""Genera EduAirControl_Arquitectura.pptx (4 slides, 16:9, formas editables).

Uso: python generar_arquitectura_pptx.py
Salida: <raíz del proyecto>/EduAirControl_Arquitectura.pptx
Fuente de contenido: Docs-ea-control/05-architecture/overview.md
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# ---------------------------------------------------------------- paleta
NAVY = RGBColor(0x0F, 0x2A, 0x43)
BLUE = RGBColor(0x1F, 0x6F, 0xB2)
BLUE_LIGHT = RGBColor(0xDA, 0xE7, 0xF4)
CYAN = RGBColor(0x11, 0x9E, 0x99)
CYAN_LIGHT = RGBColor(0xD8, 0xF0, 0xEF)
ORANGE = RGBColor(0xDD, 0x77, 0x35)
ORANGE_LIGHT = RGBColor(0xFA, 0xE7, 0xD7)
GREY = RGBColor(0x53, 0x64, 0x74)
GREY_LIGHT = RGBColor(0xF1, 0xF4, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT = RGBColor(0x1E, 0x2A, 0x35)
FONT = "Segoe UI"

SW, SH = 13.333, 7.5  # tamaño de diapositiva (16:9)


# ---------------------------------------------------------------- helpers
def set_lines(tf, lines, align=PP_ALIGN.CENTER, space_after=2):
    """lines: lista de (texto, tamaño, bold, color)."""
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    for i, (text, size, bold, color) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = FONT


def add_box(slide, x, y, w, h, lines, fill, line=None,
            shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is not None:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    if shape in (MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.RECTANGLE):
        try:
            sh.adjustments[0] = 0.09
        except (IndexError, ValueError):
            pass
    if lines:
        set_lines(sh.text_frame, lines, align=align)
    return sh


def add_arrow(slide, x, y, w, h, direction="down", color=GREY):
    shape = {
        "down": MSO_SHAPE.DOWN_ARROW,
        "right": MSO_SHAPE.RIGHT_ARROW,
        "left": MSO_SHAPE.LEFT_ARROW,
    }[direction]
    return add_box(slide, x, y, w, h, None, color, shape=shape)


def add_text(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    set_lines(tb.text_frame, lines, align=align, space_after=3)
    return tb


def title_bar(slide, title, subtitle=None):
    add_box(slide, 0, 0, SW, 0.85, None, NAVY, shape=MSO_SHAPE.RECTANGLE)
    lines = [(title, 24, True, WHITE)]
    add_text(slide, 0.5, 0.05, 9.5, 0.75, lines, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, 9.6, 0.05, 3.3, 0.75,
                 [(subtitle, 11, False, RGBColor(0xA8, 0xC4, 0xDE))],
                 align=PP_ALIGN.RIGHT)


def new_slide(prs, bg=WHITE, title=None, subtitle=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = bg
    if title:
        title_bar(slide, title, subtitle)
    return slide


# ---------------------------------------------------------------- slide 1
def slide_portada(prs):
    s = new_slide(prs, bg=NAVY)
    add_box(s, 1.0, 2.45, 11.33, 0.06, None, RGBColor(0x2C, 0xA6, 0xA4),
            shape=MSO_SHAPE.RECTANGLE)
    add_text(s, 1.0, 2.7, 11.33, 1.6,
             [("EduAirControl", 48, True, WHITE),
              ("Arquitectura del Sistema", 30, False, RGBColor(0x9F, 0xD6, 0xD4))],
             align=PP_ALIGN.LEFT)
    add_text(s, 1.0, 4.55, 11.33, 1.2,
             [("Microservicios + API Gateway + Event-Driven (RabbitMQ)", 16, True,
               RGBColor(0xDC, 0xE6, 0xEF)),
              ("Migración strangler-fig desde monolito · cada servicio con arquitectura hexagonal",
               14, False, RGBColor(0xA8, 0xC4, 0xDE))],
             align=PP_ALIGN.LEFT)
    add_text(s, 1.0, 6.5, 11.33, 0.6,
             [("Fuente: Docs-ea-control/05-architecture/overview.md  ·  Octubre 2026",
               11, False, RGBColor(0x7E, 0x99, 0xB3))],
             align=PP_ALIGN.LEFT)


# ---------------------------------------------------------------- slide 2
def slide_arquitectura(prs):
    s = new_slide(prs, GREY_LIGHT, "Arquitectura general", "C4 · nivel contenedor")

    # ---- columna izquierda: clientes -> gateway -> microservicios -> BD
    add_box(s, 0.6, 1.05, 6.6, 0.7,
            [("Usuarios · Frontend React (web) + React Native (móvil)", 13, True, WHITE)],
            BLUE)
    add_arrow(s, 3.65, 1.78, 0.5, 0.3)

    add_box(s, 0.6, 2.1, 6.6, 0.7,
            [("API Gateway · Spring Cloud Gateway  ·  :8080", 14, True, WHITE),
             ("Validación JWT (JWKS) · rate limit (Redis) · correlation IDs", 10, False,
              RGBColor(0xDA, 0xE7, 0xF4))],
            NAVY)
    add_arrow(s, 3.65, 2.8, 0.5, 0.3)

    container = add_box(s, 0.6, 3.1, 6.6, 2.7, None, WHITE, line=BLUE)
    container.text_frame.text = ""
    add_text(s, 0.7, 3.13, 6.4, 0.32,
             [("Microservicios Spring Boot · arquitectura hexagonal (domain / application / infrastructure)",
               9, True, BLUE)], align=PP_ALIGN.CENTER)

    servicios = [
        ("ms-security", ":8081 · OAuth2 · JWT RS256"),
        ("ms-user-management", ":3007 · perfiles"),
        ("ms-classroom-management", ":3002 · aulas y campus"),
        ("ms-user-experience", ":3006 · preferencias"),
        ("ms-sensor-management", ":3004 · sensores (outbox)"),
        ("ms-environment-monitoring", ":3003 · medición y alertas"),
    ]
    xs = (0.75, 3.95)
    ys = (3.5, 4.23, 4.96)
    for i, (name, sub) in enumerate(servicios):
        x = xs[i % 2]
        y = ys[i // 2]
        add_box(s, x, y, 3.1, 0.62,
                [(name, 11, True, NAVY), (sub, 8.5, False, GREY)],
                BLUE_LIGHT, line=BLUE)

    add_arrow(s, 3.65, 5.85, 0.5, 0.3)
    add_box(s, 0.6, 6.2, 6.6, 0.72,
            [("PostgreSQL 15 ×6", 13, True, NAVY),
             ("una instancia por servicio (Database-per-Service)", 10, False, GREY)],
            WHITE, line=BLUE)

    # ---- Redis (al lado del gateway)
    add_arrow(s, 7.26, 2.3, 0.32, 0.28, direction="right", color=CYAN)
    add_box(s, 7.62, 2.1, 1.58, 0.7,
            [("Redis", 12, True, WHITE),
             ("rate limit · sesiones · deny-list", 8, False, CYAN_LIGHT)],
            CYAN)

    # ---- columna derecha: IoT -> monolito -> RabbitMQ
    add_box(s, 9.35, 1.05, 3.4, 0.7,
            [("ESP32 / IoT", 13, True, WHITE),
             ("HTTP + X-API-Key", 9, False, ORANGE_LIGHT)],
            ORANGE)
    add_arrow(s, 10.83, 1.78, 0.45, 0.3, color=ORANGE)

    add_box(s, 9.35, 2.1, 3.4, 0.95,
            [("Monolito legacy (strangler-fig)", 11, True, ORANGE),
             ("ingest IoT · outbox de mediciones", 9, False, GREY)],
            ORANGE_LIGHT, line=ORANGE)
    add_arrow(s, 10.83, 3.08, 0.45, 0.3, color=CYAN)

    add_box(s, 9.35, 3.42, 3.4, 0.85,
            [("RabbitMQ", 13, True, WHITE),
             ("topic exchange · outbox → DLQ", 9, False, CYAN_LIGHT)],
            CYAN)

    # eventos: RabbitMQ -> microservicios (consumidores)
    add_text(s, 7.3, 3.4, 2.0, 0.28,
             [("eventos", 9, True, CYAN)], align=PP_ALIGN.CENTER)
    add_arrow(s, 7.45, 3.68, 1.7, 0.34, direction="left", color=CYAN)

    # ---- notas columna derecha
    add_box(s, 9.35, 4.5, 3.4, 1.05,
            [("Migración por bounded contexts", 10.5, True, NAVY),
             ("cada servicio con responsabilidad y base de datos propia", 9, False, GREY)],
            WHITE, line=GREY)
    add_box(s, 9.35, 5.8, 3.4, 1.12,
            [("Transversal", 10.5, True, NAVY),
             ("Liquibase · /health · Swagger · errores {status,message} · logs SLF4J",
              9, False, GREY)],
            WHITE, line=GREY)


# ---------------------------------------------------------------- slide 3
def slide_catalogo(prs):
    s = new_slide(prs, WHITE, "Catálogo de microservicios",
                  "Fuente: overview.md §4")

    filas = [
        ("Servicio", "Puerto", "Base de datos", "Responsabilidad"),
        ("api-gateway", "8080", "Redis (rate/session)",
         "Punto de entrada: routing, JWT (JWKS), rate limit, correlation IDs"),
        ("ms-security", "8081", "PostgreSQL seguridad",
         "Registro, login OAuth2/OIDC, JWT RS256, tenants/instituciones"),
        ("ms-user-management", "3007", "PostgreSQL user_management",
         "Gestión y consulta de perfiles de usuario"),
        ("ms-classroom-management", "3002", "PostgreSQL classrooms",
         "Aulas, campus y tipos de ambiente educativo"),
        ("ms-sensor-management", "3004", "PostgreSQL sensors",
         "Sensores, variables e instalaciones; publica eventos (outbox)"),
        ("ms-environment-monitoring", "3003", "PostgreSQL environment_monitoring",
         "Mediciones, dashboard, análisis y alertas (consume RabbitMQ, CQRS)"),
        ("ms-user-experience", "3006", "PostgreSQL user_experience",
         "Preferencias, favoritos, ratings y experiencia de búsqueda"),
    ]
    widths = (3.0, 1.0, 3.0, 5.3)
    x, y = 0.5, 1.15
    total_w = sum(widths)
    total_h = 5.1
    table = s.shapes.add_table(len(filas), 4, Inches(x), Inches(y),
                               Inches(total_w), Inches(total_h)).table
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(w)

    for r, fila in enumerate(filas):
        table.rows[r].height = Inches(0.5 if r == 0 else 0.65)
        for c, valor in enumerate(fila):
            cell = table.cell(r, c)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r == 0:
                cell.fill.fore_color.rgb = NAVY
            else:
                cell.fill.fore_color.rgb = WHITE if r % 2 else GREY_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c == 1 else PP_ALIGN.LEFT
            run = p.add_run()
            run.text = valor
            run.font.name = FONT
            run.font.size = Pt(11.5 if r == 0 else 10.5)
            run.font.bold = r == 0 or c == 0
            run.font.color.rgb = WHITE if r == 0 else TEXT

    add_text(s, 0.5, 6.5, 12.3, 0.7,
             [("Infraestructura: 6 × PostgreSQL 15 (puertos 5433–5439) · RabbitMQ 5672 · Redis 6379 · despliegue con Docker Compose (ea-control-infra)",
               10.5, False, GREY),
              ("Comunicación: REST/HTTP síncrono (frontend → gateway → servicios) · RabbitMQ asíncrono (outbox → consumidores idempotentes + DLQ)",
               10.5, False, GREY)])


# ---------------------------------------------------------------- slide 4
def slide_flujo(prs):
    s = new_slide(prs, WHITE, "Flujo de datos ambientales y patrones")

    # fila 1: ESP32 -> outbox -> RabbitMQ
    add_box(s, 0.5, 1.3, 2.5, 1.1,
            [("ESP32 / IoT", 13, True, WHITE),
             ("HTTP + X-API-Key", 9.5, False, ORANGE_LIGHT)], ORANGE)
    add_arrow(s, 3.0, 1.7, 0.45, 0.3, direction="right", color=ORANGE)
    add_box(s, 3.45, 1.3, 2.5, 1.1,
            [("Monolito legacy", 13, True, ORANGE),
             ("outbox de mediciones", 9.5, False, GREY)], ORANGE_LIGHT, line=ORANGE)
    add_arrow(s, 5.95, 1.7, 0.45, 0.3, direction="right", color=CYAN)
    add_box(s, 6.4, 1.3, 2.5, 1.1,
            [("RabbitMQ", 13, True, WHITE),
             ("topic exchange · at-least-once", 9.5, False, CYAN_LIGHT)], CYAN)

    # enlace fila 1 -> fila 2
    add_arrow(s, 7.42, 2.42, 0.45, 0.55, direction="down", color=CYAN)

    # fila 2 (en sentido inverso): monitoring -> proyección -> dashboard
    add_box(s, 6.4, 3.0, 2.5, 1.1,
            [("ms-environment-monitoring", 11, True, NAVY),
             ("inbox idempotente (inbox table)", 9.5, False, GREY)],
            BLUE_LIGHT, line=BLUE)
    add_arrow(s, 5.95, 3.4, 0.45, 0.3, direction="left", color=BLUE)
    add_box(s, 3.45, 3.0, 2.5, 1.1,
            [("Proyección + umbrales", 12.5, True, NAVY),
             ("read model (CQRS) · alertas", 9.5, False, GREY)],
            BLUE_LIGHT, line=BLUE)
    add_arrow(s, 3.0, 3.4, 0.45, 0.3, direction="left", color=BLUE)
    add_box(s, 0.5, 3.0, 2.5, 1.1,
            [("Dashboard / API REST", 12, True, NAVY),
             ("consultas del frontend", 9.5, False, GREY)], BLUE_LIGHT, line=BLUE)

    # salida hacia el usuario
    add_arrow(s, 1.52, 4.15, 0.45, 0.38, direction="down", color=BLUE)
    add_box(s, 0.5, 4.6, 8.4, 0.75,
            [("API Gateway (:8080)  →  Frontend React / React Native  →  Usuario",
              13, True, NAVY)], GREY_LIGHT, line=BLUE)

    # concern transversal
    add_box(s, 0.5, 5.7, 8.4, 1.25,
            [("Transversal a todos los servicios", 12, True, WHITE),
             ("JWT / OAuth2 · rate limit Redis · correlation IDs · Liquibase · /health · Swagger (springdoc) · errores {status,message} · logs SLF4J",
              10.5, False, RGBColor(0xC8, 0xD8, 0xE8))],
            NAVY)

    # ---- columna derecha: patrones + despliegue
    add_box(s, 9.3, 1.3, 3.5, 0.5, [("Patrones clave", 14, True, WHITE)],
            NAVY, shape=MSO_SHAPE.RECTANGLE)
    patrones = [
        "Microservicios + API Gateway",
        "Arquitectura hexagonal (ports & adapters)",
        "Database-per-Service (PostgreSQL ×6)",
        "Transactional Outbox + inbox idempotente",
        "Event-driven RabbitMQ (at-least-once + DLQ)",
        "CQRS (read model en monitoring)",
        "OAuth2 / OIDC + JWT (RS256)",
        "API-First (OpenAPI · /api/v1)",
        "Strangler-fig (monolito → microservicios)",
    ]
    panel = add_box(s, 9.3, 1.8, 3.5, 3.4,
                    [(p, 11, False, TEXT) for p in patrones],
                    GREY_LIGHT, line=GREY, align=PP_ALIGN.LEFT)
    panel.text_frame.margin_left = Inches(0.15)
    for p in panel.text_frame.paragraphs:
        p.space_after = Pt(6)

    add_box(s, 9.3, 5.4, 3.5, 1.55,
            [("Despliegue", 13, True, WHITE),
             ("Docker Compose (ea-control-infra)", 10.5, True,
              RGBColor(0xC8, 0xD8, 0xE8)),
             ("7 contenedores + 6 PostgreSQL + RabbitMQ + Redis", 10, False,
              RGBColor(0xC8, 0xD8, 0xE8)),
             ("Overlay: Prometheus · Grafana · OpenTelemetry", 10, False,
              RGBColor(0xC8, 0xD8, 0xE8))],
            NAVY)


# ---------------------------------------------------------------- main
def main():
    raiz = Path(__file__).resolve().parents[3]
    salida = raiz / "EduAirControl_Arquitectura.pptx"

    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    prs.core_properties.title = "EduAirControl — Arquitectura del Sistema"
    prs.core_properties.author = "Generado desde Docs-ea-control/05-architecture"

    slide_portada(prs)
    slide_arquitectura(prs)
    slide_catalogo(prs)
    slide_flujo(prs)

    prs.save(salida)
    print(f"OK -> {salida} ({salida.stat().st_size} bytes, {len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
