"""
styles.py
Paleta de colores, helpers de fuente, factory de QLabel y renderizador SVG.
Importar desde cualquier widget de la UI.
"""

from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QFont, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel

# ── Paleta ────────────────────────────────────────────────────────────────────
SIDEBAR_BG     = "#1c201e"
SIDEBAR_ACTIVE = "#2d7a4f"
MAIN_BG        = "#f7f7f5"
CARD_BG        = "#ffffff"
CARD_BORDER    = "#e5e5e1"
GREEN          = "#2d7a4f"
GREEN_ICON_BG  = "#e0f2ea"
BLUE_ICON_BG   = "#e3eef9"
AMBER_ICON_BG  = "#faecd6"
AMBER_BG       = "#fdf6e3"
AMBER_BORDER   = "#e8d9a0"
BAR_TRACK      = "#e5e5e1"
TEXT_PRI       = "#111211"
TEXT_SEC       = "#74746e"

# ── Tipografía ────────────────────────────────────────────────────────────────
APP_FONT = "Outfit"   # fallback automático a Segoe UI si no está instalada


def font(size: int = 13, weight: QFont.Weight = QFont.Normal) -> QFont:
    f = QFont(APP_FONT, size)
    f.setWeight(weight)
    return f


# ── Helpers de widget ─────────────────────────────────────────────────────────

def make_label(
    text: str,
    size: int = 13,
    weight: QFont.Weight = QFont.Normal,
    color: str = TEXT_PRI,
    wrap: bool = False,
) -> QLabel:
    """Crea un QLabel con fuente y color aplicados."""
    w = QLabel(text)
    w.setFont(font(size, weight))
    w.setStyleSheet(f"color:{color}; background:transparent; border:none;")
    if wrap:
        w.setWordWrap(True)
    return w


def render_svg(svg_str: str, size: int = 18, color: str = "#ffffff") -> QPixmap:
    """
    Renderiza un string SVG como QPixmap.
    Usa el token FILL_COLOR dentro del SVG para inyectar el color deseado.
    """
    colored = svg_str.replace("FILL_COLOR", color)
    renderer = QSvgRenderer(QByteArray(colored.encode()))
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return pix