-- ALINEA · esquema Sprint 1 (SQLite; compatible con PostgreSQL cambiando AUTOINCREMENT por SERIAL)
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS programa (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS materia (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  programa_id INTEGER NOT NULL REFERENCES programa(id),
  nombre TEXT NOT NULL, semestre INTEGER);
CREATE TABLE IF NOT EXISTS habilidad (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  alias TEXT NOT NULL DEFAULT '',
  categoria TEXT NOT NULL DEFAULT 'General');
CREATE TABLE IF NOT EXISTS materia_habilidad (
  materia_id INTEGER NOT NULL REFERENCES materia(id),
  habilidad_id INTEGER NOT NULL REFERENCES habilidad(id),
  fragmento TEXT, PRIMARY KEY (materia_id, habilidad_id));
CREATE TABLE IF NOT EXISTS oferta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL, empresa TEXT, ciudad TEXT, fuente TEXT, fecha TEXT,
  descripcion TEXT NOT NULL, UNIQUE (titulo, empresa, descripcion));
CREATE TABLE IF NOT EXISTS oferta_habilidad (
  oferta_id INTEGER NOT NULL REFERENCES oferta(id),
  habilidad_id INTEGER NOT NULL REFERENCES habilidad(id),
  fragmento TEXT, PRIMARY KEY (oferta_id, habilidad_id));
CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor REAL NOT NULL);
CREATE INDEX IF NOT EXISTS ix_oh_hab ON oferta_habilidad(habilidad_id);
CREATE INDEX IF NOT EXISTS ix_mh_hab ON materia_habilidad(habilidad_id);
CREATE TABLE IF NOT EXISTS programa_perfil (   -- perfiles de empleo a los que apunta cada carrera
  programa_id INTEGER NOT NULL REFERENCES programa(id),
  perfil TEXT NOT NULL, PRIMARY KEY (programa_id, perfil));

CREATE TABLE IF NOT EXISTS oferta_real (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  empresa TEXT NOT NULL,
  ciudad TEXT,
  modalidad TEXT,
  salario TEXT,
  contrato TEXT,
  requisitos TEXT NOT NULL,
  fuente TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  fecha_consulta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS oferta_real_habilidad (
  oferta_id INTEGER NOT NULL REFERENCES oferta_real(id),
  habilidad_id INTEGER NOT NULL REFERENCES habilidad(id),
  PRIMARY KEY (oferta_id, habilidad_id)
);
CREATE INDEX IF NOT EXISTS ix_orh_hab ON oferta_real_habilidad(habilidad_id);
CREATE TABLE IF NOT EXISTS oferta_real_programa (
  oferta_id INTEGER NOT NULL REFERENCES oferta_real(id),
  programa_id INTEGER NOT NULL REFERENCES programa(id),
  PRIMARY KEY (oferta_id, programa_id)
);
CREATE INDEX IF NOT EXISTS ix_orp_prog ON oferta_real_programa(programa_id);

-- Registro institucional y preferencias de privacidad.
-- No se almacenan contraseñas: el acceso de ALINEA se valida con correo
-- institucional y una cookie de sesión firmada por Flask.
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
