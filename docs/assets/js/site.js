/* Busco Tu Coche — interacción (sin dependencias). Todo funciona también sin JS. */
(function () {
  "use strict";
  var body = document.body;
  var WA = body.getAttribute("data-wa");
  var ENDPOINT = body.getAttribute("data-endpoint");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function waLink(text) { return "https://wa.me/" + WA + "?text=" + encodeURIComponent(text); }
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9 ]+/g, " ").trim(); }

  /* ---------- Menú móvil ---------- */
  var menuBtn = document.querySelector(".menu-btn");
  if (menuBtn) {
    var setMenu = function (open) {
      body.classList.toggle("menu-open", open);
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      menuBtn.textContent = open ? "Cerrar" : "Menú";
    };
    menuBtn.addEventListener("click", function () { setMenu(!body.classList.contains("menu-open")); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && body.classList.contains("menu-open")) { setMenu(false); menuBtn.focus(); }
    });
    document.querySelectorAll(".nav a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
  }

  /* ---------- Entradas al aparecer ---------- */
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -10% 0px" });
    var pending = Array.prototype.slice.call(document.querySelectorAll(".rv, .shutter"));
    pending.forEach(function (el) { io.observe(el); });
    /* Si se salta con un enlace o un scroll muy rápido, lo que ya quedó por encima se muestra igual */
    var sweep = function () {
      pending = pending.filter(function (el) {
        if (el.classList.contains("is-in")) return false;
        if (el.getBoundingClientRect().top < window.innerHeight) { el.classList.add("is-in"); io.unobserve(el); return false; }
        return true;
      });
      if (!pending.length) window.removeEventListener("scroll", onScroll);
    };
    var ticking = false;
    var onScroll = function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; sweep(); }); } };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("load", sweep);
  } else {
    document.querySelectorAll(".rv, .shutter").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- El hueco de la frase: pasa por los coches más buscados ---------- */
  var slot = document.querySelector(".hero .slot");
  var slotImgs = slot ? slot.querySelectorAll("img") : [];
  var cycle = 0, cycleTimer = null, typing = false;
  function show(i) { slotImgs.forEach(function (im, k) { im.classList.toggle("is-on", k === i); }); }
  function startCycle() {
    if (reduce || slotImgs.length < 2) return;
    stopCycle();
    cycleTimer = setInterval(function () {
      if (typing || document.hidden) return;
      cycle = (cycle + 1) % slotImgs.length; show(cycle);
    }, 3200);
  }
  function stopCycle() { if (cycleTimer) clearInterval(cycleTimer); cycleTimer = null; }
  startCycle();

  /* ---------- Buscador de la portada: «Busco…» ---------- */
  var finder = document.getElementById("finder");
  var dataEl = document.getElementById("cars-data");
  if (finder && dataEl && slot) {
    var cars = JSON.parse(dataEl.textContent);
    var input = finder.querySelector("input");
    var out = document.getElementById("finder-out");
    var live = document.createElement("img");
    live.alt = ""; live.decoding = "async";
    slot.appendChild(live);
    var best = function (q) {
      q = norm(q); if (q.length < 2) return null;
      var words = q.split(" "), top = null, topScore = 0;
      cars.forEach(function (c) {
        var hay = norm(c.name + " " + c.keys + " " + c.chassis), score = 0;
        words.forEach(function (w) { if (w.length > 1 && hay.indexOf(w) > -1) score += w.length; });
        if (score > topScore) { topScore = score; top = c; }
      });
      return topScore >= 2 ? top : null;
    };
    input.addEventListener("input", function () {
      var q = input.value.trim();
      typing = q.length > 0;
      var c = best(q);
      if (c) {
        live.src = c.img; live.alt = c.name; live.style.objectPosition = c.pos || "";
        slotImgs.forEach(function (im) { im.classList.remove("is-on"); });
        live.classList.add("is-on");
        out.innerHTML = "Lo tenemos de ejemplo: <a href=\"" + c.url + "\">" + c.name + "</a>, " + c.chassis_text + "desde " + c.origin + ".";
      } else {
        live.classList.remove("is-on"); show(cycle);
        out.textContent = q.length > 1 ? "No está en nuestros ejemplos, pero lo buscamos igual." : "";
      }
    });
  }

  /* ---------- Índice «Los más buscados»: la fila señalada muestra su foto ---------- */
  var preview = document.querySelector(".index-preview");
  if (preview) {
    var pimgs = preview.querySelectorAll("img"), pcap = preview.querySelector("figcaption");
    document.querySelectorAll(".index-row").forEach(function (row, i) {
      var on = function () {
        pimgs.forEach(function (im, k) { im.classList.toggle("is-on", k === i); });
        if (pcap) pcap.textContent = row.getAttribute("data-cap");
      };
      row.addEventListener("mouseenter", on); row.addEventListener("focus", on);
    });
  }

  /* ---------- Filtros del catálogo ---------- */
  document.querySelectorAll("[data-filter-group]").forEach(function (group) {
    var id = group.getAttribute("data-filter-group");
    var target = document.getElementById(id), empty = document.getElementById(id + "-empty");
    group.addEventListener("click", function (e) {
      var btn = e.target.closest(".chip"); if (!btn) return;
      group.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      var val = btn.getAttribute("data-value"), shown = 0;
      target.querySelectorAll("[data-tags]").forEach(function (card) {
        var ok = val === "todos" || card.getAttribute("data-tags").split(" ").indexOf(val) > -1;
        card.hidden = !ok; if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    });
  });

  /* ---------- Contacto: rellena el modelo que viene en el enlace ---------- */
  var params = new URLSearchParams(location.search);
  var modelo = params.get("modelo");
  var fModelo = document.getElementById("f-modelo");
  if (modelo && fModelo) { fModelo.value = modelo; }

  /* ---------- Formularios: servicio de formularios si existe; si no, WhatsApp ---------- */
  function buildMessage(form) {
    var lines = [form.getAttribute("data-intro")];
    form.querySelectorAll("[data-label]").forEach(function (el) {
      var v = (el.value || "").trim(); if (v) lines.push(el.getAttribute("data-label") + ": " + v);
    });
    return lines.join("\n");
  }
  function status(form, cls, html) {
    var s = form.querySelector(".form-status");
    s.className = "form-status " + cls; s.innerHTML = html; s.setAttribute("tabindex", "-1"); s.focus();
  }
  document.querySelectorAll("form[data-intro]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var msg = buildMessage(form), link = waLink(msg);
      var btn = form.querySelector("button[type=submit]");
      if (!ENDPOINT) {
        var w = window.open(link, "_blank", "noopener");
        status(form, "ok", form.getAttribute("data-ok-wa") + " Si no se ha abierto, <a href=\"" + link + "\" target=\"_blank\" rel=\"noopener\">ábrelo aquí</a>.");
        return w;
      }
      btn.disabled = true;
      var data = new FormData(form); data.append("_subject", form.getAttribute("data-subject"));
      fetch(ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); })
        .then(function () { form.reset(); status(form, "ok", form.getAttribute("data-ok")); })
        .catch(function () { status(form, "err", "No se ha podido enviar. Mándanos la solicitud por <a href=\"" + link + "\" target=\"_blank\" rel=\"noopener\">WhatsApp</a> y te respondemos igual de rápido."); })
        .finally(function () { btn.disabled = false; });
    });
  });

  /* ---------- Configurador ---------- */
  var cfg = document.getElementById("configurador");
  if (cfg) {
    var wanted = params.get("coche"), sumPhoto = document.getElementById("sum-photo");
    if (wanted) {
      var match = Array.prototype.find.call(cfg.querySelectorAll("input[name=coche]"), function (r) { return r.value === wanted; });
      if (match) { match.checked = true; }
    }
    var carVal = function () { var r = cfg.querySelector("input[name=coche]:checked"); return r ? r : null; };
    var outs = {};
    ["coche", "ruedas", "suspension", "aleron", "motor"].forEach(function (k) { outs[k] = document.getElementById("sum-" + k); });
    var meter = document.getElementById("cfg-meter"), gainTxt = document.getElementById("cfg-gain"), waBtn = document.getElementById("cfg-wa");
    var update = function () {
      var gain = 0, parts = {};
      ["ruedas", "suspension", "aleron", "motor"].forEach(function (k) {
        var el = cfg.querySelector("input[name=" + k + "]:checked");
        parts[k] = el.value; gain += parseInt(el.getAttribute("data-gain") || "0", 10); outs[k].textContent = el.value;
      });
      var cr = carVal(); var carName = cr ? cr.value : (wanted || "");
      outs.coche.textContent = carName;
      if (cr && sumPhoto && sumPhoto.getAttribute("src") !== cr.getAttribute("data-img")) { sumPhoto.src = cr.getAttribute("data-img"); sumPhoto.alt = carName; sumPhoto.style.objectPosition = cr.getAttribute("data-pos") || ""; }
      meter.style.width = Math.min(100, 20 + gain * 1.4) + "%";
      gainTxt.textContent = gain > 0 ? "+" + gain + " %" : "De serie";
      waBtn.href = waLink("Hola, quiero configurar mi " + carName + " (ruedas: " + parts.ruedas + ", suspensión: " + parts.suspension +
        ", alerón: " + parts.aleron + ", motor: " + parts.motor + (gain > 0 ? ", +" + gain + " % de potencia estimada" : "") + ")");
    };
    cfg.addEventListener("change", update); update();
  }
  /* ---------- WhatsApp flotante: se aparta cuando taparía un botón ---------- */
  var waFloat = document.querySelector(".wa-float");
  if (waFloat && "IntersectionObserver" in window) {
    var blockers = document.querySelectorAll("#finder, form .form-actions, .page-head .side, .cta-band, .footer");
    var onScreen = new Set();
    var waIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) onScreen.add(en.target); else onScreen.delete(en.target); });
      waFloat.classList.toggle("is-away", onScreen.size > 0);
    }, { rootMargin: "0px 0px -0px 0px" });
    blockers.forEach(function (b) { waIo.observe(b); });
  }
})();
