#!/usr/bin/env python3
"""
Generador de la web de Busco Tu Coche.

Uso:
    python3 build.py            -> genera la web en docs/ (lo que publica GitHub Pages)
    python3 build.py --preview  -> genera una copia en preview/ con enlaces a index.html,
                                   para verla abriendo los archivos directamente

Para cambiar textos, coches o datos de contacto, edita este archivo (sección DATOS)
o data/stock.json, y vuelve a ejecutar el script.
"""
import html
import json
import os
import shutil
import sys

import scenes
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = "--preview" in sys.argv
OUT = os.path.join(ROOT, "preview" if PREVIEW else "docs")

# =====================================================================
# CONFIGURACIÓN
# =====================================================================
BRAND = "Busco Tu Coche"
DOMAIN = "buscotucoche.com"      # dominio principal (sin https). buscotuclasico.com redirige aquí desde el proveedor del dominio
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
    ("Motor V8 Competición", 2023, "usa", "car-competition.jpg", "circuito", "race", "#e0412f", 8),
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
    "Motor V8 Competición": ("", "V8 de competición", "", "Propulsión"),
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

BOARD = [
    ("DUBÁI", "SUV y deportivos de lujo", "Lamborghini Urus, Mercedes-AMG G63, Range Rover SVR"),
    ("EE. UU.", "Muscle cars y clásicos", "Mustang, Camaro, Charger, Corvette"),
    ("JAPÓN", "JDM y drift", "Skyline R34, Supra MK4, Silvia, 350Z"),
    ("ALEMANIA", "Clásicos y deportivos alemanes", "Mercedes E 500 W124, BMW 325i E30, Porsche 911, BMW M"),
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


def load_stock():
    path = os.path.join(ROOT, "data", "stock.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def img_exists(name):
    return bool(name) and os.path.exists(os.path.join(ROOT, "assets", "img", name))


class Page:
    def __init__(self, path):
        self.path = path  # p. ej. "nosotros/index.html"

    def href(self, target):
        rel = os.path.relpath(target, os.path.dirname(self.path) or ".")
        rel = rel.replace(os.sep, "/")
        if not PREVIEW and rel.endswith("index.html"):
            rel = rel[: -len("index.html")] or "./"
        return rel

    def asset(self, p):
        return os.path.relpath("assets/" + p, os.path.dirname(self.path) or ".").replace(os.sep, "/")


def wa(text=WA_DEFAULT):
    return f"https://wa.me/{WHATSAPP}?text={quote(text)}"


ICONS = {
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.3-.6-.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4C2.7 15.6 2.2 13.8 2.2 12 2.2 6.6 6.6 2.2 12 2.2c2.6 0 5.1 1 6.9 2.9 1.8 1.8 2.9 4.3 2.9 6.9 0 5.4-4.4 9.8-9.8 9.8zm8.4-18.2C18.1 1.3 15.2.1 12 .1 5.5.1.1 5.4.1 12c0 2.1.5 4.1 1.6 5.9L0 24l6.3-1.7c1.7.9 3.7 1.4 5.7 1.4 6.6 0 11.9-5.3 11.9-11.9 0-3.2-1.2-6.2-3.5-8.4z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "eye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "stars": '<svg viewBox="0 0 24 24" fill="#ffcc00" aria-hidden="true">' + "".join(
        f'<circle cx="{12 + 8 * __import__("math").cos(i * 0.5236):.2f}" cy="{12 + 8 * __import__("math").sin(i * 0.5236):.2f}" r="1.5"/>' for i in range(12)) + '</svg>',
}

FAVICON = ("data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0f1b33"/>'
    '<rect x="6" y="20" width="52" height="24" rx="4" fill="#fff"/><rect x="6" y="20" width="11" height="24" rx="3" fill="#1d3fa3"/>'
    '<text x="38" y="38.5" font-family="Arial Black,Arial" font-weight="900" font-size="14" text-anchor="middle" fill="#0f1b33">BTC</text></svg>'))


# =====================================================================
# PIEZAS COMUNES
# =====================================================================
NAV = [
    ("inicio", "Inicio", "index.html"),
    ("nosotros", "Nosotros", "nosotros/index.html"),
    ("servicios", "Servicios", None),
    ("stock", "Stock", "stock/index.html"),
    ("ventajas", "Ventajas", "ventajas/index.html"),
    ("contacto", "Contacto", "contacto/index.html"),
]


def header(p, active):
    items = []
    for key, label, target in NAV:
        if key == "servicios":
            items.append(
                '<details>'
                f'<summary{" aria-current=page" if active in ("calle", "competicion", "drift") else ""}>Servicios<span class="caret" aria-hidden="true"></span></summary>'
                '<div class="submenu">'
                f'<a href="{p.href("servicios/calle/index.html")}"{" aria-current=page" if active == "calle" else ""}>Coches de calle<small>Clásicos, deportivos y SUV de lujo</small></a>'
                f'<a href="{p.href("servicios/competicion/index.html")}"{" aria-current=page" if active == "competicion" else ""}>Coches de competición<small>Circuito y drift, configurables</small></a>'
                f'<a href="{p.href("drift-72h/index.html")}"{" aria-current=page" if active == "drift" else ""}>Drift en 72 horas<small>Tu coche listo para derrapar</small></a>'
                '</div></details>'
            )
        else:
            cur = ' aria-current="page"' if active == key else ""
            items.append(f'<a href="{p.href(target)}"{cur}>{label}</a>')
    nav = "\n".join(items)
    return f"""<a class="skip" href="#main">Saltar al contenido</a>
<header class="site-header">
  <div class="wrap">
    {logo(p)}
    <nav class="nav" id="nav" aria-label="Principal">
      {nav}
      <a class="btn btn-gold header-cta" href="{p.href("contacto/index.html")}">Pedir presupuesto</a>
    </nav>
    <a class="btn btn-gold header-cta header-cta-desktop" href="{p.href("contacto/index.html")}">Pedir presupuesto</a>
    <button class="menu-btn" type="button" aria-controls="nav" aria-expanded="false"><span class="bars"></span><span class="sr-only">Menú</span></button>
  </div>
</header>"""


