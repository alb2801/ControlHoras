from dataclasses import dataclass
from typing import Optional


@dataclass
class Cliente:
    nombre: str
    tarifa_hora: float = 0.0
    activo: bool = True
    id_cliente: Optional[int] = None
    fecha_creacion: Optional[str] = None

    @staticmethod
    def from_row(row) -> "Cliente":
        return Cliente(
            id_cliente=row["id_cliente"],
            nombre=row["nombre"],
            tarifa_hora=row["tarifa_hora"] or 0.0,
            activo=bool(row["activo"]),
            fecha_creacion=row["fecha_creacion"],
        )