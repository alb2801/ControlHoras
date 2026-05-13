"""
dashboard/metric_card.py
Tarjeta de métrica: ícono + label + valor grande.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout
from src.ui.styles import CARD_BG, CARD_BORDER, make_label, render_svg


class MetricCard(QFrame):
    def __init__(
        self,
        icon_svg: str,
        icon_color: str,
        icon_bg: str,
        metric_label: str,
        value: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:14px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(90)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(14)

        icon_box = QLabel()
        icon_box.setFixedSize(42, 42)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(
            f"background:{icon_bg}; border-radius:11px; border:none;"
        )
        icon_box.setPixmap(render_svg(icon_svg, 22, icon_color))

        col = QVBoxLayout()
        col.setSpacing(4)
        col.addWidget(make_label(metric_label, size=11, color="#74746e"))
        col.addWidget(make_label(value, size=24, weight=QFont.Medium))

        lay.addWidget(icon_box)
        lay.addLayout(col)
        lay.addStretch()