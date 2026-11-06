# SESSION_STATE — studiomalibu-site (kuratiert, 2026-11-06)

Repo: `Web/studiomalibu-site`, Branch `main` == `origin/main` (letzter Commit `3a26f9f`). Vercel deployt bei Push (Deploy nicht geprueft).

## Aufgabe dieser Session (Okt/Nov 2026)
Pflege der Studio-Malibu-Site auf Zuruf von Knut: Film Craft, Ideas, Projects, Talent Pool, Hilfeseiten.

## Erledigt (alles gepusht)
- **Film Craft**: This-Guy-Edits-Video `jvCPTeW3U0M` + 14 weitere Theorie-Videos (382 Videos gesamt, 46 TGE). Daten in `film-craft/index.html` (`<script id="videoData">`).
- **Talent Pool versteckt** (reversibel): Kachel in `index.html` auskommentiert, Eintrag in `nav.js` auskommentiert, `experts/index.html` noindex. Zum Reaktivieren die Kommentare entfernen.
- **Ideas** (`ideas/index.html`, `requestData`): 27 Eintraege auf Knuts Abhak-Liste gestrichen, 45 uebrig; gegen FCP 12.4 (Stand Okt 2026) geprueft: 1 fixed / 3 partial / 7 third party / 34 open, `fcpUpdate`-Notizen zu Drittanbietern und eigenen Apps (MalibuSync, Malibu Live, MalibuReview).
- **Projects** (`projects/index.html`, `PROJECTS`): neu "Das verrückte Labyrinth" (2028, Platzhalter-Poster = Ravensburger-Box, quer; Knut: so lassen), Poster Das Geschenk (Netflix, sauber), Poster "Mein Bester Freund, seine Freundin und ich" (Netflix, alte PNGs geloescht).
- **MalibuClip 2.11.0**: `apps/malibuclip/help/index.html` mit `scripts/build_help.py` aus `Malibu Clip/docs/help` neu gebaut, Versionsstrings in `apps/malibuclip/index.html` 2.8.1 -> 2.11.0 (`3a26f9f`).

## Offen / naechste Schritte (Backlog)
1. **Frage an Knut offen**: "Mein Bester Freund, seine Freundin und ich" steht auf der Site mit Jahr 2025, Netflix-Start war 2026-08-14. Auf 2026 setzen? (Karte rutscht in der Sortierung nach oben.)
2. Labyrinth-Platzhalter-Poster ersetzen, sobald es ein offizielles Hochkant-Plakat gibt.
3. Vercel-Deploy der letzten Pushes nicht verifiziert.
4. Ideas: einige Bugs brauchen echtes FCP-Testen (nur per Release-Notes geprueft).
5. Weitere This-Guy-Edits-Kandidaten (Rest der Liste in Scratchpad `tge.txt`, geht mit Session verloren).
6. MalibuScreener-Deploy (Branch `malibuscreener-discontinued` in `Web/Knut webseite`) bleibt gesperrt bis Knuts Ja im Codebook-Chat.
7. Alter Plan `~/.claude/plans/glistening-brewing-dongarra.md` (App-Seiten Bento/Blau, Polar-Kauflinks) ist nicht Teil dieser Session-Arbeit; Stand dort unklar.
8. `scripts/notion_site_sync.py` braucht Token `~/.malibu_credentials/notion_website_sync_token.txt` (existiert nicht).

## Lokal liegende, NICHT committete Dateien (4)
- `.claude/launch.json` (Preview-Server `python3 -m http.server 8099`) — nuetzlich, klein; nur lokal behalten oder bei Gelegenheit committen.
- `.claude/skills/design-inspiration/` und `.claude/skills/scrollytelling/` — Skills (SKILL.md, Referenzen); `app-help-docs` liegt dagegen schon getrackt. Wichtig, falls diese Skills gebraucht werden; Commit-Entscheidung bei Knut.
- `SESSION_STATE.md` — diese Datei.

## Gotchas
- Netflix-Poster: og:image ist nur 16:9-Still; `boxshot300` (300x420) steht im Titel-Seiten-JSON, oft nur in den Related-Listen anderer Titel. Immer das Bild ansehen (Spieleabend-Verwechslung).
- Poster-Pipeline: sharp jpg q90 + Blur-Variante (x1.15, GaussianBlur 25, brightness 0.54, q85) in `projects/posters/blur/`.
- Notion-Public-Page ist virtualisiert: Vergleich nur ueber normalisierten Text nach vollem Scrollen/"Load more groups".
- macOS `sed -i` braucht `''`; JSON-Edits per Python-Roundtrip mit `ensure_ascii=False` und Asserts.
- Hilfeseiten bauen: `build_help.py --slug --name --accent --ink` mit allen `--en/--de` Paaren (Reihenfolge ueber Frontmatter `order`); Clip: `#B968FF`, ink `#14041f`. Danach Versionsstrings in `apps/<slug>/index.html` nachziehen.
- Peer-Sessions sagen "Hilfeseiten neu bauen" -> hier in dieser Session (Webseiten), nicht in der App-Session.
