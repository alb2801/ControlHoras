"""
main_window.py
Ventana principal: ensambla Sidebar + stack de páginas.
Toda la lógica visual vive en sus módulos respectivos.
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QFrame, QMainWindow, QHBoxLayout, QScrollArea,
    QSizePolicy, QStackedWidget, QVBoxLayout, QWidget, QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.ui.styles import MAIN_BG, SIDEBAR_BG, TEXT_SEC, make_label
from src.ui.sidebar import Sidebar
from src.ui.dashboard import DashboardWidget
from src.ui.registro_semana.registro_semanal_widget import RegistroSemanalWidget


# ── Placeholder para pantallas no implementadas aún ──────────────────────────

class PlaceholderWidget(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{MAIN_BG};")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        t = make_label(title, size=18, weight=QFont.Medium, color=TEXT_SEC)
        t.setAlignment(Qt.AlignCenter)
        s = make_label("Próximamente", size=13, color=TEXT_SEC)
        s.setAlignment(Qt.AlignCenter)
        lay.addWidget(t)
        lay.addWidget(s)


# ── Ventana principal ─────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Horas")
        self.resize(1000, 680)
        self.setMinimumSize(820, 540)

        central = QWidget()
        central.setStyleSheet(f"background:{SIDEBAR_BG};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._dashboard        = DashboardWidget()
        self._registro_semanal = RegistroSemanalWidget()
        self._stack = self._build_stack()

        root.addWidget(Sidebar(on_nav=self._navigate))
        root.addWidget(self._stack)

        self._load_dashboard()

    # ── Stack de páginas ──────────────────────────────────────────────────────

    def _build_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        stack.setStyleSheet(f"background:{MAIN_BG};")

        pages = [
            self._dashboard,
            self._registro_semanal,
            PlaceholderWidget("Vista Mensual"),
            PlaceholderWidget("Personas"),
            PlaceholderWidget("Clientes"),
            PlaceholderWidget("Comentarios"),
            PlaceholderWidget("Configuración"),
        ]
        for page in pages:
            scroll = QScrollArea()
            scroll.setWidget(page)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setStyleSheet(f"background:{MAIN_BG}; border:none;")
            stack.addWidget(scroll)

        return stack

    def _navigate(self, index: int):
        self._stack.setCurrentIndex(index)

    # ── Carga de datos ────────────────────────────────────────────────────────

    def _load_dashboard(self):
        """
        Descomenta cuando la BD esté lista:

        from src.controllers.registro_horas_controller import RegistroHorasController
        from src.controllers.trabajador_controller import TrabajadorController
        from src.controllers.cliente_controller import ClienteController

        now = datetime.now()
        rc  = RegistroHorasController()
        tc  = TrabajadorController()
        cc  = ClienteController()

        self._dashboard.set_data(
            total_horas       = rc.total_horas_mes(now.year, now.month),
            personas_activas  = len(tc.get_all(solo_activos=True)),
            clientes_activos  = len(cc.get_all(solo_activos=True)),
            horas_por_persona = rc.horas_por_trabajador_mes(now.year, now.month),
            horas_por_cliente = rc.horas_por_cliente_mes(now.year, now.month),
            alertas           = self._build_alertas(rc, now),
        )
        """
        pass

    def _build_alertas(self, rc, now) -> list[str]:
        dias = rc.dias_sin_registro(now.year, now.month)
        por_trabajador: dict[str, list[str]] = {}
        for d in dias:
            por_trabajador.setdefault(d["nombre"], []).append(d["fecha"])

        alertas = []
        for nombre, fechas in por_trabajador.items():
            fechas_fmt = ", ".join(
                datetime.strptime(f, "%Y-%m-%d").strftime("%-d %b")
                for f in fechas[:3]
            )
            extra = f" (+{len(fechas) - 3} más)" if len(fechas) > 3 else ""
            alertas.append(
                f"{nombre} — {len(fechas)} día(s) sin registro ({fechas_fmt}{extra})"
            )
        return alertas