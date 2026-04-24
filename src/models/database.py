import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS TRABAJADORES (
                id_trabajador INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                color_ui TEXT,
                fecha_creacion TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS CLIENTES (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tarifa_hora REAL,
                activo INTEGER DEFAULT 1,
                fecha_creacion TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS REGISTRO_HORAS (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                id_trabajador INTEGER NOT NULL,
                id_cliente INTEGER NOT NULL,
                horas_manana REAL DEFAULT 0,
                horas_tarde REAL DEFAULT 0,
                horas_total REAL GENERATED ALWAYS AS (horas_manana + horas_tarde) VIRTUAL,
                comentario TEXT,
                fecha_creacion TEXT DEFAULT (datetime('now')),
                fecha_actualizacion TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (id_trabajador) REFERENCES TRABAJADORES(id_trabajador),
                FOREIGN KEY (id_cliente) REFERENCES CLIENTES(id_cliente)
            );

            CREATE TABLE IF NOT EXISTS COMENTARIOS_DIARIOS (
                id_comentario INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                id_trabajador INTEGER,
                comentario TEXT,
                fecha_creacion TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS CONFIGURACION (
                clave TEXT PRIMARY KEY,
                valor TEXT
            );
        """)
    conn.close()