def logo(p):
    return (f'<a class="plate" href="{p.href("index.html")}" aria-label="{BRAND}, ir al inicio">'
            f'<span class="plate-eu">{ICONS["stars"]}E</span><span class="plate-txt">{e(BRAND)}</span></a>')


def footer(p):
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        {logo(p)}
        <p>Importación de coches premium, clásicos y de competición a España desde Dubái, EE. UU., Japón y Alemania. Servicio integral, transparente y con garantía legal.</p>
      </div>
      <div>
        <h3>La web</h3>
        <ul>
          <li><a href="{p.href("nosotros/index.html")}">Nosotros</a></li>
          <li><a href="{p.href("servicios/calle/index.html")}">Coches de calle</a></li>
          <li><a href="{p.href("servicios/competicion/index.html")}">Coches de competición</a></li>
          <li><a href="{p.href("drift-72h/index.html")}">Drift en 72 horas</a></li>
          <li><a href="{p.href("stock/index.html")}">Stock</a></li>
          <li><a href="{p.href("ventajas/index.html")}">Ventajas</a></li>
        </ul>
      </div>
      <div>
        <h3>Contacto</h3>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
          <li><a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{CITY}</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {YEAR} {BRAND}. Todos los derechos reservados.</span>
      <ul>
        <li><a href="{p.href("aviso-legal/index.html")}">Aviso legal</a></li>
        <li><a href="{p.href("privacidad/index.html")}">Política de privacidad</a></li>
        <li><a href="{p.href("creditos/index.html")}">Créditos de las fotos</a></li>
      </ul>
    </div>
  </div>
</footer>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp al {PHONE_DISPLAY}">{ICONS["wa"]}</a>"""


def layout(p, title, desc, active, main, extra_head="", dark_head=True):
    canonical = ""
    og_url = ""
    if DOMAIN:
        clean = p.path[: -len("index.html")] if p.path.endswith("index.html") else p.path
        canonical = f'<link rel="canonical" href="https://{DOMAIN}/{clean}">'
        og_url = f'<meta property="og:url" content="https://{DOMAIN}/{clean}">'
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0f1b33">
{canonical}
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="{e(BRAND)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{og_url}
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="{p.asset("fonts/archivo.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p.asset("css/site.css")}">
{extra_head}
</head>
<body data-wa="{WHATSAPP}" data-endpoint="{e(FORM_ENDPOINT)}">
{header(p, active)}
<main id="main">
{main}
</main>
{footer(p)}
<script src="{p.asset("js/site.js")}" defer></script>
</body>
</html>
"""


def page_head(p, crumbs, h1, lead, race=False, extra=""):
    trail = " / ".join(
        f'<a href="{p.href(t)}">{e(l)}</a>' if t else e(l) for l, t in crumbs)
    return f"""<section class="page-head dark{' race' if race else ''}">
  <div class="wrap">
    <nav class="crumbs" aria-label="Estás en">{trail}</nav>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {extra}
  </div>
</section>"""


SCENE_FILES = {}


def scene_file(scene, kind, paint, number=None):
    """Registra una ilustración y devuelve su nombre de archivo."""
    name = f"{scene}-{kind}-{paint.lstrip('#')}{'-' + str(number) if number else ''}.svg"
    SCENE_FILES[name] = (scene, kind, paint, number)
    return name


def photo_tag(p, img, alt, lazy=True, sizes="(max-width: 640px) 100vw, 400px"):
    sm = img.replace(".jpg", "-sm.jpg")
    srcset = f'{p.asset("img/" + sm)} 600w, {p.asset("img/" + img)} 1200w' if img_exists(sm) else ""
    return (f'<img src="{p.asset("img/" + img)}"' + (f' srcset="{srcset}" sizes="{sizes}"' if srcset else "")
            + f' alt="{e(alt)}"' + (' loading="lazy"' if lazy else "") + ' decoding="async" width="1200" height="800">')


def car_media(p, name, sub, img, tag, scene, kind, paint, number=None, tag_race=False, chassis="", lazy=True):
    if img_exists(img):
        inner = photo_tag(p, img, f"{name}, {sub}", lazy)
    else:
        src = p.asset("img/escenas/" + scene_file(scene, kind, paint, number))
        inner = f'<img src="{src}" alt="{e(name)}, {e(sub)}"{' loading="lazy"' if lazy else ""} decoding="async" width="800" height="600">'
    t = f'<span class="tag{" tag-race" if tag_race else ""}">{e(tag)}</span>' if tag else ""
    if chassis:
        t += f'<span class="tag tag-chassis" title="Chasis">{e(chassis)}</span>'
    return f'<div class="car-media">{inner}{t}</div>'


def specs_html(name):
    sp = SPECS.get(name)
    if not sp:
        return ""
    chasis, motor, cv, trac = sp
    items = []
    if motor:
        items.append(("Motor", motor))
    if cv:
        items.append(("Potencia", cv))
    if trac:
        items.append(("Tracción", trac))
    rows = "".join(f"<div><dt>{k}</dt><dd>{e(v)}</dd></div>" for k, v in items)
    return f'<dl class="spec">{rows}</dl>'


def chassis_tag(name):
    sp = SPECS.get(name)
    return sp[0] if sp and sp[0] and not sp[0].endswith("generación") else ""


def find_car(name):
    for n, year, o, img, kind, paint in STREET_CARS:
        if n == name:
            return dict(year=year, o=o, img=img, scene=o, kind=kind, paint=paint, num=None, race=False)
    for n, year, o, img, k, body, paint, num in RACE_CARS:
        if n == name:
            return dict(year=year, o=o, img=img, scene=k, kind=body, paint=paint, num=num, race=True)
    raise KeyError(name)


def legends_html(p):
    cards = ""
    for name, blurb in LEGENDS:
        c = find_car(name)
        target = "servicios/competicion/index.html" if c["race"] else "servicios/calle/index.html"
        link = p.href("contacto/index.html") + "?modelo=" + quote(f"{name} {c['year']}")
        cards += f"""<article class="car legend">
  {car_media(p, name, f"{c['year']}, desde {ORIGINS[c['o']]}", c["img"], ORIGINS[c["o"]], c["scene"], c["kind"], c["paint"], c["num"], chassis=chassis_tag(name), lazy=False)}
  <div class="car-body"><h3>{e(name)}</h3><p class="car-meta">{e(blurb)}</p>
  {specs_html(name)}
  <a class="btn btn-navy" href="{e(link)}">Quiero uno así</a></div>
