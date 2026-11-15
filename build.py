#!/usr/bin/env python3
"""
Generador de la web de Busco Tu Coche.

Uso:
    python3 build.py            -> genera la web en docs/ (lo que publica GitHub Pages)
    python3 build.py --preview  -> genera una copia en preview/ con enlaces a index.html

Para cambiar textos, coches o datos de contacto, edita este archivo (CONFIGURACIÓN y DATOS)
o data/stock.json, y vuelve a ejecutar el script.
"""
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = "--preview" in sys.argv
OUT = os.path.join(ROOT, "preview" if PREVIEW else "docs")

# =====================================================================
# CONFIGURACIÓN
# =====================================================================
BRAND = "Busco Tu Coche"
DOMAIN = "www.buscotucoche.com"      # dominio principal (sin https). buscotuclasico.com redirige aquí desde el proveedor del dominio
PHONE_DISPLAY = "+34 629 61 76 93"
PHONE_TEL = "+34629617693"
WHATSAPP = "34629617693"
EMAIL = "info@buscotucoche.es"
CITY = "Madrid, España"
# Servicio para recibir los formularios en el correo (p. ej. "https://formspree.io/f/xxxxxxx").
# Si se deja vacío, los formularios abren WhatsApp con la solicitud ya escrita.
FORM_ENDPOINT = ""
YEAR = 2026

WA_DEFAULT = f"Hola, me interesa importar un coche con {BRAND}"

# =====================================================================
# DATOS
# =====================================================================
ORIGINS = {
    "ae": "Dubái",
    "usa": "EE. UU.",
    "jp": "Japón",
    "de": "Alemania",
}

# (nombre, año, origen, foto real si la hay, carrocería de la ilustración, color)
STREET_CARS = [
    ("Ford Mustang Boss 429", 1969, "usa", "car-mustang-boss.jpg", "classic", "#1f3f8f"),
    ("Lamborghini Urus", 2021, "ae", "car-urus.jpg", "suv", "#f07c19"),
    ("Toyota Supra MK4 Turbo", 1994, "jp", "car-supra.jpg", "jdm", "#d1281f"),
    ("Porsche 911 Turbo S", 2022, "de", "car-porsche.jpg", "coupe", "#c3c7cd"),
    ("BMW M5 Competition", 2023, "de", "car-bmw.jpg", "sedan", "#1d3557"),
    ("Mercedes-AMG G63", 2022, "ae", "car-mercedes-g.jpg", "boxy", "#22252b"),
    ("Range Rover SVR", 2021, "ae", "car-range-rover.jpg", "suv", "#e9e9e6"),
    ("Chevrolet Camaro SS", 2020, "usa", "car-camaro.jpg", "muscle", "#f0c419"),
    ("Dodge Charger Hellcat", 2021, "usa", "car-charger.jpg", "muscle", "#5b2a86"),
    ("Chevrolet Corvette C8", 2022, "usa", "car-corvette.jpg", "coupe", "#c1121f"),
    ("Ford Mustang GT 5.0", 2020, "usa", "car-mustang.jpg", "muscle", "#1565c0"),
    ("Mercedes-Benz E 500", 1994, "de", "car-mercedes-e500.jpg", "w124", "#2b2f36"),
]

# (nombre, año, origen, foto, tipo, carrocería, color, dorsal)
RACE_CARS = [
    ("BMW 325i E30", 1988, "de", "car-bmw-325.jpg", "circuito", "e30", "#f2f2f2", 25),
    ("Nissan Skyline R34 GT-R", 1999, "jp", "car-skyline.jpg", "circuito", "jdm", "#2a5bd7", 34),
    ("Ford Mustang V8 de circuito", 2023, "usa", "car-competition.jpg", "circuito", "race", "#e0412f", 8),
    ("Nissan 350Z Drift Spec", 2006, "jp", "car-350z-drift.jpg", "drift", "jdm", "#f97316", None),
    ("BMW Serie 3 E46 Drift", 2004, "de", "car-bmw-drift.jpg", "drift", "sedan", "#e8eaed", None),
]

# (nivel, slug, descripción, [(coche, foto, carrocería, color)])
DRIFT_LEVELS = [
    ("Principiantes", "principiante",
     "Coches manejables, baratos de mantener, perfectos para tus primeros derrapes.",
     [("BMW Serie 3 E36", "drift-bmw-e36.jpg", "sedan", "#2e7d32"), ("BMW Serie 3 E46", "drift-bmw-e46.jpg", "sedan", "#c0c4ca"),
      ("Lexus IS200", "drift-lexus-is200.jpg", "sedan", "#8e1b1b"), ("Lexus IS300", "drift-lexus-is300.jpg", "sedan", "#1d1f24")]),
    ("Amateurs", "amateur",
     "Más potencia y propulsión trasera de referencia para subir de nivel.",
     [("Toyota Supra", "drift-supra.jpg", "jdm", "#f4f4f2"), ("Nissan Silvia S13", "drift-silvia-s13.jpg", "jdm", "#d63384"),
      ("Nissan Silvia S14", "drift-silvia-s14.jpg", "jdm", "#0ea5a4"), ("BMW M3 E46", "drift-bmw-m3.jpg", "sedan", "#1e40af")]),
    ("Profesionales", "profesional",
     "Plataformas serias, alta potencia, listas para competición.",
     [("Ford Mustang GT", "drift-mustang-gt.jpg", "muscle", "#111827"), ("Dodge Charger", "drift-charger.jpg", "muscle", "#e0412f"),
      ("Toyota GR86 / GT86", "drift-gt86.jpg", "jdm", "#f8fafc")]),
]

# Ficha técnica que ve el aficionado: (chasis, motor, potencia de fábrica, tracción). Datos orientativos.
SPECS = {
    "Ford Mustang Boss 429": ("1.ª generación", "V8 7.0 (429 ci)", "375 hp", "Propulsión"),
    "Lamborghini Urus": ("", "V8 4.0 biturbo", "650 CV", "4x4"),
    "Toyota Supra MK4 Turbo": ("A80", "2JZ-GTE 3.0 biturbo", "280 CV", "Propulsión"),
    "Porsche 911 Turbo S": ("992", "Bóxer 6 3.8 biturbo", "650 CV", "4x4"),
    "BMW M5 Competition": ("F90", "V8 4.4 biturbo", "625 CV", "xDrive"),
    "Mercedes-AMG G63": ("W463", "V8 4.0 biturbo", "585 CV", "4x4"),
    "Range Rover SVR": ("L494", "V8 5.0 compresor", "575 CV", "4x4"),
    "Chevrolet Camaro SS": ("6.ª generación", "V8 6.2", "455 hp", "Propulsión"),
    "Dodge Charger Hellcat": ("LD", "V8 6.2 compresor", "717 hp", "Propulsión"),
    "Chevrolet Corvette C8": ("C8", "V8 6.2 central", "495 hp", "Propulsión"),
    "Ford Mustang GT 5.0": ("S550", "V8 5.0 Coyote", "450 CV", "Propulsión"),
    "Mercedes-Benz E 500": ("W124", "V8 5.0", "326 CV", "Propulsión"),
    "BMW 325i E30": ("E30", "6 en línea 2.5", "170 CV", "Propulsión"),
    "Nissan Skyline R34 GT-R": ("BNR34", "RB26DETT 2.6 biturbo", "280 CV", "4x4 ATTESA"),
    "Ford Mustang V8 de circuito": ("", "V8 de competición", "", "Propulsión"),
    "Nissan 350Z Drift Spec": ("Z33", "V6 3.5", "", "Propulsión"),
    "BMW Serie 3 E46 Drift": ("E46", "6 en línea", "", "Propulsión"),
    "BMW Serie 3 E36": ("E36", "6 en línea", "", "Propulsión"),
    "BMW Serie 3 E46": ("E46", "6 en línea", "", "Propulsión"),
    "Lexus IS200": ("XE10", "6 en línea 2.0", "155 CV", "Propulsión"),
    "Lexus IS300": ("XE10", "2JZ-GE 3.0", "214 CV", "Propulsión"),
    "Toyota Supra": ("A80", "2JZ 3.0", "", "Propulsión"),
    "Nissan Silvia S13": ("S13", "4 cil. turbo", "", "Propulsión"),
    "Nissan Silvia S14": ("S14", "SR20DET 2.0 turbo", "", "Propulsión"),
    "BMW M3 E46": ("E46", "S54 3.2 6 en línea", "343 CV", "Propulsión"),
    "Ford Mustang GT": ("", "V8 5.0", "", "Propulsión"),
    "Dodge Charger": ("", "V8 HEMI", "", "Propulsión"),
    "Toyota GR86 / GT86": ("", "Bóxer 4 2.0", "", "Propulsión"),
}

