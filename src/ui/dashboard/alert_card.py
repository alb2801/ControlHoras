"""
dashboard/alert_card.py
Tarjeta de alertas con fondo ámbar.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from src.ui.styles import AMBER_BG, AMBER_BORDER, make_label, render_svg

_WARN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
    '<path d="M10 2L18.5 17H1.5L10 2Z" fill="FILL_COLOR"/>'
    '<path d="M10 8v4" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>'
    '<circle cx="10" cy="14.5" r="1" fill="#fff"/>'
    '</svg>'
)
_WARN_COLOR  = "#e8a020"
_TITLE_COLOR = "#7a5c0a"
_TEXT_COLOR  = "#5a4208"


class AlertCard(QFrame):
    def __init__(self, alerts: list[str], parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{AMBER_BG}; border:1px solid {AMBER_BORDER}; border-radius:14px;"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        lay.addLayout(self._build_header())

        for alert in alerts:
            lay.addLayout(self._build_row(alert))

    def _build_header(self) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.setSpacing(8)

        icon = QLabel()
        icon.setFixedSize(18, 18)
        icon.setStyleSheet("background:transparent; border:none;")
        icon.setPixmap(render_svg(_WARN_SVG, 18, _WARN_COLOR))

        lay.addWidget(icon)
        lay.addWidget(make_label("Alertas", size=13, weight=QFont.Medium, color=_TITLE_COLOR))
        lay.addStretch()
        return lay

    def _build_row(self, text: str) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.setSpacing(8)

        dot = QLabel()
        dot.setFixedSize(16, 16)
        dot.setStyleSheet("background:transparent; border:none;")
        dot.setPixmap(render_svg(_WARN_SVG, 16, _WARN_COLOR))
        lay.addWidget(dot, 0, Qt.AlignTop)

        txt = make_label(text, size=13, color=_TEXT_COLOR, wrap=True)
        lay.addWidget(txt, 1)
        return lay