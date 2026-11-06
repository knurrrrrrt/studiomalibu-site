---
name: scrollytelling
description: Scroll-gekoppelte Story-Sektionen (GSAP + ScrollTrigger) fuer die App-Landingpages unter apps/* -- statt einer statischen Feature-Liste den echten Workflow (z.B. Import -> Match -> Export) beim Scrollen durchlaufen lassen.
when_to_use: Wenn eine App-Seite unter apps/* neu gebaut oder ueberarbeitet wird UND die App einen echten sequenziellen Ablauf hat, der sich fuers Scrollen eignet. Nicht ziehen, um eine sonst leere Seite aufzuhuebschen -- siehe Gimmick-Warnung unten.
---

# Scrollytelling fuer Studio-Malibu-App-Seiten

Stand 2026-09-28, angelegt nach Auswertung eines Webdesign-Workflow-Videos
(Alex Sprogis, "Opus 5.5: Webdesign macht ENDLICH wieder Spass"). Noch auf keiner
Live-Seite im Einsatz -- das hier ist die vorbereitete Option, kein Rollout-Plan.

## Wann ziehen, wann nicht

**Ziehen**, wenn die App einen echten, in Schritten erzaehlbaren Ablauf hat --
bei MalibuSync z.B. Import -> Match -> FCP-Export. Der Scroll-Fortschritt muss
etwas Inhaltliches zeigen, nicht nur Bewegung erzeugen.

**Nicht ziehen**, um eine sonst generische Seite zu kaschieren. Der Video-Autor
selbst hat im Cocktail-Beispiel eine interaktive Bilderwand nachtraeglich als
ueberfluessig bezeichnet -- gleiche Falle hier vermeiden. Im Zweifel: statische
Seite (siehe die drei Richtungsvorschlaege vom 2026-09-23 in dieser Session:
Bento/Blau, Console/Raw, Studio/Warm) bleibt die bessere Wahl.

## Tech-Entscheidung

**GSAP Core + ScrollTrigger-Plugin per CDN**, kein Build-Step:

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.7/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.7/dist/ScrollTrigger.min.js"></script>
<script>gsap.registerPlugin(ScrollTrigger);</script>
```

(Versionsnummer beim Einsatz gegen die aktuelle auf gsap.com pruefen und pinnen,
nicht `@latest`.) Passt zu den bestehenden Seiten unter `apps/*` -- reines
statisches HTML mit inline CSS/JS, kein npm/bundler vorhanden, das soll so bleiben.

**Kosten:** GSAP inkl. aller Plugins (auch ScrollTrigger, vormals Club-GreenSock-
pflichtig) ist seit April 2025 komplett kostenlos, keine Mitgliedschaft noetig
(Webflow-Akquise 2024). Keine laufenden Kosten, anders als Mobbin (siehe unten).

## Site-spezifische Stolperfalle: doppelte sticky Nav

`/nav.js` (site-weit, auf jeder App-Seite per `<script src="/nav.js" defer>`
eingebunden) injiziert `#sm-nav` -- 52px hoch, `position:sticky;top:0` -- **vor**
der Seiten-eigenen Nav (`.nav-inner`, 60px, ebenfalls `position:sticky;top:0`,
direkt im Markup jeder `apps/*/index.html`). Beide sind sticky auf denselben
Offset gesetzt.

Für jeden `ScrollTrigger`-Start-Offset diese ~112px (52 + 60, live pruefen falls
sich eine der beiden Hoehen aendert) mit einrechnen -- sonst pinnt die Story-
Sektion sichtbar hinter oder unter der Nav-Leiste.

## Reduced Motion & Mobile

- `prefers-reduced-motion: reduce` -> komplett auf den statischen Ruhezustand
  zurueckfallen (die Sektion so zeigen, wie sie ohne JS aussehen wuerde), keine
  reduzierte Animation als Mittelweg.
- Unter dem bestehenden Breakpoint der Seiten (`max-width:700px`) grundsaetzlich
  kein `pin` setzen -- entweder ganz weglassen oder als einfache, ungepinnte
  Sequenz zeigen. Pro Einsatz neu entscheiden, hier keine Pauschal-Vorgabe.

## Nicht Teil dieses Skills

- **Three.js/3D** -- im Video fuer verspielte Consumer-/Awwwards-Beispiele
  genutzt, nicht fuer die B2B-Pro-Tool-Seiten von Studio Malibu. Separate,
  spaetere Entscheidung, falls ueberhaupt.
- **Mobbin** (kostenpflichtige Referenz-Plattform aus dem Video, eigener MCP-
  Server) -- Inspo deckt denselben Bedarf (Referenz-Websites, Paletten, Fonts)
  bereits kostenlos ab, kein zusaetzliches Abo noetig.

## Fertige Rezepte

Drei ausgearbeitete Scroll-Patterns, passend zu den drei MalibuSync-Richtungs-
vorschlaegen vom 2026-09-23 -- siehe `reference/recipes.md` fuer Markup-Struktur
und Timeline-Codegeruest pro Rezept. Erst laden, wenn eine Seite konkret gebaut
wird.
