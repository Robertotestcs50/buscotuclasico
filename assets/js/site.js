/* Busco Tu Coche — interacción de la web (sin dependencias) */
(function () {
  "use strict";
  var body = document.body;
  var WA = body.getAttribute("data-wa");             // número de WhatsApp, solo dígitos
  var ENDPOINT = body.getAttribute("data-endpoint");  // Formspree u otro (opcional)
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function waLink(text) {
    return "https://wa.me/" + WA + "?text=" + encodeURIComponent(text);
  }

  /* ---------- Menú móvil ---------- */
  var menuBtn = document.querySelector(".menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      var open = body.classList.toggle("menu-open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && body.classList.contains("menu-open")) {
        body.classList.remove("menu-open");
        menuBtn.setAttribute("aria-expanded", "false");
        menuBtn.focus();
      }
    });
  }

  /* ---------- Submenú "Servicios" ----------
     En móvil se muestra siempre abierto dentro del menú; en ordenador se cierra al pulsar fuera. */
  var mobile = window.matchMedia("(max-width: 980px)");
  function syncSubmenu() {
    document.querySelectorAll(".nav details").forEach(function (d) {
      if (mobile.matches) d.setAttribute("open", ""); else d.removeAttribute("open");
    });
  }
  syncSubmenu();
  if (mobile.addEventListener) mobile.addEventListener("change", syncSubmenu);
  document.addEventListener("click", function (e) {
    if (mobile.matches) return;
    document.querySelectorAll(".nav details[open]").forEach(function (d) {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });

  /* ---------- Panel de salidas: efecto de letras al cargar ---------- */
  if (!reduceMotion) {
    var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ";
    document.querySelectorAll(".flaps").forEach(function (row, r) {
      row.querySelectorAll(".flap:not(.sp)").forEach(function (cell, i) {
        var final = cell.textContent;
        var ticks = 6 + i * 2 + r * 3;
        var n = 0;
        cell.textContent = chars[Math.floor(Math.random() * chars.length)];
        var t = setInterval(function () {
          n++;
          if (n >= ticks) { cell.textContent = final; clearInterval(t); return; }
          cell.textContent = chars[Math.floor(Math.random() * chars.length)];
        }, 55);
      });
    });
  }

  /* ---------- Filtros de listados ---------- */
  document.querySelectorAll("[data-filter-group]").forEach(function (group) {
    var target = document.getElementById(group.getAttribute("data-filter-group"));
    var empty = document.getElementById(group.getAttribute("data-filter-group") + "-empty");
    group.addEventListener("click", function (e) {
      var btn = e.target.closest(".chip");
      if (!btn) return;
      group.querySelectorAll(".chip").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      var val = btn.getAttribute("data-value");
      var shown = 0;
      target.querySelectorAll("[data-tags]").forEach(function (card) {
        var ok = val === "todos" || card.getAttribute("data-tags").split(" ").indexOf(val) > -1;
        card.hidden = !ok;
        if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    });
  });

  /* ---------- Formularios ----------
     Si hay un servicio de formularios configurado (data-endpoint), se envía allí.
     Si no, se abre WhatsApp con la solicitud ya escrita: ningún cliente se pierde. */
  function buildMessage(form) {
    var lines = [form.getAttribute("data-intro")];
    form.querySelectorAll("[data-label]").forEach(function (el) {
      var v = (el.value || "").trim();
      if (v) lines.push(el.getAttribute("data-label") + ": " + v);
    });
    return lines.join("\n");
  }
  function status(form, cls, html) {
    var s = form.querySelector(".form-status");
    s.className = "form-status " + cls;
    s.innerHTML = html;
    s.setAttribute("tabindex", "-1");
    s.focus();
  }
  document.querySelectorAll("form[data-intro]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var msg = buildMessage(form);
      var btn = form.querySelector("button[type=submit]");

      if (!ENDPOINT) {
        window.open(waLink(msg), "_blank", "noopener");
        status(form, "ok", form.getAttribute("data-ok-wa") +
          ' Si no se ha abierto, <a href="' + waLink(msg) + '" target="_blank" rel="noopener">pulsa aquí</a>.');
        return;
      }

      btn.disabled = true;
      var data = new FormData(form);
      data.append("_subject", form.getAttribute("data-subject"));
      fetch(ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); })
        .then(function () {
          form.reset();
          status(form, "ok", form.getAttribute("data-ok"));
        })
        .catch(function () {
          status(form, "err", 'No se ha podido enviar el formulario. Envíanos la solicitud por <a href="' +
            waLink(msg) + '" target="_blank" rel="noopener">WhatsApp</a> y te respondemos igual de rápido.');
        })
        .finally(function () { btn.disabled = false; });
    });
  });

  /* ---------- Configurador ---------- */
  var cfg = document.getElementById("configurador");
  if (cfg) {
    var carSel = cfg.querySelector("#cfg-coche");
    var params = new URLSearchParams(location.search);
    var wanted = params.get("coche");
    if (wanted) {
      var found = Array.prototype.some.call(carSel.options, function (o) { return o.value === wanted; });
      if (!found) carSel.add(new Option(wanted, wanted), 0);
      carSel.value = wanted;
    }
    var out = {
      coche: document.getElementById("sum-coche"),
      ruedas: document.getElementById("sum-ruedas"),
      suspension: document.getElementById("sum-suspension"),
      aleron: document.getElementById("sum-aleron"),
      motor: document.getElementById("sum-motor")
    };
    var meter = document.getElementById("cfg-meter");
    var gainTxt = document.getElementById("cfg-gain");
    var waBtn = document.getElementById("cfg-wa");

    function picked(name) { return cfg.querySelector("input[name=" + name + "]:checked"); }
    function update() {
      var gain = 0, parts = {};
      ["ruedas", "suspension", "aleron", "motor"].forEach(function (k) {
        var el = picked(k);
        parts[k] = el.value;
        gain += parseInt(el.getAttribute("data-gain") || "0", 10);
        out[k].textContent = el.value;
      });
      out.coche.textContent = carSel.value;
      meter.style.width = Math.min(100, 20 + gain * 1.4) + "%";
      gainTxt.textContent = gain > 0 ? "+" + gain + " %" : "De serie";
      var msg = "Hola, quiero configurar mi " + carSel.value +
        " (ruedas: " + parts.ruedas + ", suspensión: " + parts.suspension +
        ", alerón: " + parts.aleron + ", motor: " + parts.motor +
        (gain > 0 ? ", +" + gain + " % de potencia estimada" : "") + ")";
      waBtn.href = waLink(msg);
    }
    cfg.addEventListener("change", update);
    update();
  }
})();
