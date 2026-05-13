"""
dashboard/hours_card.py
Tarjeta de barras horizontales para horas por persona / cliente.

Fix: el label del nombre usa ancho mínimo + wrap en lugar de ancho fijo,
     y la barra fill usa QWidget con stretch proporcional en vez de px fijos,
     para que no se rompa con nombres largos como "Cliente A".
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget,
)
from src.ui.styles import CARD_BG, CARD_BORDER, GREEN, BAR_TRACK, TEXT_SEC, make_label


class BarRow(QWidget):
    """Una fila: nombre | barra de progreso | valor."""

    _NAME_MIN_W = 72   # ancho mínimo del label de nombre (px)
    _NAME_MAX_W = 110  # ancho máximo antes de hacer wrap

    def __init__(self, name: str, hours: int, max_hours: int, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # ── Nombre: ancho mínimo fijo, wrap si es muy largo ──────────────────
        name_lbl = make_label(name, size=13, color=TEXT_SEC, wrap=True)
        name_lbl.setMinimumWidth(self._NAME_MIN_W)
        name_lbl.setMaximumWidth(self._NAME_MAX_W)
        name_lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        lay.addWidget(name_lbl)

        # ── Barra proporcional ────────────────────────────────────────────────
        lay.addWidget(self._build_track(hours, max_hours), 1)

        # ── Valor ─────────────────────────────────────────────────────────────
        val = make_label(f"{hours}h", size=13, weight=QFont.Medium)
        val.setFixedWidth(36)
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(val)

    def _build_track(self, hours: int, max_hours: int) -> QWidget:
        """
        Track con dos zonas en un QHBoxLayout:
          - fill  → stretch = pct        (parte verde)
          - empty → stretch = 100 - pct  (parte gris)
        Así la proporción es siempre correcta sin calcular px.
        """
        container = QWidget()
        container.setFixedHeight(10)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        pct   = max(int((hours / max_hours) * 100), 4) if max_hours else 4
        empty = 100 - pct

        fill = QFrame()
        fill.setFixedHeight(10)
        fill.setStyleSheet(f"background:{GREEN}; border-radius:5px; border:none;")

        track = QFrame()
        track.setFixedHeight(10)
        track.setStyleSheet(f"background:{BAR_TRACK}; border-radius:5px; border:none;")

        lay.addWidget(fill,  pct)
        lay.addWidget(track, empty)
        return container


class HoursCard(QFrame):
    """Card con título y lista de BarRows."""

    def __init__(self, title: str, rows: list[tuple[str, int]], parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:14px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)

        lay.addWidget(make_label(title, size=14, weight=QFont.Medium))

        max_h = max((h for _, h in rows), default=1)
        for name, hours in rows:
            lay.addWidget(BarRow(name, hours, max_h))