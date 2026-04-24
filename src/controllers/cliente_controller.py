from typing import Optional
from src.models.database import get_connection
from src.models.cliente import Cliente


class ClienteController:

    def get_all(self, solo_activos: bool = False) -> list[Cliente]:
        conn = get_connection()
        query = "SELECT * FROM CLIENTES"
        if solo_activos:
            query += " WHERE activo = 1"
        query += " ORDER BY nombre"
        rows = conn.execute(query).fetchall()
        conn.close()
        return [Cliente.from_row(r) for r in rows]

    def get_by_id(self, id_cliente: int) -> Optional[Cliente]:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM CLIENTES WHERE id_cliente = ?",
            (id_cliente,)
        ).fetchone()
        conn.close()
        return Cliente.from_row(row) if row else None

    def crear(self, cliente: Cliente) -> Cliente:
        conn = get_connection()
        with conn:
            cursor = conn.execute(
                """INSERT INTO CLIENTES (nombre, tarifa_hora, activo)
                   VALUES (?, ?, ?)""",
                (cliente.nombre, cliente.tarifa_hora, int(cliente.activo))
            )
            cliente.id_cliente = cursor.lastrowid
        conn.close()
        return cliente

    def actualizar(self, cliente: Cliente) -> bool:
        conn = get_connection()
        with conn:
            affected = conn.execute(
                """UPDATE CLIENTES
                   SET nombre = ?, tarifa_hora = ?, activo = ?
                   WHERE id_cliente = ?""",
                (cliente.nombre, cliente.tarifa_hora,
                 int(cliente.activo), cliente.id_cliente)
            ).rowcount
        conn.close()
        return affected > 0

    def desactivar(self, id_cliente: int) -> bool:
        conn = get_connection()
        with conn:
            affected = conn.execute(
                "UPDATE CLIENTES SET activo = 0 WHERE id_cliente = ?",
                (id_cliente,)
            ).rowcount
        conn.close()
        return affected > 0

    def eliminar(self, id_cliente: int) -> bool:
        """Elimina solo si no tiene registros de horas asociados."""
        conn = get_connection()
        tiene_registros = conn.execute(
            "SELECT 1 FROM REGISTRO_HORAS WHERE id_cliente = ? LIMIT 1",
            (id_cliente,)
        ).fetchone()
        if tiene_registros:
            conn.close()
            return False
        with conn:
            conn.execute(
                "DELETE FROM CLIENTES WHERE id_cliente = ?",
                (id_cliente,)
            )
        conn.close()
        return True