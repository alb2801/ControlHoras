from dataclasses import dataclass
from typing import Optional


@dataclass
class ComentarioDiario:
    fecha: str                        # 'YYYY-MM-DD'
    comentario: str
    id_trabajador: Optional[int] = None
    id_comentario: Optional[int] = None
    fecha_creacion: Optional[str] = None

    @staticmethod
    def from_row(row) -> "ComentarioDiario":
        return ComentarioDiario(
            id_comentario=row["id_comentario"],
            fecha=row["fecha"],
            id_trabajador=row["id_trabajador"],
            comentario=row["comentario"],
            fecha_creacion=row["fecha_creacion"],
        )