(function () {
  var LINKS = [
    { label: "Apps", href: "/apps/" },
    { label: "Workflow", href: "/workflow/" },
    { label: "Videos", href: "/videos/" },
    { label: "Infographics", href: "/infographics/" },
    { label: "FCP Around the World", href: "/projects/" }
  ];

  var css = "" +
    "#sm-nav{position:sticky;top:0;left:0;right:0;z-index:1000;" +
    "height:52px;display:flex;align-items:center;gap:22px;padding:0 20px;" +
    "background:rgba(10,10,13,0.86);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);" +
    "border-bottom:1px solid rgba(255,255,255,0.08);" +
    "font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',Arial,sans-serif;" +
    "font-size:13px;}" +
    "#sm-nav a{text-decoration:none;color:inherit;}" +
    "#sm-nav .sm-brand{display:flex;align-items:center;gap:8px;flex:none;color:#f0f0f2;font-weight:700;letter-spacing:-0.01em;white-space:nowrap;}" +
    "#sm-nav .sm-dot{width:9px;height:9px;border-radius:50%;background:linear-gradient(135deg,#5ea1ff,#b968ff);flex:none;}" +
    "#sm-nav .sm-links{display:flex;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;}" +
    "#sm-nav .sm-links::-webkit-scrollbar{display:none;}" +
    "#sm-nav .sm-links a{flex:none;white-space:nowrap;padding:7px 11px;border-radius:7px;color:#a5a5ad;font-weight:500;transition:background .15s,color .15s;}" +
    "#sm-nav .sm-links a:hover{color:#f0f0f2;background:rgba(255,255,255,0.06);}" +
    "#sm-nav .sm-links a.active{color:#f0f0f2;background:rgba(255,255,255,0.1);}" +
    "#sm-nav .sm-spacer{flex:1;min-width:12px;}" +
    "@media(max-width:640px){#sm-nav{gap:14px;padding:0 14px;}#sm-nav .sm-brand span.sm-word{display:none;}}";

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

  var nav = document.createElement("div");
  nav.id = "sm-nav";
  nav.innerHTML =
    '<a class="sm-brand" href="/"><span class="sm-dot"></span><span class="sm-word">Studio Malibu Berlin</span></a>' +
    '<div class="sm-links">' + linksHtml + '</div>' +
    '<div class="sm-spacer"></div>';

  document.body.insertBefore(nav, document.body.firstChild);
})();
