"""
sidebar.py
Sidebar de navegación: logo, NavButton por sección y selección activa.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)
from src.ui.styles import (
    SIDEBAR_BG, SIDEBAR_ACTIVE, GREEN,
    font, make_label, render_svg,
)

# ── SVGs de cada ítem de navegación ──────────────────────────────────────────
_ICONS: dict[str, str] = {
    "dashboard": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
        '<rect x="2" y="2" width="7" height="7" rx="1.5" fill="FILL_COLOR"/>'
        '<rect x="11" y="2" width="7" height="7" rx="1.5" fill="FILL_COLOR" opacity=".6"/>'
        '<rect x="2" y="11" width="7" height="7" rx="1.5" fill="FILL_COLOR" opacity=".6"/>'
        '<rect x="11" y="11" width="7" height="7" rx="1.5" fill="FILL_COLOR" opacity=".6"/>'
        '</svg>'
    ),
    "semana": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
        '<rect x="2" y="4" width="16" height="13" rx="2" stroke="FILL_COLOR" stroke-width="1.6"/>'
        '<path d="M2 8h16" stroke="FILL_COLOR" stroke-width="1.4"/>'
        '<path d="M7 2v3M13 2v3" stroke="FILL_COLOR" stroke-width="1.6" stroke-linecap="round"/>'
        '</svg>'
    ),
    "mensual": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
        '<rect x="2" y="4" width="16" height="13" rx="2" stroke="FILL_COLOR" stroke-width="1.6"/>'
        '<path d="M2 8h16M8 8v9M14 8v9M2 13h16" stroke="FILL_COLOR" stroke-width="1.3"/>'
        '<path d="M7 2v3M13 2v3" stroke="FILL_COLOR" stroke-width="1.6" stroke-linecap="round"/>'
        '</svg>'
    ),
    "trabajadores": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
        '<circle cx="10" cy="7" r="3.5" stroke="FILL_COLOR" stroke-width="1.6"/>'
        '<path d="M3 18c0-3.866 3.134-6 7-6s7 2.134 7 6" stroke="FILL_COLOR" '
        'stroke-width="1.6" stroke-linecap="round"/>'
        '</svg>'
    ),
    "clientes": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
        '<rect x="2" y="6" width="16" height="11" rx="2" stroke="FILL_COLOR" stroke-width="1.6"/>'
        '<path d="M6 6V5a4 4 0 0 1 8 0v1" stroke="FILL_COLOR" stroke-width="1.6" stroke-linecap="round"/>'
        '</svg>'
    ),
    "comentar": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
        '<path d="M3 4h14a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6l-4 3V5a1 1 0 0 1 1-1Z" '
        'stroke="FILL_COLOR" stroke-width="1.6" stroke-linejoin="round"/>'
        '</svg>'
    ),
    "config": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
        '<circle cx="10" cy="10" r="2.5" stroke="FILL_COLOR" stroke-width="1.5"/>'
        '<path d="M10 2v2M10 16v2M2 10h2M16 10h2'
        'M4.22 4.22l1.42 1.42M14.36 14.36l1.42 1.42'
        'M4.22 15.78l1.42-1.42M14.36 5.64l1.42-1.42" '
        'stroke="FILL_COLOR" stroke-width="1.5" stroke-linecap="round"/>'
        '</svg>'
    ),
}

NAV_ITEMS: list[tuple[str, str]] = [
    ("Dashboard",        "dashboard"),
    ("Registro Semanal", "semana"),
    ("Vista Mensual",    "mensual"),
    ("Trabajadores",     "trabajadores"),
    ("Clientes",         "clientes"),
    ("Comentarios",      "comentar"),
    ("Configuración",    "config"),
]


# ── NavButton ─────────────────────────────────────────────────────────────────

class NavButton(QPushButton):
    _COLOR_ACTIVE   = "#ffffff"
    _COLOR_INACTIVE = "rgba(255,255,255,0.52)"

    def __init__(self, icon_key: str, text: str, parent=None):
        super().__init__(parent)
        self._icon_key = icon_key
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(40)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(10)

        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(18, 18)
        self._icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setStyleSheet("background:transparent; border:none;")

        self._text_lbl = QLabel(text)
        self._text_lbl.setFont(font(13))
        self._text_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)

        lay.addWidget(self._icon_lbl)
        lay.addWidget(self._text_lbl)
        lay.addStretch()

        self._apply(active=False)

    def _apply(self, active: bool):
        color = self._COLOR_ACTIVE if active else self._COLOR_INACTIVE
        bg    = SIDEBAR_ACTIVE if active else "transparent"
        hover = SIDEBAR_ACTIVE if active else "rgba(255,255,255,0.07)"

        self.setStyleSheet(f"""
            QPushButton {{
                background:{bg}; border:none; border-radius:8px;
            }}
            QPushButton:hover {{ background:{hover}; }}
        """)
        self._text_lbl.setStyleSheet(
            f"color:{color}; background:transparent; border:none;"
        )
        self._icon_lbl.setPixmap(render_svg(_ICONS[self._icon_key], 18, color))

    def activate(self):   self._apply(True)
    def deactivate(self): self._apply(False)


# ── Sidebar ───────────────────────────────────────────────────────────────────

_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="9" stroke="FILL_COLOR" stroke-width="2"/>'
    '<path d="M12 7v5.5l3 2" stroke="FILL_COLOR" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)


class Sidebar(QWidget):
    def __init__(self, on_nav, parent=None):
        super().__init__(parent)
        self.setFixedWidth(210)
        self.setStyleSheet(f"background:{SIDEBAR_BG};")
        self._on_nav  = on_nav
        self._buttons: list[NavButton] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_nav(), 1)

        self._select(0)

    # ── Secciones internas ────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(68)
        header.setStyleSheet(
            f"background:{SIDEBAR_BG}; "
            "border-bottom:1px solid rgba(255,255,255,0.07);"
        )
        lay = QHBoxLayout(header)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(10)

        logo_box = QLabel()
        logo_box.setFixedSize(36, 36)
        logo_box.setAlignment(Qt.AlignCenter)
        logo_box.setStyleSheet(f"background:{GREEN}; border-radius:10px; border:none;")
        logo_box.setPixmap(render_svg(_LOGO_SVG, 20, "#9ee6c0"))

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        text_col.addWidget(make_label("Control de Horas", 13, QFont.Medium, "#e8ede9"))
        text_col.addWidget(make_label("v1.0", 11, color="rgba(255,255,255,0.35)"))

        lay.addWidget(logo_box)
        lay.addLayout(text_col)
        return header

    def _build_nav(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background:{SIDEBAR_BG};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(10, 14, 10, 14)
        lay.setSpacing(3)

        for i, (text, icon_key) in enumerate(NAV_ITEMS):
            btn = NavButton(icon_key, text)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            self._buttons.append(btn)
            lay.addWidget(btn)

        lay.addStretch()
        return container

    def _select(self, index: int):
        for i, btn in enumerate(self._buttons):
            btn.activate() if i == index else btn.deactivate()
        self._on_nav(index)