# -*- coding: utf-8 -*-
"""Contenido de las guías «Importar un coche a España» (una general y una por país).

Datos revisados en noviembre de 2026. Si cambia una norma, se cambia aquí y se vuelve a generar la web.
Fuentes:
- Arancel EE. UU.: Reglamento (UE) 2026/1455, aplicable desde el 1 de julio de 2026, 0 % para productos
  industriales originarios de EE. UU. con prueba de origen.
- Arancel Japón: Acuerdo de Asociación Económica UE-Japón (en vigor desde el 1-2-2019); el arancel de la UE
  a los turismos japoneses se eliminó por tramos hasta 2026. Requiere prueba de origen.
- Vehículos históricos: Real Decreto 892/2024 (en vigor desde el 1-10-2024).
- Impuesto de matriculación (IEDMT): tramos de CO2 de la Ley 38/1992 para península y Baleares.
"""

UPDATED = "2026-11-15"
UPDATED_TEXT = "noviembre de 2026"

SOURCES = [
    ("Real Decreto 892/2024, Reglamento de Vehículos Históricos (BOE)",
     "https://www.boe.es/buscar/act.php?id=BOE-A-2024-18614"),
    ("Reglamento (UE) 2026/1455: arancel cero para productos industriales de EE. UU. (EUR-Lex)",
     "https://eur-lex.europa.eu/eli/reg/2026/1455/oj"),
    ("Acuerdo de Asociación Económica UE-Japón (Comisión Europea)",
     "https://trade.ec.europa.eu/access-to-markets/es/content/acuerdo-de-asociacion-economica-ue-japon"),
]

# Tramos del impuesto de matriculación (península y Baleares)
IEDMT = [
    ("Menos de 120 g/km", "0 %"),
    ("De 120 a menos de 160 g/km", "4,75 %"),
    ("De 160 a menos de 200 g/km", "9,75 %"),
    ("200 g/km o más", "14,75 %"),
]

GUIDE_STEPS = [
    ("Elegir y revisar el coche",
     "Antes de pagar, alguien tiene que verlo en persona: chasis, mecánica, kilómetros e historial. "
     "También hay que comprobar que ese modelo se puede matricular en España."),
    ("Comprarlo con garantías",
     "Contrato, factura y el título de propiedad del país de origen, sin cargas. "
     "El pago, a través de una cuenta escrow o una garantía equivalente."),
    ("Traerlo a España",
     "Desde fuera de Europa, en barco y con seguro. Desde Alemania, en camión portacoches "
     "o conduciendo con matrícula de exportación."),
    ("Pasar la aduana",
     "Solo si viene de fuera de la UE. Se presenta el DUA y se pagan el IVA de importación "
     "y, si toca, el arancel."),
    ("Homologar y pasar la ITV",
     "Con certificado europeo de conformidad (COC) basta la ficha técnica reducida. "
     "Sin él, hace falta homologación individual. Después, la ITV en España."),
    ("Matricular",
     "Se paga el impuesto de matriculación (modelo 576) y la tasa de Tráfico, "
     "y la DGT asigna la matrícula española."),
]

# Tabla comparativa: (concepto, Alemania, EE. UU., Japón, Dubái)
COMPARE_COLS = ["Alemania", "EE. UU.", "Japón", "Dubái"]
COMPARE = [
    ("Aduana", ["No", "Sí", "Sí", "Sí"]),
    ("Arancel", ["No",
                 "10 %, o 0 % si el coche se fabricó en EE. UU. y se acredita el origen",
                 "10 %, o 0 % si el coche se fabricó en Japón y se acredita el origen",
                 "10 % por regla general"]),
    ("IVA", ["Incluido en el precio si es usado y lo vende un profesional; 21 % en España si es nuevo",
             "21 % de importación", "21 % de importación", "21 % de importación"]),
    ("Homologación", ["Ficha técnica reducida con el COC", "Individual", "Individual",
                      "Individual, o ficha reducida si tiene COC"]),
    ("Impuesto de matriculación", ["Según CO₂", "Según CO₂", "Según CO₂", "Según CO₂"]),
]

