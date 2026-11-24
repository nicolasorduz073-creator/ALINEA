"""Consultas SQL del buscador: qué enseña la USTA y qué tan útil es en la demanda laboral."""

from nlp.extractor import extraer
from urllib.parse import quote

RECURSOS_APRENDIZAJE = {
    "Python": [("Tutorial oficial de Python", "https://docs.python.org/es/3/tutorial/")],
    "SQL": [("SQLBolt: ejercicios interactivos", "https://sqlbolt.com/")],
    "Git": [("Libro Pro Git en espaÃ±ol", "https://git-scm.com/book/es/v2")],
    "Excel avanzado": [("FormaciÃ³n de Excel - Microsoft Learn", "https://learn.microsoft.com/es-es/training/browse/?products=excel")],
    "Power BI": [("Rutas oficiales de Power BI", "https://learn.microsoft.com/training/powerplatform/power-bi/")],
    "Docker": [("Curso inicial de Docker", "https://docs.docker.com/get-started/")],
    "ComputaciÃ³n en la nube": [("AWS Cloud Practitioner", "https://aws.amazon.com/training/digital/aws-cloud-practitioner/")],
    "Linux": [("Tutoriales de Ubuntu/Linux", "https://ubuntu.com/tutorials")],
    "Seguridad informÃ¡tica": [("Fundamentos de seguridad - Microsoft Learn", "https://learn.microsoft.com/training/paths/describe-concepts-of-security-compliance-identity/")],
    "AutoCAD": [("Aprendizaje oficial de Autodesk", "https://www.autodesk.com/learn/ondemand/collection/architecture-engineering-construction")],
    "Revit / BIM": [("Aprendizaje oficial de Revit", "https://www.autodesk.com/learn/ondemand/collection/revit")],
    "MATLAB": [("MATLAB Onramp", "https://matlabacademy.mathworks.com/details/matlab-onramp/getting-started")],
    "C / C++ embebido": [("LearnCpp: curso de C++", "https://www.learncpp.com/")],
    "IoT": [("DocumentaciÃ³n de Arduino IoT", "https://docs.arduino.cc/")],
    "SAP / ERP": [("Cursos de SAP Learning", "https://learning.sap.com/")],
    "Lean Manufacturing": [("Recursos de Lean Enterprise Institute", "https://www.lean.org/explore-lean/")],
    "EstadÃ­stica": [("EstadÃ­stica - Khan Academy", "https://es.khanacademy.org/math/statistics-probability")],
    "GestiÃ³n de proyectos": [("Recursos de project management - PMI", "https://www.pmi.org/learning")],
    "Procesamiento de seÃ±ales": [("SeÃ±ales y sistemas - MIT OpenCourseWare", "https://ocw.mit.edu/search/?q=signals+and+systems")],
}

def _cfg(con):
    return {r["clave"]: r["valor"] for r in con.execute("SELECT clave, valor FROM configuracion")}

def nivel(pct, n_ofertas, cfg):
    if n_ofertas < cfg["muestra_minima"]: return "Muestra insuficiente"
    if pct >= cfg["umbral_alta"]: return "Alta"
    if pct >= cfg["umbral_media"]: return "Media"
    return "Baja"

def ranking(con):
    """Todas las habilidades con % de ofertas que las piden (índice de utilidad laboral)."""
    cfg = _cfg(con)
    total = con.execute("SELECT COUNT(*) FROM oferta").fetchone()[0]
    filas = con.execute("""
        SELECT h.id, h.nombre, h.categoria,
               COUNT(DISTINCT oh.oferta_id) AS n_ofertas,
               (SELECT COUNT(*) FROM materia_habilidad mh WHERE mh.habilidad_id = h.id) AS n_materias
        FROM habilidad h LEFT JOIN oferta_habilidad oh ON oh.habilidad_id = h.id
        GROUP BY h.id ORDER BY n_ofertas DESC, h.nombre""").fetchall()
    out = []
    for pos, f in enumerate(filas, 1):
        d = dict(f); d["pct"] = round(100 * f["n_ofertas"] / total, 1) if total else 0
        d["nivel"] = nivel(d["pct"], f["n_ofertas"], cfg); d["puesto"] = pos
        d["total_ofertas"] = total; out.append(d)
    return out

def buscar(con, texto):
    """Busca por nombre, alias o categoría (sin distinguir mayúsculas)."""
    q = f"%{texto.strip()}%"
    ids = {r["id"] for r in con.execute(
        "SELECT id FROM habilidad WHERE nombre LIKE ? OR alias LIKE ? OR categoria LIKE ?", (q, q, q))}
    return [r for r in ranking(con) if r["id"] in ids]