</article>"""
    return f"""<section class="section dark legends">
  <div class="wrap">
    <div class="section-head split-head">
      <div>
        <h2>Los más buscados</h2>
        <p class="lead">Clásicos alemanes, JDM de los 90 y muscle cars. Si lo tienes en la cabeza, lo encontramos.</p>
      </div>
      <a class="btn btn-line" href="{p.href("servicios/calle/index.html")}">Ver todos los coches</a>
    </div>
    <div class="legend-row">{cards}</div>
  </div>
</section>"""


def cta_final(p):
    return f"""<section class="section dark cta-final">
  <div class="wrap">
    <div>
      <h2>Pide tu presupuesto sin compromiso</h2>
      <p class="lead">Cuéntanos qué coche quieres importar y te enviamos un estudio personalizado en menos de 24 horas.</p>
    </div>
    <div class="actions">
      <a class="btn btn-gold" href="{p.href("contacto/index.html")}">Pedir presupuesto</a>
      <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{ICONS["wa"]}Escribir por WhatsApp</a>
    </div>
  </div>
</section>"""


def steps_html(dark=False):
    lis = "\n".join(f'<li class="step"><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in STEPS)
    return f'<ol class="steps">{lis}</ol>'


def faq_html(p, title="Preguntas frecuentes"):
    items = "".join(f'<details class="faq-item"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    return f"""<section class="section white" id="preguntas">
  <div class="wrap faq">
    <div>
      <h2>{title}</h2>
      <p class="lead">Lo que más nos preguntan antes de importar. Si te queda alguna duda, escríbenos.</p>
      <a class="btn btn-wa" href="{wa("Hola, tengo una duda sobre importar un coche")}" target="_blank" rel="noopener">{ICONS["wa"]}Preguntar por WhatsApp</a>
    </div>
    <div class="faq-list">{items}</div>
  </div>
</section>"""


def faq_jsonld():
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def ship_banner(p):
    if img_exists("barco.jpg"):
        return (f'<figure class="banner"><img src="{p.asset("img/barco.jpg")}" srcset="{p.asset("img/barco-sm.jpg")} 800w, {p.asset("img/barco.jpg")} 1600w" '
                f'sizes="(max-width: 1200px) 100vw, 1120px" alt="Barco portacoches navegando al atardecer" loading="lazy" width="1600" height="610"></figure>')
    return (f'<figure class="banner"><img src="{p.asset("img/escenas/barco.svg")}" alt="Barco portacontenedores rumbo a Europa" '
            f'width="800" height="600"></figure>')


def perks_html():
    return '<div class="perks">' + "".join(
        f'<div class="perk">{ICONS[i]}<h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in PERKS) + "</div>"


# =====================================================================
# PÁGINAS
# =====================================================================
def page_home():
    p = Page("index.html")
    board_rows = ""
    for origin, what, models in BOARD:
        flaps = "".join('<span class="flap sp"> </span>' if c == " " else f'<span class="flap">{e(c)}</span>' for c in origin)
        board_rows += f'<div class="board-row"><div class="flaps" aria-label="{e(origin.title())}">{flaps}</div><div class="board-what">{e(what)}<small>{e(models)}</small></div></div>'

    jsonld = {
        "@context": "https://schema.org",
        "@type": "AutoDealer",
        "name": BRAND,
        "description": "Importación de coches de lujo, clásicos, drift y competición desde Dubái, EE. UU., Japón y Alemania a España y Europa.",
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressLocality": "Madrid", "addressCountry": "ES"},
        "areaServed": "Europa",
    }
    if DOMAIN:
        jsonld["url"] = f"https://{DOMAIN}/"
    head = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' + faq_jsonld()

    main = f"""
