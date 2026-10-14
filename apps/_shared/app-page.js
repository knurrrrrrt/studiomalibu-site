// Shared behaviour for the app pages. A page defines, before loading this file:
//   window.PAGE_T      = { de: {key: html}, en: {key: html} }   (applied to [data-i18n])
//   window.PAGE_CONFIG = { buyUrl: "https://..." | null }        (Buy button stays hidden without it)
(function () {
  var T = window.PAGE_T || { de: {}, en: {} };
  var CFG = window.PAGE_CONFIG || {};

  function applyLang(l) {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var v = (T[l] || {})[el.getAttribute("data-i18n")];
      if (v !== undefined) el.innerHTML = v;
    });
    var de = document.getElementById("btn-de"), en = document.getElementById("btn-en");
    if (de) de.classList.toggle("active", l === "de");
    if (en) en.classList.toggle("active", l === "en");
    document.documentElement.lang = l;
    try { localStorage.setItem("malibu-lang", l); } catch (e) {}
  }
  window.setLang = applyLang;

  var stored = null;
  try { stored = localStorage.getItem("malibu-lang"); } catch (e) {}
  var browser = (navigator.language || "").toLowerCase().indexOf("de") === 0 ? "de" : "en";
  applyLang(stored || browser);

  if (CFG.buyUrl) {
    document.querySelectorAll("[data-buy]").forEach(function (a) {
      a.href = CFG.buyUrl;
      a.hidden = false;
    });
  }
})();
