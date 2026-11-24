# ALINEA · Sprint 1
Elige una carrera de la Universidad Santo Tomás y mira qué habilidades enseña, qué tan útiles son en la demanda laboral y cuáles se piden sin enseñarse. También permite buscar una habilidad suelta.
Python + Flask + SQL (SQLite; el esquema es portable a PostgreSQL).

## Ejecutar
    pip install -r requirements.txt
    python -m db.seed        # crea data/alinea.db con datos ILUSTRATIVOS
    python -m web.app        # http://127.0.0.1:5000  (inicio: lista de carreras)
    python buscar.py sql     # búsqueda por consola

## Actualizar ofertas en vivo
Cada ingenieria tiene ofertas vinculadas por programa en la tabla oferta_real_programa.
La pagina permite filtrar por ciudad y modalidad y consultar ofertas nuevas con el boton
Actualizar ofertas. Para activar la consulta en vivo, configura RAPIDAPI_KEY en el entorno.
La integracion usa JSearch para consultar ofertas publicas agregadas de distintos portales;
sin la clave, la pagina usa las ofertas verificadas guardadas en SQLite y muestra el motivo.

## Estructura
    db/      schema.sql, conexion.py, consultas.py (SQL), seed.py (datos de ejemplo)
    nlp/     extractor.py (diccionario + alias)
    web/     app.py y templates/
    tests/   pruebas del extractor

## Cargar datos reales (Sprint 2)
Insertar filas en `oferta` (texto crudo) y repetir la extracción de `db/seed.py` sobre ellas;
insertar materias en `materia` y sus habilidades en `materia_habilidad`.
Los umbrales de utilidad están en la tabla `configuracion`.
