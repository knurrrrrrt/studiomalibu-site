---
name: app-help-docs
description: Verfahren, mit dem eine App-Session aus dem Code-Stand von heute verifizierte Anleitungen und Hilfeseiten (EN+DE) fuer ihre App schreibt, durch ein Pruefskript schickt und auf studiomalibu.de veroeffentlichen laesst.
when_to_use: Wenn fuer eine Studio-Malibu-App Anleitungen/Hilfe geschrieben oder nach einer Aenderung aktualisiert werden sollen. Pilot-Stand 2026-10-14 (Malibu Sync, Malibu Drop); danach ins studio-malibu-Plugin ueberfuehren.
---

# App-Hilfe: schreiben, pruefen, veroeffentlichen

Warum es das gibt: Auf den App-Seiten standen Aussagen, die die Apps nicht (mehr)
einloesen. Hilfetexte haben dasselbe Risiko. Deshalb ist **der Beleg wichtiger als
der Text**: Was nicht im Code von heute belegt ist, wird nicht geschrieben.

## Ablage

In **deinem App-Repo**: `docs/help/<name>.en.md` und `docs/help/<name>.de.md`.
Englisch ist die Quelle, Deutsch die Uebersetzung mit **identischer Struktur** (gleiche
Abschnitte, gleiche Belege). Produkttext ist immer Englisch/Deutsch, nie Chat-Deutsch
mit Anglizismen-Misch.

## Welche Dokumente (Diataxis, Minimum)

| Datei | Typ | Inhalt |
|---|---|---|
| `getting-started` | Tutorial | Ein Beispiel von Start bis Ergebnis, ein Weg, keine Verzweigungen |
| `howto-<aufgabe>` (4-8) | How-to | Ein Ziel pro Datei: "So ... ", nur Handlung, Erklaerung nur verlinken |
| `reference` | Referenz | Menues, Einstellungen mit Default, Tastenkuerzel, Formate/Versionen, Limits |
| `troubleshooting` | FAQ | Symptom -> Ursache -> Loesung; nur bekannte, belegte Faelle |

Typen nicht mischen: kein Tutorial mit Hintergrundkapitel, kein How-to mit Erklaerblock.
Das Tutorial hat keine Verzweigungen; Optionen (z.B. ein zweites Importformat) werden dort nur
als Verweis auf das passende How-to genannt.

## Schreibregeln

- Aufgabenorientiert, Imperativ, Mac-Begriffe ("klicken", nicht "tippen"). Standard-
  Bedienelemente (Fenster schliessen etc.) nicht erklaeren.
- **`**Fett**` ist ausschliesslich fuer UI-Beschriftungen** (Button, Menue, Einstellung).
  Der Text muss woertlich im Quellcode/String-Katalog stehen. Betonung nur mit `_kursiv_`.
- **Ausgelieferte Version:** Die Hilfe beschreibt, was der aktuelle Download kann. Funktionen
  aus dem Branch oder der naechsten Version nur mit "ab Version X" oder gar nicht.
- Nur was die App **heute** tut. Opt-in/Default benennen ("ist standardmaessig aus").
  Experimentelles, Stubs und tote Schalter nicht beschreiben.
- Grenzen offen sagen (was die App nicht kann, Voraussetzungen, Mindest-macOS).
- **Trial-Dauer nie nennen.** Der Lizenzserver entscheidet (MalibuLicenseServer main.go:
  `trialDuration` = 10 Tage; Apps in `LICENSE_UNLIMITED_TRIAL_APP_IDS` laufen als offenes
  Beta mit gleitendem Fenster). Die "30" in den Apps ist nur eine kosmetische
  Offline-Schaetzung. Schreibe "kostenlose Testphase, E-Mail beim ersten Start", ohne Tage.
- Keine Latenz-/Genauigkeitszahlen ohne Messbeleg, keine Marketing-Adjektive.
- **Generisch fuer fremde Nutzer:** Keine Studio-internen Pfade, Volume-Namen, Rechnernamen,
  Tester- oder Kundennamen im Text ("studio volume", "/Volumes/...", "bei uns"). Defaults, die
  nur im Studio sinnvoll sind, als "Platzhalter" beschreiben und sagen, was der Nutzer setzen
  muss. Beispiele im Text immer neutral (Beispielnamen, nicht echte Projekte).
- Keine Tabellen (der Site-Build lehnt sie ab), Listen und Absaetze reichen.
- Bilder optional; wenn, dann Fenster-Screenshots per `screencapture -l <windowID>` unter
  `docs/help/img/`, relativ verlinkt. Keine Mockups.

## Format jeder Datei

