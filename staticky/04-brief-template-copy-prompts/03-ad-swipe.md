# Ad Swipe: Competitor Ad → New Template

## Účel

Vezme konkurenčný ad (obrázok) a vyrobí z neho **nový template definition** (`.md` súbor) pre tvoj brand. Template je language-agnostic, layout-only, bez konkrétneho copy.

**Ad-swipe vyrába LEN TEMPLATE.** Nevyrába ad. Nevyrába prompts.json. Nepúšťa scoring agentov. Po vytvorení template-u user pokračuje v štandardnom `/image-ad-generator` workflow:

```
Ad-swipe (template) → Krok 4a Brief → Krok 4b vyber nový template → Krok 4c Copy → Krok 5 Agents → Krok 6 Generation
```

## Vstup

1. Obrázok konkurenčného ad-u
2. Brand pre ktorý sa template vyrába (napr. `moja-znacka`, `expertnavlasy`, `yoopy`)

## Výstup

Nový `.md` súbor uložený do:
```
brands/{brand}/{brand}-templates/{NN}-{slug-name}.md
```
kde `NN` je nasledujúce poradové číslo v sade (existujúce moja-znacka má 01-08, takže ďalší by bol `09-{slug-name}.md`).

## Workflow (2 stages)

### Stage 1 — Deconstruct competitor ad

Načítaj nahraný obrázok a urob štruktúrovanú analýzu. Výstup deconstruction-u si len pre seba (interne) — pomôže ti zostavit template v Stage 2.

#### Layout analysis
```json
{
  "aspect_ratio": "",
  "format_type": "headline | before-after | testimonial | social-proof | us-vs-them | statistics | features-benefits | bullet-points | press | news | ugc | founder-story | carousel | handwriting | negative-marketing | other",
  "composition": {
    "text_position": "top-third | center | bottom-third | left-aligned | right-aligned | overlaid",
    "product_position": "center | left | right | top | bottom | absent | background",
    "product_frame_percentage": "estimated % of frame the product occupies",
    "negative_space": "minimal | moderate | generous",
    "visual_hierarchy": "What the eye reads first, second, third"
  }
}
```

#### Typography extraction
```json
{
  "headline_treatment": {
    "case": "uppercase | lowercase | title case | sentence case",
    "estimated_font_category": "sans-serif geometric | sans-serif humanist | serif modern | serif traditional | slab serif | display | handwritten | monospace",
    "weight": "light | regular | medium | bold | black",
    "alignment": "left | center | right",
    "letter_spacing": "tight | normal | wide | very wide",
    "line_count": "",
    "color": "describe the color"
  },
  "subhead_treatment": "same structure or 'none'",
  "body_treatment": "same structure or 'none'",
  "cta_treatment": {
    "shape": "rounded | pill | sharp corners | no button (text only)",
    "fill": "solid color | outline | ghost",
    "text_case": "uppercase | sentence case",
    "color": "describe fill and text colors"
  }
}
```

#### Color and mood extraction
```json
{
  "background": {
    "type": "solid color | gradient | photograph | texture | pattern",
    "dominant_color": "",
    "secondary_color": ""
  },
  "color_palette": ["list all visible colors"],
  "lighting": "flat | soft natural | dramatic side | overhead | backlit | warm golden | cool blue",
  "mood": "1-3 adjectives describing the emotional feel",
  "energy_level": "quiet and restrained | confident and direct | bold and loud | playful and energetic | premium and elevated | urgent and high-pressure"
}
```

#### Structural roles (count + position only — NIE konkrétny text)
```json
{
  "text_elements_count": "N",
  "elements": [
    {
      "role": "headline | subhead | body | cta | review_text | reviewer | rating | label | proof | offer",
      "position_in_frame": "top-left | center | bottom-right | ...",
      "approximate_word_count": "N (just count, NOT the words themselves)"
    }
  ]
}
```

**Vedome NEZAPISUJ konkrétny text z konkurenčného ad-u.** Berieme štruktúru, nie copy. Copy patrí do Krok 4c.

#### What makes this ad work
```json
{
  "strongest_element": "The single best creative decision in this ad",
  "visual_copy_coherence": "Does the image reinforce the copy's concept? Yes/No and why",
  "scroll_stop_factor": "What would make someone stop scrolling? Rate 1-10",
  "steal_worthy": ["List 1-3 specific structural techniques worth borrowing"]
}
```

---

### Stage 2 — Build template `.md` file

Vyrob súbor podľa štruktúry existujúcich moja-znacka-templates (`brands/moja-znacka/moja-znacka-templates/01-*.md` ako referencia):

