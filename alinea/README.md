# ALINEA

ALINEA es una plataforma académica de la Universidad Santo Tomás que conecta el plan de estudios de cinco ingenierías con las habilidades y ofertas del mercado laboral.

## Funcionalidades

- Catálogo de carreras: Sistemas, Telecomunicaciones, Industrial, Civil y Electrónica.
- Vista detallada por ingeniería con materias, habilidades, brechas y ofertas vinculadas.
- Buscador de habilidades por nombre, alias o categoría.
- Ranking de demanda laboral con porcentajes de aparición en ofertas.
- Recursos de aprendizaje para habilidades que no aparecen en las materias.
- Ofertas filtrables por cargo, empresa, ciudad y modalidad.
- Enlaces de postulación a LinkedIn, Computrabajo, Indeed y otras fuentes públicas.
- Actualización opcional de ofertas mediante JSearch/RapidAPI.
- Asistente conversacional ALINEA para encontrar carreras, habilidades y oportunidades.
- Registro con correo institucional de la Universidad Santo Tomás.
- ID incremental y fecha de llegada para cada usuario registrado.
- Consentimiento inicial de cookies técnicas.
- Página de ciberseguridad y privacidad.
- Manual de usuario en `/ayuda`.
- Tema claro/oscuro, diseño responsive e imágenes de carreras y habilidades.

## Rutas principales

| Ruta | Función |
|---|---|
| `/` | Carreras, métricas y ofertas generales |
| `/programa/<id>` | Detalle académico y laboral de una ingeniería |
| `/buscar` | Búsqueda de habilidades y recursos |
| `/habilidad/<id>` | Demanda, materias y ofertas relacionadas |
| `/ranking` | Ranking de habilidades por demanda |
| `/seguridad` | Ciberseguridad, cookies y privacidad |
| `/ayuda` | Manual de usuario |

## APIs internas

La interfaz se comunica con Flask mediante estos endpoints:

- `POST /api/asistente`: devuelve recomendaciones desde SQLite.
- `POST /api/registro`: valida el correo institucional y guarda el usuario.
- `POST /api/cookies`: registra el consentimiento técnico.
- `POST /api/ofertas/actualizar`: consulta ofertas nuevas para una carrera.

El asistente actual es local y basado en reglas, datos de la base y coincidencias de habilidades. No requiere una clave de OpenAI.

## Ofertas en vivo

La integración opcional está en `web/live_jobs.py` y utiliza JSearch mediante RapidAPI. Para activarla, configura:

```text
RAPIDAPI_KEY=tu_clave
```

Sin esa variable, ALINEA utiliza las ofertas de referencia guardadas en SQLite. Los enlaces de LinkedIn se convierten en búsquedas recientes por cargo, empresa y ciudad para evitar vínculos caducados.

## Registro y privacidad

ALINEA acepta estos dominios institucionales:

- `@usta.edu.co`
- `@usantotomas.edu.co`

No se almacenan contraseñas. La tabla `usuario` guarda nombre, correo, dominio, fecha de registro, último acceso y consentimiento de cookies. `evento_seguridad` conserva eventos básicos y un hash de la IP para auditoría, no la IP en texto plano.

En producción se recomienda usar HTTPS, definir `ALINEA_SECRET_KEY`, usar PostgreSQL para conservar registros y no subir `data/alinea.db` ni archivos `.env` a un repositorio público.

## Instalación local

Desde la carpeta `alinea`:

```bash
pip install -r requirements.txt
python -m db.seed
python -m web.app
```

La aplicación queda disponible en `http://127.0.0.1:5000/`.

Para buscar desde consola:

```bash
python buscar.py sql
```

## Despliegue en Render

El repositorio contiene `render.yaml`, `Procfile` y `requirements.txt` en la raíz.

Si el servicio usa como raíz la carpeta `alinea`:

```text
Build Command: pip install -r requirements.txt && python -m db.seed
Start Command: gunicorn web.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4
```

Si Render usa la raíz del repositorio:

```text
Start Command: gunicorn --chdir alinea web.app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4
```

El plan gratuito puede suspender la aplicación por inactividad. El archivo SQLite local puede reiniciarse durante despliegues, por lo que no se recomienda como almacenamiento permanente de usuarios.

## Estructura

```text
alinea/
├── db/                 SQLite, esquema, consultas y seed
├── nlp/                extracción de habilidades
├── web/
│   ├── app.py          rutas Flask y APIs internas
│   ├── live_jobs.py    integración opcional con JSearch
│   ├── static/         logos, CSS e ilustraciones
│   └── templates/      vistas HTML
├── data/               base SQLite local, excluida del repositorio
├── tests/              pruebas automatizadas
├── Procfile            comando de producción
└── render.yaml         configuración de Render
```

## Estado de los datos

Las ofertas, salarios y requisitos incluidos en el seed son datos de referencia. Las publicaciones externas pueden cerrar o cambiar; antes de postularse, el usuario debe confirmar la información en la fuente original.

## Autores

- Nicolás Orduz
- Kevin Sabogal
- Cristhian Caro

Universidad Santo Tomás · Equipo de Ingeniería de Telecomunicaciones.