```
---
title: Getting started
app: MalibuSync
slug: malibusync          # = apps/<slug>/ auf der Website
lang: en                  # passend zum Dateinamen
version: 0.17.18          # App-Version, gegen die verifiziert wurde (Skript warnt bei Drift)
order: 1                  # optional: Reihenfolge der Seiten auf der Hilfeseite
reviewed: 2026-10-14 review-agent, 9 findings fixed   # Pflicht: Nachweis von Schritt 4
---
# Getting started

## Scan your files
Click **Scan & Match** to read all timecodes.
<!-- evidence: Sources/App/ImportController.swift:120, Sources/App/Strings.swift -->
```

Jeder `## `-Abschnitt braucht **einen** Evidence-Kommentar mit Dateipfaden relativ zum
Repo-Root. Beleg = die Stelle, die die Aussage wahr macht. Zulaessige Formen:
`pfad:123` (Zeile muss existieren) oder `pfad#Symbolname` (muss in der Datei vorkommen).
Ein reiner Dateipfad zaehlt nicht als Beleg; pro Abschnitt muss mindestens ein Eintrag mit
Zeile oder Symbol dabei sein.

**Fett-Labels** bleiben so, wie sie in der App stehen. Ist die App englisch, bleiben sie
auch in der deutschen Datei englisch. Das Skript sucht das Label als vollstaendiges
String-Literal im Quellcode; nur als Teilstring gefundene Labels sind Warnungen mit
Fundstelle und muessen von Hand geprueft werden.

**Zur Laufzeit zusammengesetzte Labels** ("Go Live in <Kanal>", "Fill In Last Code <Code>")
bestehen den Literal-Check nicht: in Anfuehrungszeichen setzen statt Fett, den festen Teil
als Fett-Label ("**Go Live**") schreiben, wenn er als Literal existiert.

**Belege in Geschwister-Paketen** (MalibuDesignKit, MalibuCMIOKit, MalibuLiveKit): Pfad mit
Praefix `external:` relativ zum Ordner neben dem App-Repo, z.B.
`external:MalibuLiveKit/Sources/Code.swift#alphabet`. Aussagen ueber fremden Code ohne
Beleg bleiben draussen.

Auslassungspunkte gehoeren **ausserhalb** der Fettung (`**Add Raw Files**…`), weil der Code
sie oft als `\u{2026}` schreibt und das Label sonst nicht matcht. Der Label-Check gilt
repo-weit: sehr kurze Labels ("Off", "Mode") bestehen trivial, sie von Hand gegen die
richtige Ansicht pruefen.

**Tastenkuerzel und Menues in der deutschen Datei:** Menues, Buttons und Einstellungen
bleiben so, wie die App sie anzeigt (meist Englisch, in Fett). Tastenkuerzel in
Backticks in Symbolschreibweise (`⌘⇧L`), im Text einmal ausgeschrieben, wenn noetig
("Befehl-Umschalt-L"). Dateinamen, Zahlen mit Einheit und Code stehen in Backticks.
Systemlokalisierte Menues (View/Darstellung) nur nennen, wenn die App sie selbst benennt.

**Referenz ohne Tabellen:** "Option, Standard" als Liste schreiben:
`- **Option** — Standard: aus. Wirkung: ...`

## Ablauf

1. Code, Menues, String-Kataloge und Settings lesen; Liste "was die App heute tut" und
   "was sie nicht tut" aufstellen.
2. EN schreiben, Pruefskript laufen lassen und fixen:
   `python3 -I "<studiomalibu-site>/.claude/skills/app-help-docs/check_help_docs.py" <App-Repo-Root> <App-Repo-Root>/docs/help`