<section class="hero dark">
  <div class="wrap">
    <div>
      <h1>El coche que buscas, nosotros lo conseguimos</h1>
      <p class="lead">Importamos coches de gama alta y de competición desde Dubái, EE. UU., Japón y Alemania. Clásicos, deportivos, SUV de lujo, drift y coches de carreras: nos encargamos de todo hasta que lo matriculas en España.</p>
      <div class="actions">
        <a class="btn btn-gold" href="{p.href("contacto/index.html")}">Pedir presupuesto gratis</a>
        <a class="btn btn-line" href="{p.href("servicios/calle/index.html")}">Ver coches</a>
      </div>
      <ul class="hero-facts">
        <li>{ICONS["clock"]}Estudio personalizado en menos de 24 h</li>
        <li>{ICONS["check"]}Aduanas, ITV y matrícula incluidas</li>
      </ul>
    </div>
    <div class="board" role="region" aria-label="Desde dónde importamos">
      <div class="board-top"><span>Rutas de importación a España</span><span class="live">Abiertas</span></div>
      <div class="board-cols"><span>Origen</span><span>Qué traemos</span></div>
      {board_rows}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>¿Qué coche quieres importar?</h2>
      <p class="lead">Dos caminos según el uso que le vayas a dar.</p>
    </div>
    <div class="paths">
      <a class="path path-street" href="{p.href("servicios/calle/index.html")}">
        <div class="path-bg">{photo_tag(p, "car-mustang-boss.jpg", "", sizes="(max-width: 760px) 100vw, 600px")}</div><div class="path-text">
        <h3>Coches de calle</h3>
        <p>Clásicos, deportivos, SUV y berlinas premium para uso diario o de colección.</p>
        <span class="fake-link">Ver coches de calle</span></div>
      </a>
      <a class="path path-race" href="{p.href("servicios/competicion/index.html")}">
        <div class="path-bg">{photo_tag(p, "car-bmw-drift.jpg", "", sizes="(max-width: 760px) 100vw, 600px")}</div><div class="path-text">
        <h3>Coches de competición</h3>
        <p>Coches preparados para circuito y drift, totalmente configurables.</p>
        <span class="fake-link">Ver coches de competición</span></div>
      </a>
    </div>
  </div>
</section>

{legends_html(p)}

<section class="section-tight drift-band">
  <div class="wrap">
    <div class="drift-72" aria-hidden="true">72h<small>listo para derrapar</small></div>
    <div>
      <h2>Driftea en una semana</h2>
      <p>Elige tu nivel (principiante, amateur o profesional), elige tu coche y configura suspensión, ángulo de giro, bloqueo de diferencial, freno de mano hidráulico, baquets y jaula antivuelco. Te lo entregamos preparado en 72 horas.</p>
    </div>
    <a class="btn" href="{p.href("drift-72h/index.html")}">Elegir mi coche de drift</a>
  </div>
</section>

<section class="section white">
  <div class="wrap">
    <div class="section-head split-head">
      <div>
        <h2>Así importamos tu coche</h2>
        <p class="lead">Siete pasos. Tú eliges el coche y nosotros hacemos el resto.</p>
      </div>
      <a class="btn btn-line" href="{p.href("nosotros/index.html")}">Conocernos</a>
    </div>
    {ship_banner(p)}
    {steps_html()}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>Por qué importar con nosotros</h2>
    </div>
    {perks_html()}
  </div>
</section>

{faq_html(p)}

{cta_final(p)}
"""
    return p, layout(p, "Busco Tu Coche | Importación de coches premium, drift y competición",
                     "Importamos coches de lujo, clásicos, drift y competición desde Dubái, EE. UU., Japón y Alemania a Europa. Servicio llave en mano: el coche que buscas, nosotros lo conseguimos.",
                     "inicio", main, head)


def page_about():
    p = Page("nosotros/index.html")
    ticks = "".join(f"<li>{e(v)}</li>" for v in VALUES)
    main = page_head(p, [("Inicio", "index.html"), ("Nosotros", None)],
                     "Tu socio de confianza para importar coches únicos",
                     "Somos una empresa especializada en la importación llave en mano de vehículos premium, clásicos, deportivos, de drift y de competición desde Dubái, EE. UU., Japón y Alemania hasta tu garaje en España y Europa.") + f"""
<section class="section white">
  <div class="wrap two-col">
    <div>
      <h2>Nuestra misión</h2>
      <p class="mission">Hacer accesible el coche que siempre soñaste, gestionando cada paso con transparencia, seguridad jurídica y trato personal.</p>
    </div>
    <div>
      <h2>Nuestros valores</h2>
      <ul class="ticks">{ticks}</ul>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>Cómo hacemos las importaciones</h2>
      <p class="lead">Un proceso probado, claro y sin sorpresas.</p>
    </div>
    {ship_banner(p)}
    {steps_html()}
  </div>
</section>
{cta_final(p)}"""
    return p, layout(p, "Nosotros | Importación de coches premium y competición - Busco Tu Coche",
                     "Conoce cómo importamos coches de lujo, clásicos, drift y competición desde Dubái, EE. UU., Japón y Alemania. Proceso transparente llave en mano.",
                     "nosotros", main)


def filters_html(target, options):
    chips = "".join(
        f'<button type="button" class="chip" data-value="{v}" aria-pressed="{"true" if i == 0 else "false"}">{e(l)}</button>'
        for i, (v, l) in enumerate(options))
    return f'<div class="filters" role="group" aria-label="Filtrar coches" data-filter-group="{target}">{chips}</div>'


def page_street():
    p = Page("servicios/calle/index.html")
    cards = ""
    for name, year, o, img, kind, paint in STREET_CARS:
        sub = f"{year}, desde {ORIGINS[o]}"
        link = p.href("contacto/index.html") + "?modelo=" + quote(f"{name} {year}")
        tags = o + (" clasico" if year < 2000 else "")
        cards += f"""<article class="car" data-tags="{tags}">
  {car_media(p, name, sub, img, ORIGINS[o], o, kind, paint, chassis=chassis_tag(name))}
  <div class="car-body"><h3>{e(name)}</h3><p class="car-meta">Año {year}. Importado desde {ORIGINS[o].rstrip(".")}.</p>
  {specs_html(name)}
  <a class="btn btn-navy" href="{e(link)}">Pedir presupuesto</a></div>
</article>"""
    opts = [("todos", "Todos"), ("clasico", "Clásicos")] + [(k, v) for k, v in ORIGINS.items()]
    main = page_head(p, [("Inicio", "index.html"), ("Coches de calle", None)],
                     "Coches de calle: clásicos, deportivos y SUV de lujo",
                     "Vehículos premium importados desde Dubái, EE. UU., Japón y Alemania, listos para circular por Europa con todos los trámites incluidos.") + f"""