GUIDE_FAQ = [
    ("¿Cuánto cuesta importar un coche a España?",
     "Hay que sumar el precio del coche, el transporte con seguro, el IVA y el arancel si viene de fuera de la UE, "
     "la homologación y la ITV, el impuesto de matriculación y la gestión. En el estudio gratuito te damos el total "
     "desglosado y por escrito antes de que decidas."),
    ("¿Qué es el COC?",
     "El certificado europeo de conformidad: el documento del fabricante que dice que el coche cumple la homologación "
     "europea. Con él basta la ficha técnica reducida y la ITV. Los coches fabricados para EE. UU., Japón o los países "
     "del Golfo normalmente no lo tienen y necesitan homologación individual."),
    ("¿Qué es el DUA?",
     "El Documento Único Administrativo: la declaración de aduanas con la que se pagan el IVA y el arancel de importación "
     "y se libera el coche. Sin él no se puede matricular un coche que llega de fuera de la UE. Lo presentamos nosotros."),
    ("¿Puede importar un coche un particular?",
     "Sí, cualquier persona puede importar un coche para uso propio. Nosotros nos ocupamos de la búsqueda, la revisión, "
     "la compra segura, el transporte y todos los trámites, para que tú no tengas que hacer ninguno."),
    ("¿Se puede matricular como histórico un coche importado?",
     "Sí, si tiene 30 años o más desde que se fabricó o se matriculó por primera vez, su modelo ya no se fabrica y "
     "conserva su estado original, sin cambios de fondo en motor, frenos, dirección, suspensión o carrocería. "
     "Un coche importado sigue el procedimiento ordinario del Real Decreto 892/2024, con el informe de un servicio "
     "técnico de vehículos históricos."),
]

