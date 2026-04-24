from typing import Optional
from src.models.database import get_connection
from src.models.registro_horas import RegistroHoras


class RegistroHorasController:

    def get_by_fecha(self, fecha: str) -> list[RegistroHoras]:
        """Todos los registros de un día (YYYY-MM-DD)."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM REGISTRO_HORAS WHERE fecha = ? ORDER BY id_trabajador",
            (fecha,)
        ).fetchall()
        conn.close()
        return [RegistroHoras.from_row(r) for r in rows]

    def get_by_semana(self, fecha_inicio: str, fecha_fin: str) -> list[RegistroHoras]:
        """Registros entre dos fechas inclusive (YYYY-MM-DD)."""
        conn = get_connection()
        rows = conn.execute(
            """SELECT * FROM REGISTRO_HORAS
               WHERE fecha BETWEEN ? AND ?
               ORDER BY fecha, id_trabajador""",
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()
        return [RegistroHoras.from_row(r) for r in rows]

    def get_by_mes(self, anio: int, mes: int) -> list[RegistroHoras]:
        """Registros de un mes completo."""
        fecha_inicio = f"{anio:04d}-{mes:02d}-01"
        fecha_fin    = f"{anio:04d}-{mes:02d}-31"
        return self.get_by_semana(fecha_inicio, fecha_fin)

    def get_by_trabajador_mes(self, id_trabajador: int, anio: int, mes: int) -> list[RegistroHoras]:
        conn = get_connection()
        rows = conn.execute(
            """SELECT * FROM REGISTRO_HORAS
               WHERE id_trabajador = ?
                 AND strftime('%Y', fecha) = ?
                 AND strftime('%m', fecha) = ?
               ORDER BY fecha""",
            (id_trabajador, f"{anio:04d}", f"{mes:02d}")
        ).fetchall()
        conn.close()
        return [RegistroHoras.from_row(r) for r in rows]

    def get_by_id(self, id_registro: int) -> Optional[RegistroHoras]:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM REGISTRO_HORAS WHERE id_registro = ?",
            (id_registro,)
        ).fetchone()
        conn.close()
        return RegistroHoras.from_row(row) if row else None

    def existe(self, fecha: str, id_trabajador: int, id_cliente: int) -> Optional[RegistroHoras]:
        """Verifica si ya existe un registro para esa combinación fecha/trabajador/cliente."""
        conn = get_connection()
        row = conn.execute(
            """SELECT * FROM REGISTRO_HORAS
               WHERE fecha = ? AND id_trabajador = ? AND id_cliente = ?""",
            (fecha, id_trabajador, id_cliente)
        ).fetchone()
        conn.close()
        return RegistroHoras.from_row(row) if row else None

    def crear(self, registro: RegistroHoras) -> RegistroHoras:
        conn = get_connection()
        with conn:
            cursor = conn.execute(
                """INSERT INTO REGISTRO_HORAS
                   (fecha, id_trabajador, id_cliente, horas_manana, horas_tarde, comentario)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (registro.fecha, registro.id_trabajador, registro.id_cliente,
                 registro.horas_manana, registro.horas_tarde, registro.comentario)
            )
            registro.id_registro = cursor.lastrowid
        conn.close()
        return registro

    def actualizar(self, registro: RegistroHoras) -> bool:
        conn = get_connection()
        with conn:
            affected = conn.execute(
                """UPDATE REGISTRO_HORAS
                   SET horas_manana = ?, horas_tarde = ?, comentario = ?,
                       fecha_actualizacion = datetime('now','localtime')
                   WHERE id_registro = ?""",
                (registro.horas_manana, registro.horas_tarde,
                 registro.comentario, registro.id_registro)
            ).rowcount
        conn.close()
        return affected > 0

    def eliminar(self, id_registro: int) -> bool:
        conn = get_connection()
        with conn:
            affected = conn.execute(
                "DELETE FROM REGISTRO_HORAS WHERE id_registro = ?",
                (id_registro,)
            ).rowcount
        conn.close()
        return affected > 0

    # ── Resúmenes para el dashboard ──────────────────────────────────────────

    def total_horas_mes(self, anio: int, mes: int) -> float:
        conn = get_connection()
        row = conn.execute(
            """SELECT COALESCE(SUM(horas_manana + horas_tarde), 0) AS total
               FROM REGISTRO_HORAS
               WHERE strftime('%Y', fecha) = ?
                 AND strftime('%m', fecha) = ?""",
            (f"{anio:04d}", f"{mes:02d}")
        ).fetchone()
        conn.close()
        return row["total"]

    def horas_por_trabajador_mes(self, anio: int, mes: int) -> list[dict]:
        """Retorna [{'id_trabajador': x, 'nombre': y, 'total': z}, ...]"""
        conn = get_connection()
        rows = conn.execute(
            """SELECT t.id_trabajador, t.nombre,
                      COALESCE(SUM(r.horas_manana + r.horas_tarde), 0) AS total
               FROM TRABAJADORES t
               LEFT JOIN REGISTRO_HORAS r
                      ON r.id_trabajador = t.id_trabajador
                     AND strftime('%Y', r.fecha) = ?
                     AND strftime('%m', r.fecha) = ?
               WHERE t.activo = 1
               GROUP BY t.id_trabajador
               ORDER BY total DESC""",
            (f"{anio:04d}", f"{mes:02d}")
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def horas_por_cliente_mes(self, anio: int, mes: int) -> list[dict]:
        """Retorna [{'id_cliente': x, 'nombre': y, 'total': z}, ...]"""
        conn = get_connection()
        rows = conn.execute(
            """SELECT c.id_cliente, c.nombre,
                      COALESCE(SUM(r.horas_manana + r.horas_tarde), 0) AS total
               FROM CLIENTES c
               LEFT JOIN REGISTRO_HORAS r
                      ON r.id_cliente = c.id_cliente
                     AND strftime('%Y', r.fecha) = ?
                     AND strftime('%m', r.fecha) = ?
               WHERE c.activo = 1
               GROUP BY c.id_cliente
               ORDER BY total DESC""",
            (f"{anio:04d}", f"{mes:02d}")
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def dias_sin_registro(self, anio: int, mes: int) -> list[dict]:
        """
        Días hábiles (lun-vie) del mes donde un trabajador activo
        no tiene ningún registro.
        Retorna [{'id_trabajador': x, 'nombre': y, 'fecha': 'YYYY-MM-DD'}, ...]
        """
        conn = get_connection()
        rows = conn.execute(
            """WITH RECURSIVE fechas(f) AS (
                   SELECT date(?, 'start of month')
                   UNION ALL
                   SELECT date(f, '+1 day')
                   FROM fechas
                   WHERE f < date(?, 'start of month', '+1 month', '-1 day')
               ),
               dias_habiles AS (
                   SELECT f FROM fechas
                   WHERE strftime('%w', f) NOT IN ('0','6')
               )
               SELECT t.id_trabajador, t.nombre, d.f AS fecha
               FROM TRABAJADORES t
               CROSS JOIN dias_habiles d
               WHERE t.activo = 1
                 AND NOT EXISTS (
                     SELECT 1 FROM REGISTRO_HORAS r
                     WHERE r.id_trabajador = t.id_trabajador
                       AND r.fecha = d.f
                 )
               ORDER BY d.f, t.nombre""",
            (f"{anio:04d}-{mes:02d}-01", f"{anio:04d}-{mes:02d}-01")
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]