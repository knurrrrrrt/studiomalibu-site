# Scrollytelling-Rezepte

Drei fertig durchdachte Patterns, je eins pro MalibuSync-Richtungsvorschlag vom
2026-09-28 in der "Knut webseite"-Session. Jedes Rezept ersetzt den statischen
Hero-Aufbau des jeweiligen Vorschlags durch eine scroll-gekoppelte Version des
gleichen Workflows: **Import -> Match -> FCP-Export**. Codegerueste, keine
fertigen Seiten -- Klassennamen und Struktur beim Ziehen an die tatsaechliche
Seite anpassen. Nav-Offset (~112px, siehe SKILL.md) in jedem `start` einrechnen.

Referenz-Artefakte (Ausgangszustand, statisch):
- Bento/Blau: https://claude.ai/artifact/9tH3P4vPUPUcaeZKgPGpX6
- Console/Raw: https://claude.ai/artifact/1YMZkCb5BDUgnvm9zeNRCq
- Studio/Warm: https://claude.ai/artifact/PgQpUXKsuAXB1ZC5s6iCd9

---

## 1. Bento/Blau -> Card-Stack-Reveal

Die drei ueberlappenden Fenster-Karten (`.card.c1/.c2/.c3` in der Direction-1-
Vorlage) starten auseinandergezogen/unsichtbar und fliegen nacheinander in ihre
finale gestapelte Position -- synchron zu drei Scroll-Abschnitten, die auch als
Textstationen neben dem Stack eingeblendet werden.

```html
<div class="scrollytell" style="height:300vh">
  <div class="stack-pin"> <!-- wird gepinnt -->
    <div class="stage-copy">
      <p data-stage="0">Zwei Ordner rein.</p>
      <p data-stage="1">MalibuSync matcht automatisch.</p>
      <p data-stage="2">Fertige FCPXML raus.</p>
    </div>
    <div class="stack">
      <div class="card c1">…Import…</div>
      <div class="card c2">…Match…</div>
      <div class="card c3">…FCP-Export…</div>
    </div>
  </div>
</div>
```

```js
gsap.set([".card.c1", ".card.c2", ".card.c3"], {opacity: 0, y: 40});
gsap.set('[data-stage="1"], [data-stage="2"]', {opacity: 0});

const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".scrollytell",
    start: "top top+=112",   // Nav-Offset
    end: "bottom top",
    scrub: 1,
    pin: ".stack-pin",
  },
});

tl.to(".card.c1", {opacity: 1, y: 0, duration: 1})
  .to('[data-stage="0"]', {opacity: 0, duration: 0.3})
  .to(".card.c2", {opacity: 1, y: 0, duration: 1}, "<")
  .to('[data-stage="1"]', {opacity: 1, duration: 0.3}, "<")
  .to('[data-stage="1"]', {opacity: 0, duration: 0.3})
  .to(".card.c3", {opacity: 1, y: 0, duration: 1}, "<")
  .to('[data-stage="2"]', {opacity: 1, duration: 0.3}, "<");
```

Reduced Motion: alle drei Karten direkt sichtbar, kein `pin`, Textstationen als
normale untereinanderstehende Absaetze (= aktueller statischer Zustand von
Direction 1).

---

## 2. Console/Raw -> Log-Playback

Die Sync-Log-Zeilen (`.console .ln` in der Direction-2-Vorlage) erscheinen nicht
mehr gleichzeitig, sondern eine nach der anderen, an die Scroll-Position
gekoppelt -- wirkt wie ein live mitlaufendes Terminal statt einem statischen
Screenshot.

```html
<div class="scrollytell" style="height:250vh">
  <div class="console-pin">
    <div class="console">
      <div class="ln" data-i="0">…</div>
      <div class="ln" data-i="1">…</div>
      <!-- ... alle Log-Zeilen aus Direction 2 ... -->
    </div>
  </div>
</div>
```

```js
const lines = gsap.utils.toArray(".console .ln");
gsap.set(lines, {opacity: 0});

ScrollTrigger.create({
  trigger: ".scrollytell",
  start: "top top+=112",
  end: "bottom top",
  scrub: 1,
  pin: ".console-pin",
  onUpdate: (self) => {
    const active = Math.floor(self.progress * lines.length);
    lines.forEach((el, i) => gsap.to(el, {opacity: i <= active ? 1 : 0, duration: 0.2}));
  },
});
```

Reduced Motion: alle Zeilen sofort sichtbar (= aktueller statischer Zustand von
Direction 2), kein `pin`.

---

## 3. Studio/Warm -> Framed-Image-Swap

Das einzelne gerahmte Bild (`.frame-inner` in der Direction-3-Vorlage) blendet
beim Scrollen durch die drei Workflow-Stationen -- ruhiger getaktet als die
anderen beiden Rezepte (weniger Bewegung pro Scroll-Strecke, passend zum
"editorial/calm"-Charakter dieser Richtung). Keine bewegten Teile, nur Crossfade
von Bildinhalt + Caption.

```html
<div class="scrollytell" style="height:250vh">
  <div class="frame-pin">
    <div class="frame">
      <div class="frame-inner" data-scene="0">…Import…</div>
      <div class="frame-inner" data-scene="1">…Match…</div>
      <div class="frame-inner" data-scene="2">…FCP-Export…</div>
    </div>
    <div class="frame-cap" data-caption>Zwei Ordner rein.</div>
  </div>
</div>
```

```js
const scenes = gsap.utils.toArray("[data-scene]");
const captions = ["Zwei Ordner rein.", "MalibuSync matcht automatisch.", "Fertige FCPXML raus."];
gsap.set(scenes.slice(1), {opacity: 0});

const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".scrollytell",
    start: "top top+=112",
    end: "bottom top",
    scrub: 1.2,          // traeger als die anderen beiden Rezepte
    pin: ".frame-pin",
    onUpdate: (self) => {
      const i = Math.min(scenes.length - 1, Math.floor(self.progress * scenes.length));
      document.querySelector("[data-caption]").textContent = captions[i];
    },
  },
});

tl.to(scenes[0], {opacity: 0, duration: 1})
  .to(scenes[1], {opacity: 1, duration: 1}, "<")
  .to(scenes[1], {opacity: 0, duration: 1})
  .to(scenes[2], {opacity: 1, duration: 1}, "<");
```

Reduced Motion: nur das erste `[data-scene]` zeigen, Caption statisch (= aktueller
statischer Zustand von Direction 3), kein `pin`.
