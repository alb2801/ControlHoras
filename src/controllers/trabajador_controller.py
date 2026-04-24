from typing import Optional
from src.models.database import get_connection
from src.models.trabajador import Trabajador


class TrabajadorController:

    def get_all(self, solo_activos: bool = False) -> list[Trabajador]:
        conn = get_connection()
        query = "SELECT * FROM TRABAJADORES"
        if solo_activos:
            query += " WHERE activo = 1"
        query += " ORDER BY nombre"
        rows = conn.execute(query).fetchall()
        conn.close()
        return [Trabajador.from_row(r) for r in rows]

    def get_by_id(self, id_trabajador: int) -> Optional[Trabajador]:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM TRABAJADORES WHERE id_trabajador = ?",
            (id_trabajador,)
        ).fetchone()
        conn.close()
        return Trabajador.from_row(row) if row else None

    def crear(self, trabajador: Trabajador) -> Trabajador:
        conn = get_connection()
        with conn:
            cursor = conn.execute(
                """INSERT INTO TRABAJADORES (nombre, activo, color_ui)
                   VALUES (?, ?, ?)""",
                (trabajador.nombre, int(trabajador.activo), trabajador.color_ui)
            )
            trabajador.id_trabajador = cursor.lastrowid
        conn.close()
        return trabajador

    def actualizar(self, trabajador: Trabajador) -> bool:
        conn = get_connection()
        with conn:
            affected = conn.execute(
                """UPDATE TRABAJADORES
                   SET nombre = ?, activo = ?, color_ui = ?
                   WHERE id_trabajador = ?""",
                (trabajador.nombre, int(trabajador.activo),
                 trabajador.color_ui, trabajador.id_trabajador)
            ).rowcount
        conn.close()
        return affected > 0

    def desactivar(self, id_trabajador: int) -> bool:
        conn = get_connection()
        with conn:
            affected = conn.execute(
                "UPDATE TRABAJADORES SET activo = 0 WHERE id_trabajador = ?",
                (id_trabajador,)
            ).rowcount
        conn.close()
        return affected > 0

    def eliminar(self, id_trabajador: int) -> bool:
        """Elimina solo si no tiene registros de horas asociados."""
        conn = get_connection()
        tiene_registros = conn.execute(
            "SELECT 1 FROM REGISTRO_HORAS WHERE id_trabajador = ? LIMIT 1",
            (id_trabajador,)
        ).fetchone()
        if tiene_registros:
            conn.close()
            return False
        with conn:
            conn.execute(
                "DELETE FROM TRABAJADORES WHERE id_trabajador = ?",
                (id_trabajador,)
            )
        conn.close()
        return True