# Leyendas destacadas en la portada: (coche, texto corto)
LEGENDS = [
    ("Mercedes-Benz E 500", "La berlina V8 de los 90 que hoy buscan los coleccionistas."),
    ("BMW 325i E30", "El seis en línea más querido para circuito y drift."),
    ("Nissan Skyline R34 GT-R", "Leyenda JDM con tracción total y el mítico RB26."),
    ("Toyota Supra MK4 Turbo", "El 2JZ biturbo que aguanta lo que le pidas."),
]

STEPS = [
    ("Búsqueda y asesoría", "Estudiamos tu petición y localizamos las mejores unidades en mercados internacionales según presupuesto, especificación y estado."),
    ("Inspección presencial", "Nuestros equipos en origen revisan el coche físicamente: chasis, mecánica, historial y documentación. Recibes informe y fotos."),
    ("Compra y pago seguro", "Negociamos el precio, firmamos contrato y gestionamos el pago con cuenta escrow o garantías equivalentes."),
    ("Logística internacional", "Transporte marítimo en contenedor cerrado con seguro a todo riesgo desde Dubái, EE. UU. o Japón hasta el puerto europeo."),
    ("Aduanas y EORI", "Tramitamos despacho aduanero, EORI, pago de aranceles e IVA y la liberación del vehículo."),
    ("ITV y homologación", "Homologación individual, ficha técnica reducida e ITV específica para que cumpla la normativa europea."),
    ("Matriculación", "Tramitamos la matriculación definitiva en España y la entrega final con todas las llaves y documentación."),
]

PERKS = [
    ("eye", "Transparencia total", "Informes detallados de cada paso. Sin costes ocultos, sin sorpresas."),
    ("shield", "Garantía legal", "Contrato formal, factura legal y documentación completa para tu tranquilidad."),
    ("globe", "Acceso global", "Vehículos exclusivos de Dubái, EE. UU., Japón y Alemania que no encontrarás en el mercado europeo."),
    ("key", "Trámites llave en mano", "Aduanas, homologación, ITV y matriculación. Tú solo recibes las llaves."),
]

VALUES = [
    "Transparencia total en cada euro y cada paso.",
    "Pasión real por los coches: somos clientes antes que proveedores.",
    "Trato directo, sin intermediarios ni sorpresas.",
    "Garantía legal y respaldo durante todo el proceso.",
]

FAQ = [
    ("¿Cuánto cuesta importar un coche?",
     "El precio final suma el coche en origen, el transporte con seguro, los aranceles y el IVA de importación, la homologación e ITV, el impuesto de matriculación y nuestra gestión. En el estudio gratuito te lo damos todo desglosado y por escrito, para que sepas el coste total antes de decidir."),
    ("¿Cuánto se tarda en tener el coche en España?",
     "Depende del país de origen, de lo que cueste encontrar la unidad adecuada y de la homologación. En el estudio te damos un plazo estimado para tu coche concreto y te avisamos en cada paso."),
    ("¿Puedo ver el coche antes de comprarlo?",
     "Sí. Nuestros equipos en origen lo revisan en persona: chasis, mecánica, historial y documentación. Te enviamos un informe con fotos y decides con toda la información en la mano."),
    ("¿Es seguro pagar un coche que está en otro país?",
     "Firmamos un contrato contigo y el pago se gestiona con cuenta escrow o garantías equivalentes. Recibes factura legal y toda la documentación del coche."),
    ("¿Se puede matricular en España un coche importado?",
     "Sí, después de homologarlo: homologación individual, ficha técnica reducida e ITV específica. Lo estudiamos antes de comprar y nos encargamos de todo el trámite."),
    ("¿Importáis coches clásicos?",
     "Sí: muscle cars americanos, JDM de los 90 y deportivos europeos de colección. Si el coche cumple los requisitos, te asesoramos sobre matricularlo como vehículo histórico."),
    ("¿Puedo pedir un coche que no aparece en la web?",
     "Claro. Los coches de la web son ejemplos. Dinos marca, modelo, año y presupuesto, y lo buscamos en Dubái, EE. UU., Japón o Alemania."),
    ("¿Qué incluye Drift en 72 horas?",
     "Eliges tu nivel y tu coche, y configuras suspensión, ángulo de giro, bloqueo de diferencial, freno de mano hidráulico, baquets y jaula antivuelco. Te lo entregamos preparado para derrapar en 72 horas."),
]

BUDGETS = ["20.000 € - 40.000 €", "40.000 € - 70.000 €", "70.000 € - 100.000 €", "100.000 € - 150.000 €", "Más de 150.000 €"]

CONFIG_OPTIONS = {
    "ruedas": ("Ruedas", [
        ("De serie", "Las llantas originales del coche", 0),
        ("Llantas ligeras 18\"", "Menos peso, mejor respuesta", 0),
        ("Llantas forjadas", "Máxima rigidez y mínimo peso", 0),
        ("Pack drift", "Llantas de repuesto y neumáticos semi-slick", 0),
    ]),
    "suspension": ("Suspensión", [
        ("De serie", "Suspensión original", 0),
        ("Coilovers regulables", "Altura y dureza ajustables", 0),
        ("Coilovers + kit de ángulo", "Más ángulo de giro para drift", 0),
        ("Suspensión de circuito", "Reglaje específico para pista", 0),
    ]),
    "aleron": ("Alerón", [
        ("Sin alerón", "Línea original", 0),
        ("Alerón de labio", "Discreto, apoyo ligero", 0),
        ("Alerón GT", "Máximo apoyo aerodinámico", 0),
    ]),
    "motor": ("Motor", [
        ("De serie", "Sin modificaciones", 0),
        ("Stage 1", "Reprogramación y admisión", 10),
        ("Stage 2", "Escape, intercooler y mapa a medida", 25),
        ("Stage 3", "Turbo, inyección y refuerzos", 45),
    ]),
}

# =====================================================================
# UTILIDADES
# =====================================================================
e = html.escape

# Palabras con las que la gente busca cada coche (para el buscador de la portada)
KEYS = {
    "Mercedes-Benz E 500": "mercedes benz w124 e500 500e clase e amg berlina",
    "BMW 325i E30": "bmw e30 325 325i serie 3",
    "Nissan Skyline R34 GT-R": "nissan skyline r34 gtr gt-r bnr34 godzilla",
    "Toyota Supra MK4 Turbo": "toyota supra mk4 mkiv a80 jza80 2jz",
    "Ford Mustang Boss 429": "ford mustang boss 429 1969 clasico americano",
    "Lamborghini Urus": "lamborghini lambo urus suv",
    "Porsche 911 Turbo S": "porsche 911 992 turbo s",
    "BMW M5 Competition": "bmw m5 f90 competition",
    "Mercedes-AMG G63": "mercedes amg g63 g 63 clase g w463 todoterreno",
    "Range Rover SVR": "range rover sport svr land rover",
    "Chevrolet Camaro SS": "chevrolet chevy camaro ss",
    "Dodge Charger Hellcat": "dodge charger hellcat srt",
    "Chevrolet Corvette C8": "chevrolet chevy corvette c8 stingray",
    "Ford Mustang GT 5.0": "ford mustang gt 5.0 s550 coyote",
    "Nissan 350Z Drift Spec": "nissan 350z z33 fairlady",
    "BMW Serie 3 E46 Drift": "bmw e46 serie 3 330 drift",
    "Ford Mustang V8 de circuito": "v8 competicion circuito mustang",
}


