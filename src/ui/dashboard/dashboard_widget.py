"""
dashboard/dashboard_widget.py
Página principal del Dashboard: ensambla MetricCard, HoursCard y AlertCard.
"""

from datetime import datetime

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout, QWidget

from src.ui.styles import (
    AMBER_ICON_BG, BLUE_ICON_BG, CARD_BG, CARD_BORDER,
    GREEN_ICON_BG, MAIN_BG, TEXT_SEC, make_label,
)
from src.ui.dashboard.metric_card import MetricCard
from src.ui.dashboard.hours_card import HoursCard
from src.ui.dashboard.alert_card import AlertCard

# ── SVGs de métricas ──────────────────────────────────────────────────────────
_ICON_CLOCK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22" fill="none">'
    '<circle cx="11" cy="11" r="8.5" stroke="FILL_COLOR" stroke-width="1.8"/>'
    '<path d="M11 7v4.5l2.5 2" stroke="FILL_COLOR" stroke-width="1.8" stroke-linecap="round"/>'
    '</svg>'
)
_ICON_USERS = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22" fill="none">'
    '<circle cx="8.5" cy="8" r="3" stroke="FILL_COLOR" stroke-width="1.6"/>'
    '<circle cx="15" cy="8" r="3" stroke="FILL_COLOR" stroke-width="1.6"/>'
    '<path d="M2 19c0-3.314 3.134-5 6.5-5" stroke="FILL_COLOR" stroke-width="1.6" stroke-linecap="round"/>'
    '<path d="M12 14c3.5 0 8 1.5 8 5" stroke="FILL_COLOR" stroke-width="1.6" stroke-linecap="round"/>'
    '</svg>'
)
_ICON_BAG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22" fill="none">'
    '<rect x="2" y="7" width="18" height="13" rx="2.5" stroke="FILL_COLOR" stroke-width="1.7"/>'
    '<path d="M7 7V6a4 4 0 0 1 8 0v1" stroke="FILL_COLOR" stroke-width="1.7" stroke-linecap="round"/>'
    '</svg>'
)

MONTH_NAMES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

# Datos de muestra para desarrollo
_SAMPLE_DATA = {
    "total_horas": 142.0,
    "trabajadores_activos": 3,
    "clientes_activos": 6,
    "horas_por_trabajadores": [
        {"nombre": "Jahir",  "total": 42},
        {"nombre": "Isabel", "total": 38},
        {"nombre": "Lisset", "total": 32},
    ],
    "horas_por_cliente": [
        {"nombre": "Cliente A", "total": 48},
        {"nombre": "Cliente B", "total": 35},
        {"nombre": "Cliente C", "total": 29},
    ],
    "alertas": [
        "Jahir — 2 días sin horas registradas (12, 13 Mar)",
        "Isabel — Registro incompleto el 10 Mar (falta cliente)",
    ],
}


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{MAIN_BG};")
        self._data = dict(_SAMPLE_DATA)
        self._build()

    # ── API pública ───────────────────────────────────────────────────────────

    def set_data(
        self,
        total_horas: float,
        trabajadores_activos: int,
        clientes_activos: int,
        horas_por_trabajadores: list[dict],
        horas_por_cliente: list[dict],
        alertas: list[str],
    ):
        """Recibe datos reales desde los controllers y redibuja."""
        self._data = {
            "total_horas":      total_horas,
            "trabajadores_activos": trabajadores_activos,
            "clientes_activos": clientes_activos,
            "horas_por_trabajadores": horas_por_trabajadores,
            "horas_por_cliente": horas_por_cliente,
            "alertas":           alertas,
        }
        old = self.layout()
        if old:
            QWidget().setLayout(old)
        self._build()

    # ── Construcción interna ──────────────────────────────────────────────────

    def _build(self):
        d = self._data
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        root.addLayout(self._build_topbar())
        root.addLayout(self._build_metrics(d))
        root.addLayout(self._build_charts(d))

        if d["alertas"]:
            root.addWidget(AlertCard(d["alertas"]))

        root.addStretch()

    def _build_topbar(self) -> QHBoxLayout:
        lay = QHBoxLayout()

        col = QVBoxLayout()
        col.setSpacing(3)
        col.addWidget(make_label("Dashboard", size=22, weight=QFont.Medium))
        col.addWidget(make_label("Resumen general del mes", size=13, color=TEXT_SEC))
        lay.addLayout(col)
        lay.addStretch()
        lay.addWidget(self._build_month_combo())
        return lay

    def _build_month_combo(self) -> QComboBox:
        now = datetime.now()
        combo = QComboBox()
        combo.setFixedSize(165, 36)
        from src.ui.styles import font
        combo.setFont(font(13))
        for m in MONTH_NAMES:
            combo.addItem(f"{m} {now.year}")
        combo.setCurrentIndex(now.month - 1)
        combo.setStyleSheet(f"""
            QComboBox {{
                background:{CARD_BG}; border:1px solid {CARD_BORDER};
                border-radius:9px; padding:0 12px; color:#111211;
            }}
            QComboBox::drop-down {{ border:none; width:24px; }}
            QComboBox QAbstractItemView {{
                background:{CARD_BG}; border:1px solid {CARD_BORDER};
                selection-background-color:{GREEN_ICON_BG}; color:#111211;
                outline:none;
            }}
        """)
        return combo

    def _build_metrics(self, d: dict) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.setSpacing(14)
        lay.addWidget(MetricCard(_ICON_CLOCK, "#1e7a4f", GREEN_ICON_BG,
                                 "Total horas", f"{int(d['total_horas'])} h"))
        lay.addWidget(MetricCard(_ICON_USERS, "#1a5fa8", BLUE_ICON_BG,
                                 "Trabajadores activos", str(d["trabajadores_activos"])))
        lay.addWidget(MetricCard(_ICON_BAG,   "#a06010", AMBER_ICON_BG,
                                 "Clientes activos", str(d["clientes_activos"])))
        return lay

    def _build_charts(self, d: dict) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.setSpacing(14)
        lay.addWidget(HoursCard(
            "Horas por Trabajador",
            [(p["nombre"], int(p["total"])) for p in d["horas_por_trabajadores"]],
        ))
        lay.addWidget(HoursCard(
            "Horas por cliente",
            [(c["nombre"], int(c["total"])) for c in d["horas_por_cliente"]],
        ))
        return lay