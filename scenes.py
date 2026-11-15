"""
Ilustraciones propias de la web: cada coche se dibuja con su tipo de carrocería y su color
sobre un paisaje de su país de origen (Dubái, EE. UU., Japón, Alemania), de circuito o de drift.
Son SVG ligeros. Si más adelante hay fotos reales, la web las usa en su lugar.
"""
import random

W, H = 800, 600
GROUND = 498  # línea del suelo en la escena

# ---------------------------------------------------------------------
# Carrocerías (vista lateral, frontal a la derecha). Caja 400 x 130, suelo en y=128.
# body: contorno; win: ventanillas; wheels: (x, radio); extra: piezas oscuras (alerones...)
# ---------------------------------------------------------------------
BODIES = {
    "sedan": dict(
        body="M8,104 L8,84 C8,74 18,68 34,66 L100,60 C122,44 148,32 180,30 L262,30 C286,30 300,40 318,58 L370,62 C386,64 394,72 394,86 L394,104 Z",
        win=["M122,58 C138,45 156,37 182,36 L214,36 L214,58 Z", "M222,36 L258,36 C277,36 291,44 304,58 L222,58 Z"],
        wheels=[(82, 24), (318, 24)], doors=[216, 150], mirror=(300, 60), extra=[]),
    "w124": dict(  # berlina clásica de líneas rectas
        body="M8,104 L8,76 C8,69 12,65 20,64 L100,59 L136,31 C139,28 142,27 146,27 L262,27 C266,27 269,28 271,31 L302,57 L384,61 C391,62 394,67 394,75 L394,104 Z",
        win=["M144,57 L154,34 L210,34 L210,57 Z", "M218,34 L262,34 L284,57 L218,57 Z"],
        wheels=[(84, 23), (318, 23)], doors=[214, 146], mirror=(288, 59),
        extra=["M8,88 L394,88 L394,92 L8,92 Z"]),
    "e30": dict(  # cupé compacto de los 80 preparado para circuito
        body="M6,104 L6,77 C6,71 10,67 18,66 L96,62 L132,34 C135,31 138,30 142,30 L236,30 C240,30 243,31 246,34 L276,60 L384,64 C392,65 396,70 396,78 L396,104 Z",
        win=["M140,58 L150,37 L232,37 L258,58 Z"],
        wheels=[(80, 25), (318, 25)], doors=[236], mirror=(262, 61),
        extra=["M2,52 L60,49 L60,55 L2,58 Z", "M24,57 L30,57 L33,66 L27,66 Z", "M44,56 L50,56 L53,65 L47,65 Z", "M370,104 L404,104 L404,108 L370,108 Z"]),
    "coupe": dict(
        body="M8,104 L8,88 C8,78 20,72 40,70 L110,66 C150,42 185,34 215,34 L250,36 C285,42 320,58 352,66 L380,72 C392,76 396,84 396,94 L396,104 Z",
        win=["M150,64 C174,46 196,40 218,40 L246,42 C268,46 288,55 304,64 Z"],
        wheels=[(84, 24), (330, 24)], doors=[250], mirror=(300, 66), extra=[]),
    "classic": dict(
        body="M6,104 L6,80 C6,74 12,70 22,70 L90,66 C120,46 150,36 185,36 L235,38 C252,44 262,56 270,64 L384,68 C392,69 396,74 396,82 L396,104 Z",
        win=["M122,62 C146,47 165,42 186,42 L226,43 C239,48 247,55 253,62 Z"],
        wheels=[(78, 23), (326, 23)], doors=[230], mirror=(258, 64), extra=["M6,92 L396,92 L396,96 L6,96 Z"]),
    "muscle": dict(
        body="M6,104 L6,78 C6,70 14,66 28,64 L95,60 C125,40 155,32 190,32 L240,34 C262,38 280,52 296,60 L378,64 C390,66 396,74 396,84 L396,104 Z",
        win=["M128,58 C150,43 170,38 192,38 L232,40 C248,44 261,51 271,58 Z"],
        wheels=[(80, 25), (322, 25)], doors=[238], mirror=(276, 60), extra=[]),
    "suv": dict(
        body="M8,104 L8,70 C8,60 16,54 30,52 L70,48 C90,26 115,18 150,18 L265,18 C290,18 308,30 326,46 L372,52 C388,54 394,64 394,78 L394,104 Z",
        win=["M94,46 C109,31 127,24 150,24 L200,24 L200,46 Z", "M208,24 L262,24 C281,24 295,33 307,46 L208,46 Z"],
        wheels=[(84, 29), (316, 29)], doors=[204, 120], mirror=(312, 48), extra=["M8,98 L394,98 L394,104 L8,104 Z"]),
    "boxy": dict(
        body="M14,104 L14,56 C14,50 18,46 26,46 L62,44 L78,14 C80,10 84,8 90,8 L280,8 C286,8 290,10 292,14 L310,44 L378,46 C386,46 390,52 390,60 L390,104 Z",
        win=["M88,40 L98,16 L178,16 L178,40 Z", "M186,16 L278,16 L290,40 L186,40 Z"],
        wheels=[(88, 27), (312, 27)], doors=[182, 96], mirror=(298, 44),
        extra=["M2,52 C2,48 4,46 8,46 L16,46 L16,94 L8,94 C4,94 2,92 2,88 Z"]),
    "jdm": dict(
        body="M8,104 L8,82 C8,74 16,70 30,68 L100,64 C130,44 158,34 190,34 L245,36 C270,40 292,54 310,62 L376,66 C390,68 396,76 396,88 L396,104 Z",
        win=["M134,60 C154,45 172,40 192,40 L238,42 C256,46 272,53 284,60 Z"],
        wheels=[(82, 24), (324, 24)], doors=[242], mirror=(290, 62), extra=["M10,68 L10,61 L58,58 L60,63 Z"]),
    "race": dict(
        body="M4,104 L4,84 C4,78 10,74 22,72 L110,66 C145,44 175,36 205,36 L245,38 C275,44 305,58 330,66 L388,72 C396,74 398,82 398,92 L398,104 Z",
        win=["M150,62 C172,46 192,42 210,42 L240,44 C262,48 280,55 294,62 Z"],
        wheels=[(84, 25), (330, 25)], doors=[250], mirror=(300, 64),
        extra=["M0,42 L78,38 L78,45 L0,49 Z", "M0,32 L8,32 L8,56 L0,56 Z", "M70,30 L78,30 L78,52 L70,52 Z", "M30,47 L36,47 L40,70 L34,70 Z", "M52,46 L58,46 L62,69 L56,69 Z", "M360,104 L404,104 L404,108 L360,108 Z"]),
}

