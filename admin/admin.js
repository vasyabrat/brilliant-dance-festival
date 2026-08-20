// Brilliant Dance Festival — admin dashboard
// Generic JSON-driven editor: every top-level key in data/content.json gets
// a sidebar entry, and the renderer walks its shape (string / array of
// strings / array of tuples / array of objects / nested object) to build a
// matching form. Saving PUTs the whole content object, the server rewrites
// data/content.json and regenerates every HTML page.

(function () {
  "use strict";

  var state = { content: null, currentSection: null, dirty: false };

  var SECTIONS = [
    { key: "site", title: "Event & Site Info", desc: "The event date, camp dates, and the external links used across the site." },
    { key: "hero", title: "Homepage Hero", desc: "The big headline and intro line at the top of the homepage." },
    { key: "organizers", title: "Leadership / Organizers", desc: "Shown on the homepage mission section, the About page, and the top of the Judges page." },
    { key: "judgingPanel", title: "Judging Panel", desc: "Full judges list shown on the About and Judges pages." },
    { key: "homeFeaturedJudges", title: "Homepage Featured Judges", desc: "A short teaser list of judges shown on the homepage." },
    { key: "officials", title: "Officials", desc: "Master of Ceremonies, Music Director, Scrutineer, etc." },
    { key: "missionText", title: "Mission Statement", desc: "The paragraph under “Our Mission & Vision” on the homepage." },
    { key: "whyChooseUs", title: "Why Choose Us", desc: "The four feature cards shown on the homepage and About page." },
    { key: "pillars", title: "Values / Pillars", desc: "The word list under “Values We Offer!”" },
    { key: "homeSchedule", title: "Homepage Schedule", desc: "Short schedule teaser on the homepage." },
    { key: "scheduleTracks", title: "Full Schedule (Schedule page)", desc: "The detailed running-order tracks on the Schedule page." },
    { key: "homePrizes", title: "Homepage Prizes", desc: "Top Studio / Top Teacher tables shown on the homepage." },
    { key: "prizeTables", title: "Prizes Page", desc: "All prize tables on the Prizes page." },
    { key: "campSchedule", title: "Camp Daily Schedule", desc: "" },
    { key: "campPricing", title: "Camp Pricing", desc: "" },
    { key: "campCoaches", title: "Camp Coaches", desc: "Standard and Latin division coaching faculty." },
    { key: "partnerSearch", title: "Partner Search Listings", desc: "" },
    { key: "vendors", title: "Vendors", desc: "" },
    { key: "sponsors", title: "Sponsors", desc: "" },
    { key: "hotel", title: "Hotel", desc: "" },
    { key: "contact", title: "Contact Info", desc: "" },
    { key: "registrationForms", title: "Registration Forms", desc: "Downloadable PDF links on the Registration page." },
    { key: "registrationPayment", title: "Registration Payment Info", desc: "" },
    { key: "rules", title: "Rules & Regulations", desc: "One entry per numbered rule." },
    { key: "_raw", title: "Advanced: Raw JSON", desc: "Direct access to the entire content file, for anything not covered above." },
    { key: "_password", title: "Change Password", desc: "" },
  ];

  var TEMPLATES = {
    organizers: { name: "", role: "Organizer", bio: "" },
    whyChooseUs: { title: "", text: "" },
    homeFeaturedJudges: { name: "", role: "Judge", quote: "" },
    judgingPanel: { name: "", role: "Judge", quote: "" },
    officials: { name: "", role: "" },
    partnerSearch: { name: "", level: "", studio: "", coaches: "", contact: "", note: "" },
    vendors: { name: "", desc: "", contact: "", link: "" },
    sponsors: { name: "", desc: "", contact: "" },
    homeSchedule: { label: "", time: "" },
    campSchedule: { label: "", time: "" },
    campPricing: { title: "", amount: "", note: "" },
    registrationForms: { name: "", href: "" },
    pillars: "",
    rules: "",
    scheduleTracks: { title: "", items: [] },
    "scheduleTracks.items": { label: "", time: "" },
    "campCoaches.standard": { name: "", quote: "" },
    "campCoaches.latin": { name: "", quote: "" },
    "prizeTables.rows": ["", ""],
    "homePrizes.topStudio": ["", ""],
    "homePrizes.topTeacher": ["", ""],
  };

  var TEXTAREA_KEYS = ["bio", "text", "quote", "lede", "note", "desc", "missiontext"];

  // -------------------------------------------------------------------
  // small helpers
  // -------------------------------------------------------------------
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    attrs = attrs || {};
    Object.keys(attrs).forEach(function (k) {
      if (k === "class") node.className = attrs[k];
      else if (k === "text") node.textContent = attrs[k];
      else if (k.indexOf("on") === 0 && typeof attrs[k] === "function") node.addEventListener(k.slice(2), attrs[k]);
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function humanize(key) {
    var s = key.replace(/([a-z0-9])([A-Z])/g, "$1 $2");
    s = s.replace(/_/g, " ");
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function singularLabel(key) {
    var h = humanize(key);
    if (/ies$/i.test(h)) return h.replace(/ies$/i, "y");
    if (/s$/i.test(h) && !/ss$/i.test(h)) return h.replace(/s$/i, "");
    return h;
  }

  function normalizePath(path) {
    return path.map(function (p) { return typeof p === "number" ? "*" : p; }).join(".");
  }

  function get(path) {
    var o = state.content;
    for (var i = 0; i < path.length; i++) o = o[path[i]];
    return o;
  }

  function setAt(path, value) {
    var o = state.content;
    for (var i = 0; i < path.length - 1; i++) o = o[path[i]];
    o[path[path.length - 1]] = value;
    markDirty();
  }

  function deriveBlank(value) {
    if (Array.isArray(value)) return [];
    if (value && typeof value === "object") {
      var out = {};
      Object.keys(value).forEach(function (k) { out[k] = deriveBlank(value[k]); });
      return out;
    }
    return "";
  }

  function templateFor(path, arr) {
    if (arr && arr.length > 0) return deriveBlank(arr[0]);
    var key = normalizePath(path);
    var tmpl = TEMPLATES[key];
    if (tmpl === undefined) return "";
    return JSON.parse(JSON.stringify(tmpl));
  }

  function markDirty() {
    state.dirty = true;
    var status = document.getElementById("save-status");
    status.textContent = "Unsaved changes";
    status.className = "status";
  }

  function toast(msg, isErr) {
    var t = document.getElementById("toast");
    t.textContent = msg;
    t.className = "toast show" + (isErr ? " err" : "");
    setTimeout(function () { t.className = "toast" + (isErr ? " err" : ""); }, 3200);
  }

  // -------------------------------------------------------------------
  // rendering
  // -------------------------------------------------------------------
  function renderField(path, value) {
    var lastKey = path[path.length - 1];
    var label = typeof lastKey === "number" ? "" : humanize(String(lastKey));
    var useTextarea = TEXTAREA_KEYS.indexOf(String(lastKey).toLowerCase()) !== -1 || value.length > 70;
    var wrap = el("div", { class: "field" });
    if (label) wrap.appendChild(el("label", { text: label }));
    var input = useTextarea ? el("textarea", {}) : el("input", { type: "text" });
    input.value = value;
    input.addEventListener("input", function () { setAt(path, input.value); });
    wrap.appendChild(input);
    return wrap;
  }

  function renderStringList(path, arr, container) {
    var list = el("div", { class: "card-list" });
    arr.forEach(function (v, i) {
      var itemPath = path.concat(i);
      var row = el("div", { class: "string-row" });
      var input = el("input", { type: "text" });
      input.value = v;
      input.addEventListener("input", function () { setAt(itemPath, input.value); });
      row.appendChild(input);
      row.appendChild(el("button", {
        class: "small", text: "Remove", onclick: function () {
          get(path).splice(i, 1);
          markDirty();
          renderSection(state.currentSection);
        }
      }));
      list.appendChild(row);
    });
    container.appendChild(list);
    container.appendChild(el("div", { class: "add-row" }, [
      el("button", {
        class: "outline", text: "+ Add " + singularLabel(path[path.length - 1]), onclick: function () {
          get(path).push(templateFor(path, arr));
          markDirty();
          renderSection(state.currentSection);
        }
      })
    ]));
  }

  function renderTupleList(path, arr, container) {
    var list = el("div", { class: "card-list" });
    arr.forEach(function (pair, i) {
      var row = el("div", { class: "tuple-row" });
      pair.forEach(function (v, j) {
        var input = el("input", { type: "text" });
        input.value = v;
        input.addEventListener("input", function () {
          get(path)[i][j] = input.value;
          markDirty();
        });
        row.appendChild(input);
      });
      row.appendChild(el("button", {
        class: "small", text: "Remove", onclick: function () {
          get(path).splice(i, 1);
          markDirty();
          renderSection(state.currentSection);
        }
      }));
      list.appendChild(row);
    });
    container.appendChild(list);
    container.appendChild(el("div", { class: "add-row" }, [
      el("button", {
        class: "outline", text: "+ Add Row", onclick: function () {
          get(path).push(templateFor(path, arr));
          markDirty();
          renderSection(state.currentSection);
        }
      })
    ]));
  }

  function renderObjectList(path, arr, container) {
    var list = el("div", { class: "card-list" });
    arr.forEach(function (item, i) {
      var itemPath = path.concat(i);
      var card = el("div", { class: "item-card" });
      var head = el("div", { class: "item-card-head" }, [
        el("span", { text: singularLabel(path[path.length - 1]) + " " + (i + 1) }),
        el("button", {
          class: "danger-text", text: "Remove", onclick: function () {
            get(path).splice(i, 1);
            markDirty();
            renderSection(state.currentSection);
          }
        })
      ]);
      card.appendChild(head);
      renderObjectFields(itemPath, item, card);
      list.appendChild(card);
    });
    container.appendChild(list);
    container.appendChild(el("div", { class: "add-row" }, [
      el("button", {
        class: "outline", text: "+ Add " + singularLabel(path[path.length - 1]), onclick: function () {
          get(path).push(templateFor(path, arr));
          markDirty();
          renderSection(state.currentSection);
        }
      })
    ]));
  }

  function renderArray(path, arr, container) {
    if (arr.length === 0) {
      container.appendChild(el("p", { class: "hint", text: "No items yet." }));
      container.appendChild(el("div", { class: "add-row" }, [
        el("button", {
          class: "outline", text: "+ Add " + singularLabel(path[path.length - 1]), onclick: function () {
            get(path).push(templateFor(path, arr));
            markDirty();
            renderSection(state.currentSection);
          }
        })
      ]));
      return;
    }
    if (typeof arr[0] === "string") return renderStringList(path, arr, container);
    if (Array.isArray(arr[0])) return renderTupleList(path, arr, container);
    return renderObjectList(path, arr, container);
  }

  function renderObjectFields(path, obj, container) {
    var simpleWrap = el("div", { class: "field-row" });
    var hasSimple = false;
    Object.keys(obj).forEach(function (k) {
      var v = obj[k];
      var childPath = path.concat(k);
      if (typeof v === "string") {
        hasSimple = true;
        simpleWrap.appendChild(renderField(childPath, v));
      }
    });
    if (hasSimple) container.appendChild(simpleWrap);

    Object.keys(obj).forEach(function (k) {
      var v = obj[k];
      var childPath = path.concat(k);
      if (typeof v === "string") return;
      var section = el("div", { style: "margin-top:18px;" });
      section.appendChild(el("h3", { text: humanize(k), style: "font-size:1rem;margin-bottom:10px;" }));
      if (Array.isArray(v)) renderArray(childPath, v, section);
      else if (v && typeof v === "object") renderObjectFields(childPath, v, section);
      container.appendChild(section);
    });
  }

  function renderRawJson(container) {
    container.appendChild(el("p", { class: "hint", text: "Edit the full content object directly. Must stay valid JSON. Click “Save & Publish” to apply." }));
    var textarea = el("textarea", { class: "raw-json" });
    textarea.value = JSON.stringify(state.content, null, 2);
    var err = el("p", { class: "hint", style: "color:#b3261e;" });
    textarea.addEventListener("input", function () {
      try {
        state.content = JSON.parse(textarea.value);
        err.textContent = "";
        markDirty();
      } catch (e) {
        err.textContent = "Invalid JSON: " + e.message;
      }
    });
    container.appendChild(textarea);
    container.appendChild(err);
  }

  function renderChangePassword(container) {
    var card = el("div", { class: "change-password-card" });
    var current = el("input", { type: "password", placeholder: "Current password" });
    var next = el("input", { type: "password", placeholder: "New password (min 8 characters)" });
    var msg = el("p", { class: "hint" });
    current.style.marginBottom = "10px";
    next.style.marginBottom = "14px";
    current.style.width = next.style.width = "100%";
    current.style.padding = next.style.padding = "11px 13px";
    current.style.border = next.style.border = "1px solid var(--border)";
    current.style.borderRadius = next.style.borderRadius = "8px";
    var btn = el("button", {
      class: "primary", text: "Update Password", onclick: function () {
        fetch("/api/admin/change-password", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ currentPassword: current.value, newPassword: next.value })
        }).then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
          .then(function (res) {
            if (!res.ok) { msg.textContent = res.data.error || "Failed to update password."; msg.style.color = "#b3261e"; return; }
            msg.textContent = "Password updated.";
            msg.style.color = "#1c7c3e";
            current.value = ""; next.value = "";
          });
      }
    });
    card.appendChild(el("h3", { text: "Change Admin Password" }));
    card.appendChild(current);
    card.appendChild(next);
    card.appendChild(btn);
    card.appendChild(msg);
    container.appendChild(card);
  }

  function renderSection(key) {
    state.currentSection = key;
    document.querySelectorAll(".nav-item").forEach(function (b) {
      b.classList.toggle("active", b.dataset.key === key);
    });
    var meta = SECTIONS.filter(function (s) { return s.key === key; })[0];
    var panel = document.getElementById("content-panel");
    panel.innerHTML = "";
    panel.appendChild(el("h2", { text: meta.title }));
    if (meta.desc) panel.appendChild(el("p", { class: "desc", text: meta.desc }));

    if (key === "_raw") return renderRawJson(panel);
    if (key === "_password") return renderChangePassword(panel);

    var value = state.content[key];
    if (typeof value === "string") panel.appendChild(renderField([key], value));
    else if (Array.isArray(value)) renderArray([key], value, panel);
    else if (value && typeof value === "object") renderObjectFields([key], value, panel);
  }

  function renderSidebar() {
    var nav = document.getElementById("nav-items");
    nav.innerHTML = "";
    SECTIONS.forEach(function (s) {
      nav.appendChild(el("button", {
        class: "nav-item", text: s.title, "data-key": s.key,
        onclick: function () { renderSection(s.key); }
      }));
    });
  }

  function saveContent() {
    var status = document.getElementById("save-status");
    status.textContent = "Saving…";
    status.className = "status";
    fetch("/api/admin/content", {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.content)
    }).then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
      .then(function (res) {
        if (!res.ok) {
          status.textContent = "Save failed";
          status.className = "status err";
          toast(res.data.error || "Save failed.", true);
          return;
        }
        state.dirty = false;
        status.textContent = "All changes saved";
        status.className = "status ok";
        toast("Saved and published.");
      })
      .catch(function () {
        status.textContent = "Save failed";
        status.className = "status err";
        toast("Network error while saving.", true);
      });
  }

  // -------------------------------------------------------------------
  // auth + boot
  // -------------------------------------------------------------------
  function showLogin() {
    document.getElementById("app").hidden = true;
    document.getElementById("login-screen").hidden = false;
  }

  function showApp() {
    document.getElementById("login-screen").hidden = true;
    document.getElementById("app").hidden = false;
    renderSidebar();
    fetch("/api/admin/content").then(function (r) { return r.json(); }).then(function (data) {
      state.content = data;
      renderSection("site");
    });
  }

  function attemptLogin() {
    var pw = document.getElementById("login-password").value;
    var errBox = document.getElementById("login-error");
    errBox.textContent = "";
    fetch("/api/login", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pw })
    }).then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
      .then(function (res) {
        if (!res.ok) { errBox.textContent = res.data.error || "Login failed."; return; }
        showApp();
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("login-btn").addEventListener("click", attemptLogin);
    document.getElementById("login-password").addEventListener("keydown", function (e) {
      if (e.key === "Enter") attemptLogin();
    });
    document.getElementById("save-btn").addEventListener("click", saveContent);
    document.getElementById("logout-btn").addEventListener("click", function () {
      fetch("/api/logout", { method: "POST" }).then(function () { showLogin(); });
    });
    window.addEventListener("beforeunload", function (e) {
      if (state.dirty) { e.preventDefault(); e.returnValue = ""; }
    });

    fetch("/api/session").then(function (r) { return r.json(); }).then(function (data) {
      if (data.authenticated) showApp(); else showLogin();
    });
  });
})();
