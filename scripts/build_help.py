#!/usr/bin/env python3
"""Build apps/<slug>/help/index.html from the EN/DE help markdown of an app.

Usage:
  build_help.py --slug malibusync --name MalibuSync --accent '#3D8BFF' --ink '#04101f' \
                --en <repo>/docs/help/getting-started.en.md --de <repo>/docs/help/getting-started.de.md \
                [--en ... --de ...]   # repeat both for more than one guide (matched by order)

The source markdown must already pass .claude/skills/app-help-docs/check_help_docs.py.
Evidence comments are stripped. Tables are not supported on purpose (fail loudly).
"""
import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# basename of a source file (e.g. "howto-x.en.md") -> id of its H1 on the built page.
# Filled in main() before rendering; links to sibling .md files are rewritten with it.
LINKMAP: dict = {}
LINK_ERRORS: list = []
LINK_COUNT = 0


def link(label: str, href: str) -> str:
    global LINK_COUNT
    target, _, frag = href.partition("#")
    if target.endswith(".md"):
        anchor = LINKMAP.get(Path(target).name)
        if anchor is None:
            LINK_ERRORS.append(f"unknown .md link target: {href!r} (label {label!r})")
            return f'<a href="{href}">{label}</a>'
        LINK_COUNT += 1
        href = "#" + anchor
    return f'<a href="{href}">{label}</a>'


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r'<strong class="ui">\1</strong>', s)
    s = re.sub(r"(?<![\w*])_([^_]+)_(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: link(m.group(1), m.group(2)), s)
    return s


def slugify(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "section"


def parse(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        body = text[m.end():]
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    return fm, body


def render(body: str, prefix: str):
    out, toc = [], []
    lines = body.splitlines()
    i, para, list_kind = 0, [], None

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    def close_list():
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = None

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush_para(); close_list()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            i += 1
            continue
        if re.match(r"^\s*\|.*\|\s*$", line):
            sys.exit("tables are not supported; use lists (line: %r)" % line)
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para(); close_list()
            level, title = len(m.group(1)), m.group(2).strip()
            sid = f"{prefix}-{slugify(title)}"
            if level == 1:
                toc.append((sid, title, 1))
            elif level == 2:
                toc.append((sid, title, 2))
            out.append(f'<h{level} id="{sid}">{inline(title)}</h{level}>')
        elif re.match(r"^\s*([-*])\s+", line):
            flush_para()
            if list_kind != "ul":
                close_list(); out.append("<ul>"); list_kind = "ul"
            out.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", line)) + "</li>")
        elif re.match(r"^\s*\d+[.)]\s+", line):
            flush_para()
            if list_kind != "ol":
                close_list(); out.append("<ol>"); list_kind = "ol"
            out.append("<li>" + inline(re.sub(r"^\s*\d+[.)]\s+", "", line)) + "</li>")
        elif line.startswith(">"):
            flush_para(); close_list()
            out.append("<blockquote>" + inline(line.lstrip("> ").strip()) + "</blockquote>")
        elif line.strip() == "---":
            flush_para(); close_list(); out.append("<hr>")
        elif not line.strip():
            flush_para(); close_list()
        else:
            if list_kind and line.startswith("  "):
                out[-1] = out[-1][:-5] + " " + inline(line.strip()) + "</li>"
            else:
                close_list(); para.append(line.strip())
        i += 1
    flush_para(); close_list()
    return "\n".join(out), toc


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} · Help</title>
<link rel="icon" type="image/png" href="/apps/{slug}/icon.png">
<meta name="description" content="How to use {name}: getting started and step-by-step guides.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@500;600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/apps/_shared/app-page.css">
<style>
:root{{--accent:{accent};--accent-ink:{ink}}}
.help{{display:grid;grid-template-columns:220px minmax(0,1fr);gap:56px;padding-block:24px 80px}}
.toc{{position:sticky;top:76px;align-self:start;font-size:13.5px}}
.toc a{{display:block;color:var(--dim);padding:5px 0}}
.toc a:hover{{color:var(--text)}}
.toc a.l1{{color:var(--text);font-weight:600;margin-top:12px}}
.toc a.l2{{padding-left:12px;font-size:12.5px}}
.doc h1{{margin-top:56px;padding-top:36px;border-top:1px solid var(--line)}}
.doc h1:first-child{{margin-top:0;padding-top:0;border-top:0}}
.toc .t{{font:500 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}}
.help>*{{min-width:0}}
.doc{{max-width:72ch;overflow-wrap:anywhere}}
.doc h1{{font-size:clamp(2rem,3.4vw,2.6rem);margin-bottom:12px}}
.doc h2{{font-size:1.45rem;margin:44px 0 10px;padding-top:28px;border-top:1px solid var(--line)}}
.doc h3{{font-family:var(--display);font-weight:600;font-size:1.1rem;margin:28px 0 6px}}
.doc p,.doc li{{color:#C9CCD3;font-size:15.5px}}
.doc li+li{{margin-top:6px}}
.doc ol,.doc ul{{padding-left:22px}}
.doc blockquote{{margin:16px 0;padding:10px 16px;border-left:2px solid var(--accent);background:var(--surface);color:var(--dim);font-size:14px;border-radius:0 8px 8px 0}}
.doc code{{font:400 13px var(--mono);background:var(--raised);border:1px solid var(--line);border-radius:5px;padding:1px 6px}}
.doc pre{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow:auto}}
.doc pre code{{background:none;border:0;padding:0}}
.doc strong.ui{{font-weight:600;color:var(--text);background:var(--raised);border:1px solid var(--line);border-radius:5px;padding:0 6px}}
.doc img{{border:1px solid var(--line);border-radius:10px;margin:14px 0}}
.doc a{{color:var(--accent);text-decoration:underline;text-underline-offset:3px}}
.ver{{font:400 11.5px var(--mono);color:var(--dim);margin-top:40px}}
@media(max-width:860px){{.help{{grid-template-columns:1fr;gap:20px}}.toc{{position:static}}}}
</style>
</head>
<body>
<script src="/nav.js" defer></script>
<div class="wrap">
  <div class="pagebar">
    <div class="pagebar-left">
      <a class="back" href="/apps/{slug}/" data-i18n="nav.back">← {name}</a>
      <div class="brand"><img src="/apps/{slug}/icon.png" alt="">{name} <span style="color:var(--dim);font-weight:500" data-i18n="nav.help">Help</span></div>
    </div>
    <div class="pagebar-right">
      <div class="lang">
        <button id="btn-de" onclick="setLang('de')">DE</button>
        <button id="btn-en" onclick="setLang('en')">EN</button>
      </div>
    </div>
  </div>
  <div class="help">
{blocks}
  </div>
  <footer>
    <div class="foot">
      <span>{name} · <span data-i18n="foot.sub">A Studio Malibu Berlin product</span></span>
      <span><a href="https://knuthake.de/impressum" data-i18n="foot.imprint">Legal Notice</a><a href="https://knuthake.de/datenschutz" data-i18n="foot.privacy">Privacy Policy</a></span>
    </div>
  </footer>
</div>
<script>
window.PAGE_CONFIG = {{ buyUrl: null }};
window.PAGE_T = {{
  en: {{"nav.back":"← {name}","nav.help":"Help","foot.sub":"A Studio Malibu Berlin product","foot.imprint":"Legal Notice","foot.privacy":"Privacy Policy"}},
  de: {{"nav.back":"← {name}","nav.help":"Hilfe","foot.sub":"Ein Studio Malibu Berlin Produkt","foot.imprint":"Impressum","foot.privacy":"Datenschutz"}}
}};
</script>
<script src="/apps/_shared/app-page.js"></script>
<script>
(function () {{
  function show(l) {{
    document.querySelectorAll("[data-lang]").forEach(function (el) {{ el.hidden = el.getAttribute("data-lang") !== l; }});
  }}
  var shared = window.setLang;
  window.setLang = function (l) {{ shared(l); show(l); }};
  show(document.documentElement.lang === "de" ? "de" : "en");
}})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--accent", required=True)
    ap.add_argument("--ink", default="#04101f")
    ap.add_argument("--en", action="append", required=True)
    ap.add_argument("--de", action="append", required=True)
    a = ap.parse_args()
    if len(a.en) != len(a.de):
        sys.exit("--en and --de must be given the same number of times")

    def order_of(path):
        fm, _ = parse(Path(path).read_text(encoding="utf-8"))
        try:
            return int(fm.get("order", 999))
        except ValueError:
            return 999
    sorted_pairs = sorted(zip(a.en, a.de), key=lambda p: order_of(p[0]))
    a.en, a.de = [p[0] for p in sorted_pairs], [p[1] for p in sorted_pairs]
    for n, (en, de) in enumerate(zip(a.en, a.de)):
        for lang, path in (("en", en), ("de", de)):
            _, body = parse(Path(path).read_text(encoding="utf-8"))
            h1 = re.search(r"^#\s+(.*)$", body, re.M)
            if h1:
                LINKMAP[Path(path).name] = f"{lang}{n}-{slugify(h1.group(1).strip())}"
    blocks = {"en": [], "de": []}
    versions = set()
    toc_by_lang = {"en": [], "de": []}
    for n, (en, de) in enumerate(zip(a.en, a.de)):
        for lang, path in (("en", en), ("de", de)):
            fm, body = parse(Path(path).read_text(encoding="utf-8"))
            if fm.get("version"):
                versions.add(fm["version"])
            htmlbody, toc = render(body, f"{lang}{n}")
            blocks[lang].append(htmlbody)
            toc_by_lang[lang] += toc
    if LINK_ERRORS:
        sys.exit("\n".join(LINK_ERRORS))
    ver = ", ".join(sorted(versions))
    label = {"en": ("On this page", f"Written for version {ver}."), "de": ("Auf dieser Seite", f"Geschrieben für Version {ver}.")}
    parts = []
    for lang in ("en", "de"):
        multi = len(blocks[lang]) > 1
        toc = "".join(
            f'<a class="l{lv}" href="#{sid}">{html.escape(t)}</a>'
            for sid, t, lv in toc_by_lang[lang] if lv == 1 or not multi or lv == 2 and False
        ) if multi else "".join(
            f'<a class="l2" href="#{sid}">{html.escape(t)}</a>' for sid, t, lv in toc_by_lang[lang] if lv == 2
        )
        parts.append(
            f'    <div class="toc" data-lang="{lang}"{" hidden" if lang == "de" else ""}><div class="t">{label[lang][0]}</div>{toc}</div>\n'
            f'    <article class="doc" data-lang="{lang}"{" hidden" if lang == "de" else ""} lang="{lang}">\n'
            + "\n".join(blocks[lang]) + f'\n<p class="ver">{label[lang][1]}</p>\n    </article>'
        )
    # the two languages share the grid; only one pair is visible at a time
    page = PAGE.format(name=a.name, slug=a.slug, accent=a.accent, ink=a.ink, blocks="\n".join(parts))
    out = ROOT / "apps" / a.slug / "help" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("wrote", out.relative_to(ROOT), f"({LINK_COUNT} sibling links rewritten)")


if __name__ == "__main__":
    main()