SPORTY = {"race", "e30", "coupe", "jdm", "muscle"}


def shade(hex_color, f):
    """f>0 aclara hacia blanco, f<0 oscurece hacia negro."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if f >= 0:
        r, g, b = [int(c + (255 - c) * f) for c in (r, g, b)]
    else:
        r, g, b = [int(c * (1 + f)) for c in (r, g, b)]
    return f"#{r:02x}{g:02x}{b:02x}"


def car_svg(kind, paint, accent, uid, number=None):
    b = BODIES[kind]
    hi, lo, deep = shade(paint, .45), shade(paint, -.35), shade(paint, -.62)
    caliper = "#e0412f" if kind in SPORTY else "#9aa3ad"
    win_clip = "".join(f'<path d="{w}"/>' for w in b["win"])
    parts = [f"""<defs>
<linearGradient id="p{uid}" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="{hi}"/><stop offset=".3" stop-color="{paint}"/><stop offset=".62" stop-color="{paint}"/><stop offset=".63" stop-color="{lo}"/><stop offset="1" stop-color="{deep}"/></linearGradient>
<linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#4b5d7d"/><stop offset=".5" stop-color="#0b1220"/><stop offset="1" stop-color="#1c2944"/></linearGradient>
<radialGradient id="r{uid}" cx=".4" cy=".35" r=".7">
 <stop offset="0" stop-color="#f4f6f9"/><stop offset=".6" stop-color="#a9b1bc"/><stop offset="1" stop-color="#5b6370"/></radialGradient>