# Guías por país. "cars" se rellena en build.py con los coches de ese origen.
ORIGIN_GUIDES = [
    dict(
        key="usa", slug="estados-unidos", name="Estados Unidos", short="EE. UU.", img="car-mustang-boss.jpg",
        title="Importar un coche de Estados Unidos a España | Busco Tu Coche",
        desc="Qué se paga y qué papeles hacen falta para traer un coche americano a España: arancel, IVA, "
             "homologación individual, ITV y matrícula. Guía actualizada en 2026.",
        card="Muscle cars y clásicos americanos. Arancel del 10 %, o 0 % si el coche se fabricó allí y se acredita.",
        lead="Un coche de Estados Unidos pasa la aduana española, paga el IVA de importación del 21 % y, por regla "
             "general, un arancel del 10 %. Después necesita homologación individual, la ITV y la matrícula. "
             "Nosotros lo hacemos todo, de la búsqueda en EE. UU. a las llaves en España.",
        pay=[
            ("Arancel", "10 % del valor en aduana (precio, transporte y seguro). Desde el 1 de julio de 2026 puede "
                        "ser del 0 % si el coche se fabricó en EE. UU. y se acredita su origen."),
            ("IVA de importación", "21 % sobre el valor en aduana más el arancel."),
            ("Impuesto de matriculación", "Del 0 % al 14,75 % según las emisiones de CO₂."),
            ("Homologación, ITV y matrícula", "Informe técnico y tasas. Te los damos cerrados en el estudio."),
        ],
        papers=[
            "Title: el título de propiedad americano, a nombre del vendedor y sin cargas.",
            "Factura de compra (bill of sale).",
            "DUA de importación con el IVA y el arancel pagados.",
            "Informe de homologación individual y ficha técnica.",
            "ITV favorable y justificante del impuesto de matriculación.",
        ],
        notes=[
            "Los coches americanos no tienen certificado europeo de conformidad (COC): necesitan homologación "
            "individual, y luces e intermitentes suelen adaptarse.",
            "No todos los modelos se pueden homologar en España. Lo comprobamos antes de comprar, no después.",
            "El arancel del 0 % depende de dónde se fabricó el coche, no de la marca: un Mustang o un Corvette pueden "
            "acogerse si se acredita el origen; un coche europeo o japonés comprado allí, no. En un coche usado esa "
            "prueba no siempre existe, y entonces se paga el 10 %.",
            "Un clásico de 30 años o más puede matricularse como vehículo histórico, con su propio procedimiento.",
        ],
        faq=[
            ("¿Cuánto se paga de aduana por un coche de Estados Unidos?",
             "El IVA de importación del 21 % y, por regla general, un 10 % de arancel sobre el precio, el transporte y "
             "el seguro. Si el coche se fabricó en EE. UU. y se puede acreditar su origen, desde julio de 2026 el "
             "arancel puede ser del 0 %. En el estudio te decimos cuál es tu caso."),
            ("¿Se puede matricular en España un coche americano?",
             "Sí, con homologación individual, porque no tiene certificado europeo. Antes de comprar comprobamos que "
             "tu modelo concreto se puede homologar y qué adaptaciones necesita."),
            ("¿Y un muscle car clásico?",
             "Si tiene 30 años o más desde su fabricación, su modelo ya no se fabrica y está en su estado original, "
             "puede matricularse como vehículo histórico."),
            ("¿Cuánto se tarda en traerlo?",
             "El barco es solo una parte: hay que sumar la búsqueda, la aduana y la homologación. En el estudio te "
             "damos un plazo estimado para tu coche y te avisamos en cada paso."),
        ],
    ),
    dict(
        key="jp", slug="japon", name="Japón", short="Japón", img="car-skyline.jpg",
        title="Importar un coche de Japón a España (JDM) | Busco Tu Coche",
        desc="Cómo traer un JDM de Japón a España: arancel tras el acuerdo UE-Japón, IVA, homologación, volante a la "
             "derecha, ITV y matrícula. Guía actualizada en 2026.",
        card="JDM de los 90 y coches de drift. Sin arancel si el coche se fabricó en Japón y se acredita el origen.",
        lead="Un coche de Japón pasa la aduana española y paga el IVA de importación del 21 %. Desde 2026 no paga "
             "arancel si se fabricó en Japón y se acredita su origen; si no, el 10 %. Después necesita homologación "
             "individual, la ITV y la matrícula. Es el origen de los JDM: Skyline, Supra, Silvia o 350Z.",
        pay=[
            ("Arancel", "0 % si el coche se fabricó en Japón y se acredita su origen, gracias al acuerdo comercial "
                        "UE-Japón. Si no se puede acreditar, 10 % del valor en aduana."),
            ("IVA de importación", "21 % sobre el valor en aduana más el arancel, si lo hay."),
            ("Impuesto de matriculación", "Del 0 % al 14,75 % según las emisiones de CO₂."),
            ("Homologación, ITV y matrícula", "Informe técnico, adaptaciones y tasas. Te los damos cerrados en el estudio."),
        ],
        papers=[
            "Certificado de exportación japonés (Export Certificate), que da de baja el coche en Japón.",
            "Factura de compra y, si viene de subasta, la hoja de subasta.",
            "DUA de importación con el IVA pagado.",
            "Informe de homologación individual y ficha técnica.",
            "ITV favorable y justificante del impuesto de matriculación.",
        ],
        notes=[
            "Volante a la derecha: se puede matricular en España, pero hay que adaptar las luces, que en Japón "
            "alumbran hacia el otro lado.",
            "Los JDM no tienen certificado europeo de conformidad: van por homologación individual o, si tienen "
            "30 años o más, como vehículo histórico.",
            "En 2026 ya cumplen 30 años los coches fabricados en 1996 o antes, como los primeros Supra MK4 y Skyline R33.",
            "Pedimos la hoja de subasta (auction sheet), que en Japón puntúa el estado del coche y anota sus kilómetros.",
        ],
        faq=[
            ("¿Se paga arancel por un coche de Japón?",
             "Desde 2026 la UE ya no cobra arancel a los coches fabricados en Japón, gracias al acuerdo comercial "
             "UE-Japón, siempre que se acredite el origen. Si no se puede acreditar, se paga el 10 %. El IVA de "
             "importación del 21 % se paga en todo caso."),
            ("¿Se puede matricular en España un coche con volante a la derecha?",
             "Sí. Hay que homologarlo y adaptar las luces. Te lo dejamos todo hecho y con matrícula española."),
            ("¿Cómo sabéis el estado real de un JDM?",
             "Pedimos la hoja de subasta, que puntúa el estado y anota los kilómetros, y además lo revisamos en persona "
             "antes de comprar: chasis, óxido, motor y documentación."),
            ("¿Puedo matricular un Skyline o un Supra como histórico?",
             "Si tiene 30 años o más desde su fabricación y conserva su configuración original, sí. Lo comprobamos con "
             "el número de bastidor antes de comprar."),
        ],
    ),
    dict(
        key="ae", slug="dubai", name="Dubái", short="Dubái", img="car-urus.jpg",
        title="Importar un coche de Dubái a España | Busco Tu Coche",
        desc="Qué se paga y qué hace falta para traer un coche de Dubái a España: aduana, arancel, IVA, homologación "
             "de coches GCC, ITV y matrícula. Guía actualizada en 2026.",
        card="SUV y deportivos de lujo. Arancel del 10 % e IVA del 21 % por regla general.",
        lead="Los Emiratos Árabes Unidos están fuera de la UE: un coche de Dubái pasa la aduana española y paga, por "
             "regla general, un 10 % de arancel y el 21 % de IVA de importación. Después necesita homologación, la "
             "ITV y la matrícula. Es buen mercado para SUV y deportivos de lujo como el Urus, el G63 o el Range Rover.",
        pay=[
            ("Arancel", "10 % del valor en aduana (precio, transporte y seguro), por regla general."),
            ("IVA de importación", "21 % sobre el valor en aduana más el arancel."),
            ("Impuesto de matriculación", "Del 0 % al 14,75 % según las emisiones de CO₂."),
            ("Homologación, ITV y matrícula", "Informe técnico y tasas. Te los damos cerrados en el estudio."),
        ],
        papers=[
            "Tarjeta de registro del coche (Mulkiya) y certificado de exportación de la autoridad de tráfico de Dubái.",
            "Factura de compra.",
            "DUA de importación con el IVA y el arancel pagados.",
            "Certificado europeo de conformidad (COC) si lo tiene, o informe de homologación individual.",
            "ITV favorable y justificante del impuesto de matriculación.",
        ],
        notes=[
            "Muchos coches de Dubái son de especificación del Golfo (GCC) y no tienen certificado europeo: entonces "
            "necesitan homologación individual.",
            "Comprobamos que el coche no tenga financiación ni cargas pendientes antes de pagar.",
            "Por el calor de la zona, revisamos con especial cuidado la refrigeración, las gomas y el interior.",
        ],
        faq=[
            ("¿Cuánto se paga de aduana por un coche de Dubái?",
             "Por regla general, un 10 % de arancel sobre el precio, el transporte y el seguro, y después el 21 % de "
             "IVA sobre todo eso. En el estudio te lo calculamos para tu coche concreto."),
            ("¿Se puede matricular en España un coche de Dubái?",
             "Sí. Si tiene certificado europeo de conformidad (COC), basta la ficha técnica reducida; si es de "
             "especificación del Golfo, necesita homologación individual. Lo comprobamos antes de comprar."),
            ("¿Por qué comprar un coche en Dubái?",
             "Hay mucha oferta de coches de lujo y versiones que en Europa cuesta encontrar. Te decimos si, con los "
             "impuestos sumados, te sale mejor que comprarlo aquí."),
        ],
    ),
    dict(
        key="de", slug="alemania", name="Alemania", short="Alemania", img="car-mercedes-e500.jpg",
        title="Importar un coche de Alemania a España | Busco Tu Coche",
        desc="Comprar un coche en Alemania y matricularlo en España: sin aduana ni arancel, IVA, COC, ITV e impuesto "
             "de matriculación. Guía actualizada en 2026.",
        card="Clásicos y deportivos alemanes. Sin aduana ni arancel: es una compra dentro de la UE.",
        lead="Alemania está en la Unión Europea: un coche comprado allí no pasa aduana ni paga arancel. Para "
             "matricularlo en España hacen falta sus papeles alemanes, el certificado europeo de conformidad (COC) o la "
             "ficha técnica reducida, la ITV y el impuesto de matriculación. Es el mejor mercado para clásicos alemanes "
             "como el Mercedes E 500 W124 o el BMW E30.",
        pay=[
            ("Arancel", "No se paga: es una compra dentro de la UE."),
            ("IVA", "Si el coche es usado y lo vende un profesional, va incluido en el precio. Si es nuevo (menos de "
                    "6 meses o de 6.000 km), el IVA del 21 % se paga en España."),
            ("Impuesto de matriculación", "Del 0 % al 14,75 % según las emisiones de CO₂, sobre el valor del coche "
                                          "según las tablas de Hacienda."),
            ("ITV y matrícula", "Tasas de ITV y de Tráfico. Te las damos cerradas en el estudio."),
        ],
        papers=[
            "Permiso de circulación alemán, partes I y II (Zulassungsbescheinigung Teil I y Teil II).",
            "Factura o contrato de compra.",
            "Certificado europeo de conformidad (COC) o ficha técnica reducida.",
            "ITV favorable en España.",
            "Justificante del impuesto de matriculación (modelo 576) y tasa de Tráfico.",
        ],
        notes=[
            "Con COC es el trámite más sencillo de todos: no hace falta homologación individual.",
            "El coche viaja en camión portacoches o, si lo prefieres, conduciendo con matrícula de exportación alemana.",
            "Revisamos el libro de mantenimiento (Scheckheft) y el estado real del coche antes de comprar.",
            "Un clásico de 30 años o más puede matricularse como vehículo histórico.",
        ],
        faq=[
            ("¿Se paga aduana por un coche comprado en Alemania?",
             "No. Alemania y España están en la UE: no hay aduana ni arancel. Sí se paga el impuesto de matriculación "
             "en España y, si el coche es nuevo, el IVA."),
            ("¿Hace falta homologar un coche alemán?",
             "Normalmente no hace falta homologación individual: con el certificado europeo de conformidad (COC) o la "
             "ficha técnica reducida se pasa la ITV y se matricula."),
            ("¿Cómo llega el coche a España?",
             "En camión portacoches o conduciendo con matrícula de exportación alemana. Te decimos qué sale mejor en tu caso."),
        ],
    ),
]
