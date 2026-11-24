"""Búsqueda por consola:  python buscar.py python"""
import sys
from db.conexion import conectar
from db import consultas
con = conectar()
for r in consultas.buscar(con, " ".join(sys.argv[1:]) or "python"):
    d = consultas.detalle(con, r["id"])
    print(f"\n{d['nombre']}: {d['pct']} % de las ofertas ({d['n_ofertas']}/{d['total_ofertas']}) -> utilidad {d['nivel']} (puesto {d['puesto']})")
    print("  Se enseña en:", "; ".join(f"{m['programa']} · {m['materia']}" for m in d["materias"]) or "no se enseña")