<linearGradient id="sh{uid}" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity=".55"/><stop offset=".7" stop-color="#fff" stop-opacity=".1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="c{uid}"><path d="{b["body"]}"/></clipPath>
<clipPath id="w{uid}">{win_clip}</clipPath>
</defs>"""]
    # sombra de contacto
    parts.append('<ellipse cx="200" cy="128" rx="210" ry="10" fill="#000" opacity=".6"/>')
    parts.append('<ellipse cx="200" cy="127" rx="160" ry="4" fill="#000" opacity=".5"/>')
    # carrocería
    parts.append(f'<path d="{b["body"]}" fill="url(#p{uid})"/>')
    parts.append(f'<g clip-path="url(#c{uid})">')
    parts.append(f'<rect x="0" y="66" width="400" height="7" fill="url(#sh{uid})" opacity=".8"/>')  # reflejo lateral
    parts.append(f'<rect x="0" y="94" width="400" height="14" fill="#000" opacity=".28"/>')  # bajos
    for dx in b["doors"]:
        parts.append(f'<path d="M{dx},{b["win"][0].split()[0][1:].split(",")[1] if False else 40} L{dx},100" stroke="#000" stroke-opacity=".3" stroke-width="1.3"/>')
    for cx, r in b["wheels"]:  # pasos de rueda
        parts.append(f'<circle cx="{cx}" cy="{128 - r}" r="{r + 7}" fill="{deep}"/>')
        parts.append(f'<circle cx="{cx}" cy="{128 - r}" r="{r + 4.5}" fill="#06080d"/>')
    parts.append('</g>')
    parts.append(f'<path d="{b["body"]}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1.2"/>')
    # cristales con reflejo
    for w in b["win"]:
        parts.append(f'<path d="{w}" fill="url(#g{uid})"/>')
    parts.append(f'<g clip-path="url(#w{uid})"><path d="M120,70 L190,20 L215,20 L145,70 Z M228,70 L298,20 L310,20 L240,70 Z" fill="#fff" opacity=".16"/></g>')
    for x in b["extra"]:
        parts.append(f'<path d="{x}" fill="{shade(paint, -.55)}"/>')
    # retrovisor
    mx, my = b["mirror"]
    parts.append(f'<path d="M{mx - 4},{my} q4,-9 14,-7 l0,8 q-8,2 -14,-1 Z" fill="{lo}"/>')
    # faros y pilotos
    parts.append('<path d="M382,70 L397,73 L397,82 L380,80 Z" fill="#fffaf0"/>')
    parts.append('<ellipse cx="398" cy="77" rx="30" ry="9" fill="#fff3c4" opacity=".25"/>')
    parts.append('<path d="M5,72 L20,70 L20,80 L5,82 Z" fill="#ff2d2d"/><path d="M5,72 L20,70 L20,73 L5,75 Z" fill="#ff8a80"/>')
    if number:
        parts.append(f'<circle cx="205" cy="84" r="15" fill="#fff"/><text x="205" y="90" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="17" fill="#111">{number}</text>')
    # ruedas: neumático, llanta de radios, pinza de freno, buje
    for cx, r in b["wheels"]:
        cy = 128 - r
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 3}" fill="#0a0b0e"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 1}" fill="none" stroke="#2a2c31" stroke-width="2"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * .7:.1f}" fill="#20242b"/>')
        parts.append(f'<path d="M{cx + r * .2:.1f},{cy - r * .52:.1f} a{r * .55:.1f},{r * .55:.1f} 0 0 1 {r * .35:.1f},{r * .42:.1f} l-{r * .14:.1f},{r * .1:.1f} a{r * .4:.1f},{r * .4:.1f} 0 0 0 -{r * .25:.1f},-{r * .3:.1f} Z" fill="{caliper}"/>')
        for k in range(10):
            parts.append(f'<path d="M{cx},{cy} l0,-{r * .68:.1f}" stroke="#c3c9d2" stroke-width="{2.6 if k % 2 == 0 else 1.6}" transform="rotate({k * 36} {cx} {cy})"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * .7:.1f}" fill="none" stroke="#d5dae1" stroke-width="2.6"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * .2:.1f}" fill="url(#r{uid})"/>')
    return "\n".join(parts)


# ---------------------------------------------------------------------
# Escenarios
# ---------------------------------------------------------------------
def sky(uid, stops):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="s{uid}" x1="0" y1="0" x2="0" y2="1">{s}</linearGradient><rect width="{W}" height="{H}" fill="url(#s{uid})"/>'


def scene_ae(r):  # Dubái: atardecer, dunas y rascacielos
    out = [sky("ae", [(0, "#2a1b4a"), (.45, "#b4462f"), (.78, "#f2a453")])]
    out.append('<circle cx="560" cy="330" r="78" fill="#ffd486" opacity=".95"/>')
    x = 70
    while x < 760:
        w = r.randint(22, 46); h = r.randint(40, 150)
        out.append(f'<rect x="{x}" y="{430 - h}" width="{w}" height="{h}" fill="#4a2340" opacity=".85"/>')
        x += w + r.randint(4, 14)
    # torre con aguja
    out.append('<path d="M612,430 L612,250 L620,250 L624,150 L628,250 L636,250 L636,430 Z" fill="#3b1c36"/>')
    out.append('<path d="M0,450 C120,410 240,440 360,425 C500,405 640,445 800,420 L800,600 L0,600 Z" fill="#d98a3e"/>')
    out.append('<path d="M0,480 C160,455 300,485 460,465 C600,450 700,475 800,462 L800,600 L0,600 Z" fill="#a9572a"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#2a1622"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="3" fill="#ffb867" opacity=".5"/>')
    return out, "#ffb867"


def scene_usa(r):  # EE. UU.: puesta de sol retro y mesetas del desierto
    out = [sky("us", [(0, "#1d2b53"), (.5, "#d9524a"), (.8, "#ffbf69")])]
    out.append('<defs><clipPath id="sunc"><rect x="0" y="0" width="800" height="455"/></clipPath></defs>')
    out.append('<g clip-path="url(#sunc)"><circle cx="400" cy="420" r="120" fill="#ffd27a"/>')
    for i, y in enumerate(range(360, 460, 16)):
        out.append(f'<rect x="270" y="{y}" width="260" height="{3 + i}" fill="#e2664c"/>')
    out.append('</g>')
    out.append('<path d="M40,455 L40,360 L70,352 L120,352 L150,362 L150,455 Z" fill="#5a2733"/>')
    out.append('<path d="M560,455 L575,330 L600,322 L690,322 L708,334 L720,455 Z" fill="#4a1f2c"/>')
    out.append('<path d="M730,455 L742,395 L780,392 L790,455 Z" fill="#5a2733"/>')
    out.append('<path d="M0,455 L800,455 L800,600 L0,600 Z" fill="#7a3a2c"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#24191d"/>')
    for x in range(0, 800, 70):
        out.append(f'<rect x="{x}" y="{GROUND + 52}" width="36" height="5" fill="#ffc94a" opacity=".85"/>')
    return out, "#ffc073"


def scene_jp(r):  # Japón: noche, volcán nevado y neones
    out = [sky("jp", [(0, "#060a1c"), (.6, "#1b2350"), (1, "#3a2e6b")])]
    for _ in range(60):
        out.append(f'<circle cx="{r.randint(0, 800)}" cy="{r.randint(0, 300)}" r="{r.choice([.8, 1.1, 1.5])}" fill="#fff" opacity="{r.uniform(.3, .9):.2f}"/>')
    out.append('<circle cx="640" cy="120" r="34" fill="#f3f0e0" opacity=".9"/>')
    out.append('<path d="M180,440 L380,230 Q400,214 420,230 L620,440 Z" fill="#2a3566"/>')
    out.append('<path d="M330,282 L380,230 Q400,214 420,230 L470,282 L448,272 L430,290 L410,270 L392,292 L370,272 L352,290 Z" fill="#e9edf7"/>')
    x = 0
    while x < 800:
        w = r.randint(30, 60); h = r.randint(50, 130)
        out.append(f'<rect x="{x}" y="{460 - h}" width="{w}" height="{h}" fill="#121735"/>')
        for wy in range(460 - h + 10, 455, 14):
            for wx in range(x + 6, x + w - 6, 10):
                if r.random() < .35:
                    out.append(f'<rect x="{wx}" y="{wy}" width="4" height="6" fill="#ffd77a" opacity=".8"/>')
        if r.random() < .3:
            c = r.choice(["#ff3d7f", "#2de2e6", "#ff3b30"])
            out.append(f'<rect x="{x + 4}" y="{460 - h + 4}" width="{w - 8}" height="4" fill="{c}"/>')
        x += w + r.randint(2, 8)
    out.append(f'<rect y="460" width="{W}" height="{GROUND - 460}" fill="#161b38"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#0b0e1f"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="2" fill="#ff3d7f" opacity=".6"/>')
    return out, "#7fd8ff"


def scene_de(r):  # Alemania: amanecer con bruma, bosque y autopista
    out = [sky("de", [(0, "#8ea7c4"), (.55, "#d5dfe9"), (1, "#eef2f6")])]
    out.append('<circle cx="200" cy="300" r="60" fill="#fff" opacity=".7"/>')
    for layer, (base, col, hmin, hmax) in enumerate([(430, "#7d91a6", 50, 90), (455, "#4b6074", 70, 120), (470, "#2b3a48", 90, 150)]):
        x = -20
        while x < 820:
            h = r.randint(hmin, hmax); w = h * .42
            out.append(f'<path d="M{x},{base} L{x + w / 2:.0f},{base - h} L{x + w:.0f},{base} Z" fill="{col}"/>')
            x += w * r.uniform(.45, .8)
        out.append(f'<rect y="{base}" width="{W}" height="40" fill="{col}"/>')
    out.append(f'<rect y="{GROUND - 28}" width="{W}" height="28" fill="#5d6b78"/>')
    for x in range(0, 800, 40):
        out.append(f'<rect x="{x}" y="{GROUND - 26}" width="4" height="22" fill="#b7c1cb"/>')
    out.append(f'<rect y="{GROUND - 22}" width="{W}" height="6" fill="#c9d2db"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#2a2f36"/>')
    for x in range(20, 800, 90):
        out.append(f'<rect x="{x}" y="{GROUND + 52}" width="50" height="5" fill="#e8ecf0" opacity=".8"/>')
    return out, "#ffffff"


def scene_circuit(r):  # circuito de noche con focos y pianos
    out = [sky("ci", [(0, "#081428"), (.7, "#1f3d73"), (1, "#2c5597")])]
    for x in (120, 400, 680):
        out.append(f'<rect x="{x - 3}" y="170" width="6" height="280" fill="#0b1527"/>')
        out.append(f'<rect x="{x - 30}" y="150" width="60" height="24" rx="3" fill="#0b1527"/>')
        out.append(f'<circle cx="{x}" cy="162" r="70" fill="#dfe9ff" opacity=".12"/>')
        for k in range(4):
            out.append(f'<circle cx="{x - 21 + k * 14}" cy="162" r="5" fill="#f4f8ff"/>')
    out.append('<path d="M0,450 L0,380 L800,330 L800,450 Z" fill="#0d1a33"/>')
    for i in range(0, 800, 16):
        y = 380 - i * 50 / 800
        out.append(f'<rect x="{i}" y="{y + 8:.0f}" width="10" height="4" fill="#9fb4d8" opacity=".35"/>')
    out.append(f'<rect y="450" width="{W}" height="{GROUND - 450}" fill="#14233f"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#16181d"/>')
    for x in range(0, 800, 40):
        out.append(f'<rect x="{x}" y="{GROUND}" width="20" height="10" fill="#e0412f"/><rect x="{x + 20}" y="{GROUND}" width="20" height="10" fill="#f4f4f4"/>')
    return out, "#bcd3ff"


def scene_drift(r):  # drift: humo, marcas de neumático y pianos
    out = [sky("dr", [(0, "#160b10"), (.7, "#4a1713"), (1, "#7a2418")])]
    out.append('<defs><filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter></defs>')
    out.append(f'<rect y="440" width="{W}" height="{GROUND - 440}" fill="#2a1414"/>')
    out.append(f'<rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#1c1517"/>')
    for k in range(3):
        y = GROUND + 30 + k * 18
        out.append(f'<path d="M0,{y} C200,{y - 30} 420,{y + 26} 800,{y - 10}" stroke="#000" stroke-opacity=".55" stroke-width="7" fill="none"/>')
    for x in range(0, 800, 40):
        out.append(f'<rect x="{x}" y="{GROUND}" width="20" height="10" fill="#e0412f"/><rect x="{x + 20}" y="{GROUND}" width="20" height="10" fill="#f4f4f4"/>')
    smoke = ['<g filter="url(#blur)">']
    for _ in range(16):
        smoke.append(f'<circle cx="{r.randint(0, 300)}" cy="{r.randint(360, 500)}" r="{r.randint(50, 110)}" fill="#e6e1df" opacity="{r.uniform(.18, .4):.2f}"/>')
    smoke.append('</g>')
    return out, "#ffb4a8", "".join(smoke)


def scene_ship(r):  # barco portacontenedores (logística) al atardecer
    out = [sky("sh", [(0, "#0f1b33"), (.55, "#274e9b"), (.85, "#d99726")])]
    out.append('<circle cx="620" cy="380" r="60" fill="#ffd486" opacity=".9"/>')
    out.append('<rect y="420" width="800" height="180" fill="#0d1a33"/>')
    for i in range(14):
        y = 430 + i * 12
        out.append(f'<rect x="{r.randint(0, 700)}" y="{y}" width="{r.randint(60, 200)}" height="2" fill="#e7b155" opacity="{r.uniform(.15, .45):.2f}"/>')
    out.append('<path d="M60,410 L740,410 L700,460 L110,460 Z" fill="#0a1426"/>')
    out.append('<rect x="610" y="330" width="70" height="80" fill="#0a1426"/><rect x="625" y="300" width="30" height="30" fill="#0a1426"/>')
    for wx in range(618, 676, 12):
        out.append(f'<rect x="{wx}" y="342" width="7" height="5" fill="#ffd77a"/>')
    colors = ["#d99726", "#274e9b", "#e0412f", "#5c6576", "#e7b155", "#223e77", "#9b7027"]
    for row in range(4):
        for col in range(11):
            if row == 3 and r.random() < .35:
                continue
            c = r.choice(colors)
            out.append(f'<rect x="{110 + col * 45}" y="{386 - row * 26}" width="42" height="24" fill="{c}"/><rect x="{110 + col * 45}" y="{386 - row * 26}" width="42" height="24" fill="none" stroke="#000" stroke-opacity=".25"/>')
    return out, None


SCENES = {"ae": scene_ae, "usa": scene_usa, "jp": scene_jp, "de": scene_de, "circuito": scene_circuit, "drift": scene_drift}


def render(scene, kind, paint, number=None, seed=1, scale=1.55):
    r = random.Random(seed)
    res = SCENES[scene](r)
    parts, accent = res[0], res[1]
    smoke = res[2] if len(res) > 2 else ""
    cw = 400 * scale
    x0 = (W - cw) / 2
    y0 = GROUND + 18 - 128 * scale
    car = car_svg(kind, paint, accent, f"{scene}{seed}", number)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
            + "".join(parts) + smoke
            + f'<g transform="translate({x0:.1f} {y0:.1f}) scale({scale})">{car}</g></svg>')


def render_ship(seed=3):
    r = random.Random(seed)
    parts, _ = scene_ship(r)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">' + "".join(parts) + "</svg>"
