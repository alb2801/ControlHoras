from dataclasses import dataclass
from typing import Optional


@dataclass
class RegistroHoras:
    fecha: str                        # 'YYYY-MM-DD'
    id_trabajador: int
    id_cliente: int
    horas_manana: float = 0.0
    horas_tarde: float = 0.0
    comentario: Optional[str] = None
    id_registro: Optional[int] = None
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None

    @property
    def horas_total(self) -> float:
        return self.horas_manana + self.horas_tarde

    @staticmethod
    def from_row(row) -> "RegistroHoras":
        return RegistroHoras(
            id_registro=row["id_registro"],
            fecha=row["fecha"],
            id_trabajador=row["id_trabajador"],
            id_cliente=row["id_cliente"],
            horas_manana=row["horas_manana"] or 0.0,
            horas_tarde=row["horas_tarde"] or 0.0,
            comentario=row["comentario"],
            fecha_creacion=row["fecha_creacion"],
            fecha_actualizacion=row["fecha_actualizacion"],
        )