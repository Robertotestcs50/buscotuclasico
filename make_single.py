#!/usr/bin/env python3
"""Empaqueta toda la web (desde preview/) en un único HTML autocontenido para verla en cualquier dispositivo."""
import base64
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "preview")
OUT = os.path.join(ROOT, "buscotucoche-vista-completa.html")

PAGES = [
    ("inicio", "index.html"),
    ("nosotros", "nosotros/index.html"),
    ("calle", "servicios/calle/index.html"),
    ("competicion", "servicios/competicion/index.html"),
    ("drift", "drift-72h/index.html"),
    ("ventajas", "ventajas/index.html"),
    ("stock", "stock/index.html"),
    ("subir", "stock/subir/index.html"),
    ("contacto", "contacto/index.html"),
    ("configurador", "configurador/index.html"),
    ("guia", "importar/index.html"),
    ("eeuu", "importar/estados-unidos/index.html"),
    ("japon", "importar/japon/index.html"),
    ("dubai", "importar/dubai/index.html"),
    ("alemania", "importar/alemania/index.html"),
    ("aviso", "aviso-legal/index.html"),
    ("privacidad", "privacidad/index.html"),
    ("creditos", "creditos/index.html"),
]
KEY_BY_DIR = {os.path.dirname(p): k for k, p in PAGES}

_cache = {}


def data_uri(path):
    if path not in _cache:
        with open(path, "rb") as f:
            raw = f.read()
        mime = "image/svg+xml" if path.endswith(".svg") else "font/woff2" if path.endswith(".woff2") else "image/jpeg"
        _cache[path] = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    return _cache[path]


def rewrite(html, page_path):
    base = os.path.dirname(page_path)

    def link(m):
        target, query = m.group(1), m.group(2) or ""
        norm = os.path.normpath(os.path.join(base, target)).replace(os.sep, "/")
        key = KEY_BY_DIR.get(os.path.dirname(norm) if norm != "index.html" else "", "inicio")
        return f'href="#{key}{query}"'

    html = re.sub(r'href="([^"#:]*?index\.html)(\?[^"#]*)?(?:#[^"]*)?"', link, html)

    def img(m):
        rel = m.group(1)
        full = os.path.normpath(os.path.join(SRC, base, rel))
        small = full.replace(".jpg", "-sm.jpg")
        if full.endswith(".jpg") and not full.endswith("-sm.jpg") and os.path.exists(small):
            full = small  # versión ligera para el archivo único
        return f'src="{data_uri(full)}"'

    html = re.sub(r' srcset="[^"]*" sizes="[^"]*"', "", html)

    html = re.sub(r'src="([^"]*assets/img/[^"]+)"', img, html)
    return html


def main_of(html):
    return re.search(r'<main id="main"[^>]*>(.*)</main>', html, re.S).group(1)