```markdown
# {Brand} — Template {NN}: {Format Name}

**1 formát · 1-3 štýly** (podľa toho koľko variácií competitor ad sugeruje)

| Štýl | Názov | Kontext |
|------|-------|---------|
| A | {Style A name} | {1-line context} |

---

## Metadata
- **aspect_ratio:** {z deconstruction}
- **needs_product_images:** true (default) / false ak je layout pure-text
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 160px
- **bottom_safe_zone:** 200px
- **brand_element:** {Wordmark position from deconstruction}

## Product reference rule (CRITICAL)
Never describe product from text. Always: "Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."

---

## Čo tento formát je

{1-paragraph description: čo tento layout dosahuje, kedy ho použiť}

---

## Styles

### Style A: {Name}
{Visual description: BG, product position, lighting, energy. NIE konkrétny text.}

#### Copy template
```
[HEADLINE] — {word count guideline}, {tone hint — napr. "rhetorical question"}
[SUBHEAD] — {word count guideline}, {tone hint}
[CTA] — {brand standard alebo "none"}
```

#### Image generation prompt
```
Reference the attached brand spec card and visual style card for typography STYLE,
colors, and photography direction ONLY. CRITICAL: Do NOT render any text from the
brand spec card or visual style card into the output image — those are style
references, not text content.

Use the attached product image as the primary reference — reproduce the product
EXACTLY as it appears in the photo, do not invent or alter shape, color, labels,
or design.

Create a {ASPECT RATIO} static ad for {BRAND NAME}.

COMPOSITION:
{Detailed layout description from deconstruction — kompozícia, lighting, focal length,
product position, BG. NIKDY konkrétny text z konkurenčného ad-u.}

HEADLINE: "{{headline}}" — {position}, {font weight + size}, {color},
{line count}. Render ONLY the {{headline}} value — do not invent or substitute
alternate text.

SUBHEAD: "{{subhead}}" — {position}, {treatment}. Render ONLY the {{subhead}} value.

CTA: "{{cta}}" — {treatment}. Render ONLY the {{cta}} value.

[Pridaj ďalšie placeholdery podľa štruktúry: {{review_text}}, {{reviewer}},
{{rating}}, {{body}} — len tie ktoré sú v deconstruction]

SAFE ZONES: Top 160px and bottom 200px clear of critical content.

BRAND IDENTITY: {Brand} wordmark per brand spec card, {position from deconstruction}.

FINAL TEXT INVENTORY (the ONLY text that appears in the rendered image):
{list of placeholders + brand wordmark}. Nothing else.

PHOTOGRAPHY DIRECTION: Per visual style card. {Style description from deconstruction}.

MOOD: {Energy level + mood from deconstruction}.
```

#### Variation vectors
- {Vector 1}: {options separated by |}
- {Vector 2}: {options}
- {Vector 3}: {options}

---

## Global rules pre tento formát

- {Rule 1 z deconstruction insights}
- {Rule 2}

### Čo sa vyhnúť
- {Anti-pattern 1}
- {Anti-pattern 2}
```

---

## Pravidlá pre Stage 2 výstup

### 1. Language-agnostic prompt body (KRITICKÉ)

Image generation prompt v template-u **NESMIE** obsahovať konkrétny copy text z konkurenčného ad-u (alebo akýkoľvek iný sample text). Layout descriptions opisujú TYPOGRAFIU (font weight, position, color, line count), nie obsah.

❌ Anti-pattern: `HEADLINE: "{{headline}}" — first line "Pain point question" runs medium`
✅ Správny pattern: `HEADLINE: "{{headline}}" — first line medium weight, second line heavier (split on newline). Render ONLY the {{headline}} value — do not invent or substitute alternate text.`

(Častá chyba — zapíš si ju do `chyby-neopakovat.md` značky.)

### 2. Placeholder konvencia

- **`{{x}}` runtime placeholdery** — pre copy fields, ktoré sa runtime substituujú v `generate_ads.py`:
  `{{headline}}`, `{{subhead}}`, `{{body}}`, `{{cta}}`, `{{review_text}}`, `{{reviewer}}`, `{{rating}}`, `{{verified_tag}}`
  Dot-notation podporovaná: `{{table.left_col_header}}`, `{{icons.0.value}}`
- **`[BRACKETED]` build-time fills** — Claude vyplňuje pri builde z brand context:
  `[BRAND NAME]`, `[ASPECT RATIO]`, `[BRAND COLOR]`, `[VOLUME]`, atď.

### 3. Žiadne ceny ani sezónne odkazy v template prompt body

