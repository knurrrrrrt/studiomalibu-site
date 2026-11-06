---
name: design-inspiration
description: Standard-Rechercheweg fuer neue Design-Vorschlaege auf studiomalibu-site -- Inspo zuerst (strukturierte Referenzen, Paletten, Fonts, Code), Dribbble/Awwwards nur als manueller Fallback bei Nischenthemen, zu denen Inspo zu wenig findet.
when_to_use: Vor jedem neuen Design-Vorschlag oder Redesign fuer eine App-Seite unter apps/* -- oder wenn nach "Referenzen", "Inspiration", "wie sollte das aussehen" gefragt wird. Nicht Dribbble/Awwwards automatisiert abfragen -- siehe Begruendung unten.
---

# Design-Recherche fuer Studio-Malibu-App-Seiten

Stand 2026-09-28. Haelt fest, warum Inspo der Standardweg ist und Dribbble/
Awwwards bewusst NICHT automatisiert werden.

## Standardweg: Inspo (`mcp__inspo__*`)

Projekt-gescopt in `studiomalibu-site/.mcp.json` eingebunden, kostenlos,
kein Login-Zwang. Einstieg immer ueber `recommend`:

```
recommend(brief, mode?, vibe?, pageType?, macrostructure?, color?, device?)
```

Liefert in einem Call: Macrostructure-Empfehlung (mit Runner-ups), 3-5 echte
Referenz-Websites mit Fold-Autopsie, Palette-Vorschlag, passende Referenz-
Komponenten (`get_reference_jsx`), und eine Evidence-Zusammenfassung (Paper-
Band, Display-Klasse, Akzentfarbe ueber die getroffenen Seiten). Kein LLM-Call,
schnell.

Budget (aus dem Tool selbst uebernommen): ein `recommend` + ein bis zwei
`search_screens` + `get_screen` auf die 3-5 behaltenen Referenzen ist eine
vollstaendige Recherche. Nicht mehr Calls draufsatteln, die Ergebnisse werden
bei jedem weiteren Turn erneut gelesen.

Fuer eine Tiefenanalyse einer einzelnen Referenz: `get_design_system(slug)`
(volle DESIGN.md mit CSS-Variablen, Typo-Ramp, Farbrollen).

## Warum NICHT Dribbble/Awwwards automatisieren

Am 2026-09-28 live getestet, bevor ein Automatisierungs-Skill gebaut wurde --
beide sind fuer automatisierte Themen-Suche ungeeignet:

- **Awwwards**: `?search=<begriff>`-Query-Parameter filtert nichts. Verifiziert:
  `awwwards.com/websites/?search=fitness` liefert exakt dieselbe generische
  "Winning Websites"-Liste wie ohne Parameter. Die Suche ist rein clientseitig/
  JS-getrieben, kein sauberer URL- oder API-Zugriff gefunden.
- **Dribbble**: `dribbble.com/search/shots?q=<begriff>` matcht kaum relevant
  (bei "fitness app" kamen thematisch beliebige Shots mit "shot" im Titel).
  Tiefere/weitere Ergebnisse sind hinter einem Login-Zwang ("Sign up to
  continue").

Ein Skill, der das automatisiert, wuerde also entweder falsche Treffer lieferen
oder staendig an der Login-/JS-Huerde scheitern. Deshalb bewusst kein
Automatisierungs-Skill dafuer -- diese Einschaetzung nicht ungeprueft
uebernehmen, falls sich die Seiten spaeter aendern, sondern bei Bedarf neu
verifizieren (kurzer Browser-Test wie oben, nicht raten).

## Manueller Fallback

Wenn Inspos Korpus (832 Websites, Stand seiner letzten Aktualisierung) zu einem
sehr spezifischen oder aktuellen Nischenthema zu wenig hergibt: Dribbble/
Awwwards im Browser-Pane oeffnen und **gemeinsam mit Knut** durchschauen --
nicht automatisiert, sondern als bewusster manueller Zwischenschritt, genau wie
im Alex-Sprogis-Video beschrieben (Schritt 1 seines Vier-Schritte-Workflows).

## Verwandter Skill

Fuer den naechsten Schritt nach der Referenz-Recherche -- scroll-gekoppelte
Story-Sektionen statt statischer Feature-Liste -- siehe `scrollytelling` in
diesem selben `.claude/skills/`-Verzeichnis.
