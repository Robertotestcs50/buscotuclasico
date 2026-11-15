# Busco Tu Coche — web

Web estática, rápida y sin dependencias, lista para GitHub Pages.

## Estructura

- `docs/` — la web ya generada. Es lo que publica GitHub Pages.
- `build.py` — genera `docs/`. Aquí están los textos, los coches y los datos de contacto.
- `assets/` — estilos, código, tipografía y fotos (`assets/img/`, ver su README).
- `scenes.py` — dibuja las ilustraciones de los coches (carrocería, color y paisaje del país de origen).
  Si pones una foto real con el nombre indicado en `assets/img/README.md`, la web la usa en lugar del dibujo.
- `data/stock.json` — coches en stock (lista vacía `[]` = página de stock sin coches).

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
Para recibirlos también por email: crea un formulario gratis en formspree.io con `info@buscotucoche.es`,
copia su dirección (`https://formspree.io/f/xxxxxxx`) en `FORM_ENDPOINT` dentro de `build.py` y vuelve a generar.

## Pendiente antes de publicar

- Rellenar los datos marcados en amarillo en Aviso legal y Política de privacidad (razón social, NIF, dirección).
- Las fotos de los coches son reales (Wikimedia Commons). Mantener la página de créditos; si tenéis fotos propias, se pueden sustituir (ver `assets/img/README.md`).
- Confirmar el email: la web usa `info@buscotucoche.es` (como el prototipo). Si el dominio es .com, crear `info@buscotucoche.com` y cambiarlo en `build.py`.
- Añadir enlaces de Instagram y Facebook cuando existan.
