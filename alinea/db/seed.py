"""Crea la BD y la llena con datos ILUSTRATIVOS (no son datos reales de la USTA ni de Adzuna).
Uso:  python -m db.seed
"""
import random, pathlib
from urllib.parse import quote_plus
from db.conexion import conectar, RUTA_BD, RAIZ
from nlp.extractor import construir_diccionario, extraer

# (nombre, alias, categoría)
HABILIDADES = [
 ("Python","","Programación"),("SQL","PostgreSQL|MySQL|consultas a bases de datos","Datos"),
 ("Git","GitHub|control de versiones","Herramientas"),("Excel avanzado","tablas dinámicas|Excel","Datos"),
 ("Power BI","tableros de control","Datos"),("Docker","contenedores","Herramientas"),
 ("Linux","","Herramientas"),("Computación en la nube","AWS|Azure|cloud","Infraestructura"),
 ("Redes IP","TCP/IP|enrutamiento","Infraestructura"),("Seguridad informática","ciberseguridad|seguridad de redes","Infraestructura"),
 ("Gestión de proyectos","Scrum|PMI|metodologías ágiles","Gestión"),("AutoCAD","","Diseño"),
 ("Revit / BIM","BIM|Revit","Diseño"),("MATLAB","","Programación"),("C / C++ embebido","C++|microcontroladores","Programación"),
 ("IoT","internet de las cosas","Infraestructura"),("SAP / ERP","ERP|SAP","Gestión"),
 ("Lean Manufacturing","Lean|mejora continua","Gestión"),("Estadística","análisis estadístico","Datos"),
 ("Procesamiento de señales","DSP","Ingeniería"),
]
PROGRAMAS = {
 "Ingeniería de Sistemas": [("Programación I",2,["Python","Git"]),("Bases de datos",4,["SQL"]),("Redes de computadores",5,["Redes IP","Linux"]),
   ("Ingeniería de software",6,["Git","Gestión de proyectos"]),("Seguridad informática",8,["Seguridad informática"])],
 "Ingeniería de Telecomunicaciones": [("Redes de datos",5,["Redes IP","Linux"]),("Señales y sistemas",4,["Procesamiento de señales","MATLAB"]),
   ("Programación aplicada",3,["Python"]),("Sistemas embebidos",7,["C / C++ embebido","IoT"])],
 "Ingeniería Industrial": [("Producción",5,["Lean Manufacturing"]),("Estadística aplicada",4,["Estadística","Excel avanzado"]),
   ("Logística",6,["SAP / ERP"]),("Costos",7,["Excel avanzado"])],
 "Ingeniería Civil": [("Topografía y dibujo",3,["AutoCAD"]),("Construcción",8,["Gestión de proyectos"]),("Estructuras",6,["AutoCAD"])],
 "Ingeniería Electrónica": [("Microcontroladores",6,["C / C++ embebido"]),("Instrumentación",5,["MATLAB"]),("Programación",2,["Python"])],
}
# Perfiles de oferta: título, nº de ofertas, {habilidad: probabilidad de pedirla}
PERFILES = [
 ("Desarrollador de software",40,{"Python":.6,"SQL":.7,"Git":.8,"Docker":.45,"Computación en la nube":.4,"Gestión de proyectos":.3,"Linux":.3}),
 ("Analista de datos",30,{"SQL":.9,"Python":.7,"Power BI":.6,"Excel avanzado":.5,"Estadística":.3}),
 ("Ingeniero de redes",20,{"Redes IP":.9,"Linux":.5,"Seguridad informática":.5,"Computación en la nube":.3}),
 ("Ingeniero de producción",20,{"Excel avanzado":.6,"Lean Manufacturing":.55,"SAP / ERP":.4,"Gestión de proyectos":.4}),
 ("Ingeniero residente de obra",15,{"AutoCAD":.7,"Revit / BIM":.5,"Gestión de proyectos":.5,"Excel avanzado":.4}),
 ("Ingeniero de sistemas embebidos",10,{"C / C++ embebido":.8,"IoT":.5,"Python":.4,"Git":.3,"MATLAB":.2}),
]
PERFILES_POR_PROGRAMA = {
 "Ingeniería de Sistemas": ["Desarrollador de software","Analista de datos"],
 "Ingeniería de Telecomunicaciones": ["Ingeniero de redes","Ingeniero de sistemas embebidos"],
 "Ingeniería Industrial": ["Ingeniero de producción","Analista de datos"],
 "Ingeniería Civil": ["Ingeniero residente de obra"],
 "Ingeniería Electrónica": ["Ingeniero de sistemas embebidos","Ingeniero de redes"],
}

