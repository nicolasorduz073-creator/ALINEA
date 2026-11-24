"""Extractor de habilidades por diccionario (línea base del Sprint 1)."""
import re

def _patron(termino):
    t = re.escape(termino.strip())
    return re.compile(r"(?<![\w+#])" + t + r"(?![\w+#])", re.IGNORECASE)

def construir_diccionario(filas):
    """filas: (id, nombre, alias) -> [(id, [patrones])]"""
    d = []
    for hid, nombre, alias in filas:
        terminos = [nombre] + [a for a in alias.split("|") if a]
        d.append((hid, [_patron(t) for t in terminos]))
    return d

def extraer(texto, diccionario):
    """Devuelve [(habilidad_id, fragmento_origen)] sin repetir habilidades."""
    out = []
    for hid, patrones in diccionario:
        for p in patrones:
            m = p.search(texto)
            if m:
                a, b = max(0, m.start() - 40), min(len(texto), m.end() + 40)
                out.append((hid, "…" + texto[a:b].strip() + "…"))
                break
    return out