def recursos_aprendizaje(con, habilidad_ids=None, limite=8):
    """Recursos introductorios para habilidades sin materia asociada."""
    if habilidad_ids:
        marcas = ",".join("?" * len(habilidad_ids))
        filas = con.execute(
            f"SELECT id, nombre, categoria FROM habilidad WHERE id IN ({marcas}) ORDER BY nombre",
            habilidad_ids,
        ).fetchall()
    else:
        filas = con.execute(
            """SELECT h.id, h.nombre, h.categoria FROM habilidad h
               WHERE NOT EXISTS (
                 SELECT 1 FROM materia_habilidad mh WHERE mh.habilidad_id = h.id
               ) ORDER BY h.nombre LIMIT ?""",
            (limite,),
        ).fetchall()
    salida = []
    for fila in filas:
        recursos = RECURSOS_APRENDIZAJE.get(fila["nombre"])
        if not recursos:
            for nombre_recurso, candidatos in RECURSOS_APRENDIZAJE.items():
                try:
                    if nombre_recurso.encode("latin1").decode("utf-8") == fila["nombre"]:
                        recursos = candidatos
                        break
                except (UnicodeEncodeError, UnicodeDecodeError):
                    continue
        if not recursos:
            recursos = [(
                f"Buscar cursos de {fila['nombre']}",
                f"https://www.google.com/search?q=cursos+{quote(fila['nombre'])}",
            )]
        salida.append({
            "id": fila["id"],
            "nombre": fila["nombre"],
            "categoria": fila["categoria"],
            "recursos": [{"nombre": nombre, "url": url} for nombre, url in recursos],
        })
    return salida

def donde_se_ensena(con, habilidad_id):
    return con.execute("""
        SELECT p.nombre AS programa, m.nombre AS materia, m.semestre
        FROM materia_habilidad mh JOIN materia m ON m.id = mh.materia_id
        JOIN programa p ON p.id = m.programa_id
        WHERE mh.habilidad_id = ? ORDER BY p.nombre, m.semestre""", (habilidad_id,)).fetchall()

def demanda_por_perfil(con, habilidad_id):
    return con.execute("""
        SELECT o.titulo AS perfil, COUNT(*) AS total,
               SUM(CASE WHEN oh.habilidad_id IS NOT NULL THEN 1 ELSE 0 END) AS piden
        FROM oferta o LEFT JOIN oferta_habilidad oh ON oh.oferta_id = o.id AND oh.habilidad_id = ?
        GROUP BY o.titulo ORDER BY 1.0 * piden / total DESC""", (habilidad_id,)).fetchall()

def fragmentos(con, habilidad_id, limite=3):
    return con.execute("""SELECT o.titulo, o.empresa, o.fuente, oh.fragmento FROM oferta_habilidad oh
        JOIN oferta o ON o.id = oh.oferta_id WHERE oh.habilidad_id = ? LIMIT ?""", (habilidad_id, limite)).fetchall()

def detalle(con, habilidad_id):
    r = next((x for x in ranking(con) if x["id"] == habilidad_id), None)
    if not r: return None
    r["materias"] = donde_se_ensena(con, habilidad_id)
    r["perfiles"] = [dict(p, pct=round(100 * p["piden"] / p["total"])) for p in demanda_por_perfil(con, habilidad_id)]
    r["fragmentos"] = fragmentos(con, habilidad_id)
    r["ofertas_reales"] = ofertas_reales(con, habilidad_id=habilidad_id)
    return r

def ofertas_reales(con, habilidad_id=None, programa_id=None, limite=12):
    """Ofertas públicas verificadas manualmente, con enlace a la fuente."""
    params = []
    joins = ""
    where = ""
    if habilidad_id is not None:
        joins = " JOIN oferta_real_habilidad orh ON orh.oferta_id = o.id"
        where = " WHERE orh.habilidad_id = ?"
        params.append(habilidad_id)
    elif programa_id is not None:
        joins = " JOIN oferta_real_programa orp ON orp.oferta_id = o.id"
        where = " WHERE orp.programa_id = ?"
        params.append(programa_id)
    params.append(limite)
    ofertas = [dict(r) for r in con.execute(
        f"""SELECT DISTINCT o.* FROM oferta_real o {joins}{where}
            ORDER BY o.fecha_consulta DESC, o.id DESC LIMIT ?""", params
    ).fetchall()]
    for oferta in ofertas:
        oferta["habilidades"] = [
            r["nombre"] for r in con.execute(
                """SELECT h.nombre FROM oferta_real_habilidad orh
                   JOIN habilidad h ON h.id = orh.habilidad_id
                   WHERE orh.oferta_id = ? ORDER BY h.nombre""",
                (oferta["id"],),
            ).fetchall()
        ]
    return ofertas

