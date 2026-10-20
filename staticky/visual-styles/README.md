# Krok 3b — Vizuálny štýl (art direction vrstva)

Vizuálny štýl je **pomenovaná, znovupoužiteľná art direction vrstva** medzi brandom a copy.

| Vrstva | Čo určuje | Kde žije |
|--------|-----------|----------|
| **Brand** | fonty, farby, logo, CTA, always/never brandu | `brands/<brand>/brand-dna/*.png` (posiela sa ako referenčný obrázok) |
| **Vizuálny štýl** | rendering, svetlo, pozadie, textúra, farebné spracovanie | `visual-styles/<id>.json` ← **tento priečinok** |
| **Copy + layout** | texty, rozloženie, produkt, safe zóny | `prompts-<lang>.json` |

Štýl **nikdy nemení** copy, layout, safe zóny ani identitu produktu. Mení len to, ako scéna vyzerá.

Predtým bola art direction písaná ručne do každého promptu zvlášť — nedala sa znovupoužiť ani merať.

---

## Ako to použiť

### 1. Vyber štýl

```bash
python3 06-image-generation/generate_ads.py --list-styles
```

### 2. Zapíš ho do prompts JSON

Default pre celý ad-set v `_meta`, voliteľný override na jednotlivom banneri:

```json
{
  "_meta": {
    "brand": "Moja značka",
    "visual_style": "retail-offer-card"
  },
  "prompts": [
    { "template_number": 1, "prompt": "..." },
    { "template_number": 2, "visual_style": "memoji-3d", "prompt": "..." }
  ]
}
```

Priorita: `--visual-style` (CLI) → `prompts[].visual_style` (banner) → `_meta.visual_style` (ad-set).

### 3. Generuj ako doteraz

```bash
./run.sh moja-znacka --provider google-batch --templates 1,2
./run.sh moja-znacka --provider google-batch --visual-style memoji-3d   # prebije celú várku (A/B štýlov)
```

Generátor pripojí blok štýlu **na koniec promptu**, aby prebil generické formulácie vyššie,
a k referenčným obrázkom pridá prípadné `ref_images` štýlu (za brand kartami).

**Neznáme ID štýlu = tvrdý fail pred generovaním.** Preklep by inak stál peniaze za celú várku.

---

## Schéma štýlu

```json
{
  "id": "memoji-3d",
  "name": "3D memoji maskot",
  "summary": "Jedna veta — čo to je.",
  "when_to_use": "Kedy tento štýl siahnuť, kedy nie.",
  "prompt_block": "EN text — rendering, svetlo, pozadie, textúra, farebné spracovanie, kompozičný register. Nikdy nie copy ani konkrétne texty.",
  "never": ["čo sa v tomto štýle nikdy neobjaví"],
  "works_with": { "aspect_ratios": ["1:1", "4:5", "9:16"], "needs_product_images": true },
  "ref_images": ["../reference/_refs/memoji-m2"],
  "brands_validated": [],
  "source": "odkiaľ štýl pochádza"
}
```

- **`prompt_block`** je jediné povinné pole. Píše sa po anglicky, v prítomnom čase, konkrétne
  (svetlo, tiene, pozadie, materiál, farebný grading) — nie prídavnými menami typu „modern, premium“.
- **`ref_images`** — súbor alebo celý priečinok, cesta relatívna k `visual-styles/`. Posielajú sa
  **max 2** a sprevádza ich guardrail „look and feel only, nikdy nekopíruj texty ani layout“.
  Neexistujúca cesta sa ticho preskočí, referencie sú voliteľné.
- **`never`** sa do promptu vloží ako jeden riadok `NEVER in this style: ...`.

## Zdieľaná vrstva remesla (`_craft.json`)

Sadzba, rytmus, zarovnanie a ukotvenie sú rovnaké naprieč štýlmi — nepatria do jednotlivého štýlu.
Žijú v `_craft.json` a štýl si ich **zapína** poľom:

```json
{ "id": "botanical-bold", "craft": true }
```

Blok sa potom pripojí za blok štýlu ako samostatná sekcia `--- CRAFT ---`. Čo rieši:

- typografia sa **sadzí, nie kladie** — negatívny tracking, tesný preklad, riadky podobnej dĺžky,
  nikdy osamotené krátke slovo na poslednom riadku
- jedna zarovnávacia hrana a konzistentný vertikálny rytmus, nie vycentrovať všetko
- cenová hierarchia — stará cena menšia a potlačená, nová dominantná, badge ukotvený pri cene
- vyrezaný produkt ukotvený kontaktným tieňom, čistá hrana bez halo a bez zvyšku pozadia
- rovnaké okraje na všetkých štyroch stranách, šírka CTA podľa textového stĺpca, nič neprekrýva produkt

`_craft.json` **nie je štýl** — podčiarkovník ho drží mimo `--list-styles` a nedá sa vybrať cez
`visual_style`. Zapnutý je zatiaľ pri `botanical-bold` a `apple-glass`; `vibrant`
a `colorblock-campaign` ho zámerne nemajú, sú postavené na hotových predlohách.

Ak štýl žiada craft a `_craft.json` chýba, generátor to vypíše a pokračuje bez neho.

---

## Pridanie nového štýlu

1. Nový `<id>.json` v tomto priečinku (id = kebab-case, rovnaké ako názov súboru).
2. Ak má referenčné obrázky, dať ich do `reference/_refs/<id>/` a odkázať cez `ref_images`.
3. Overiť `--list-styles` a jedným `--dry-run` behom skontrolovať `prompt.txt` na výstupe.
4. Po prvej overenej várke doplniť brand do `brands_validated`.

## Čo sa zapisuje na výstup

- `<ad-set>/outputs/<NN>-<template>/visual-style.txt` — ID štýlu, prežije prestavbu manifestu z disku
- `manifest.json` → `visual_styles` (súhrn várky) + `results[].visual_style` (per banner)