<section class="section">
  <div class="wrap">
    <p class="lead" style="margin-bottom:24px">Estos son ejemplos de lo que traemos. Si buscas otro modelo, pídelo: lo localizamos.</p>
    {filters_html("lista-calle", opts)}
    <div class="cars" id="lista-calle">{cards}</div>
    <div class="empty" id="lista-calle-empty" hidden><p>No hay coches con ese filtro en esta lista, pero podemos buscarlo por ti.</p><a class="btn btn-navy" href="{p.href("contacto/index.html")}">Pedir un coche concreto</a></div>
  </div>
</section>
{cta_final(p)}"""
    return p, layout(p, "Coches de calle | Importación de coches premium - Busco Tu Coche",
                     "Importa coches premium de calle: clásicos, deportivos, SUV de lujo y berlinas desde Dubái, EE. UU., Japón y Alemania. Listos para circular en Europa.",
                     "calle", main)


def page_race():
    p = Page("servicios/competicion/index.html")
    cards = ""
    for name, year, o, img, kind, body, paint, num in RACE_CARS:
        sub = f"{year}, desde {ORIGINS[o]}"
        tag = "Drift" if kind == "drift" else "Circuito"
        link = p.href("configurador/index.html") + "?coche=" + quote(name)
        cards += f"""<article class="car" data-tags="{kind}">
  {car_media(p, name, sub, img, tag, kind, body, paint, num, tag_race=True, chassis=chassis_tag(name))}
  <div class="car-body"><h3>{e(name)}</h3><p class="car-meta">Año {year}. Importado desde {ORIGINS[o].rstrip(".")}.</p>
  {specs_html(name)}
  <a class="btn btn-navy" href="{e(link)}">Configurar</a></div>
</article>"""
    main = page_head(p, [("Inicio", "index.html"), ("Coches de competición", None)],
                     "Coches de competición y drift",
                     "Preparaciones reales para circuito y drift. Cada coche se puede configurar a medida: ruedas, suspensión, alerones y potencia de motor.", race=True) + f"""
<section class="section">
  <div class="wrap">
    {filters_html("lista-comp", [("todos", "Todos"), ("circuito", "Circuito"), ("drift", "Drift")])}
    <div class="cars" id="lista-comp">{cards}</div>
  </div>
</section>
<section class="section-tight drift-band">
  <div class="wrap">
    <div class="drift-72" aria-hidden="true">72h<small>listo para derrapar</small></div>
    <div><h2>¿Empiezas en el drift?</h2><p>Tenemos coches preparados por niveles, de principiante a profesional, listos en 72 horas.</p></div>
    <a class="btn" href="{p.href("drift-72h/index.html")}">Ver coches por nivel</a>
  </div>
</section>
{cta_final(p)}"""
    return p, layout(p, "Coches de competición y drift | Configurables - Busco Tu Coche",
                     "Importa y configura coches de competición y drift: ruedas, suspensión, alerones y tuning. Skyline R34, Supra MK4, Nissan 350Z, BMW M3 E46 y más.",
                     "competicion", main)


def page_drift():
    p = Page("drift-72h/index.html")
    feats = "".join(f"<li>{x}</li>" for x in ["Suspensión", "Ángulo de giro", "Bloqueo de diferencial", "Freno de mano hidráulico", "Baquets", "Jaula antivuelco"])
    levels = ""
    for title, slug, desc, cars in DRIFT_LEVELS:
        cards = ""
        for name, img, body, paint in cars:
            link = p.href("configurador/index.html") + "?coche=" + quote(name + " (drift)")
            cards += f"""<article class="car">
  {car_media(p, name, "preparación drift", img, "", "drift", body, paint, chassis=chassis_tag(name))}
  <div class="car-body"><h3>{e(name)}</h3><p class="car-meta">Nivel {slug}.</p>
  {specs_html(name)}
  <a class="btn btn-navy" href="{e(link)}">Configurar este coche</a></div>
</article>"""
        levels += f"""<div class="level" id="{slug}">
  <div class="level-head"><div><h2>{title}</h2></div><p>{e(desc)}</p></div>
  <div class="cars">{cards}</div>
</div>"""
    main = page_head(p, [("Inicio", "index.html"), ("Drift en 72 horas", None)],
                     "Drift en 72 horas: tu coche listo para derrapar",
                     "Elige tu nivel, elige tu coche y configura cada detalle. Lo preparamos y te lo entregamos en 72 horas.", race=True,
                     extra=f'<ul class="feature-list" aria-label="Qué puedes configurar">{feats}</ul>') + f"""
<section class="section">
  <div class="wrap">
    {levels}
  </div>
</section>
{cta_final(p)}"""
    return p, layout(p, "Drift en 72h | Configura tu coche para derrapar - Busco Tu Coche",
                     "Coches preparados para drift listos en 72 horas. BMW E36/E46, Lexus IS200/300, Supra, Silvia S13/S14, M3, Mustang GT, Charger, GT86. Configura suspensión, ángulo, diferencial, hidráulico, baquets y jaula.",
                     "drift", main)


def page_perks():
    p = Page("ventajas/index.html")
    main = page_head(p, [("Inicio", "index.html"), ("Ventajas", None)],
                     "Por qué elegirnos",
                     "Confianza, exclusividad y un servicio integral que cuida cada detalle.") + f"""
<section class="section white">
  <div class="wrap">
    {perks_html()}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Todo lo que hacemos por ti</h2><p class="lead">De la búsqueda a la matrícula española, sin que tengas que hacer un solo trámite.</p></div>
    {steps_html()}
  </div>
