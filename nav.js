(function () {
  var LINKS = [
    { label: "FCP Videos", href: "/videos/" },
    { label: "FCP Ideas", href: "/ideas/" },
    { label: "FCP Worldwide", href: "/projects/" },
    { label: "FCP Talent Pool", href: "/experts/" },
    { label: "FCP Workflow", href: "/workflow/" },
    { label: "Film Craft", href: "/film-craft/" }
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
    "#sm-nav .sm-links{display:flex;align-items:center;gap:4px;overflow-x:auto;min-width:0;scrollbar-width:none;-ms-overflow-style:none;}" +
    "#sm-nav .sm-links::-webkit-scrollbar{display:none;}" +
    "#sm-nav .sm-links>a{flex:none;white-space:nowrap;padding:7px 11px;border-radius:7px;color:#a5a5ad;font-weight:500;transition:background .15s,color .15s;}" +
    "#sm-nav .sm-links>a:hover{color:#f0f0f2;background:rgba(255,255,255,0.06);}" +
    "#sm-nav .sm-links>a.active{color:#f0f0f2;background:rgba(255,255,255,0.1);}" +
    "#sm-nav .sm-spacer{flex:1;min-width:12px;}" +
    "#sm-menu{position:relative;flex:none;display:none;align-items:center;}" +
    "#sm-menu.sm-menu-visible{display:flex;}" +
    "#sm-menu-toggle{display:flex;align-items:center;gap:5px;background:none;border:none;padding:7px 9px;border-radius:7px;color:#a5a5ad;cursor:pointer;font:inherit;font-weight:500;white-space:nowrap;}" +
    "#sm-menu-toggle:hover,#sm-menu.sm-open #sm-menu-toggle{color:#f0f0f2;background:rgba(255,255,255,0.06);}" +
    "#sm-menu-toggle svg{width:15px;height:15px;flex:none;}" +
    "#sm-menu-panel{position:absolute;top:100%;right:0;margin-top:8px;display:none;flex-direction:column;min-width:220px;" +
    "background:rgba(16,16,20,0.98);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);" +
    "border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:8px;box-shadow:0 16px 40px rgba(0,0,0,0.5);}" +
    "#sm-menu.sm-open #sm-menu-panel{display:flex;}" +
    "#sm-menu-panel a{padding:8px 10px;border-radius:8px;color:#c8c8ce;font-weight:500;white-space:nowrap;}" +
    "#sm-menu-panel a:hover{background:rgba(255,255,255,0.07);color:#fff;}" +
    "#sm-menu-panel a.active{color:#f0f0f2;background:rgba(255,255,255,0.1);}" +
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
      '<div id="sm-menu">' +
        '<button id="sm-menu-toggle" type="button" aria-label="More pages">' +
          '<svg viewBox="0 0 16 16" fill="none"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>' +
        '</button>' +
        '<div id="sm-menu-panel">' + linksHtml + '</div>' +
      '</div>' +
      '<div class="sm-spacer"></div>' +
      '<a class="sm-discord" href="https://discord.gg/sgFQ7WZtN4" target="_blank" rel="noopener noreferrer" aria-label="Join our Discord" title="Join our Discord">' +
        '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/></svg>' +
      '</a>' +
    '</div>';

  document.body.insertBefore(nav, document.body.firstChild);

  var dd = document.getElementById("sm-dd");
  var ddToggle = dd.querySelector(".sm-dd-toggle");
  ddToggle.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    dd.classList.toggle("sm-open");
  });

  var menu = document.getElementById("sm-menu");
  var menuToggle = document.getElementById("sm-menu-toggle");
  var smLinks = nav.querySelector(".sm-links");
  menuToggle.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    menu.classList.toggle("sm-open");
  });
  document.addEventListener("click", function (e) {
    if (!dd.contains(e.target)) dd.classList.remove("sm-open");
    if (!menu.contains(e.target)) menu.classList.remove("sm-open");
  });

  // .sm-links can scroll horizontally, but that's not discoverable (hidden
  // scrollbar, no visual cue) -- so whenever it doesn't fully fit, swap in
  // a proper dropdown menu that guarantees every page stays reachable.
  function checkNavOverflow() {
    var overflowing = smLinks.scrollWidth > smLinks.clientWidth + 1;
    menu.classList.toggle("sm-menu-visible", overflowing);
    if (!overflowing) menu.classList.remove("sm-open");
  }
  checkNavOverflow();
  window.addEventListener("resize", checkNavOverflow);
})();
