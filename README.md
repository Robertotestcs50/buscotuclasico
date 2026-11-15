# Busco Tu Coche — web

Web estática, rápida y sin dependencias, lista para GitHub Pages.

## Estructura

- `docs/` — la web ya generada. Es lo que publica GitHub Pages.
- `build.py` — genera `docs/`. Aquí están los textos, los coches y los datos de contacto.
- `guias.py` — textos de las guías «Importar un coche a España» (general y por país), con sus impuestos y fuentes.
  Revisar si cambia la normativa y actualizar la fecha `UPDATED`.
- `focus.py` — punto importante de cada foto, para que el coche salga centrado en todos los recortes.
  Si añades una foto nueva, añade aquí su punto (en % de ancho y alto).
- `assets/` — estilos, código, tipografía y fotos (`assets/img/`, ver su README).
- `static/` — iconos y manifiesto que van en la raíz de la web.
- `data/stock.json` — coches en stock (lista vacía `[]` = página de stock sin coches, que no se indexa).
- `make_single.py` — empaqueta toda la web en un solo HTML para verla sin conexión.

## Cambiar algo

1. Edita `build.py` (sección CONFIGURACIÓN y DATOS) o `data/stock.json`.
2. Ejecuta `python3 build.py`.
3. Sube los cambios a GitHub.

Ejemplo de coche en `data/stock.json`:

```json
[
  {"marca": "BMW", "modelo": "M3 E46", "año": 2004, "km": 120000, "precio": 25000,
   "origen": "Alemania", "descripcion": "Estado impecable, historial completo.", "foto": "stock-m3.jpg"}
]
```

## Publicar en GitHub Pages

1. Sube todo el contenido de esta carpeta al repositorio.
2. En GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**,
   rama `main`, carpeta `/docs`, y **Save**.
3. En un par de minutos la web estará en `https://USUARIO.github.io/REPOSITORIO/`.

## Dominios

La web usa **www.buscotucoche.com** como dominio principal (buscotucoche.com redirige solo a www) (ya configurado en `build.py`, con su `CNAME`,
`sitemap.xml` y `robots.txt`). GitHub Pages solo admite un dominio por web, así que **buscotuclasico.com**
se redirige al principal.

**buscotucoche.com** (en el proveedor donde está comprado):
- Cuatro registros **A** para `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- Un registro **CNAME** para `www` apuntando a `USUARIO.github.io`
- En GitHub, **Settings → Pages**: escribe `buscotucoche.com` en "Custom domain" y marca **Enforce HTTPS** cuando aparezca.

**buscotuclasico.com**:
- En el panel del proveedor, crea una **redirección permanente (301)** de `buscotuclasico.com` y `www.buscotuclasico.com`
  a `https://buscotucoche.com`. Casi todos los proveedores (IONOS, DonDominio, GoDaddy, Namecheap…) lo llaman
  "Redirección web" o "URL forwarding".

Si preferís que el principal sea buscotuclasico.com, cambia `DOMAIN` en `build.py`, vuelve a generar y haz la redirección al revés.

## Recibir los formularios en el correo (opcional)

Sin configurar nada, los formularios abren WhatsApp con la solicitud ya escrita.
Para recibirlos también por email: crea un formulario gratis en formspree.io con `info@buscotucoche.com`,
copia su dirección (`https://formspree.io/f/xxxxxxx`) en `FORM_ENDPOINT` dentro de `build.py` y vuelve a generar.

## SEO y buscadores con IA (GEO)

`build.py` genera solo:

- Título, descripción, canonical, Open Graph y Twitter únicos por página.
- Datos estructurados (schema.org): negocio (AutoDealer), web, migas de pan, servicios, artículos de las guías y preguntas frecuentes.
- `sitemap.xml` (solo páginas indexables, con fecha), `robots.txt` (abierto a Google, Bing y asistentes de IA) y `llms.txt` (resumen del negocio para asistentes de IA).
- `noindex` en aviso legal, privacidad, créditos, 404, subir anuncio y stock mientras esté vacío.

Por hacer una vez (lo tiene que hacer el dueño, con su cuenta):

1. Google Search Console: añadir la propiedad de dominio `buscotucoche.com` (verificación por registro TXT en IONOS) y enviar `https://www.buscotucoche.com/sitemap.xml`.
2. Bing Webmaster Tools: importar la propiedad desde Search Console (Bing alimenta también a ChatGPT y Copilot).
3. Perfil de Empresa de Google, solo si hay una dirección o zona de servicio real.
4. Redirección 301 de `buscotuclasico.com` a `https://www.buscotucoche.com` en IONOS.

## Pendiente antes de publicar

- Rellenar los datos marcados en amarillo en Aviso legal y Política de privacidad (razón social, NIF, dirección).
- Las fotos de los coches son reales (Wikimedia Commons). Mantener la página de créditos; si tenéis fotos propias, se pueden sustituir (ver `assets/img/README.md`).
- Email de contacto: `info@buscotucoche.com`. Comprobar que el buzón existe y recibe correo (está en `EMAIL`, dentro de `build.py`).
- Añadir enlaces de Instagram y Facebook cuando existan.