</section>
{cta_final(p)}"""
    return p, layout(p, "Ventajas | Por qué importar con Busco Tu Coche",
                     "Transparencia total, garantía legal, acceso global y trámites llave en mano. Descubre las ventajas de importar tu coche con nosotros.",
                     "ventajas", main)


def page_stock():
    p = Page("stock/index.html")
    stock = load_stock()
    if stock:
        cards = ""
        for c in stock:
            title = f"{c.get('marca', '')} {c.get('modelo', '')}".strip()
            year = c.get("año", "")
            bits = []
            if c.get("km"):
                bits.append(f"{int(c['km']):,} km".replace(",", "."))
            if c.get("origen"):
                bits.append(f"origen {c['origen']}")
            meta = f"Año {year}" + (". " + ", ".join(bits).capitalize() if bits else "") + "."
            price = f'<p style="font-weight:800;font-size:1.3rem;margin:0 0 14px">{int(c["precio"]):,} €</p>'.replace(",", ".") if c.get("precio") else ""
            desc = f'<p class="car-meta">{e(c["descripcion"])}</p>' if c.get("descripcion") else ""
            msg = f"Hola, me interesa el {title} {year} publicado en stock"
            cards += f"""<article class="car">
  {car_media(p, title, str(year), c.get("foto", ""), "En stock", c.get("escena", "de"), c.get("carroceria", "sedan"), c.get("color", "#274e9b"))}
  <div class="car-body"><h3>{e(title)}</h3><p class="car-meta">{e(meta)}</p>{desc}{price}
  <a class="btn btn-wa" href="{wa(msg)}" target="_blank" rel="noopener">{ICONS["wa"]}Más detalles por WhatsApp</a></div>
</article>"""
        listing = f'<div class="cars">{cards}</div>'
    else:
        listing = f"""<div class="empty">
  <p>Ahora mismo no hay coches publicados en stock. Si buscas uno concreto, lo importamos por encargo. Y si vendes el tuyo, publícalo aquí.</p>
  <div class="actions" style="justify-content:center;margin-top:0">
    <a class="btn btn-navy" href="{p.href("contacto/index.html")}">Pedir un coche por encargo</a>
    <a class="btn btn-line" href="{p.href("stock/subir/index.html")}">Subir mi anuncio</a>
  </div>
</div>"""
    main = page_head(p, [("Inicio", "index.html"), ("Stock", None)],
                     "Coches en stock",
                     "Vehículos disponibles ahora mismo, listos para entrega rápida en España.",
                     extra=f'<div class="actions"><a class="btn btn-gold" href="{p.href("stock/subir/index.html")}">Subir mi anuncio</a></div>') + f"""
<section class="section">
  <div class="wrap">{listing}</div>
</section>"""
    return p, layout(p, "Coches en stock | Disponibles ahora - Busco Tu Coche",
                     "Coches importados disponibles ahora mismo para entrega rápida en España.",
                     "stock", main)


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
            f'<span>He leído y acepto la <a href="{p.href("privacidad/index.html")}">política de privacidad</a>.</span></label></div>')


def form_note():
    if FORM_ENDPOINT:
        return ""
    return '<p class="form-note">Al enviar se abrirá WhatsApp con tu solicitud ya escrita. Solo tienes que pulsar enviar.</p>'


def page_upload():
    p = Page("stock/subir/index.html")
    main = page_head(p, [("Inicio", "index.html"), ("Stock", "stock/index.html"), ("Subir anuncio", None)],
                     "Sube tu anuncio",
                     "Publica tu coche en nuestra sección de stock. Revisamos cada anuncio antes de publicarlo.") + f"""
<section class="section">
  <div class="wrap" style="max-width:860px">
    <form class="card-panel" novalidate
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
      <div class="actions"><button class="btn btn-navy" type="submit">Enviar anuncio</button></div>
      <p class="form-note">Las fotos del coche nos las mandas por WhatsApp después de enviar el anuncio.</p>
      {form_note()}
      <div class="form-status" role="status" aria-live="polite"></div>
    </form>
  </div>
</section>"""
    return p, layout(p, "Sube tu anuncio | Stock - Busco Tu Coche",
                     "Publica tu coche en la sección de stock de Busco Tu Coche.", "stock", main)


def page_contact():
    p = Page("contacto/index.html")
    main = page_head(p, [("Inicio", "index.html"), ("Contacto", None)],
                     "Solicita tu estudio gratuito",
                     "Cuéntanos qué coche buscas y te preparamos un presupuesto sin compromiso en menos de 24 horas.") + f"""
<section class="section">
  <div class="wrap contact-grid">
    <div>
      <h2>Habla con nosotros</h2>
      <ul class="contact-list">
        <li><a href="{wa()}" target="_blank" rel="noopener">{ICONS["wa"]}<span><small>WhatsApp, la vía más rápida</small><b>{PHONE_DISPLAY}</b></span></a></li>
        <li><a href="tel:{PHONE_TEL}">{ICONS["phone"]}<span><small>Teléfono</small><b>{PHONE_DISPLAY}</b></span></a></li>
        <li><a href="mailto:{EMAIL}">{ICONS["mail"]}<span><small>Email</small><b>{EMAIL}</b></span></a></li>
        <li><div>{ICONS["pin"]}<span><small>Dónde estamos</small><b>{CITY}</b></span></div></li>
      </ul>
    </div>
    <form class="card-panel" novalidate
      data-intro="Hola, quiero un estudio de importación:"
      data-subject="Nueva solicitud de presupuesto"
      data-ok="Solicitud enviada. Te escribimos en menos de 24 horas."
      data-ok-wa="Te hemos abierto WhatsApp con tu solicitud ya escrita. Envíala y te respondemos en menos de 24 horas.">
      <div class="form-grid">
        {field("Nombre", "nombre", placeholder="Tu nombre completo", required=True, auto="name")}
        {field("Teléfono", "telefono", "tel", "+34 600 000 000", required=True, auto="tel")}
        {field("Email", "email", "email", "tu@email.com", auto="email")}
        {field("Presupuesto aproximado", "presupuesto", "select", opts=BUDGETS)}
        {field("Marca y modelo que buscas", "modelo", placeholder="Ej. Mercedes E 500, BMW 325i, Supra MK4...", required=True)}
        {field("Generación o chasis", "chasis", placeholder="Ej. W124, E30, A80, R34")}
        {field("Algo más que debamos saber", "comentarios", "textarea", "Año, color, kilómetros, cambio manual o automático, uso que le vas a dar...", full=True)}
        {consent(p)}
      </div>
      <div class="actions"><button class="btn btn-navy" type="submit">Solicitar estudio gratuito</button></div>
      {form_note()}
      <div class="form-status" role="status" aria-live="polite"></div>
    </form>
  </div>
