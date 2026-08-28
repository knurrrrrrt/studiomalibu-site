(function () {
  var LINKS = [
    { label: "FCP Videos & Infographics", href: "/videos/" },
    { label: "FCP Ideas", href: "/ideas/" },
    { label: "FCP Around the World", href: "/projects/" },
    { label: "FCP Talent Pool", href: "/experts/" },
    { label: "FCP Workflow", href: "/workflow/" }
  ];

  // Kept in sync by hand with the app arrays in apps/index.html (postProductionApps/
  // everydayApps/personalApps) -- only apps with a real local href or externalHref are
  // listed here (skips Malibu Sound2Pro/on-hold and FundusKit/no page yet).
  var APP_GROUPS = [
    {
      heading: "For film post-production",
      apps: [
        { name: "SyncScript Pro", href: "/apps/syncscript-pro" },
        { name: "MalibuSync", href: "/apps/malibusync" },
        { name: "Malibu Meter", href: "/apps/malibu-meter" },
        { name: "MalibuMesh", href: "/apps/malibu-media-sync" },
        { name: "MalibuReview", href: "/apps/malibu-review", soon: true },
        { name: "Malibu Burn", href: "/apps/malibu-burn", soon: true },
        { name: "MalibuToDo", href: "/apps/malibutodo", soon: true },
        { name: "Malibu Conform", href: "/apps/malibu-conform", soon: true }
      ]
    },
    {
      heading: "For everyday work",
      apps: [
        { name: "MalibuClip", href: "/apps/malibuclip" },
        { name: "MalibuDictate", href: "/apps/malibudictate" },
        { name: "Malibu Calc", href: "/apps/malibucalc" },
        { name: "Malibu Screen Capture", href: "/apps/malibuscreener" },
        { name: "Malibu Meeting Notes", href: "/apps/malibumeeting" },
        { name: "Malibu NotesBar", href: "/apps/malibu-notesbar" }
      ]
    },
    {
      heading: "Also from Studio Malibu",
      apps: [
        { name: "MalibuPlay", href: "/apps/malibuplay", soon: true },
        { name: "Malibu Occhio", href: "/apps/malibu-occhio", soon: true },
        { name: "Malibu Marantz", href: "/apps/malibu-marantz", soon: true },
        { name: "LifeLotse", href: "https://lifelotse.de", external: true },
        { name: "TaxLotse", href: "https://taxlotse.de", external: true, soon: true }
      ]
    }
  ];

  var css = "" +
    "#sm-nav{position:sticky;top:0;left:0;right:0;z-index:1000;" +
    "height:52px;display:flex;align-items:stretch;" +
    "background:rgba(10,10,13,0.86);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);" +
    "border-bottom:1px solid rgba(255,255,255,0.08);" +
    "font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',Arial,sans-serif;" +
    "font-size:13px;}" +
    "#sm-nav .sm-inner{width:100%;max-width:1100px;margin:0 auto;padding:0 20px;" +
    "display:flex;align-items:center;gap:22px;}" +
    "#sm-nav a{text-decoration:none;color:inherit;}" +
    "#sm-nav .sm-brand{display:flex;align-items:center;gap:8px;flex:none;color:#f0f0f2;font-weight:700;letter-spacing:-0.01em;white-space:nowrap;}" +
    "#sm-nav .sm-dot{width:9px;height:9px;border-radius:50%;background:linear-gradient(135deg,#5ea1ff,#b968ff);flex:none;}" +
    "#sm-nav .sm-links{display:flex;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;}" +
    "#sm-nav .sm-links::-webkit-scrollbar{display:none;}" +
    "#sm-nav .sm-links>a{flex:none;white-space:nowrap;padding:7px 11px;border-radius:7px;color:#a5a5ad;font-weight:500;transition:background .15s,color .15s;}" +
    "#sm-nav .sm-links>a:hover{color:#f0f0f2;background:rgba(255,255,255,0.06);}" +
    "#sm-nav .sm-links>a.active{color:#f0f0f2;background:rgba(255,255,255,0.1);}" +
    "#sm-nav .sm-spacer{flex:1;min-width:12px;}" +
    "#sm-dd{position:relative;flex:none;display:flex;align-items:center;border-radius:7px;color:#a5a5ad;transition:background .15s,color .15s;}" +
    "#sm-dd:hover,#sm-dd.sm-open{color:#f0f0f2;background:rgba(255,255,255,0.06);}" +
    "#sm-dd.sm-dd-active{color:#f0f0f2;background:rgba(255,255,255,0.1);}" +
    "#sm-dd .sm-dd-trigger{display:flex;align-items:center;padding:7px 2px 7px 11px;color:inherit;font-weight:500;white-space:nowrap;}" +
    "#sm-dd .sm-dd-caret{width:9px;height:9px;flex:none;opacity:0.7;transition:transform .15s;}" +
    "#sm-dd.sm-open .sm-dd-caret{transform:rotate(180deg);}" +
    "#sm-dd .sm-dd-toggle{display:flex;align-items:center;background:none;border:none;padding:7px 10px 7px 2px;color:inherit;cursor:pointer;}" +
    "#sm-dd-panel{position:absolute;top:100%;left:0;margin-top:8px;display:none;grid-template-columns:repeat(3,168px);gap:22px;" +
    "background:rgba(16,16,20,0.98);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);" +
    "border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:18px;box-shadow:0 16px 40px rgba(0,0,0,0.5);}" +
    "#sm-dd.sm-open #sm-dd-panel{display:grid;}" +
    "@media(hover:hover){#sm-dd:hover #sm-dd-panel{display:grid;}}" +
    "#sm-dd-panel .sm-dd-heading{font-size:10px;letter-spacing:0.06em;text-transform:uppercase;color:#6e6e78;margin:0 0 8px;font-weight:600;}" +
    "#sm-dd-panel .sm-dd-col{display:flex;flex-direction:column;}" +
    "#sm-dd-panel a{display:flex;align-items:center;justify-content:space-between;gap:6px;padding:6px 8px;margin:0 -8px;border-radius:6px;color:#c8c8ce;font-weight:500;white-space:nowrap;}" +
    "#sm-dd-panel a:hover{background:rgba(255,255,255,0.07);color:#fff;}" +
    "#sm-dd-panel .sm-dd-soon{font-size:9px;letter-spacing:0.02em;color:#6e6e78;font-weight:600;}" +
    "@media(max-width:640px){#sm-nav .sm-inner{gap:14px;padding:0 14px;}#sm-nav .sm-brand span.sm-word{display:none;}" +
    "#sm-dd-panel{grid-template-columns:1fr;gap:14px;left:-14px;max-width:calc(100vw - 28px);}}";

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var path = window.location.pathname;

  function isActive(href) {
    if (href === "/") return path === "/";
    return path.indexOf(href) === 0;
  }

  var linksHtml = LINKS.map(function (l) {
    return '<a href="' + l.href + '"' + (isActive(l.href) ? ' class="active"' : '') + '>' + l.label + '</a>';
  }).join("");

  var panelHtml = APP_GROUPS.map(function (g) {
    var itemsHtml = g.apps.map(function (a) {
      var target = a.external ? ' target="_blank" rel="noopener noreferrer"' : "";
      return '<a href="' + a.href + '"' + target + '>' + a.name +
        (a.soon ? '<span class="sm-dd-soon">Soon</span>' : '') + '</a>';
    }).join("");
    return '<div class="sm-dd-col"><p class="sm-dd-heading">' + g.heading + '</p>' + itemsHtml + '</div>';
  }).join("");

  var nav = document.createElement("div");
  nav.id = "sm-nav";
  nav.innerHTML =
    '<div class="sm-inner">' +
      '<a class="sm-brand" href="/"><span class="sm-dot"></span><span class="sm-word">Studio Malibu Berlin</span></a>' +
      '<div id="sm-dd"' + (isActive("/apps/") ? ' class="sm-dd-active"' : '') + '>' +
        '<a class="sm-dd-trigger" href="/apps/">Apps</a>' +
        '<button class="sm-dd-toggle" type="button" aria-label="Toggle apps menu">' +
          '<svg class="sm-dd-caret" viewBox="0 0 10 10" fill="none"><path d="M2 3.5L5 6.5L8 3.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
        '</button>' +
        '<div id="sm-dd-panel">' + panelHtml + '</div>' +
      '</div>' +
      '<div class="sm-links">' + linksHtml + '</div>' +
      '<div class="sm-spacer"></div>' +
    '</div>';

  document.body.insertBefore(nav, document.body.firstChild);

  var dd = document.getElementById("sm-dd");
  var ddToggle = dd.querySelector(".sm-dd-toggle");
  ddToggle.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    dd.classList.toggle("sm-open");
  });
  document.addEventListener("click", function (e) {
    if (!dd.contains(e.target)) dd.classList.remove("sm-open");
  });
})();