3. DE als Uebersetzung (gleiche Struktur), Pruefskript erneut. Gruen = Exit 0.
4. **Gegenlesen (verpflichtend):** Einen Review-Agenten ohne Schreibrechte jede Funktionsaussage
   gegen den Code pruefen lassen ("zu welcher Aussage gibt es keinen Beleg?"). Findings
   einarbeiten und im Frontmatter unter `reviewed:` nachweisen (Datum, was, wie viele Funde).
   Erfahrung aus dem Pilot: nach gruenem Skript fand der Review-Agent noch 14 (Drop) bzw.
   ~62 (Sync) inhaltliche Fehler. Hilfreich: Reviewer parallel nach Dokumentgruppen schneiden
   (3 Fakten-Agenten, ~5 min) plus einer fuer EN/DE-Paritaet; den Brief ohne eigene
   Vermutungen halten; `check_help_docs.py ... --show-lines` gibt die zitierte Zeile aus.
   Haeufigste Fehlerklasse: Belegzeile zeigt auf Kommentar, Leerzeile oder Klammer; bevorzuge
   `pfad#Symbol` (zeilenstabil). Das Skript lehnt Leerzeilen/Klammern ab und warnt bei Kommentaren. Das Skript prueft Existenz, nicht Wahrheit; dieser Schritt ist das eigentliche Gate.
   **Baustein fuer den Review-Prompt:** "Pruefe jede Aussage in diesen Dateien gegen den
   Code. Melde NUR Probleme, nie Lob. Klassen: FALSCH, UNBELEGT, UEBERTRIEBEN (every/always/
   never), VERALTET, FALSCHE BELEGZEILE. Zu jedem Fund Datei, Abschnitt und die richtige
   Stelle im Code." Den Brief ohne eigene Vermutungen halten.
   **Funde, die die App betreffen** (Bug, toter Schalter, falscher App-Text) nicht in der Doku
   verstecken: an die App-Session zurueckmelden und in der Hilfe nur den Ist-Zustand
   beschreiben.
   **Korrigierte Saetze erneut pruefen lassen:** Nach dem Einarbeiten der Funde einen weiteren
   Review-Lauf nur ueber die geaenderten Stellen (Live: 61 Funde, danach noch 5 in den
   Korrekturen selbst). In Dateien, die gerade umgebaut werden (UI-Refactoring), nur
   `pfad#Symbol` als Beleg verwenden.
   **Zwei Review-Runden sind die Regel** (Burn: 1. Runde Sachfehler, 2. Runde Fehler in den
   Korrekturen). Gegen den **ausgelieferten Tag/Commit** pruefen, nicht gegen den Arbeitsstand.
   **Evidence-Syntax:** Mehrere Belege mit Komma trennen. Ein Symbol darf Leerzeichen und
   Kommas enthalten (UI-Text), solange nach dem Komma kein Pfad mit Dateiendung + `:`/`#` folgt.
   Bei Apps mit mehreren Bundles (Host + Plugin) zaehlt die Version des Bundles, das die Hilfe
   beschreibt (`--app-version` setzt sie explizit).
   **Branches:** Die Hilfe beschreibt `main`/die ausgelieferte Version. UI-Umbauten auf
   Branches machen Seiten beim Merge ungueltig; das Gate meldet das beim naechsten Lauf, also
   nach jedem Merge das Skript laufen lassen.
5. Wirkung im UI mindestens einmal selbst nachvollziehen, wenn ein Schritt nicht rein
   aus dem Code folgt; ungeprueft = streichen, nicht abschwaechen.
6. **Meldung an "Knuts Obsidian"** (legt eine Lesekopie unter `Studio Malibu/Hilfeseiten/<App-Name>/` ab,
   Quelle der Wahrheit bleibt dein Repo; du schreibst nicht selbst im Vault). Format der Meldung,
   eine Nachricht pro App: **App-Name** (wie auf der App-Seite, z.B. "Malibu Burn"), **Version**,
   **Verifikationsdatum**, **absoluter Pfad zu docs/help/**, **Liste der Dateien** (en/de).
   Bei Aenderungen der Hilfe dieselbe Meldung erneut.
7. Der Session **"Studio Malibu Webseiten"** per send_message melden: App-Name, Slug,
   Akzentfarbe, Pfade der Dateien. Sie baut `apps/<slug>/help/index.html`
   (`scripts/build_help.py`) und pusht. Bitte nicht selbst in der Website-Repo schreiben.
8. In der App: Help-Menue `<App> Help` oeffnet `https://studiomalibu.de/apps/<slug>/help/`
   (SwiftUI `HelpLink(destination:)` bzw. Menueeintrag + `NSWorkspace.open`).

## Pflege

In die CLAUDE.md der App eintragen:
"Aendert eine Aenderung etwas, das `docs/help/*.md` beschreibt (Beschriftung, Schritte,
Default, Kuerzel, Reifegrad), werden EN und DE im selben Commit angepasst und das
Pruefskript laeuft gruen." Beim Release: Pruefskript ausfuehren; rot = vor dem Release
Doku nachziehen.

## Was das Pruefskript prueft (und was nicht)

Prueft: EN/DE-Paare, Frontmatter inkl. `reviewed`, Evidence je Abschnitt mit existierender
Zeile oder Symbol, **Fett-Labels als exaktes String-Literal im Quellcode**, keine
TODO-verify-Marker, relative Links/Bilder, EN/DE-Strukturgleichheit; warnt bei Versions-Drift
gegenueber project.yml/Info.plist.
Prueft **nicht**: ob eine Aussage inhaltlich stimmt. Das leistet Schritt 4/5.
