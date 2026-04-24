from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Trabajador:
    nombre: str
    activo: bool = True
    color_ui: Optional[str] = None
    id_trabajador: Optional[int] = None
    fecha_creacion: Optional[str] = None

    @staticmethod
    def from_row(row) -> "Trabajador":
        return Trabajador(
            id_trabajador=row["id_trabajador"],
            nombre=row["nombre"],
            activo=bool(row["activo"]),
            color_ui=row["color_ui"],
            fecha_creacion=row["fecha_creacion"],
        )