def guardar_ofertas_reales(con, ofertas, diccionario, programa_id=None):
    """Guarda resultados nuevos sin duplicar enlaces y enlaza habilidades detectadas."""
    nuevos = 0
    for oferta in ofertas:
        con.execute(
            """INSERT OR IGNORE INTO oferta_real
               (titulo, empresa, ciudad, modalidad, salario, contrato, requisitos, fuente, url, fecha_consulta)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(oferta[k] for k in (
                "titulo", "empresa", "ciudad", "modalidad", "salario", "contrato",
                "requisitos", "fuente", "url", "fecha_consulta"
            )),
        )
        row = con.execute("SELECT id FROM oferta_real WHERE url = ?", (oferta["url"],)).fetchone()
        if not row:
            continue
        if programa_id is not None:
            con.execute(
                "INSERT OR IGNORE INTO oferta_real_programa VALUES (?, ?)",
                (row["id"], programa_id),
            )
        before = con.total_changes
        for habilidad_id, _fragmento in extraer(oferta["requisitos"], diccionario):
            con.execute(
                "INSERT OR IGNORE INTO oferta_real_habilidad VALUES (?, ?)",
                (row["id"], habilidad_id),
            )
        if con.total_changes > before:
            nuevos += 1
    con.commit()
    return nuevos

# ---------- Vista por carrera ----------
def programas(con):
    return [dict(r) for r in con.execute("""
        SELECT p.id, p.nombre,
          (SELECT COUNT(*) FROM materia m WHERE m.programa_id = p.id) AS n_materias,
          (SELECT COUNT(*) FROM oferta o WHERE o.titulo IN
              (SELECT perfil FROM programa_perfil pp WHERE pp.programa_id = p.id)) AS n_ofertas
        FROM programa p ORDER BY p.nombre""")]

def programa_detalle(con, pid):
    """Qué enseña la carrera, qué tan pedido es eso para SUS perfiles de empleo y qué se pide sin enseñarse."""
    cfg = _cfg(con)
    p = con.execute("SELECT id, nombre FROM programa WHERE id = ?", (pid,)).fetchone()
    if not p: return None
    perfiles = [r["perfil"] for r in con.execute("SELECT perfil FROM programa_perfil WHERE programa_id = ?", (pid,))]
    marca = ",".join("?" * len(perfiles))
    n_of = con.execute(f"SELECT COUNT(*) FROM oferta WHERE titulo IN ({marca})", perfiles).fetchone()[0]
    dem = {r["id"]: r for r in con.execute(f"""
        SELECT h.id, h.nombre, h.categoria, COUNT(DISTINCT oh.oferta_id) AS n
        FROM habilidad h JOIN oferta_habilidad oh ON oh.habilidad_id = h.id
        JOIN oferta o ON o.id = oh.oferta_id AND o.titulo IN ({marca}) GROUP BY h.id""", perfiles)}
    ensena = {}
    for r in con.execute("""SELECT h.id, h.nombre, h.categoria, m.nombre AS materia, m.semestre FROM materia_habilidad mh
        JOIN materia m ON m.id = mh.materia_id JOIN habilidad h ON h.id = mh.habilidad_id
        WHERE m.programa_id = ? ORDER BY m.semestre""", (pid,)):
        e = ensena.setdefault(r["id"], {"id": r["id"], "nombre": r["nombre"], "materias": []})
        e["materias"].append(f'{r["materia"]} (sem. {r["semestre"]})')
    def fila(hid, nombre, materias):
        n = dem[hid]["n"] if hid in dem else 0
        pct = round(100 * n / n_of, 1) if n_of else 0
        return {"id": hid, "nombre": nombre, "materias": materias, "n": n, "pct": pct,
                "nivel": nivel(pct, 999, cfg), "pocas": n < cfg["muestra_minima"]}
    ens = sorted((fila(h, e["nombre"], e["materias"]) for h, e in ensena.items()), key=lambda x: -x["pct"])
    faltan = sorted((fila(h, d["nombre"], []) for h, d in dem.items() if h not in ensena and 100 * d["n"] / n_of >= cfg["umbral_media"]),
                    key=lambda x: -x["pct"])
    utiles = [x for x in ens if x["nivel"] in ("Alta", "Media")]
    return {"id": p["id"], "nombre": p["nombre"], "perfiles": perfiles, "n_ofertas": n_of,
            "ensena": ens, "faltan": faltan, "n_utiles": len(utiles), "n_ensena": len(ens),
            "ofertas_reales": ofertas_reales(con, programa_id=pid)}