</section>
{faq_html(p, "Antes de escribirnos")}
<script>
  (function () {{
    var m = new URLSearchParams(location.search).get("modelo");
    if (m) document.addEventListener("DOMContentLoaded", function () {{ document.getElementById("f-modelo").value = m; }});
  }})();
</script>"""
    return p, layout(p, "Contacto | Busco Tu Coche - Importación de coches a Europa",
                     f"Habla con nuestro equipo de importación de coches. Teléfono, WhatsApp {PHONE_DISPLAY} y email. Atención personalizada.",
                     "contacto", main)


def page_config():
    p = Page("configurador/index.html")
    all_cars = [c[0] for c in RACE_CARS] + [n + " (drift)" for _, _, _, cars in DRIFT_LEVELS for n, *_ in cars]
    car_opts = "".join(f"<option>{e(c)}</option>" for c in all_cars)
    sets = ""
    for key, (legend, options) in CONFIG_OPTIONS.items():
        cards = ""
        for i, (label, hint, gain) in enumerate(options):
            cards += (f'<label class="opt-card"><input type="radio" name="{key}" value="{e(label)}" data-gain="{gain}"{" checked" if i == 0 else ""}>'
                      f'<span>{e(label)}<small>{e(hint)}{f" (+{gain} %)" if gain else ""}</small></span></label>')
        sets += f'<fieldset><legend>{legend}</legend><div class="opts">{cards}</div></fieldset>'
    main = page_head(p, [("Inicio", "index.html"), ("Coches de competición", "servicios/competicion/index.html"), ("Configurador", None)],
                     "Configura tu coche",
                     "Elige ruedas, suspensión, alerón y preparación de motor. Te mandamos el presupuesto de la configuración por WhatsApp.", race=True) + f"""
<section class="section">
  <div class="wrap config" id="configurador">
    <div>
      <div class="field" style="margin-bottom:32px"><label for="cfg-coche">Coche</label><select id="cfg-coche">{car_opts}</select></div>
      {sets}
    </div>
    <aside class="card-panel summary" aria-label="Resumen de tu configuración">
      <h2>Tu configuración</h2>
      <dl>
        <div><dt>Coche</dt><dd id="sum-coche"></dd></div>
        <div><dt>Ruedas</dt><dd id="sum-ruedas"></dd></div>
        <div><dt>Suspensión</dt><dd id="sum-suspension"></dd></div>
        <div><dt>Alerón</dt><dd id="sum-aleron"></dd></div>
        <div><dt>Motor</dt><dd id="sum-motor"></dd></div>
      </dl>
      <div class="meter" aria-hidden="true"><i id="cfg-meter"></i></div>
      <div class="meter-label"><span>Potencia estimada</span><b id="cfg-gain" aria-live="polite">De serie</b></div>
      <a class="btn btn-wa" id="cfg-wa" href="{wa()}" target="_blank" rel="noopener" style="width:100%">{ICONS["wa"]}Pedir presupuesto</a>
      <p class="form-note">Te abrimos WhatsApp con tu configuración ya escrita. La ganancia de potencia es orientativa y depende del coche y su estado.</p>
    </aside>
  </div>
</section>"""
    return p, layout(p, "Configurador | Prepara tu coche de competición - Busco Tu Coche",
                     "Configura ruedas, suspensión, alerón y motor de tu coche de competición o drift y pide presupuesto.",
                     "competicion", main)


def page_legal():
    F = lambda t: f'<span class="fill">{t}</span>'
    p1 = Page("aviso-legal/index.html")
    main1 = page_head(p1, [("Inicio", "index.html"), ("Aviso legal", None)], "Aviso legal", "Información sobre el titular de esta web, conforme a la Ley 34/2002 de Servicios de la Sociedad de la Información (LSSI).") + f"""
<section class="section white"><div class="wrap prose">
<h2>Titular de la web</h2>
<ul>
<li>Nombre o razón social: {F("[Nombre o razón social]")}</li>
<li>NIF/CIF: {F("[NIF]")}</li>
<li>Domicilio: {F("[Dirección completa]")}, Madrid, España</li>
<li>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>Teléfono: {PHONE_DISPLAY}</li>
<li>Datos registrales: {F("[Registro Mercantil, tomo, folio, hoja — solo si es sociedad]")}</li>
</ul>
<h2>Objeto</h2>
<p>Esta web informa sobre los servicios de {BRAND} de búsqueda, compra, importación, homologación y matriculación de vehículos, y permite solicitar presupuestos.</p>
<h2>Uso de la web</h2>
<p>Quien navega por la web se compromete a usarla de forma lícita y a no dañar su funcionamiento. Los coches que aparecen en las páginas de servicios son ejemplos de modelos que podemos importar; la disponibilidad, el precio y los plazos se confirman siempre en el presupuesto personalizado.</p>
<h2>Propiedad intelectual</h2>
<p>Los textos, el diseño y el logotipo de esta web pertenecen a su titular o se usan con permiso. Las marcas y modelos de coches citados pertenecen a sus fabricantes y se mencionan solo para identificar los vehículos.</p>
<h2>Responsabilidad</h2>
<p>Hacemos lo posible para que la información sea correcta y esté actualizada, pero no nos hacemos responsables de errores puntuales ni de los contenidos de webs externas enlazadas.</p>
<h2>Legislación aplicable</h2>
<p>Este aviso legal se rige por la legislación española.</p>
</div></section>"""
    p2 = Page("privacidad/index.html")
    main2 = page_head(p2, [("Inicio", "index.html"), ("Política de privacidad", None)], "Política de privacidad", "Cómo tratamos los datos que nos envías, conforme al Reglamento General de Protección de Datos (RGPD) y la LOPDGDD.") + f"""