def load_json(name):
    path = os.path.join(ROOT, "data", name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def img_exists(name):
    return bool(name) and os.path.exists(os.path.join(ROOT, "assets", "img", name))


class Page:
    def __init__(self, path):
        self.path = path

    def href(self, target):
        rel = os.path.relpath(target, os.path.dirname(self.path) or ".").replace(os.sep, "/")
        if not PREVIEW and rel.endswith("index.html"):
            rel = rel[: -len("index.html")] or "./"
        return rel

    def asset(self, p):
        return os.path.relpath("assets/" + p, os.path.dirname(self.path) or ".").replace(os.sep, "/")

    def contact(self, modelo=None):
        q = ("?modelo=" + quote(modelo)) if modelo else ""
        return self.href("contacto/index.html") + q + "#solicitud"


def wa(text=WA_DEFAULT):
    return f"https://wa.me/{WHATSAPP}?text={quote(text)}"


def photo(p, img, alt="", lazy=True, sizes="(max-width: 640px) 100vw, 33vw", cls="", extra=""):
    sm = img.replace(".jpg", "-sm.jpg")
    srcset = f' srcset="{p.asset("img/" + sm)} 600w, {p.asset("img/" + img)} 1200w" sizes="{sizes}"' if img_exists(sm) else ""
    c = f' class="{cls}"' if cls else ""
    lz = ' loading="lazy"' if lazy else ""
    return f'<img src="{p.asset("img/" + img)}"{srcset} alt="{e(alt)}"{c}{lz} decoding="async" width="1200" height="800"{extra}>'


WA_ICON = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.3-.6-.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4C2.7 15.6 2.2 13.8 2.2 12 2.2 6.6 6.6 2.2 12 2.2c2.6 0 5.1 1 6.9 2.9 1.8 1.8 2.9 4.3 2.9 6.9 0 5.4-4.4 9.8-9.8 9.8zm8.4-18.2C18.1 1.3 15.2.1 12 .1 5.5.1.1 5.4.1 12c0 2.1.5 4.1 1.6 5.9L0 24l6.3-1.7c1.7.9 3.7 1.4 5.7 1.4 6.6 0 11.9-5.3 11.9-11.9 0-3.2-1.2-6.2-3.5-8.4z"/></svg>')

FAVICON = "data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#eeecea"/>'
    '<rect x="8" y="21" width="48" height="22" rx="7" fill="#4f5e48"/></svg>')


def mark(p):
    return f'<a class="mark" href="{p.href("index.html")}" aria-label="{BRAND}, ir al inicio">Busco<i aria-hidden="true"></i>tu coche</a>'


# =====================================================================
# PIEZAS COMUNES
# =====================================================================
NAV = [
    ("calle", "Coches de calle", "servicios/calle/index.html"),
    ("competicion", "Competición", "servicios/competicion/index.html"),
    ("drift", "Drift en 72 h", "drift-72h/index.html"),
    ("nosotros", "Cómo trabajamos", "nosotros/index.html"),
    ("stock", "Stock", "stock/index.html"),
]


def header(p, active):
    links = "".join(
        f'<a href="{p.href(t)}"{" aria-current=\"page\"" if active == k else ""}>{l}</a>' for k, l, t in NAV)
    return f"""<a class="skip" href="#main">Saltar al contenido</a>
<header class="site-header">
  <div class="wrap">
    {mark(p)}
    <button class="menu-btn" type="button" aria-controls="nav" aria-expanded="false">Menú</button>
    <nav class="nav" id="nav" aria-label="Principal">
      {links}
      <a class="btn" href="{p.contact()}">Pedir presupuesto</a>
    </nav>
  </div>
</header>"""


def footer(p):
    return f"""<footer class="footer">
  <div class="wrap g12 footer-grid">
    <div class="f-brand">
      {mark(p)}
      <p>Importamos coches de Dubái, EE. UU., Japón y Alemania y te los entregamos matriculados en España. {CITY}.</p>
    </div>
    <div class="f-contact">
      <a class="tel" href="tel:{PHONE_TEL}" aria-label="Llamar al {PHONE_DISPLAY}">{PHONE_DISPLAY}</a>
      <a href="{wa()}" target="_blank" rel="noopener">Escribir por WhatsApp</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
    <ul class="f-links">
      <li><a href="{p.href("servicios/calle/index.html")}">Coches de calle</a></li>
      <li><a href="{p.href("servicios/competicion/index.html")}">Competición</a></li>
      <li><a href="{p.href("drift-72h/index.html")}">Drift en 72 h</a></li>
      <li><a href="{p.href("nosotros/index.html")}">Cómo trabajamos</a></li>
      <li><a href="{p.href("ventajas/index.html")}">Ventajas</a></li>
      <li><a href="{p.href("stock/index.html")}">Stock</a></li>
      <li><a href="{p.contact()}">Contacto</a></li>
    </ul>
  </div>
  <div class="wrap footer-meta">
    <p>© {YEAR} {BRAND}</p>
    <p><a href="{p.href("aviso-legal/index.html")}">Aviso legal</a> <a href="{p.href("privacidad/index.html")}">Privacidad</a> <a href="{p.href("creditos/index.html")}">Créditos de las fotos</a></p>
  </div>
  <a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp al {PHONE_DISPLAY}">{WA_ICON}</a>
</footer>"""