Cross-brand pravidlo: `prompts.json` nesmie obsahovať €/Kč/Ft/lei/zł v copy fields. Template by tiež nemal sugerovať cenové layoutu (žiadne "PRICE" placeholdery).

### 4. Žiadny copy

Stage 2 výstup neobsahuje **žiadny napísaný copy**. Žiadne sample headliny, žiadne sample CTA texty, žiadne ukážky review-ov. Len structural slots a guidelines (word counts, tone hints).

### 5. Save location

Uloží sa do:
```
brands/{brand}/{brand}-templates/{NN}-{slug-name}.md
```

`NN` = nasledujúce poradové číslo v sade. `slug-name` = krátky kebab-case popis (max 4 slová), napr. `09-split-screen-before-after.md`.

Po uložení **oznám userovi cestu** a inštrukciu:
> Nový template uložený: `brands/{brand}/{brand}-templates/09-split-screen-before-after.md`. Použi ho cez `/image-ad-generator` Krok 4b ako "Brand template" zdroj.

---

## Príklad workflow

**Vstup:** User uploads Caraway cookware ad (pink pan, marble counter, "Cook Without Compromise" headline, "Non-toxic ceramic coating. Naturally nonstick." subhead).

**Stage 1 deconstruction:**
- Format: Headline + product hero
- Composition: product center, headline top-third, subhead below product
- Typography: large bold serif headline white, smaller sans subhead dark
- Color: warm cream BG, pastel pink product, warm domestic lighting
- 3 text elements: headline (4 words), subhead (2 sentences), brand wordmark
- Steal-worthy: generous negative space + warm domestic lighting

**Stage 2 output (uložený do `brands/moja-znacka/moja-znacka-templates/09-product-hero-warm-scene.md`):**

```markdown
# MojaZnačka — Template 09: Product Hero + Warm Scene

**1 formát · 1 štýl**

| Štýl | Názov | Kontext |
|------|-------|---------|
| A | Warm Domestic Hero | Product center, generous negative space, warm domestic lighting |

## Metadata
- aspect_ratio: 4:5
- needs_product_images: true
...

## Styles

### Style A: Warm Domestic Hero

#### Copy template
[HEADLINE] — max 4 slov, claim alebo statement
[SUBHEAD] — 1-2 vety, mechanism alebo positioning
[CTA] — brand standard

#### Image generation prompt
Reference the attached brand spec card and visual style card for typography STYLE...
[CRITICAL guardrail block]
Use the attached product image as the primary reference...

Create a 4:5 static ad for MojaZnačka.

COMPOSITION:
One continuous image filling the entire frame. Background: warm cream surface
with generous negative space. Product (reproduced exactly from reference)
positioned center, sharp, occupying ~30% of frame, warm domestic lighting from
upper-left. Shot at 50mm f/2.8.

HEADLINE: "{{headline}}" — top third, very large bold sans-serif, dark, 1-2
lines. Render ONLY the {{headline}} value — do not invent or substitute
alternate text.

SUBHEAD: "{{subhead}}" — below product, smaller weight, dark, 1-2 lines.
Render ONLY the {{subhead}} value.

CTA: "{{cta}}" — orange pill button, white bold text + arrow, bottom-right.
Render ONLY the {{cta}} value.

SAFE ZONES: Top 160px and bottom 200px clear of critical content.

BRAND IDENTITY: MojaZnačka wordmark per brand spec card, bottom-left corner.

FINAL TEXT INVENTORY: headline + subhead + CTA + MojaZnačka wordmark. Nothing else.

PHOTOGRAPHY DIRECTION: Per visual style card. Generous negative space. Warm
domestic feel — felt like home, not studio.

MOOD: Quiet, premium, accessible. Confident without aggression.
```

**Hotovo.** User dostane správu o uloženej ceste a pokračuje v štandardnom `/image-ad-generator` flow.

---

## Pravidlá

1. **Nikdy nekopíruj copy z konkurenčného ad-u** — ani v deconstruction-e, ani v template-e
2. **Berieme len štruktúru a vizuálny prístup**, nie creative content
3. **Template MUSÍ byť language-agnostic** — žiadny sample text v prompt body
4. **Žiadne agenty v ad-swipe** — agenti bežia až v Krok 5 na vyrobenom ad-e (nie na template)
5. **Žiadny prompts.json output** — ad-swipe vyrába .md template, nie ad entry
6. **Save path je povinný** — vždy `brands/{brand}/{brand}-templates/{NN}-{slug}.md`
7. **Po uložení oznám userovi cestu + next step** (použi v Krok 4b)
