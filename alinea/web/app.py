from flask import Flask, render_template, request, abort, jsonify, session, make_response
from datetime import datetime, timezone
import hashlib
import os
import re
from db.conexion import conectar
from db import consultas
from nlp.extractor import construir_diccionario
from web.live_jobs import buscar_ofertas, LiveJobsNotConfigured

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("ALINEA_SECRET_KEY", "alinea-dev-key-change-in-production"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("ALINEA_COOKIE_SECURE", "0") == "1",
)

INSTITUTIONAL_DOMAINS = {"usta.edu.co", "usantotomas.edu.co"}

def ahora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def correo_institucional(correo):
    correo = correo.strip().lower()
    match = re.fullmatch(r"[a-z0-9._%+\-]+@([a-z0-9.\-]+)", correo)
    return correo, bool(match and match.group(1) in INSTITUTIONAL_DOMAINS), (match.group(1) if match else "")

def registrar_evento(con, usuario_id, evento):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest() if ip else ""
    con.execute("INSERT INTO evento_seguridad (usuario_id, evento, fecha, ip_hash) VALUES (?, ?, ?, ?)",
                (usuario_id, evento, ahora(), ip_hash))

@app.after_request
def cabeceras_seguridad(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return response

@app.route("/")
def carreras():
    con = conectar()
    return render_template("carreras.html", progs=consultas.programas(con), ofertas=consultas.ofertas_reales(con))

@app.route("/programa/<int:pid>")
def programa(pid):
    d = consultas.programa_detalle(conectar(), pid)
    if not d: abort(404)
    return render_template("programa.html", p=d)

@app.route("/buscar")
def inicio():
    con = conectar(); q = request.args.get("q", "").strip()
    rk = consultas.ranking(con)
    res = consultas.buscar(con, q) if q else None
    ids_sin_materia = [r["id"] for r in (res or []) if not r["n_materias"]]
    recursos = consultas.recursos_aprendizaje(con, ids_sin_materia) if q and ids_sin_materia else (
        [] if q else consultas.recursos_aprendizaje(con)
    )
    return render_template("inicio.html", q=q, res=res, top=rk[:8], total=rk[0]["total_ofertas"] if rk else 0, recursos=recursos)

@app.route("/habilidad/<int:hid>")
def habilidad(hid):
    d = consultas.detalle(conectar(), hid)
    if not d: abort(404)
    return render_template("habilidad.html", h=d)

@app.route("/ranking")
def ranking():
    return render_template("ranking.html", rk=consultas.ranking(conectar()))

@app.route("/seguridad")
def seguridad():
    con = conectar()
    total = con.execute("SELECT COUNT(*) AS total FROM usuario").fetchone()["total"]
    return render_template("seguridad.html", total_registros=total)

@app.post("/api/registro")
def registro():
    data = request.get_json(silent=True) or request.form
    nombre = str(data.get("nombre", "")).strip()[:80]
    correo, valido, dominio = correo_institucional(str(data.get("correo", "")))
    consentimiento = data.get("cookies", True)
    if not valido:
        return jsonify(ok=False, mensaje="Usa tu correo institucional @usta.edu.co o @usantotomas.edu.co."), 400
    con = conectar()
    ahora_ = ahora()
    existente = con.execute("SELECT id FROM usuario WHERE correo = ?", (correo,)).fetchone()
    if existente:
        usuario_id = existente["id"]
        con.execute("UPDATE usuario SET nombre = ?, ultimo_acceso = ?, cookie_consentimiento = ? WHERE id = ?",
                    (nombre, ahora_, int(bool(consentimiento)), usuario_id))
        mensaje = "Tu sesión institucional fue actualizada."
        evento = "inicio_sesion"
    else:
        cur = con.execute("""INSERT INTO usuario
            (nombre, correo, dominio, fecha_registro, ultimo_acceso, cookie_consentimiento)
            VALUES (?, ?, ?, ?, ?, ?)""", (nombre, correo, dominio, ahora_, ahora_, int(bool(consentimiento))))
        usuario_id = cur.lastrowid
        mensaje = "Registro completado. Bienvenido a ALINEA."
        evento = "registro"
    registrar_evento(con, usuario_id, evento)
    con.commit()
    session["usuario_id"] = usuario_id
    session["usuario_correo"] = correo
    response = make_response(jsonify(ok=True, id=usuario_id, mensaje=mensaje))
    response.set_cookie("alinea_cookie_consent", "accepted", max_age=60 * 60 * 24 * 180,
                        httponly=True, samesite="Lax", secure=app.config["SESSION_COOKIE_SECURE"])
    return response

@app.post("/api/cookies")
def cookies():
    response = make_response(jsonify(ok=True))
    response.set_cookie("alinea_cookie_consent", "accepted", max_age=60 * 60 * 24 * 180,
                        httponly=True, samesite="Lax", secure=app.config["SESSION_COOKIE_SECURE"])
    return response

@app.post("/api/asistente")
def asistente():
    data = request.get_json(silent=True) or {}
    pregunta = str(data.get("mensaje", "")).strip()[:300]
    if not pregunta:
        return jsonify(ok=False, mensaje="Escribe una pregunta para poder ayudarte."), 400
    con = conectar()
    texto = pregunta.lower()
    ranking_ = consultas.ranking(con)
    ofertas = consultas.ofertas_reales(con, limite=6)
    programas_ = consultas.programas(con)
    if any(palabra in texto for palabra in ("oferta", "trabajo", "empleo", "vacante", "postular")):
        respuesta = "Encontré oportunidades públicas que puedes filtrar por carrera, ciudad y modalidad."
        sugerencias = [{"titulo": o["titulo"], "detalle": f'{o["empresa"]} · {o["ciudad"]} · {o["modalidad"]}', "url": o["url"]} for o in ofertas]
    elif any(palabra in texto for palabra in ("carrera", "ingeniería", "ingenieria", "estudiar")):
        respuesta = "Puedo ayudarte a comparar estas carreras y sus habilidades más demandadas: " + ", ".join(p["nombre"] for p in programas_[:5]) + "."
        sugerencias = [{"titulo": p["nombre"], "detalle": f'{p["n_materias"]} materias · {p["n_ofertas"]} ofertas de referencia', "url": f'/programa/{p["id"]}'} for p in programas_]
    else:
        consulta = consultas.buscar(con, pregunta)
        if consulta:
            respuesta = f"La habilidad que más coincide es {consulta[0]['nombre']}. Tiene utilidad {consulta[0]['nivel'].lower()} y aparece en {consulta[0]['n_ofertas']} ofertas."
            sugerencias = [{"titulo": r["nombre"], "detalle": f'{r["pct"]}% de demanda · {r["nivel"]}', "url": f'/habilidad/{r["id"]}'} for r in consulta[:5]]
        else:
            top = ranking_[:5]
            respuesta = "Puedo buscar carreras, habilidades, ofertas, requisitos y rutas de aprendizaje. Prueba: ‘¿qué ofertas hay para telecomunicaciones?’ o ‘quiero aprender Python’."
            sugerencias = [{"titulo": r["nombre"], "detalle": f'{r["pct"]}% de demanda', "url": f'/habilidad/{r["id"]}'} for r in top]
    return jsonify(ok=True, respuesta=respuesta, sugerencias=sugerencias)

@app.post("/api/ofertas/actualizar")
def actualizar_ofertas():
    data = request.get_json(silent=True) or {}
    pid = data.get("programa_id")
    if not isinstance(pid, int):
        return jsonify(ok=False, mensaje="Falta el programa que se quiere actualizar."), 400
    con = conectar()
    programa = consultas.programa_detalle(con, pid)
    if not programa:
        return jsonify(ok=False, mensaje="La ingeniería no existe."), 404
    try:
        ofertas = buscar_ofertas(programa["perfiles"])
    except LiveJobsNotConfigured as exc:
        return jsonify(ok=False, configuracion=True, mensaje=str(exc)), 503
    except Exception:
        return jsonify(ok=False, mensaje="La fuente de ofertas no respondió. Intenta nuevamente."), 502
    diccionario = construir_diccionario(con.execute("SELECT id,nombre,alias FROM habilidad").fetchall())
    nuevas = consultas.guardar_ofertas_reales(con, ofertas, diccionario, programa_id=pid)
    return jsonify(
        ok=True,
        nuevas=nuevas,
        ofertas=consultas.ofertas_reales(con, programa_id=pid, limite=12),
        mensaje=f"Actualización terminada: {nuevas} oferta(s) nueva(s).",
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