# Ofertas publicas consultadas en portales de empleo. Deben actualizarse
# periodicamente porque los anuncios pueden cerrar o cambiar de condiciones.
OFERTAS_REALES = [
    {
        "titulo": "Ingeniero de Sistemas - Inteligencia de Negocios",
        "empresa": "Servicios Profesionales",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "$3.794.000 + prestaciones y auxilio de transporte",
        "contrato": "Jornada completa",
        "requisitos": "Profesional en Sistemas o afines; 1 ano de experiencia; SQL, Power BI, ETL, MySQL y Python.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-at-servicios-profesionales-4460541680",
        "habilidades": ["SQL", "Power BI", "Python"],
    },
    {
        "titulo": "Ingeniero de sistemas, Analista de Sistemas de Informacion",
        "empresa": "CUN",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "$3.200.000 + prestaciones de ley",
        "contrato": "Indefinido",
        "requisitos": "Profesional en Sistemas; minimo 1 ano; Oracle, SQL/PL-SQL, Excel avanzado y sistemas de tickets.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-analista-sistemas-de-informacion-at-corporaci%C3%B3n-unificada-nacional-de-educaci%C3%B3n-superior-cun-4463669521",
        "habilidades": ["SQL", "Excel avanzado"],
    },
    {
        "titulo": "Ingeniero de Sistemas Embebidos",
        "empresa": "Sofia Sanjuan / Adecco",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "Hasta $12.000.000 segun experiencia",
        "contrato": "Obra labor 6 meses; luego indefinido",
        "requisitos": "Minimo 4 anos; C/C++, Linux, integracion entre dispositivos, hardware y troubleshooting.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-embebidos-at-sofia-sanjuan-4407892582",
        "habilidades": ["C / C++ embebido", "Linux", "IoT"],
    },
    {
        "titulo": "Ingeniero de Sistemas SAP",
        "empresa": "Comfama Empleo",
        "ciudad": "Medellin",
        "modalidad": "Presencial",
        "salario": "$5.000.000 - $6.000.000 + auxilios",
        "contrato": "Termino indefinido",
        "requisitos": "36 meses de experiencia en SAP; roles PFCG, usuarios SU01, transportes STMS, infraestructura TI y Linux.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-sap-at-comfama-empleo-4452653938",
        "habilidades": ["SAP / ERP", "Linux"],
    },
    {
        "titulo": "Ingeniero de infraestructura tecnologica",
        "empresa": "elempleo",
        "ciudad": "Bogota",
        "modalidad": "Mixta",
        "salario": "$5.500.000 + auxilio de comunicacion de $85.000",
        "contrato": "Obra o labor",
        "requisitos": "Profesional en Sistemas, Electronica o Telecomunicaciones; 2 anos; SAN/NAS, backup, virtualizacion e ingles B1.",
        "fuente": "LinkedIn / elempleo",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-con-experiencia-en-infraestructura-tecn%C3%B3logica-con-ingles-b1-at-elempleo-4450794741",
        "habilidades": ["Linux", "Computación en la nube"],
    },
    {
        "titulo": "Ingeniero de Sistemas Junior",
        "empresa": "Dinamica Grupo Empresarial",
        "ciudad": "Pereira",
        "modalidad": "Presencial",
        "salario": "$3.000.000 + prestaciones de ley",
        "contrato": "Directo con la compania",
        "requisitos": "Recién graduado; redes, Windows/Linux, Active Directory, VMware, telefonia IP y seguridad.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-junior-%E2%80%93-primera-oportunidad-profesional-at-din%C3%A1mica-grupo-empresarial-4476950659",
        "habilidades": ["Linux", "Redes IP", "Seguridad informática"],
    },
]
EMPRESAS = ["Tecnova","Andina Digital","Logiplus","Constructora Sabana","Redes del Sur","Manufacturas Cundí"]
OFERTAS_REALES.extend([
    {
        "titulo": "Ingeniero Residente de Interventoria",
        "empresa": "D&B Ingenieros Civiles",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "$6.000.000 + prestaciones de ley",
        "contrato": "Tiempo completo",
        "requisitos": "Ingenieria Civil; tarjeta profesional; minimo 4 anos de titulado y 2 anos en obra o interventoria; planos, cronogramas, presupuestos y AutoCAD.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-residente-de-interventoria-at-d-b-ingenieros-civiles-4480514569",
        "habilidades": ["AutoCAD", "Gestión de proyectos"],
    },
    {
        "titulo": "Ingeniero(a) Civil",
        "empresa": "Empleos del Eje",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "A convenir segun experiencia",
        "contrato": "Termino fijo",
        "requisitos": "Ingeniero Civil titulado; 2 anos en direccion y supervision de obras; planos, presupuestos, cronogramas y normatividad de construccion.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-a-civil-at-empleos-del-eje-4475978046",
        "habilidades": ["AutoCAD", "Gestión de proyectos"],
    },
    {
        "titulo": "Ingeniero industrial con especializacion SST",
        "empresa": "Coleccion Talento",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "$4.104.000 + $49.500 + auxilio de transporte",
        "contrato": "Jornada completa",
        "requisitos": "Ingenieria Industrial; especializacion SST; 2 a 5 anos; PESV, SG-SST, gestion de riesgos y auditoria.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-industrial-con-especializacion-sst-experiencia-en-seguridad-vial-at-colecci%C3%B3n-talento-4471959437",
        "habilidades": ["GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniero Industrial - Procesos y Lean Manufacturing",
        "empresa": "M&J Soluciones",
        "ciudad": "Bogota",
        "modalidad": "Presencial",
        "salario": "$3.000.000 + prestaciones; honorarios iniciales $4.000.000",
        "contrato": "Prestacion de servicios inicial",
        "requisitos": "Ingeniero Industrial; 5 anos en manufactura; Lean, 5S, Kaizen, KPI, Excel avanzado y liderazgo de planta.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-industrial-at-m-j-soluciones-estrategicas-e-integrales-4467786254",
        "habilidades": ["Lean Manufacturing", "Excel avanzado"],
    },
    {
        "titulo": "Ingeniero Electronico",
        "empresa": "EUROCARES SAS",
        "ciudad": "Medellin",
        "modalidad": "Presencial",
        "salario": "No publicado",
        "contrato": "Obra o labor",
        "requisitos": "Ingenieria Electronica; electronica analogica y digital; circuit design, PCBs, testing, CAD/EDA e instrumentacion de laboratorio.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-electr%C3%B3nico-at-eurocares-sas-4424760960",
        "habilidades": ["C / C++ embebido", "MATLAB"],
    },
    {
        "titulo": "Ingeniero residente Telecomunicaciones",
        "empresa": "Inmel Ingenieria",
        "ciudad": "Medellin",
        "modalidad": "Presencial",
        "salario": "$4.200.000 + bono de productividad",
        "contrato": "Termino fijo",
        "requisitos": "Ingeniero de Telecomunicaciones con tarjeta profesional; 5 anos; FTTH, coordinacion de proyectos, Office y disponibilidad para viajar.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-residente-telecomunicaciones-medell%C3%ADn-at-inmel-ingenier%C3%ADa-4238226110",
        "habilidades": ["Redes IP", "Gestión de proyectos"],
    },
    {
        "titulo": "Ingeniero de redes de IT",
        "empresa": "Coltecno",
        "ciudad": "Bogota",
        "modalidad": "No especificada",
        "salario": "No publicado",
        "contrato": "No especificado",
        "requisitos": "Ingenieria de Telecomunicaciones, Electronica o Sistemas; datacenter, switching, routing, access points y seguridad de red.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-redes-de-it-at-coltecno-4468334242",
        "habilidades": ["Redes IP", "Seguridad informática"],
    },
])

# Publicaciones adicionales consultadas en LinkedIn el 2026-10-22.
# Se conservan como referencia: la vigencia depende del portal original.
OFERTAS_REALES.extend([
    {
        "titulo": "Ingeniero de sistemas con experiencia en seguridad informatica",
        "empresa": "ENLACE EMPRESARIAL DE SERVICIOS S.A",
        "ciudad": "Bogota", "modalidad": "Presencial",
        "salario": "$3.000.000 + auxilio de transporte + prestaciones",
        "contrato": "Jornada completa",
        "requisitos": "Ingeniero de Sistemas; minimo 2 anos; seguridad informatica, administracion de sistemas, indicadores y soporte a usuarios.",
        "fuente": "LinkedIn",
        "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-con-experiencia-en-seguridad-inform%C3%A1tica-at-enlace-empresarial-de-servicios-s-a-4444230184",
        "habilidades": ["Seguridad informÃ¡tica", "Linux", "GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniera de Sistemas", "empresa": "RedCom Ltda", "ciudad": "Bogota",
        "modalidad": "Presencial", "salario": "No publicado", "contrato": "Jornada completa",
        "requisitos": "Ingenieria de Sistemas o Software; 3 anos; bases de datos, redes, analitica y resolucion de problemas tecnicos.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniera-de-sistemas-at-redcom-ltda-4478531328",
        "habilidades": ["SQL", "Redes IP", "GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniero de Telecomunicaciones y Automatizacion", "empresa": "Confidential", "ciudad": "Bogota",
        "modalidad": "Presencial", "salario": "No publicado", "contrato": "Jornada completa",
        "requisitos": "Ingenieria de Telecomunicaciones, Electronica o Sistemas; telefonia en la nube, VoIP, APIs, scripting y herramientas BI.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-de-telecomunicaciones-automatizaci%C3%B3n-at-confidential-4480125348",
        "habilidades": ["Redes IP", "Python", "Power BI"],
    },
    {
        "titulo": "Ingeniero de telecomunicaciones", "empresa": "Latcom SAS", "ciudad": "Bogota",
        "modalidad": "Presencial", "salario": "No publicado", "contrato": "Jornada completa",
        "requisitos": "Diseno, implementacion y mantenimiento de redes de datos; troubleshooting, VoIP, monitorizacion y seguridad.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-de-telecomunicaciones-at-latcom-sas-4473908694",
        "habilidades": ["Redes IP", "Seguridad informÃ¡tica", "Linux"],
    },
    {
        "titulo": "Ingeniero Industrial (Planta de Procesos de alimentos)", "empresa": "Carnes la Suiza", "ciudad": "Bogota",
        "modalidad": "Presencial", "salario": "Salario competitivo + beneficios", "contrato": "Jornada completa",
        "requisitos": "Ingenieria Industrial o de Alimentos; 3 a 5 anos liderando plantas; productividad, calidad, inventarios y mejora continua.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-industrial-planta-de-procesos-de-alimentos-at-carnes-la-suiza-4480180434",
        "habilidades": ["Lean Manufacturing", "Excel avanzado", "GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniero industrial", "empresa": "Agencia Publica de Empleo SENA", "ciudad": "Ibague",
        "modalidad": "Presencial", "salario": "$4.000.000", "contrato": "Termino fijo",
        "requisitos": "Ingenieria Industrial; minimo 2 anos en procesos industriales, supervision y control de equipos termicos.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-industrial-at-agencia-p%C3%BAblica-de-empleo-sena-4468824377",
        "habilidades": ["Lean Manufacturing", "Excel avanzado"],
    },
    {
        "titulo": "Ingeniero civil de estructuras", "empresa": "Construcciones el Nuevo Milenio S.A.S", "ciudad": "Bogota",
        "modalidad": "Presencial", "salario": "A convenir", "contrato": "No especificado",
        "requisitos": "Ingenieria Civil; minimo 2 anos; supervision de obras, AutoCAD, Excel, lectura de planos y programacion de obra.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-civil-de-estructuras-at-construcciones-el-nuevo-milenio-s-a-s-4479554894",
        "habilidades": ["AutoCAD", "Revit / BIM", "Excel avanzado"],
    },
    {
        "titulo": "Ingeniero Civil", "empresa": "HMV Ingenieros", "ciudad": "Medellin",
        "modalidad": "Presencial", "salario": "No publicado", "contrato": "Jornada completa",
        "requisitos": "Profesional en Ingenieria Civil; 3 anos en diseno estructural; AutoCAD, SAP 2000, ETABS, Project y Civil 3D.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-civil-at-hmv-ingenieros-4467914103",
        "habilidades": ["AutoCAD", "Revit / BIM", "GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniero Electronico sin experiencia Cali", "empresa": "Comfenalco Valle delagente", "ciudad": "Cali",
        "modalidad": "Presencial", "salario": "1 a 2 SMMLV + prestaciones de ley", "contrato": "Indefinido",
        "requisitos": "Ingenieria Electronica o estudiante proximo a graduarse; instrumentos de medicion, osciloscopio, multimetro y diagnostico.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-electronico-sin-experiencia-cali-at-comfenalco-valle-delagente-4481796750",
        "habilidades": ["C / C++ embebido", "MATLAB"],
    },
    {
        "titulo": "Ingeniero Electronico", "empresa": "INEL LTDA", "ciudad": "Bogota",
        "modalidad": "Presencial", "salario": "A convenir", "contrato": "Jornada completa",
        "requisitos": "Ingenieria Electronica; tarjeta profesional; sistemas RITEL, CCTV, control de acceso y telecomunicaciones.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-electronico-at-inel-ltda-4476530413",
        "habilidades": ["C / C++ embebido", "Redes IP", "GestiÃ³n de proyectos"],
    },
])

OFERTAS_REALES.extend([
    {
        "titulo": "Ingeniero de infraestructura TI, Datacenter",
        "empresa": "Alianza Temporales SAS",
        "ciudad": "Bogota", "modalidad": "Hibrida",
        "salario": "$4.230.000 + $470.000 de auxilio de alimentacion",
        "contrato": "Obra o labor", "requisitos": "Ingenieria de Sistemas, Electronica o Telecomunicaciones; 3 anos; infraestructura, servidores, redes, virtualizacion, cloud y seguridad.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-de-infraestructura-ti-datacenter-at-alianza-temporales-sas-4465776862",
        "habilidades": ["Linux", "Redes IP", "ComputaciÃ³n en la nube"],
    },
    {
        "titulo": "Ingeniero de sistemas",
        "empresa": "Morango", "ciudad": "Bogota", "modalidad": "Presencial",
        "salario": "A convenir segun perfil y experiencia", "contrato": "Directo con la empresa",
        "requisitos": "Ingenieria de Sistemas; minimo 3 anos; SIESA, desarrollo, integraciones, soporte y optimizacion de procesos.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-de-sistemas-at-morango-4468669714",
        "habilidades": ["Python", "SQL", "GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniero Civil - Infraestructura y Obras Civiles",
        "empresa": "TSG The IT Experts", "ciudad": "Bogota", "modalidad": "Presencial",
        "salario": "No publicado", "contrato": "Prestacion de servicios",
        "requisitos": "Ingenieria Civil; minimo 2 anos; supervision de obras, planos, infraestructura, canalizaciones y coordinacion tecnica.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-civil-infraestructura-y-obras-civiles-at-tsg-the-it-experts-4478127388",
        "habilidades": ["AutoCAD", "GestiÃ³n de proyectos"],
    },
    {
        "titulo": "Ingeniero Electronico - Electromecanico",
        "empresa": "Susequid SAS", "ciudad": "Bogota", "modalidad": "Presencial",
        "salario": "A convenir + prestaciones de ley", "contrato": "Termino indefinido",
        "requisitos": "Ingenieria Electronica o Electromecanica; minimo 2 anos; sistemas fotovoltaicos, planos, automatismos y liderazgo tecnico.",
        "fuente": "LinkedIn", "url": "https://co.linkedin.com/jobs/view/ingeniero-electronico-electromec%C3%A1nico-at-susequid-sas-4478488444",
        "habilidades": ["C / C++ embebido", "GestiÃ³n de proyectos"],
    },
])

OFERTAS_POR_PROGRAMA = {
    "Ingeniería de Sistemas": [
        "Ingeniero de Sistemas - Inteligencia de Negocios",
        "Ingeniero de sistemas, Analista de Sistemas de Informacion",
        "Ingeniero de Sistemas SAP",
        "Ingeniero de Sistemas Junior",
    ],
    "Ingeniería de Telecomunicaciones": ["Ingeniero de infraestructura tecnologica", "Ingeniero de Sistemas Embebidos", "Ingeniero residente Telecomunicaciones", "Ingeniero de redes de IT"],
    "Ingeniería Electrónica": ["Ingeniero de Sistemas Embebidos", "Ingeniero de infraestructura tecnologica", "Ingeniero Electronico", "Ingeniero de redes de IT"],
    "Ingeniería Industrial": ["Ingeniero de Sistemas - Inteligencia de Negocios", "Ingeniero de infraestructura tecnologica", "Ingeniero industrial con especializacion SST", "Ingeniero Industrial - Procesos y Lean Manufacturing"],
    "Ingeniería Civil": ["Ingeniero Residente de Interventoria", "Ingeniero(a) Civil"],
}
OFERTAS_ADICIONALES_POR_PROGRAMA = {
    "Sistemas": ["Ingeniero de sistemas con experiencia en seguridad informatica", "Ingeniera de Sistemas", "Ingeniero de infraestructura TI, Datacenter", "Ingeniero de sistemas"],
    "Telecomunicaciones": ["Ingeniero de Telecomunicaciones y Automatizacion", "Ingeniero de telecomunicaciones", "Ingeniero de infraestructura TI, Datacenter"],
    "Electr": ["Ingeniero Electronico sin experiencia Cali", "Ingeniero Electronico", "Ingeniero de infraestructura TI, Datacenter", "Ingeniero Electronico - Electromecanico"],
    "Industrial": ["Ingeniero Industrial (Planta de Procesos de alimentos)", "Ingeniero industrial"],
    "Civil": ["Ingeniero civil de estructuras", "Ingeniero Civil", "Ingeniero Civil - Infraestructura y Obras Civiles"],
}
for clave_programa, titulos in OFERTAS_ADICIONALES_POR_PROGRAMA.items():
    programa = next((nombre for nombre in OFERTAS_POR_PROGRAMA if clave_programa in nombre), None)
    if programa:
        OFERTAS_POR_PROGRAMA[programa].extend(titulos)

# LinkedIn cierra o redirige las publicaciones individuales con frecuencia.
# Usamos una búsqueda viva por cargo, empresa y ciudad para que el botón nunca
# apunte a una página caducada y siempre muestre vacantes recientes.
for oferta in OFERTAS_REALES:
    if "linkedin" in oferta["fuente"].lower():
        consulta = " ".join((oferta["titulo"], oferta["empresa"]))
        oferta["url"] = (
            "https://www.linkedin.com/jobs/search/?keywords="
            f"{quote_plus(consulta)}&location={quote_plus(oferta['ciudad'])}&f_TPR=r2592000"
        )
        oferta["fuente"] = "LinkedIn · búsqueda reciente"

FRASES = {"Python":"Experiencia en {} para automatizar procesos","SQL":"Dominio de {} y modelado de datos","Git":"Manejo de {} en trabajo colaborativo",
 "Docker":"Despliegues con {}","Computación en la nube":"Conocimientos de {} (AWS o Azure)","Gestión de proyectos":"Deseable {} con Scrum",
 "Linux":"Administración básica de {}","Power BI":"Construcción de tableros en {}","Excel avanzado":"{} con tablas dinámicas","Estadística":"Fundamentos de {}",
 "Redes IP":"Configuración de {} y enrutamiento","Seguridad informática":"Nociones de {}","Lean Manufacturing":"Conocimiento de {}","SAP / ERP":"Uso de {}",
 "AutoCAD":"Manejo de {}","Revit / BIM":"Modelado en {}","C / C++ embebido":"Programación en {}","IoT":"Proyectos de {}","MATLAB":"Simulación en {}"}

def main():
    if RUTA_BD.exists(): RUTA_BD.unlink()
    con = conectar()
    con.executescript((RAIZ / "db" / "schema.sql").read_text(encoding="utf-8"))
    for n, a, c in HABILIDADES:
        con.execute("INSERT INTO habilidad(nombre,alias,categoria) VALUES (?,?,?)", (n, a, c))
    hid = {r["nombre"]: r["id"] for r in con.execute("SELECT id,nombre FROM habilidad")}
    def habilidad_id(nombre):
        for _ in range(3):
            if nombre in hid:
                return hid[nombre]
            try:
                nombre = nombre.encode("latin1").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                break
        raise KeyError(nombre)
    programa_ids = {}
    for prog, mats in PROGRAMAS.items():
        pid = con.execute("INSERT INTO programa(nombre) VALUES (?)", (prog,)).lastrowid
        programa_ids[prog] = pid
        for pf in PERFILES_POR_PROGRAMA[prog]:
            con.execute("INSERT INTO programa_perfil VALUES (?,?)", (pid, pf))
        for nom, sem, habs in mats:
            mid = con.execute("INSERT INTO materia(programa_id,nombre,semestre) VALUES (?,?,?)", (pid, nom, sem)).lastrowid
            for h in habs:
                con.execute("INSERT INTO materia_habilidad VALUES (?,?,?)", (mid, hid[h], f"Unidad de {nom}: {h}"))
    random.seed(2026)
    for titulo, n, probs in PERFILES:
        for i in range(n):
            pedidas = [h for h, p in probs.items() if random.random() < p]
            desc = f"Buscamos {titulo.lower()}. " + ". ".join(FRASES[h].format(h) for h in pedidas) + ". Trabajo en equipo."
            con.execute("INSERT OR IGNORE INTO oferta(titulo,empresa,ciudad,fuente,fecha,descripcion) VALUES (?,?,?,?,?,?)",
                (f"{titulo}", random.choice(EMPRESAS), "Bogotá", "ejemplo", f"2026-10-{random.randint(1,18):02d}", desc + f" (ref. {i})"))
    # Extracción: el mismo código que se usará con ofertas reales
    for oferta in OFERTAS_REALES:
        oid = con.execute(
            """INSERT INTO oferta_real
               (titulo,empresa,ciudad,modalidad,salario,contrato,requisitos,fuente,url,fecha_consulta)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (oferta["titulo"], oferta["empresa"], oferta["ciudad"], oferta["modalidad"],
             oferta["salario"], oferta["contrato"], oferta["requisitos"], oferta["fuente"],
             oferta["url"], "2026-10-19"),
        ).lastrowid
        for habilidad in oferta["habilidades"]:
            con.execute("INSERT INTO oferta_real_habilidad VALUES (?,?)", (oid, habilidad_id(habilidad)))
        for programa, titulos in OFERTAS_POR_PROGRAMA.items():
            if oferta["titulo"] in titulos:
                con.execute("INSERT INTO oferta_real_programa VALUES (?,?)", (oid, programa_ids[programa]))
    dic = construir_diccionario(con.execute("SELECT id,nombre,alias FROM habilidad").fetchall())
    for o in con.execute("SELECT id,descripcion FROM oferta").fetchall():
        for h, frag in extraer(o["descripcion"], dic):
            con.execute("INSERT OR IGNORE INTO oferta_habilidad VALUES (?,?,?)", (o["id"], h, frag))
    for k, v in {"umbral_alta": 30, "umbral_media": 10, "muestra_minima": 5}.items():
        con.execute("INSERT INTO configuracion VALUES (?,?)", (k, v))
    con.commit()
    print("BD creada:", RUTA_BD)
    for t in ("programa","materia","habilidad","oferta","oferta_habilidad","materia_habilidad"):
        print(f"  {t}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]}")

if __name__ == "__main__":
    main()