def layout(p, title, desc, active, main, extra_head="", og_img="car-mercedes-e500.jpg"):
    canonical = og = ""
    if DOMAIN:
        clean = p.path[: -len("index.html")] if p.path.endswith("index.html") else p.path
        canonical = f'<link rel="canonical" href="https://{DOMAIN}/{clean}">'
        og = (f'<meta property="og:url" content="https://{DOMAIN}/{clean}">\n'
              f'<meta property="og:image" content="https://{DOMAIN}/assets/img/{og_img}">\n'
              f'<meta name="twitter:card" content="summary_large_image">')
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#eeecea">
{canonical}
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="{e(BRAND)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{og}
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="{p.asset("fonts/imbue.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p.asset("fonts/albert-sans.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p.asset("css/site.css")}">
<script>document.documentElement.classList.add("js")</script>
{extra_head}
</head>
<body data-wa="{WHATSAPP}" data-endpoint="{e(FORM_ENDPOINT)}">
{header(p, active)}
<main id="main" tabindex="-1">
{main}
</main>
{footer(p)}
<script src="{p.asset("js/site.js")}" defer></script>
</body>
</html>
"""


def sentence(p, w1, img, w2, cls="", tag="h1"):
    slot = ""
    if img:
        slot = f'<span class="slot shutter" aria-hidden="true">{photo(p, img, "", lazy=False, sizes="(max-width: 760px) 100vw, 45vw", cls="is-on")}</span>'
    return f'<{tag} class="sentence {cls}"><span class="w">{e(w1)}</span>{slot}<span class="w">{e(w2)}</span></{tag}>'


def page_head(p, crumb, w1, img, w2, lead, side="", long=False):
    trail = f'<a href="{p.href("index.html")}">Inicio</a> / {e(crumb)}'
    side_html = f'<div class="side">{side}</div>' if side else ""
    return f"""<section class="page-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Estás en">{trail}</nav>
    {sentence(p, w1, img, w2, "long" if long else "")}
    <div class="g12 intro"><p class="lead">{lead}</p>{side_html}</div>
  </div>
</section>"""


def closing(p, title="¿Lo buscamos por ti?", text="Dinos marca, modelo, año y presupuesto. Te mandamos un estudio gratis en menos de 24 horas."):
    return cta_band(p, title, text)


def specs_html(name):
    sp = SPECS.get(name)
    if not sp:
        return ""
    _, motor, cv, trac = sp
    items = [(k, v) for k, v in (("Motor", motor), ("Potencia", cv), ("Tracción", trac)) if v]
    return '<dl class="spec">' + "".join(f"<div><dt>{k}</dt><dd>{e(v)}</dd></div>" for k, v in items) + "</dl>"


def chassis_of(name):
    sp = SPECS.get(name)
    return sp[0] if sp and sp[0] and not sp[0].endswith("generación") else ""


def car_item(p, name, meta, img, tags, actions):
    media = photo(p, img, name) if img_exists(img) else ""
    return f"""<article class="car rv" data-tags="{tags}">
  <div class="car-media">{media}</div>
  <h3>{e(name)}</h3>
  <p class="car-meta">{e(meta)}</p>
  {specs_html(name)}
  <div class="car-actions">{actions}</div>
</article>"""


def origin_meta(year, o, name):
    ch = chassis_of(name)
    return f"{year}, desde {ORIGINS[o].rstrip('.')}." + (f" Chasis {ch}." if ch else "")


def filters_html(target, options):
    chips = "".join(
        f'<button type="button" class="chip" data-value="{v}" aria-pressed="{"true" if i == 0 else "false"}">{e(l)}</button>'
        for i, (v, l) in enumerate(options))
    return f'<div class="filters" role="group" aria-label="Filtrar coches" data-filter-group="{target}">{chips}</div>'


def faq_html(title, items=None, more=""):
    items = items if items is not None else FAQ
    rows = "".join(f'<details class="qa"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in items)
    more_html = f'<p class="qa-more">{more}</p>' if more else ""
    return f'''<div class="g12 faq">
  <div class="faq-head"><h2>{e(title)}</h2><p>Pulsa en una pregunta para ver la respuesta.</p></div>
  <div class="faq-list">{rows}{more_html}</div>
</div>'''


def faq_jsonld():
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


PERK_TILES = [
    ("t-surface", "Sin sorpresas", "Te damos el coste total por escrito antes de decidir y un informe en cada paso."),
    ("t-field", "Todo en regla", "Contrato, factura legal y toda la documentación del coche. Respaldo legal en todo el proceso."),
    ("t-ink", "Tú solo conduces", "Aduanas, homologación, ITV y matrícula corren de nuestra cuenta. Tú recibes las llaves."),
    ("t-accent", "Lo que aquí no hay", "Coches de Dubái, EE. UU., Japón y Alemania que no encuentras en el mercado europeo."),
]


def tiles_html():
    return '<ul class="tiles">' + "".join(
        f'<li class="tile {c} rv"><h3>{e(t)}</h3><p>{e(d)}</p></li>' for c, t, d in PERK_TILES) + "</ul>"


STEP_SHOW = [
    ("Buscamos", "car-skyline.jpg", "Localizamos la unidad que encaja con tu presupuesto en cuatro mercados."),
    ("Revisamos", "car-competition.jpg", "La vemos en persona: chasis, mecánica, historial y papeles. Te mandamos informe y fotos."),
    ("Compramos", "car-mercedes-e500.jpg", "Negociamos, firmamos contrato y el pago va por cuenta escrow o garantía equivalente."),
    ("Traemos", "barco.jpg", "En contenedor cerrado y asegurado. Aduanas, EORI, aranceles e IVA incluidos."),
    ("Matriculamos", "car-camaro.jpg", "Homologación, ITV y matrícula española. Te damos las llaves y los papeles."),
]


def steps_show(p):
    return '<ol class="steps5">' + "".join(
        f'<li class="rv"><div class="car-media">{photo(p, img, "", sizes="(max-width: 860px) 30vw, 20vw")}</div><h3>{v}</h3><p>{e(t)}</p></li>'
        for v, img, t in STEP_SHOW) + "</ol>"


def cta_band(p, title="¿Lo buscamos por ti?", text="Dinos marca, modelo, año y presupuesto. Te mandamos un estudio gratis en menos de 24 horas."):
    return f"""<section class="cta-band">
  <div class="wrap g12">
    <h2>{e(title)}</h2>
    <div class="cta-side"><p>{e(text)}</p>
      <div class="form-actions"><a class="btn btn-light" href="{p.contact()}">Pedir presupuesto</a>
      <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{WA_ICON}WhatsApp</a></div></div>
  </div>
</section>"""


# =====================================================================
# PÁGINAS
# =====================================================================
def all_cars():
    out = []
    for n, y, o, img, kind, paint in STREET_CARS:
        out.append(dict(name=n, year=y, o=o, img=img, race=False))
    for n, y, o, img, k, body, paint, num in RACE_CARS:
        out.append(dict(name=n, year=y, o=o, img=img, race=True))
    return out


def page_home():
    p = Page("index.html")
    cars = all_cars()
    by = {c["name"]: c for c in cars}
    hero_cars = ["Mercedes-Benz E 500", "Nissan Skyline R34 GT-R", "Ford Mustang Boss 429", "BMW 325i E30", "Toyota Supra MK4 Turbo"]
    slot_imgs = "".join(photo(p, by[n]["img"], "", lazy=(i > 0), sizes="(max-width: 760px) 100vw, 45vw", cls="is-on" if i == 0 else "")
                        for i, n in enumerate(hero_cars))
    finder_data = [dict(name=c["name"], keys=KEYS.get(c["name"], ""), chassis=chassis_of(c["name"]),
                        chassis_text=(f"chasis {chassis_of(c['name'])}, " if chassis_of(c["name"]) else ""),
                        origin=ORIGINS[c["o"]], img=p.asset("img/" + c["img"].replace(".jpg", "-sm.jpg")),
                        url=p.contact(f"{c['name']} {c['year']}")) for c in cars]
    for _, _, _, items in DRIFT_LEVELS:
        for n, img, *_ in items:
            if img_exists(img) and n not in by:
                finder_data.append(dict(name=n, keys=n.lower(), chassis=chassis_of(n),
                                        chassis_text=(f"chasis {chassis_of(n)}, " if chassis_of(n) else ""), origin="nuestro programa de drift",
                                        img=p.asset("img/" + img.replace(".jpg", "-sm.jpg")), url=p.href("drift-72h/index.html")))

    index_names = ["Mercedes-Benz E 500", "BMW 325i E30", "Nissan Skyline R34 GT-R", "Toyota Supra MK4 Turbo", "Ford Mustang Boss 429", "Lamborghini Urus"]
    rows, prev = "", ""
    for i, n in enumerate(index_names):
        c = by[n]
        sp = SPECS.get(n, ("", "", "", ""))
        cap = f"{n}, {c['year']}. {sp[1]}, {sp[2]}." if sp[2] else f"{n}, {c['year']}."
        ch = chassis_of(n)
        meta = (ch + ", " if ch else "") + ORIGINS[c["o"]]
        rows += (f'<li><a class="index-row" href="{p.contact(n + " " + str(c["year"]))}" data-cap="{e(cap)}">'
                 f'{photo(p, c["img"].replace(".jpg", "-sm.jpg") if img_exists(c["img"].replace(".jpg", "-sm.jpg")) else c["img"], "", cls="thumb")}'
                 f'<span class="name">{e(n)}</span><span class="meta">{e(meta)}</span></a></li>')
        prev += photo(p, c["img"], n, lazy=True, sizes="40vw", cls="is-on" if i == 0 else "")
    first_cap = f"{index_names[0]}, {by[index_names[0]]['year']}. {SPECS[index_names[0]][1]}, {SPECS[index_names[0]][2]}."

    jsonld = {"@context": "https://schema.org", "@type": "AutoDealer", "name": BRAND,
              "description": "Importación de coches clásicos, JDM, muscle y de lujo desde Dubái, EE. UU., Japón y Alemania a España.",
              "telephone": PHONE_TEL, "email": EMAIL, "areaServed": "España",
              "address": {"@type": "PostalAddress", "addressLocality": "Madrid", "addressCountry": "ES"}}
    if DOMAIN:
        jsonld["url"] = f"https://{DOMAIN}/"
    head = (f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' + faq_jsonld())

    paths = [
        ("Coches de calle", "car-urus.jpg", "Clásicos, deportivos, SUV y berlinas de lujo.", "servicios/calle/index.html"),
        ("Competición", "car-bmw-325.jpg", "Coches de circuito y drift, configurables a medida.", "servicios/competicion/index.html"),
        ("Drift en 72 horas", "drift-mustang-gt.jpg", "Tu coche de drift preparado y listo en tres días.", "drift-72h/index.html"),
    ]
    paths_html = "".join(
        f'<li class="rv"><a class="path" href="{p.href(t)}"><div class="car-media">{photo(p, img, "", sizes="(max-width: 860px) 100vw, 33vw")}</div>'
        f'<h3>{e(n)}</h3><p>{e(d)}</p><span class="link">Ver coches</span></a></li>' for n, img, d, t in paths)

    main = f"""
<section class="hero">
  <div class="wrap">
    <h1 class="sentence"><span class="w">Busco</span><span class="slot shutter" aria-hidden="true">{slot_imgs}</span><span class="w">tu coche</span></h1>
    <div class="g12 hero-foot">
      <p class="lead">Importamos clásicos, JDM, muscle cars y deportivos de lujo desde Dubái, EE. UU., Japón y Alemania, y te los entregamos matriculados en España.</p>
      <form class="finder" id="finder" action="{p.href("contacto/index.html")}#solicitud" method="get" role="search">
        <label for="busco">¿Qué coche buscas?</label>
        <div class="finder-row">
          <input id="busco" name="modelo" type="search" autocomplete="off" placeholder="Por ejemplo: W124, Supra MK4, E30" required>
          <button class="btn" type="submit">Pedir estudio gratis</button>
        </div>
        <p class="finder-out" id="finder-out" aria-live="polite"></p>
      </form>
    </div>
  </div>
  <script type="application/json" id="cars-data">{json.dumps(finder_data, ensure_ascii=False).replace("</", "<\\/")}</script>
</section>

<section class="section">
  <div class="wrap">
    <div class="g12 head rv"><h2>¿Qué tipo de coche buscas?</h2><p>Elige por dónde empezar. En cada sección verás ejemplos con su ficha técnica.</p></div>
    <ul class="paths3">{paths_html}</ul>
  </div>
</section>

<section class="section surface">
  <div class="wrap">
    <div class="g12 head rv"><h2>Leyendas que traemos</h2><p>Clásicos alemanes, JDM de los 90 y muscle cars. Pulsa en uno y te preparamos el estudio de ese modelo.</p></div>
    <div class="g12">
      <ul class="index-list rv">{rows}</ul>
      <figure class="index-preview"><div class="frame">{prev}</div><figcaption>{e(first_cap)}</figcaption></figure>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="g12 head rv"><h2>Así lo traemos</h2><p>Cinco pasos y uno solo es tuyo: elegir el coche.</p></div>
    {steps_show(p)}
  </div>
</section>

<section class="section surface">
  <div class="wrap">
    <div class="g12 head rv"><h2>Por qué con nosotros</h2></div>
    {tiles_html()}
  </div>
</section>

<section class="section">
  <div class="wrap">{faq_html("Preguntas frecuentes", FAQ[:5], f'<a class="link" href="{p.contact()}">Ver todas las preguntas</a>')}</div>
</section>

{cta_band(p)}
"""
    return p, layout(p, "Busco Tu Coche | Importación de coches clásicos, JDM, muscle y de lujo",
                     "Importamos coches clásicos, JDM, muscle, de lujo, drift y competición desde Dubái, EE. UU., Japón y Alemania a España. Servicio llave en mano con homologación y matrícula.",
                     "inicio", main, head)


ORIGIN_SHOW = [
    ("Japón", "car-skyline.jpg", "JDM de los 90 y coches para drift: Skyline, Supra, Silvia, 350Z."),
    ("EE. UU.", "car-mustang-boss.jpg", "Muscle cars y clásicos americanos: Mustang, Camaro, Charger, Corvette."),
    ("Dubái", "car-urus.jpg", "SUV y deportivos de lujo con pocos kilómetros: Urus, G63, Range Rover."),
    ("Alemania", "car-mercedes-e500.jpg", "Clásicos y deportivos alemanes: E 500 W124, E30, Porsche 911, BMW M."),
]


def origins_html(p):
    return "".join(f'<li class="rv"><div class="car-media">{photo(p, img, f"Coche importado desde {o}", sizes="(max-width: 1020px) 50vw, 25vw")}</div>'
                   f'<h3>{o}</h3><p>{e(t)}</p></li>' for o, img, t in ORIGIN_SHOW)


def page_about():
    p = Page("nosotros/index.html")
    vals = "".join(f"<li>{e(v)}</li>" for v in VALUES)
    steps = "".join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in STEPS)
    main = page_head(p, "Cómo trabajamos", "Quiénes", "car-mercedes-e500.jpg", "somos",
                     "Somos especialistas en importar llave en mano coches premium, clásicos, deportivos, de drift y de competición desde Dubái, EE. UU., Japón y Alemania hasta tu garaje.") + f"""
<section class="section">
  <div class="wrap g12 split rv">
    <div><h2 style="margin-bottom:24px">Nuestra misión</h2><p class="statement">Hacer accesible el coche que siempre soñaste.</p><p style="margin-top:20px">Con transparencia, seguridad jurídica y trato personal en cada paso.</p></div>
    <div><h2 style="margin-bottom:24px">Lo que nos mueve</h2><ul class="values">{vals}</ul></div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="g12 head rv"><h2>De dónde los traemos</h2><p>Cuatro mercados, cada uno con lo suyo. Buscamos en el que mejor encaja con tu coche y tu presupuesto.</p></div>
    <ul class="g12 origins">{origins_html(p)}</ul>
  </div>
</section>
<section class="section surface">
  <div class="wrap">
    <div class="g12 head rv"><h2>Cómo hacemos las importaciones</h2><p>Siete pasos, en este orden. Tú eliges el coche y nosotros hacemos el resto.</p></div>
    <figure class="banner">{photo(p, "barco.jpg", "Barco portacoches navegando al atardecer", sizes="100vw")}</figure>
    <ol class="g12 steps rv">{steps}</ol>
  </div>
</section>
{closing(p)}"""
    return p, layout(p, "Cómo trabajamos | Importación de coches - Busco Tu Coche",
                     "Cómo importamos coches de lujo, clásicos, drift y competición desde Dubái, EE. UU., Japón y Alemania. Proceso transparente llave en mano.",
                     "nosotros", main)


def page_street():
    p = Page("servicios/calle/index.html")
    cards = ""
    for name, year, o, img, kind, paint in STREET_CARS:
        tags = o + (" clasico" if year < 2000 else "")
        act = f'<a class="link" href="{p.contact(f"{name} {year}")}">Pedir presupuesto de este coche</a>'
        cards += car_item(p, name, origin_meta(year, o, name), img, tags, act)
    opts = [("todos", "Todos"), ("clasico", "Clásicos")] + [(k, v) for k, v in ORIGINS.items()]
    main = page_head(p, "Coches de calle", "Coches", "car-urus.jpg", "de calle",
                     "Clásicos, deportivos, SUV de lujo y berlinas premium importados desde Dubái, EE. UU., Japón y Alemania, listos para circular con todos los trámites hechos.",
                     side=f'<p>Son ejemplos de lo que traemos. ¿Buscas otro? <a class="link" href="{p.contact()}">Pídenoslo</a></p>') + f"""
<section class="section" style="padding-top:0">
  <div class="wrap">
    <h2 class="sr-only">Coches de ejemplo</h2>
    {filters_html("lista-calle", opts)}
    <div class="cars" id="lista-calle">{cards}</div>
    <div class="empty" id="lista-calle-empty" hidden><p>No hay ejemplos con ese filtro, pero lo buscamos igual.</p><a class="btn" href="{p.contact()}">Pedir un coche concreto</a></div>
  </div>
</section>
{closing(p)}"""
    return p, layout(p, "Coches de calle | Importación de coches premium y clásicos - Busco Tu Coche",
                     "Importa clásicos, deportivos, SUV de lujo y berlinas desde Dubái, EE. UU., Japón y Alemania. Listos para circular en España.",
                     "calle", main, og_img="car-urus.jpg")


def page_race():
    p = Page("servicios/competicion/index.html")
    cards = ""
    for name, year, o, img, kind, body, paint, num in RACE_CARS:
        act = (f'<a class="link" href="{p.href("configurador/index.html")}?coche={quote(name)}">Configurarlo</a>'
               f'<a class="link" href="{p.contact(f"{name} {year}")}">Pedir presupuesto</a>')
        cards += car_item(p, name, origin_meta(year, o, name), img, kind, act)
    main = page_head(p, "Competición y drift", "Competición", "car-bmw-drift.jpg", "y drift",
                     "Preparaciones reales para circuito y drift. Cada coche se configura a medida: ruedas, suspensión, alerones y potencia.",
                     side=f'<p>¿Empiezas en el drift? Tenemos coches por niveles, listos en 72 horas. <a class="link" href="{p.href("drift-72h/index.html")}">Ver coches por nivel</a></p>', long=True) + f"""
<section class="section" style="padding-top:0">
  <div class="wrap">
    <h2 class="sr-only">Coches de ejemplo</h2>
    {filters_html("lista-comp", [("todos", "Todos"), ("circuito", "Circuito"), ("drift", "Drift")])}
    <div class="cars" id="lista-comp">{cards}</div>
  </div>
</section>
{closing(p, "¿Tienes uno en mente?")}"""
    return p, layout(p, "Competición y drift | Coches configurables - Busco Tu Coche",
                     "Importa y configura coches de competición y drift: BMW 325i E30, Skyline R34, 350Z, E46 y más.",
                     "competicion", main, og_img="car-bmw-drift.jpg")


def page_drift():
    p = Page("drift-72h/index.html")
    feats = "".join(f"<li>{x}</li>" for x in ["Suspensión", "Ángulo de giro", "Bloqueo de diferencial", "Freno de mano hidráulico", "Baquets", "Jaula antivuelco"])
    levels = ""
    for title, slug, desc, items in DRIFT_LEVELS:
        cards = ""
        for name, img, body, paint in items:
            act = f'<a class="link" href="{p.href("configurador/index.html")}?coche={quote(name + " (drift)")}">Configurar este coche</a>'
            cards += car_item(p, name, f"Nivel {slug}.", img, slug, act)
        levels += f'<div class="level" id="{slug}"><div class="g12 head rv"><h2>{title}</h2><p>{e(desc)}</p></div><div class="cars">{cards}</div></div>'
    main = page_head(p, "Drift en 72 horas", "Drift", "drift-mustang-gt.jpg", "en 72 h",
                     "Elige tu nivel, elige tu coche y configura cada detalle. Lo preparamos y te lo entregamos listo para derrapar en 72 horas.",
                     side=f'<ul class="tags" aria-label="Qué puedes configurar">{feats}</ul>') + f"""
<section class="section" style="padding-top:0"><div class="wrap">{levels}</div></section>
{closing(p, "¿Cuál es el tuyo?")}"""
    return p, layout(p, "Drift en 72 horas | Coches preparados para derrapar - Busco Tu Coche",
                     "Coches de drift listos en 72 horas: BMW E36 y E46, Lexus IS200 e IS300, Supra, Silvia S13 y S14, M3, Mustang GT, Charger y GT86.",
                     "drift", main, og_img="drift-mustang-gt.jpg")


def page_perks():
    p = Page("ventajas/index.html")
    steps = "".join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in STEPS)
    main = page_head(p, "Ventajas", "Por qué", "car-skyline.jpg", "nosotros",
                     "Confianza, coches que en Europa no encuentras y un servicio que se ocupa de cada trámite.",
                     side=f'<p>Te preparamos un estudio gratis de tu coche en menos de 24 horas.</p><a class="btn" href="{p.contact()}">Pedir presupuesto</a>') + f"""
<section class="section" style="padding-top:0"><div class="wrap"><h2 class="sr-only">Nuestras garantías</h2>{tiles_html()}</div></section>
<section class="section">
  <div class="wrap">
    <div class="g12 head rv"><h2>Lo que en Europa no encuentras</h2><p>Buscamos en el mercado que mejor encaja con tu coche y tu presupuesto.</p></div>
    <ul class="g12 origins">{origins_html(p)}</ul>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="g12 head rv"><h2>Todo lo que hacemos por ti</h2><p>De la búsqueda a la matrícula española, sin que tengas que hacer un solo trámite.</p></div>
    <ol class="g12 steps rv">{steps}</ol>
  </div>
</section>
{closing(p)}"""
    return p, layout(p, "Ventajas | Por qué importar con Busco Tu Coche",
                     "Transparencia total, garantía legal, acceso global y trámites llave en mano.", "ventajas", main)


def page_stock():
    p = Page("stock/index.html")
    stock = load_json("stock.json")
    if stock:
        cards = ""
        for c in stock:
            title = f"{c.get('marca', '')} {c.get('modelo', '')}".strip()
            year = c.get("año", "")
            bits = [f"Año {year}"]
            if c.get("km"):
                bits.append(f"{int(c['km']):,} km".replace(",", "."))
            if c.get("precio"):
                bits.append(f"{int(c['precio']):,} €".replace(",", "."))
            msg = f"Hola, me interesa el {title} {year} publicado en stock"
            act = f'<a class="btn btn-wa" href="{wa(msg)}" target="_blank" rel="noopener">{WA_ICON}Más detalles por WhatsApp</a>'
            cards += car_item(p, title, ". ".join(bits) + ".", c.get("foto", ""), "stock", act)
        listing = f'<div class="cars">{cards}</div>'
    else:
        listing = (f'<div class="empty rv"><p>Ahora mismo no hay coches publicados. Si buscas uno concreto, lo importamos por encargo; '
                   f'y si vendes el tuyo, publícalo aquí.</p><div class="form-actions">'
                   f'<a class="btn" href="{p.contact()}">Pedir un coche por encargo</a>'
                   f'<a class="btn btn-ink" href="{p.href("stock/subir/index.html")}">Subir mi anuncio</a></div></div>')
    main = page_head(p, "Stock", "Coches", "car-mercedes-g.jpg", "en stock",
                     "Coches disponibles ahora mismo, listos para entrega rápida en España.",
                     side=f'<p>¿Vendes un coche especial? Publícalo aquí y lo revisamos antes de mostrarlo.</p><a class="btn btn-ink" href="{p.href("stock/subir/index.html")}">Subir mi anuncio</a>') + f"""
<section class="section" style="padding-top:0"><div class="wrap">{listing}</div></section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="g12 head rv"><h2>O te lo traemos por encargo</h2><p>Pulsa en uno y te preparamos el estudio de importación de ese modelo.</p></div>
    <ul class="g12 origins">{pick_models(p)}</ul>
  </div>
</section>"""
    return p, layout(p, "Coches en stock | Disponibles ahora - Busco Tu Coche",
                     "Coches importados disponibles ahora mismo para entrega rápida en España.", "stock", main)


def field(label, name, kind="text", placeholder="", required=False, full=False, opts=None, auto=""):
    req = " required" if required else ""
    opt = "" if required else ' <span class="opt">(opcional)</span>'
    ac = f' autocomplete="{auto}"' if auto else ""
    cls = "field full" if full else "field"
    fid = "f-" + name
    if kind == "select":
        options = '<option value="">Selecciona un rango</option>' + "".join(f"<option>{e(o)}</option>" for o in opts)
        ctrl = f'<select id="{fid}" name="{name}" data-label="{e(label)}"{req}>{options}</select>'
    elif kind == "textarea":
        ctrl = f'<textarea id="{fid}" name="{name}" placeholder="{e(placeholder)}" data-label="{e(label)}"{req}></textarea>'
    else:
        extra = ' inputmode="numeric"' if kind == "number" else ""
        ctrl = f'<input id="{fid}" name="{name}" type="{kind}" placeholder="{e(placeholder)}" data-label="{e(label)}"{req}{ac}{extra}>'
    return f'<div class="{cls}"><label for="{fid}">{e(label)}{opt}</label>{ctrl}</div>'


def consent(p):
    return (f'<div class="full"><label class="check"><input type="checkbox" name="privacidad" required>'
            f'<span>He leído y acepto la <a class="link" href="{p.href("privacidad/index.html")}">política de privacidad</a>.</span></label></div>')


def form_note():
    return "" if FORM_ENDPOINT else '<p class="form-note">Al enviarlo se abre WhatsApp con tu solicitud ya escrita: solo tienes que pulsar enviar.</p>'


def page_upload():
    p = Page("stock/subir/index.html")
    shots = "".join(f'<li class="rv"><div class="car-media">{photo(p, img, alt, sizes="25vw")}</div><p>{e(t)}</p></li>' for img, alt, t in [
        ("car-mercedes-e500.jpg", "Coche fotografiado de tres cuartos delantero", "De tres cuartos por delante, con luz de día."),
        ("drift-charger.jpg", "Coche fotografiado por detrás", "También por detrás, con la matrícula tapada si quieres."),
        ("car-competition.jpg", "Vano motor de un coche", "El motor y el interior, limpios y a la vista."),
        ("car-porsche.jpg", "Coche fotografiado de cerca", "Los detalles: llantas, frenos y cualquier marca.")])
    main = page_head(p, "Subir anuncio", "Sube tu", "car-supra.jpg", "anuncio",
                     "Publica tu coche en nuestra sección de stock. Revisamos cada anuncio antes de publicarlo.") + f"""
<section class="section" style="padding-top:0">
  <div class="wrap g12">
    <form class="panel c-form wide" style="grid-column: 1 / span 8" novalidate
      data-intro="Hola, quiero publicar mi coche en el stock de {BRAND}:"
      data-subject="Nuevo anuncio para el stock"
      data-ok="Anuncio enviado. Lo revisamos y te avisamos cuando esté publicado."
      data-ok-wa="Te hemos abierto WhatsApp con el anuncio. Envíalo y adjunta ahí las fotos del coche.">
      <div class="form-grid">
        {field("Marca", "marca", placeholder="BMW", required=True)}
        {field("Modelo", "modelo", placeholder="M3 E46", required=True)}
        {field("Año", "anio", "number", "2004", required=True)}
        {field("Kilometraje (km)", "km", "number", "120000")}
        {field("Precio (€)", "precio", "number", "25000")}
        {field("País de origen", "origen", placeholder="Alemania")}
        {field("Descripción", "descripcion", "textarea", "Estado, equipamiento, historial...", full=True)}
        {field("Email de contacto", "email", "email", "tu@email.com", required=True, auto="email")}
        {field("Teléfono de contacto", "telefono", "tel", "+34 600 000 000", auto="tel")}
        {consent(p)}
      </div>
      <div class="form-actions"><button class="btn" type="submit">Enviar anuncio</button></div>
      <p class="form-note">Las fotos del coche nos las mandas por WhatsApp después de enviar el anuncio.</p>
      {form_note()}
      <div class="form-status" role="status" aria-live="polite"></div>
    </form>
    <aside class="c-side" style="grid-column: 10 / span 3">
      <h2 style="font-size: clamp(1.75rem, 1.2rem + 1.4vw, 2.5rem); margin-bottom: 20px">Fotos que venden</h2>
      <ul class="shots">{shots}</ul>
    </aside>
  </div>
</section>"""
    return p, layout(p, "Sube tu anuncio | Stock - Busco Tu Coche", "Publica tu coche en el stock de Busco Tu Coche.", "stock", main)


def pick_models(p):
    by = {c["name"]: c for c in all_cars()}
    out = ""
    for n in ["Mercedes-Benz E 500", "BMW 325i E30", "Nissan Skyline R34 GT-R", "Toyota Supra MK4 Turbo"]:
        c = by[n]
        out += (f'<li class="rv"><a href="{p.contact(f"{n} {c["year"]}")}" style="text-decoration:none"><div class="car-media">'
                f'{photo(p, c["img"], "", sizes="(max-width: 1020px) 50vw, 25vw")}</div><h3>{e(n)}</h3></a>'
                f'<p>{e(origin_meta(c["year"], c["o"], n))}</p></li>')
    return out


def page_contact():
    p = Page("contacto/index.html")
    main = page_head(p, "Contacto", "Pide tu", "car-camaro.jpg", "estudio",
                     "Cuéntanos qué coche buscas y te preparamos un estudio de importación gratis y sin compromiso en menos de 24 horas.") + f"""
<section class="section" style="padding-top:0" id="solicitud">
  <div class="wrap g12 contact-grid">
    <form class="panel c-form" novalidate
      data-intro="Hola, quiero un estudio de importación:"
      data-subject="Nueva solicitud de presupuesto"
      data-ok="Solicitud enviada. Te escribimos en menos de 24 horas."
      data-ok-wa="Te hemos abierto WhatsApp con tu solicitud ya escrita. Envíala y te respondemos en menos de 24 horas.">
      <h2 style="font-size: clamp(1.75rem, 1.2rem + 1.4vw, 2.5rem); margin-bottom: 24px">Solicitud de estudio</h2>
      <div class="form-grid">
        {field("Nombre", "nombre", placeholder="Tu nombre completo", required=True, auto="name")}
        {field("Teléfono", "telefono", "tel", "+34 600 000 000", required=True, auto="tel")}
        {field("Marca y modelo que buscas", "modelo", placeholder="Mercedes E 500, BMW 325i, Supra MK4...", required=True)}
        {field("Generación o chasis", "chasis", placeholder="W124, E30, A80, R34")}
        {field("Email", "email", "email", "tu@email.com", auto="email")}
        {field("Presupuesto aproximado", "presupuesto", "select", opts=BUDGETS)}
        {field("Algo más que debamos saber", "comentarios", "textarea", "Año, color, kilómetros, cambio manual o automático, uso que le vas a dar...", full=True)}
        {consent(p)}
      </div>
      <div class="form-actions"><button class="btn" type="submit">Solicitar estudio gratis</button></div>
      {form_note()}
      <div class="form-status" role="status" aria-live="polite"></div>
    </form>
    <div class="c-side">
      <h2 style="font-size: clamp(1.75rem, 1.2rem + 1.4vw, 2.5rem); margin-bottom: 24px">O háblanos directamente</h2>
      <ul class="contact-list">
        <li><a href="{wa()}" target="_blank" rel="noopener"><b>{PHONE_DISPLAY}</b><small>WhatsApp, la vía más rápida</small></a></li>
        <li><a href="tel:{PHONE_TEL}"><b>{PHONE_DISPLAY}</b><small>Teléfono</small></a></li>
        <li><a href="mailto:{EMAIL}"><b>{EMAIL}</b><small>Email</small></a></li>
        <li><div><b>{CITY}</b><small>Dónde estamos</small></div></li>
      </ul>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="g12 head rv"><h2>¿Buscas alguno de estos?</h2><p>Pulsa en uno y lo dejamos escrito en tu solicitud.</p></div>
    <ul class="g12 origins">{pick_models(p)}</ul>
  </div>
</section>
<section class="section surface"><div class="wrap">{faq_html("Antes de escribirnos")}</div></section>"""
    return p, layout(p, "Contacto | Pide tu estudio de importación gratis - Busco Tu Coche",
                     f"Pide tu estudio de importación gratis. WhatsApp y teléfono {PHONE_DISPLAY}. Respuesta en menos de 24 horas.",
                     "contacto", main, faq_jsonld())


def page_config():
    p = Page("configurador/index.html")
    all_c, seen = [], set()
    for n, img in [(c[0], c[3]) for c in RACE_CARS] + [(n + " (drift)", img) for _, _, _, items in DRIFT_LEVELS for n, img, *_ in items]:
        k = re.sub(r"\W|drift|spec", "", n.lower())
        if k not in seen:
            seen.add(k); all_c.append((n, img))
    picks = "".join(
        f'<label class="pick"><input type="radio" name="coche" value="{e(n)}" data-img="{p.asset("img/" + img.replace(".jpg", "-sm.jpg"))}"{" checked" if i == 0 else ""}>'
        f'{photo(p, img.replace(".jpg", "-sm.jpg"), "", sizes="25vw")}<span>{e(n)}</span></label>'
        for i, (n, img) in enumerate(all_c))
    sets = ""
    for key, (legend, options) in CONFIG_OPTIONS.items():
        cards = "".join(
            f'<label class="opt-card"><input type="radio" name="{key}" value="{e(l)}" data-gain="{g}"{" checked" if i == 0 else ""}>'
            f'<span>{e(l)}<small>{e(h)}{f" (+{g} %)" if g else ""}</small></span></label>'
            for i, (l, h, g) in enumerate(options))
        sets += f'<fieldset class="rv"><legend>{legend}</legend><div class="opts">{cards}</div></fieldset>'
    main = page_head(p, "Configurador", "Configura", "car-bmw-325.jpg", "tu coche",
                     "Elige ruedas, suspensión, alerón y preparación de motor. Te mandamos el presupuesto de esa configuración por WhatsApp.", long=True) + f"""
<section class="section" style="padding-top:0">
  <div class="wrap g12 config" id="configurador">
    <div class="config-main">
      <fieldset class="rv"><legend>Coche</legend><div class="picker">{picks}</div></fieldset>
      {sets}
    </div>
    <aside class="panel summary" aria-label="Resumen de tu configuración">
      <h2>Tu configuración</h2>
      <figure class="summary-photo"><img id="sum-photo" src="{p.asset("img/" + all_c[0][1].replace(".jpg", "-sm.jpg"))}" alt="" width="600" height="400"></figure>
      <dl>
        <div><dt>Coche</dt><dd id="sum-coche"></dd></div>
        <div><dt>Ruedas</dt><dd id="sum-ruedas"></dd></div>
        <div><dt>Suspensión</dt><dd id="sum-suspension"></dd></div>
        <div><dt>Alerón</dt><dd id="sum-aleron"></dd></div>
        <div><dt>Motor</dt><dd id="sum-motor"></dd></div>
      </dl>
      <div class="meter" aria-hidden="true"><i id="cfg-meter"></i></div>
      <div class="meter-label"><span>Potencia estimada</span><b id="cfg-gain" aria-live="polite">De serie</b></div>
      <a class="btn btn-wa" id="cfg-wa" href="{wa()}" target="_blank" rel="noopener" style="width:100%">{WA_ICON}Pedir presupuesto por WhatsApp</a>
      <p class="form-note">Se abre WhatsApp con tu configuración escrita. La ganancia de potencia es orientativa y depende del coche y su estado.</p>
    </aside>
  </div>
</section>"""
    return p, layout(p, "Configurador | Prepara tu coche de competición - Busco Tu Coche",
                     "Configura ruedas, suspensión, alerón y motor de tu coche de competición o drift y pide presupuesto.", "competicion", main)


def plain_head(p, crumb, title, lead):
    return f"""<section class="page-head"><div class="wrap">
  <nav class="crumbs" aria-label="Estás en"><a href="{p.href("index.html")}">Inicio</a> / {e(crumb)}</nav>
  <h1 class="sentence long">{e(title)}</h1>
  <div class="g12 intro"><p class="lead">{lead}</p></div>
</div></section>"""


def page_legal():
    F = lambda t: f'<span class="fill">{t}</span>'
    p1 = Page("aviso-legal/index.html")
    main1 = plain_head(p1, "Aviso legal", "Aviso legal", "Información sobre el titular de esta web, conforme a la Ley 34/2002 de Servicios de la Sociedad de la Información (LSSI).") + f"""
<section class="section" style="padding-top:0"><div class="wrap prose">
<h2>Titular de la web</h2>
<ul>
<li>Nombre o razón social: {F("[Nombre o razón social]")}</li>
<li>NIF/CIF: {F("[NIF]")}</li>
<li>Domicilio: {F("[Dirección completa]")}, Madrid, España</li>
<li>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>Teléfono: {PHONE_DISPLAY}</li>
<li>Datos registrales: {F("[Registro Mercantil, tomo, folio y hoja, solo si es sociedad]")}</li>
</ul>
<h2>Objeto</h2>
<p>Esta web informa sobre los servicios de {BRAND} de búsqueda, compra, importación, homologación y matriculación de vehículos, y permite solicitar presupuestos.</p>
<h2>Uso de la web</h2>
<p>Quien navega por la web se compromete a usarla de forma lícita y a no dañar su funcionamiento. Los coches que aparecen son ejemplos de modelos que podemos importar; la disponibilidad, el precio y los plazos se confirman siempre en el presupuesto personalizado.</p>
<h2>Propiedad intelectual</h2>
<p>Los textos, el diseño y el logotipo de esta web pertenecen a su titular. Las fotos son de Wikimedia Commons y se usan según su licencia (ver <a href="{p1.href("creditos/index.html")}">créditos</a>). Las marcas y modelos de coches citados pertenecen a sus fabricantes y se mencionan solo para identificar los vehículos.</p>
<h2>Responsabilidad</h2>
<p>Hacemos lo posible para que la información sea correcta y esté actualizada, pero no nos hacemos responsables de errores puntuales ni de los contenidos de webs externas enlazadas.</p>
<h2>Legislación aplicable</h2>
<p>Este aviso legal se rige por la legislación española.</p>
</div></section>"""
    p2 = Page("privacidad/index.html")
    main2 = plain_head(p2, "Política de privacidad", "Privacidad", "Cómo tratamos los datos que nos envías, conforme al Reglamento General de Protección de Datos (RGPD) y la LOPDGDD.") + f"""
<section class="section" style="padding-top:0"><div class="wrap prose">
<h2>Responsable del tratamiento</h2>
<p>{F("[Nombre o razón social]")}, con NIF {F("[NIF]")} y domicilio en {F("[Dirección completa]")}. Contacto: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Qué datos recogemos</h2>
<p>Los que nos das en los formularios de contacto y de anuncios, o por WhatsApp, teléfono y email: nombre, teléfono, email y los datos del coche que buscas o vendes.</p>
<h2>Para qué los usamos</h2>
<ul><li>Responder a tu solicitud y prepararte un presupuesto.</li><li>Gestionar la importación si la contratas.</li><li>Revisar y publicar tu anuncio en la sección de stock, si lo envías.</li></ul>
<h2>Base legal</h2>
<p>Tu consentimiento al enviar el formulario y, si contratas, la ejecución del contrato.</p>
<h2>Cuánto tiempo los guardamos</h2>
<p>Mientras dure la relación y, después, el tiempo que exijan las obligaciones legales. Si no llegas a contratar, borramos los datos de la solicitud en un plazo máximo de {F("[12 meses]")}.</p>
<h2>Con quién los compartimos</h2>
<p>No vendemos tus datos. Solo los compartimos cuando es necesario para la importación (transportistas, agentes de aduanas, gestorías, estaciones de ITV) y con los proveedores técnicos de la web: {F("[GitHub Pages (alojamiento), WhatsApp (mensajería); revisar]")}.</p>
<h2>Tus derechos</h2>
<p>Puedes pedir acceso, rectificación, supresión, oposición, limitación y portabilidad de tus datos escribiendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. Si crees que no los tratamos bien, puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>
<h2>Cookies</h2>
<p>Esta web no usa cookies de análisis ni de publicidad. Las tipografías se sirven desde nuestro propio servidor.</p>
</div></section>"""
    return [(p1, layout(p1, f"Aviso legal - {BRAND}", f"Aviso legal de {BRAND}.", "", main1)),
            (p2, layout(p2, f"Política de privacidad - {BRAND}", f"Política de privacidad de {BRAND}.", "", main2))]


def page_credits():
    p = Page("creditos/index.html")
    rows = ""
    for f in load_json("fotos.json"):
        lic = f'<a href="{e(f["licurl"])}" target="_blank" rel="noopener">{e(f["lic"])}</a>' if f.get("licurl") else e(f["lic"])
        thumb = photo(p, f["file"].replace(".jpg", "-sm.jpg"), f["coche"], sizes="120px")
        rows += (f'<li class="rv">{thumb}<p><b>{e(f["coche"])}</b>. Foto de {e(f["artist"])}, licencia {lic}. '
                 f'<a href="{e(f["page"])}" target="_blank" rel="noopener">Ver original en Wikimedia Commons</a>. Recortada y reducida para la web.</p></li>')
    main = plain_head(p, "Créditos de las fotos", "Créditos de las fotos", "Las fotos de los coches son de Wikimedia Commons y se usan según su licencia libre. Gracias a sus autores.") + f"""
<section class="section" style="padding-top:0"><div class="wrap">
<p>Los coches de las fotos son ejemplos de los modelos que importamos; no son unidades a la venta salvo que aparezcan en la sección de stock.</p>
<ul class="g12 credits">{rows}</ul>
</div></section>"""
    return p, layout(p, f"Créditos de las fotos - {BRAND}", f"Autores y licencias de las fotos de {BRAND}.", "", main)


def page_404():
    p = Page("404.html")
    main = f"""<section class="hero"><div class="wrap">
  <h1 class="sentence long">Esta página no existe</h1>
  <p class="lead" style="margin-top:32px">Puede que el enlace esté mal escrito o que la página se haya movido.</p>
  <div class="form-actions"><a class="btn" href="/">Ir al inicio</a><a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{WA_ICON}Escribir por WhatsApp</a></div>
</div></section>"""
    return p, layout(p, f"Página no encontrada - {BRAND}", "La página que buscas no existe.", "", main)


# =====================================================================
# GENERACIÓN
# =====================================================================
def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"), ignore=shutil.ignore_patterns("README*"))

    pages = [page_home(), page_about(), page_street(), page_race(), page_drift(), page_perks(),
             page_stock(), page_upload(), page_contact(), page_config(), page_credits(), page_404()]
    pages += page_legal()
    for p, content in pages:
        dest = os.path.join(OUT, p.path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    open(os.path.join(OUT, ".nojekyll"), "w").close()
    if DOMAIN and not PREVIEW:
        with open(os.path.join(OUT, "CNAME"), "w") as f:
            f.write(DOMAIN + "\n")
        urls = "".join(
            f"<url><loc>https://{DOMAIN}/{p.path[:-len('index.html')] if p.path.endswith('index.html') else p.path}</loc></url>"
            for p, _ in pages if p.path != "404.html")
        with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        with open(os.path.join(OUT, "robots.txt"), "w") as f:
            f.write(f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n")
    print(f"Web generada en {OUT}: {len(pages)} páginas")


if __name__ == "__main__":
    main()