def main():
    home = open(os.path.join(SRC, "index.html"), encoding="utf-8").read()
    header = re.search(r'(<a class="skip".*?</header>)', home, re.S).group(1)
    footer = re.search(r"(<footer class=\"footer\">.*?</footer>)", home, re.S).group(1)
    header, footer = rewrite(header, "index.html"), rewrite(footer, "index.html")
    header = header.replace(' aria-current="page"', "")

    sections = []
    for key, path in PAGES:
        html = open(os.path.join(SRC, path), encoding="utf-8").read()
        title = re.search(r"<title>(.*?)</title>", html).group(1)
        body = main_of(html)
        body = re.sub(r"<script>.*?</script>", "", body, flags=re.S)  # el router se encarga del relleno
        body = re.sub(r'(id|for)="f-', rf'\1="f-{key}-', body)            # ids únicos entre páginas
        body = rewrite(body, path)
        def fix_json(m):
            data = json.loads(m.group(2).replace("<\\/", "</"))
            for c in data:
                c["img"] = data_uri(os.path.normpath(os.path.join(SRC, os.path.dirname(path), c["img"])))
                u = c["url"]
                if "contacto/index.html" in u:
                    q = u.split("?", 1)[1].split("#")[0] if "?" in u else ""
                    c["url"] = "#contacto" + ("?" + q if q else "")
                elif "drift-72h" in u:
                    c["url"] = "#drift"
            return m.group(1) + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + m.group(3)
        body = re.sub(r'(<script type="application/json" id="cars-data">)(.*?)(</script>)', fix_json, body, flags=re.S)
        body = re.sub(r'(<form class="finder" id="finder") action="[^"]*"', r'\1 action="#contacto"', body)
        sections.append(f'<section class="page" data-page="{key}" data-title="{title}" hidden>{body}</section>')

    css = open(os.path.join(SRC, "assets/css/site.css"), encoding="utf-8").read()
    for font in ("imbue.woff2", "albert-sans.woff2"):
        css = css.replace(f'url("../fonts/{font}")', f'url("{data_uri(os.path.join(SRC, "assets/fonts/" + font))}")')
    js = open(os.path.join(SRC, "assets/js/site.js"), encoding="utf-8").read()
    body_attrs = re.search(r"<body([^>]*)>", home).group(1)
    head_meta = '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="theme-color" content="#eeecea">'
    svg = open(os.path.join(ROOT, "static", "favicon.svg"), encoding="utf-8").read().strip()
    favicon = '<link rel="icon" href="data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '">'

    router = r"""
(function () {
  var pages = document.querySelectorAll(".page");
  var navLinks = document.querySelectorAll(".nav a, .nav summary");
  function show() {
    var h = location.hash.slice(1) || "inicio";
    var key = h.split("?")[0], params = new URLSearchParams(h.split("?")[1] || "");
    var page = document.querySelector('.page[data-page="' + key + '"]');
    if (!page) { var anchor = document.getElementById(key); if (anchor) { anchor.scrollIntoView(); return; } key = "inicio"; page = document.querySelector('.page[data-page="inicio"]'); }
    pages.forEach(function (p) { p.hidden = p !== page; });
    document.title = page.getAttribute("data-title");
    navLinks.forEach(function (a) { a.removeAttribute("aria-current"); });
    var cur = document.querySelector('.nav a[href="#' + key + '"]');
    if (cur) cur.setAttribute("aria-current", "page");
    var modelo = params.get("modelo");
    if (modelo) { var f = page.querySelector("[name=modelo]"); if (f) f.value = modelo; }
    var coche = params.get("coche");
    if (coche) {
      var sel = page.querySelector("#cfg-coche");
      if (sel) {
        if (!Array.prototype.some.call(sel.options, function (o) { return o.value === coche; })) sel.add(new Option(coche, coche), 0);
        sel.value = coche; sel.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }
    document.body.classList.remove("menu-open");
    window.scrollTo(0, 0);
  }
  var fd = document.getElementById("finder");
  if (fd) fd.addEventListener("submit", function (ev) { ev.preventDefault(); var v = fd.querySelector("input").value.trim(); if (v) location.hash = "#contacto?modelo=" + encodeURIComponent(v); });
  window.addEventListener("hashchange", show);
  show();
})();
"""

    out = f"""<!doctype html>
<html lang="es">
<head>
{head_meta}
<title>Busco Tu Coche — vista completa</title>
<script>document.documentElement.classList.add("js")</script>
{favicon}
<style>{css}</style>
</head>
<body{body_attrs}>
{header}
<main id="main">
{''.join(sections)}
</main>
{footer}
<script>{js}</script>
<script>{router}</script>
</body>
</html>
"""
    # Cada foto se incrusta una sola vez y se reparte por la página al cargar
    uris = {}
    def keep(m):
        u = m.group(1)
        k = uris.setdefault(u, str(len(uris)))
        return f'src="data:," data-k="{k}"'
    out = re.sub(r'src="(data:image/jpeg;base64,[^"]+)"', keep, out)
    table = "window.__IMG=" + json.dumps({k: u for u, k in uris.items()}) + ";" \
            "document.querySelectorAll('img[data-k]').forEach(function(i){i.src=window.__IMG[i.getAttribute('data-k')];});"
    out = out.replace("<main id=\"main\">", "<script>" + table.replace("document.querySelectorAll", "document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll") + "});</script>\n<main id=\"main\">", 1)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print(OUT, round(len(out) / 1024), "KB")


if __name__ == "__main__":
    main()
