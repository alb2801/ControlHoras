"""
registro_semanal/registro_semanal_widget.py
Página de registro semanal: selector de semana, filtros persona/cliente,
tabla editable de horas por día y botón guardar.
"""

from datetime import date, timedelta

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget,
)

from src.ui.styles import (
    CARD_BG, CARD_BORDER, GREEN, MAIN_BG, TEXT_PRI, TEXT_SEC,
    font, make_label, render_svg,
)

# ── Constantes ────────────────────────────────────────────────────────────────
DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

_ICON_SAVE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
    '<rect x="3" y="2" width="14" height="16" rx="2" stroke="FILL_COLOR" stroke-width="1.6"/>'
    '<path d="M7 2v5h6V2" stroke="FILL_COLOR" stroke-width="1.4"/>'
    '<rect x="6" y="11" width="8" height="5" rx="1" stroke="FILL_COLOR" stroke-width="1.4"/>'
    '</svg>'
)
_ICON_COPY = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" fill="none">'
    '<rect x="5" y="5" width="10" height="11" rx="1.5" stroke="FILL_COLOR" stroke-width="1.4"/>'
    '<path d="M3 13V3h10" stroke="FILL_COLOR" stroke-width="1.4" stroke-linecap="round"/>'
    '</svg>'
)
_ICON_PREV = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none">'
    '<path d="M10 12L6 8l4-4" stroke="FILL_COLOR" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)
_ICON_NEXT = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none">'
    '<path d="M6 4l4 4-4 4" stroke="FILL_COLOR" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