<section class="section white"><div class="wrap prose">
<h2>Responsable del tratamiento</h2>
<p>{F("[Nombre o razón social]")}, con NIF {F("[NIF]")} y domicilio en {F("[Dirección completa]")}. Contacto: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Qué datos recogemos</h2>
<p>Los que nos das en los formularios de contacto y de anuncios, o por WhatsApp, teléfono y email: nombre, teléfono, email y los datos del coche que buscas o vendes.</p>
<h2>Para qué los usamos</h2>
<ul>
<li>Responder a tu solicitud y prepararte un presupuesto.</li>
<li>Gestionar la importación si la contratas.</li>
<li>Revisar y publicar tu anuncio en la sección de stock, si lo envías.</li>
</ul>
<h2>Base legal</h2>
<p>Tu consentimiento al enviar el formulario y, si contratas, la ejecución del contrato.</p>
<h2>Cuánto tiempo los guardamos</h2>
<p>Mientras dure la relación y, después, el tiempo que exijan las obligaciones legales. Si no llegas a contratar, borramos los datos de la solicitud en un plazo máximo de {F("[12 meses]")}.</p>
<h2>Con quién los compartimos</h2>
<p>No vendemos tus datos. Solo los compartimos cuando es necesario para la importación (transportistas, agentes de aduanas, gestorías, estaciones de ITV) y con los proveedores técnicos de la web: {F("[GitHub Pages (alojamiento), Formspree (formularios), WhatsApp (mensajería) — revisar]")}.</p>
<h2>Tus derechos</h2>
<p>Puedes pedir acceso, rectificación, supresión, oposición, limitación y portabilidad de tus datos escribiendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. Si crees que no los tratamos bien, puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>
<h2>Cookies</h2>
<p>Esta web no usa cookies de análisis ni de publicidad. Las fuentes tipográficas se sirven desde nuestro propio servidor.</p>
</div></section>"""
    return [
        (p1, layout(p1, f"Aviso legal - {BRAND}", f"Aviso legal de {BRAND}.", "", main1)),
        (p2, layout(p2, f"Política de privacidad - {BRAND}", f"Política de privacidad de {BRAND}.", "", main2)),
    ]


def page_credits():
    p = Page("creditos/index.html")
    path = os.path.join(ROOT, "data", "fotos.json")
    fotos = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    rows = ""
    for f in fotos:
        lic = f'<a href="{e(f["licurl"])}" target="_blank" rel="noopener">{e(f["lic"])}</a>' if f.get("licurl") else e(f["lic"])
        rows += (f'<li><b>{e(f["coche"])}</b>: foto de {e(f["artist"])}, licencia {lic}. '
                 f'<a href="{e(f["page"])}" target="_blank" rel="noopener">Ver original en Wikimedia Commons</a>. Recortada y reducida para la web.</li>')
    main = page_head(p, [("Inicio", "index.html"), ("Créditos de las fotos", None)], "Créditos de las fotos",
                     "Las fotos de los coches son de Wikimedia Commons y se usan según su licencia libre. Gracias a sus autores.") + f"""
<section class="section white"><div class="wrap prose">
<p>Los coches de las fotos son ejemplos de los modelos que importamos; no son unidades a la venta salvo que aparezcan en la sección de stock.</p>
<ul class="credits">{rows}</ul>
</div></section>"""
    return p, layout(p, f"Créditos de las fotos - {BRAND}", f"Autores y licencias de las fotos de {BRAND}.", "", main)


def page_404():
    p = Page("404.html")
    main = f"""<section class="page-head dark" style="min-height:60vh;display:flex;align-items:center">
  <div class="wrap">
    <h1>Esta página no existe</h1>
    <p class="lead">Puede que el enlace esté mal escrito o que la página se haya movido.</p>
    <div class="actions"><a class="btn btn-gold" href="/">Ir al inicio</a><a class="btn btn-line" href="{wa()}" target="_blank" rel="noopener">Escribir por WhatsApp</a></div>
  </div>
</section>"""
    return p, layout(p, f"Página no encontrada - {BRAND}", "La página que buscas no existe.", "", main)


# =====================================================================
# GENERACIÓN
# =====================================================================
def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"),
                    ignore=shutil.ignore_patterns("README*"))

    pages = [page_home(), page_about(), page_street(), page_race(), page_drift(),
             page_perks(), page_stock(), page_upload(), page_contact(), page_config(), page_credits(), page_404()]
    pages += page_legal()

    for p, content in pages:
        dest = os.path.join(OUT, p.path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    # Ilustraciones
    sdir = os.path.join(OUT, "assets", "img", "escenas")
    os.makedirs(sdir, exist_ok=True)
    for i, (name, (scene, kind, paint, number)) in enumerate(sorted(SCENE_FILES.items())):
        seed = sum(ord(c) for c in name)
        with open(os.path.join(sdir, name), "w", encoding="utf-8") as f:
            f.write(scenes.render(scene, kind, paint, number, seed=seed))
    with open(os.path.join(sdir, "barco.svg"), "w", encoding="utf-8") as f:
        f.write(scenes.render_ship())

    # Archivos para GitHub Pages y buscadores
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
