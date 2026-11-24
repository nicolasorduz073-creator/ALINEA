"""Cliente opcional para consultar ofertas actuales mediante JSearch/RapidAPI.

No se guardan credenciales en el repositorio. Configurar RAPIDAPI_KEY en el
entorno activa la actualización desde ofertas públicas agregadas por JSearch.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class LiveJobsNotConfigured(RuntimeError):
    pass


def buscar_ofertas(perfiles, limite_por_perfil=5):
    api_key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not api_key:
        raise LiveJobsNotConfigured("Configura RAPIDAPI_KEY para actualizar ofertas en vivo.")

    ofertas = {}
    for perfil in perfiles:
        params = urlencode({
            "query": f"{perfil} Colombia",
            "page": "1",
            "num_pages": "1",
            "country": "co",
            "date_posted": "month",
        })
        request = Request(
            f"https://jsearch.p.rapidapi.com/search?{params}",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
                "Accept": "application/json",
            },
        )
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))

        for item in payload.get("data", [])[:limite_por_perfil]:
            url = item.get("job_apply_link") or item.get("job_google_link")
            if not url:
                continue
            descripcion = " ".join((item.get("job_description") or "").split())
            ofertas[url] = {
                "titulo": item.get("job_title") or perfil,
                "empresa": item.get("employer_name") or "Empresa no publicada",
                "ciudad": ", ".join(filter(None, [item.get("job_city"), item.get("job_state")])) or "Colombia",
                "modalidad": "Remota" if item.get("job_is_remote") else "No especificada",
                "salario": _salario(item),
                "contrato": item.get("job_employment_type") or "No especificado",
                "requisitos": descripcion[:900] or "Consulta los requisitos en la fuente original.",
                "fuente": f"JSearch / {item.get('job_publisher') or 'portal público'}",
                "url": url,
                "fecha_consulta": item.get("job_posted_at_datetime_utc", "")[:10] or "actualizada hoy",
            }
    return list(ofertas.values())


def _salario(item):
    minimo = item.get("job_min_salary")
    maximo = item.get("job_max_salary")
    moneda = item.get("job_salary_currency") or ""
    periodo = item.get("job_salary_period") or ""
    if minimo and maximo:
        return f"{moneda} {minimo:,.0f} - {maximo:,.0f} ({periodo})"
    if minimo:
        return f"Desde {moneda} {minimo:,.0f} ({periodo})"
    return "Salario no publicado"