MONTH_ES = {
    1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
    7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _monday_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _fmt_range(start: date, end: date) -> str:
    if start.month == end.month:
        return f"{start.day:02d} – {end.day:02d} {MONTH_ES[start.month]} {start.year}"
    return (
        f"{start.day:02d} {MONTH_ES[start.month]} – "
        f"{end.day:02d} {MONTH_ES[end.month]} {end.year}"
    )


def _combo_style() -> str:
    return f"""
        QComboBox {{
            background:{CARD_BG}; border:1px solid {CARD_BORDER};
            border-radius:8px; padding:0 10px; color:{TEXT_PRI};
            min-height:32px;
        }}
        QComboBox::drop-down {{ border:none; width:22px; }}
        QComboBox QAbstractItemView {{
            background:{CARD_BG}; border:1px solid {CARD_BORDER};
            color:{TEXT_PRI}; outline:none;
            selection-background-color:#e0f2ea;
        }}
    """


def _icon_btn(svg: str, size: int = 28, icon_size: int = 16,
              color: str = TEXT_SEC, hover_bg: str = "#ebebeb") -> QPushButton:
    btn = QPushButton()
    btn.setFixedSize(size, size)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setIcon(render_svg(svg, icon_size, color))
    from PySide6.QtCore import QSize
    btn.setIconSize(QSize(icon_size, icon_size))
    btn.setStyleSheet(f"""
        QPushButton {{
            background:transparent; border:none; border-radius:6px;
        }}
        QPushButton:hover {{ background:{hover_bg}; }}
    """)
    return btn


# ══════════════════════════════════════════════════════════════════════════════
#  FILA DE DÍA
# ══════════════════════════════════════════════════════════════════════════════

class DayRow(QWidget):
    """
    Fila editable: Día | Mañana | Tarde | Total | Comentario | Copiar
    """

    def __init__(self, day_name: str, is_weekend: bool = False, parent=None):
        super().__init__(parent)
        self._is_weekend = is_weekend
        self.setStyleSheet("background:transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(0)

        # Día
        self._day_lbl = make_label(day_name, size=13,
                                   color=TEXT_SEC if is_weekend else TEXT_PRI)
        self._day_lbl.setFixedWidth(90)
        lay.addWidget(self._day_lbl)

        # Mañana
        self._manana = self._make_input()
        self._manana.textChanged.connect(self._update_total)
        lay.addWidget(self._manana)
        lay.addSpacing(24)

        # Tarde
        self._tarde = self._make_input()
        self._tarde.textChanged.connect(self._update_total)
        lay.addWidget(self._tarde)
        lay.addSpacing(24)

        # Total (solo lectura)
        self._total_lbl = make_label("—", size=13,
                                      color=TEXT_SEC if is_weekend else TEXT_PRI)
        self._total_lbl.setFixedWidth(40)
        self._total_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lay.addWidget(self._total_lbl)
        lay.addSpacing(16)

        # Comentario
        self._comentario = self._make_comment()
        lay.addWidget(self._comentario, 1)
        lay.addSpacing(12)

        # Botón copiar
        self._copy_btn = _icon_btn(_ICON_COPY, size=28, icon_size=15,
                                   color="#aaaaaa", hover_bg="#ebebeb")
        self._copy_btn.setToolTip("Copiar fila anterior")
        lay.addWidget(self._copy_btn)

        if is_weekend:
            for w in (self._manana, self._tarde, self._comentario):
                w.setEnabled(False)
                w.setStyleSheet(w.styleSheet() + "opacity:0.5;")

    # ── Widgets internos ──────────────────────────────────────────────────────

    def _make_input(self) -> QLineEdit:
        inp = QLineEdit()
        inp.setFixedSize(52, 32)
        inp.setAlignment(Qt.AlignCenter)
        inp.setFont(font(13))
        inp.setValidator(QDoubleValidator(0, 24, 1))
        inp.setPlaceholderText("")
        inp.setStyleSheet(f"""
            QLineEdit {{
                background:{CARD_BG}; border:1px solid {CARD_BORDER};
                border-radius:7px; color:{TEXT_PRI};
            }}
            QLineEdit:focus {{
                border:1px solid {GREEN};
            }}
            QLineEdit:disabled {{
                background:#f5f5f3; color:#cccccc;
            }}
        """)
        return inp

    def _make_comment(self) -> QLineEdit:
        inp = QLineEdit()
        inp.setFixedHeight(32)
        inp.setFont(font(13))
        inp.setPlaceholderText("Observación")
        inp.setStyleSheet(f"""
            QLineEdit {{
                background:{CARD_BG}; border:1px solid {CARD_BORDER};
                border-radius:7px; padding:0 10px; color:{TEXT_PRI};
            }}
            QLineEdit:focus {{
                border:1px solid {GREEN};
            }}
            QLineEdit:disabled {{
                background:#f5f5f3; color:#cccccc;
            }}
        """)
        return inp

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _update_total(self):
        try:
            m = float(self._manana.text() or 0)
            t = float(self._tarde.text()  or 0)
            total = m + t
            self._total_lbl.setText(f"{total:g}" if total else "—")
        except ValueError:
            self._total_lbl.setText("—")

    def get_data(self) -> dict:
        try:
            manana = float(self._manana.text() or 0)
            tarde  = float(self._tarde.text()  or 0)
        except ValueError:
            manana = tarde = 0.0
        return {
            "horas_manana": manana,
            "horas_tarde":  tarde,
            "comentario":   self._comentario.text().strip() or None,
        }

    def set_data(self, manana: float, tarde: float, comentario: str = ""):
        self._manana.setText(str(manana) if manana else "")
        self._tarde.setText(str(tarde)   if tarde  else "")
        self._comentario.setText(comentario or "")
        self._update_total()

    def clear(self):
        self._manana.clear()
        self._tarde.clear()
        self._comentario.clear()
        self._total_lbl.setText("—")

    def set_copy_callback(self, cb):
        self._copy_btn.clicked.connect(cb)

    @property
    def total(self) -> float:
        try:
            return float(self._manana.text() or 0) + float(self._tarde.text() or 0)
        except ValueError:
            return 0.0


# ══════════════════════════════════════════════════════════════════════════════
#  CABECERA DE TABLA
# ══════════════════════════════════════════════════════════════════════════════

class TableHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setStyleSheet(f"background:#f0f0ee; border-radius:8px;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(0)

        cols = [("Día", 90), ("Mañana", 76), ("  Tarde", 76), ("Total", 56), ("Comentario", -1)]
        for label, w in cols:
            lbl = make_label(label, size=12, weight=QFont.Medium, color=TEXT_SEC)
            if w > 0:
                lbl.setFixedWidth(w)
            else:
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            lay.addWidget(lbl)


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGET PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class RegistroSemanalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{MAIN_BG};")

        # Estado
        self._week_start = _monday_of_week(date.today())
        self._trabajadores: list[dict] = [{"id": None, "nombre": "Jahir"}]
        self._clientes: list[dict]     = [{"id": None, "nombre": "Cliente A"}]
        self._rows: list[DayRow]       = []

        self._build()

    # ── Construcción ──────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        root.addLayout(self._build_topbar())
        root.addLayout(self._build_filters())
        root.addWidget(self._build_table())
        root.addLayout(self._build_footer())

    def _build_topbar(self) -> QHBoxLayout:
        lay = QHBoxLayout()

        col = QVBoxLayout()
        col.setSpacing(3)
        col.addWidget(make_label("Registro Semanal", size=22, weight=QFont.Medium))
        col.addWidget(make_label("Registra las horas de trabajo diarias",
                                 size=13, color=TEXT_SEC))
        lay.addLayout(col)
        lay.addStretch()
        lay.addWidget(self._build_week_nav())
        return lay

    def _build_week_nav(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(
            f"background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:9px;"
        )
        lay = QHBoxLayout(container)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(4)

        prev_btn = _icon_btn(_ICON_PREV, size=30, icon_size=14, color=TEXT_SEC)
        prev_btn.clicked.connect(self._prev_week)

        self._week_lbl = make_label("", size=13)
        self._week_lbl.setAlignment(Qt.AlignCenter)
        self._week_lbl.setFixedWidth(168)
        self._refresh_week_label()

        next_btn = _icon_btn(_ICON_NEXT, size=30, icon_size=14, color=TEXT_SEC)
        next_btn.clicked.connect(self._next_week)

        lay.addWidget(prev_btn)
        lay.addWidget(self._week_lbl)
        lay.addWidget(next_btn)
        return container

    def _build_filters(self) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.setSpacing(10)

        self._trabajador_combo = QComboBox()
        self._trabajador_combo.setFixedSize(160, 36)
        self._trabajador_combo.setFont(font(13))
        self._trabajador_combo.setStyleSheet(_combo_style())
        for t in self._trabajadores:
            self._trabajador_combo.addItem(t["nombre"], t["id"])

        self._cliente_combo = QComboBox()
        self._cliente_combo.setFixedSize(160, 36)
        self._cliente_combo.setFont(font(13))
        self._cliente_combo.setStyleSheet(_combo_style())
        for c in self._clientes:
            self._cliente_combo.addItem(c["nombre"], c["id"])

        lay.addWidget(self._trabajador_combo)
        lay.addWidget(self._cliente_combo)
        lay.addStretch()
        return lay

    def _build_table(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:14px;"
        )

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 12, 0, 12)
        lay.setSpacing(0)

        # Cabecera
        header_wrapper = QWidget()
        header_wrapper.setContentsMargins(0, 0, 0, 0)
        hw = QHBoxLayout(header_wrapper)
        hw.setContentsMargins(0, 0, 0, 0)
        hw.addWidget(TableHeader())
        lay.addWidget(header_wrapper)

        # Filas
        self._rows = []
        for i, day in enumerate(DAYS_ES):
            is_weekend = i >= 5
            row = DayRow(day, is_weekend)

            # Callback de copiar: copia la fila anterior
            if i > 0:
                prev = self._rows[i - 1]
                row.set_copy_callback(lambda _, p=prev, r=row: self._copy_row(p, r))

            self._rows.append(row)

            # Separador (excepto último)
            lay.addWidget(row)
            if i < len(DAYS_ES) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet(f"background:{CARD_BORDER}; border:none; max-height:1px;")
                lay.addWidget(sep)

        return card

    def _build_footer(self) -> QHBoxLayout:
        lay = QHBoxLayout()

        self._total_lbl = make_label("Total semana:  0 h", size=13)
        # Negrita en la parte numérica la hacemos con rich text
        self._total_lbl.setTextFormat(Qt.RichText)
        self._refresh_total()

        # Conectar cambios de inputs al total
        for row in self._rows:
            row._manana.textChanged.connect(self._refresh_total)
            row._tarde.textChanged.connect(self._refresh_total)

        lay.addWidget(self._total_lbl)
        lay.addStretch()
        lay.addWidget(self._build_save_btn())
        return lay

    def _build_save_btn(self) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(38)
        btn.setFont(font(13, QFont.Medium))

        icon_pix = render_svg(_ICON_SAVE, 16, "#ffffff")
        btn.setIcon(icon_pix)
        from PySide6.QtCore import QSize
        btn.setIconSize(QSize(16, 16))
        btn.setText("  Guardar")
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{GREEN}; color:#ffffff;
                border:none; border-radius:9px; padding:0 20px;
            }}
            QPushButton:hover {{ background:#256b43; }}
            QPushButton:pressed {{ background:#1e5a38; }}
        """)
        btn.clicked.connect(self._save)
        return btn

    # ── Lógica de navegación ──────────────────────────────────────────────────

    def _prev_week(self):
        self._week_start -= timedelta(weeks=1)
        self._refresh_week_label()
        self._load_week()

    def _next_week(self):
        self._week_start += timedelta(weeks=1)
        self._refresh_week_label()
        self._load_week()

    def _refresh_week_label(self):
        end = self._week_start + timedelta(days=6)
        self._week_lbl.setText(_fmt_range(self._week_start, end))

    def _refresh_total(self):
        total = sum(r.total for r in self._rows)
        self._total_lbl.setText(
            f'Total semana: &nbsp;<b>{total:g} h</b>'
        )

    # ── Lógica de datos ───────────────────────────────────────────────────────

    def _copy_row(self, source: DayRow, target: DayRow):
        data = source.get_data()
        target.set_data(data["horas_manana"], data["horas_tarde"],
                        data["comentario"] or "")

    def _load_week(self):
        """
        Carga los registros de la semana desde el controller.
        Por ahora limpia las filas. Conectar con RegistroHorasController.
        """
        for row in self._rows:
            row.clear()
        self._refresh_total()

    def _save(self):
        """
        Guarda los registros usando el controller.

        Ejemplo de integración:
            from src.controllers.registro_horas_controller import RegistroHorasController
            from src.models.registro_horas import RegistroHoras

            rc = RegistroHorasController()
            id_trabajador = self._trabajador_combo.currentData()
            id_cliente    = self._cliente_combo.currentData()

            for i, row in enumerate(self._rows):
                if row._is_weekend:
                    continue
                data  = row.get_data()
                fecha = (self._week_start + timedelta(days=i)).isoformat()
                existing = rc.existe(fecha, id_trabajador, id_cliente)
                registro  = existing or RegistroHoras(
                    fecha=fecha,
                    id_trabajador=id_trabajador,
                    id_cliente=id_cliente,
                )
                registro.horas_manana = data["horas_manana"]
                registro.horas_tarde  = data["horas_tarde"]
                registro.comentario   = data["comentario"]
                if existing:
                    rc.actualizar(registro)
                else:
                    rc.crear(registro)
        """
        # Feedback visual temporal hasta conectar BD
        QMessageBox.information(self, "Guardado", "Registros guardados correctamente.")

    # ── API pública ───────────────────────────────────────────────────────────

    def set_trabajadores(self, trabajadores: list[dict]):
        """[{'id': int, 'nombre': str}, ...]"""
        self._trabajadores = trabajadores
        self._trabajador_combo.clear()
        for t in trabajadores:
            self._trabajador_combo.addItem(t["nombre"], t["id"])

    def set_clientes(self, clientes: list[dict]):
        """[{'id': int, 'nombre': str}, ...]"""
        self._clientes = clientes
        self._cliente_combo.clear()
        for c in clientes:
            self._cliente_combo.addItem(c["nombre"], c["id"])