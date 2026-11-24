import sqlite3, pathlib
RAIZ = pathlib.Path(__file__).resolve().parent.parent
RUTA_BD = RAIZ / "data" / "alinea.db"

def conectar(ruta=RUTA_BD):
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    # Migracion ligera: permite que una base existente reciba las tablas nuevas
    # sin perder las ofertas, materias ni habilidades ya cargadas.
    con.executescript("""
    CREATE TABLE IF NOT EXISTS usuario (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT NOT NULL DEFAULT '',
      correo TEXT NOT NULL UNIQUE,
      dominio TEXT NOT NULL,
      fecha_registro TEXT NOT NULL,
      ultimo_acceso TEXT NOT NULL,
      cookie_consentimiento INTEGER NOT NULL DEFAULT 0 CHECK (cookie_consentimiento IN (0, 1))
    );
    CREATE INDEX IF NOT EXISTS ix_usuario_fecha ON usuario(fecha_registro, id);
    CREATE TABLE IF NOT EXISTS evento_seguridad (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario_id INTEGER REFERENCES usuario(id),
      evento TEXT NOT NULL,
      fecha TEXT NOT NULL,
      ip_hash TEXT
    );
    CREATE INDEX IF NOT EXISTS ix_evento_seguridad_fecha ON evento_seguridad(fecha);
    """)
    return con
