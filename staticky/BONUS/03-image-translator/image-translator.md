# BONUS 03 — Image Translator

Preloží všetky texty v hotovom ad obrázku do zadaných jazykov — okrem textov na produktoch. Vizuál, kompozícia, farby a typografia zostanú nezmenené.

## Podmienka

Vstup musí byť finalizovaný ad obrázok — buď po kroku 08 (Output Check PASS) alebo reálny winner s performance signálom.

## Vstup

- **Obrázok** — hotový ad (PNG/JPG)
- **Jazyky** — zoznam cieľových jazykov (napr. HU, CZ, RO, PL)

## Prompt template

Pre každý jazyk odošli obrázok + tento prompt do generátora:

```
Role: Professional Multilingual Graphic Designer & Translator for [BRAND].

Task: Replace ALL text in this image with its [LANGUAGE] translation, maintaining 100% visual identity.

Translation Rules:
1. TARGET: Translate all headlines, benefits, ingredient lists (outside the product), and CTAs.
2. TERMINOLOGY: Use the established terminology of the product's category in [LANGUAGE] (the words real customers and shops use).
3. EXCLUSIONS: 
   - Do NOT translate or modify text on the product packaging, labels, or bottle. 
   - Keep '[BRAND]' as the brand name.
   - Keep numerical values and ratings (e.g., 4.9/5) in their original format.
4. TONE: Keep the tone of the original copy.

Visual Consistency Rules:
- POSITION: Place translated text at the EXACT coordinates of the original text.
- STYLE: Match font family, weight (bold/italic), and color perfectly.
- SPACING: If [LANGUAGE] text is longer, use tighter kerning or slightly smaller font size. Do NOT overlap other visual elements.
- QUALITY: No blurring or artifacts around the text. The background must remain untouched.

Double-check: Ensure even the small text at the bottom is translated.
```

`[LANGUAGE]` nahraď názvom jazyka (napr. `Hungarian`, `Czech`, `Romanian`, `Polish`).

## Čo sa prekladá / čo nie

| Prekladá sa | Zachováva sa |
|-------------|--------------|
| Headline | Texty na produktovom obale |
| Subhead | Brand name ([BRAND]) |
| Body copy | Loga |
| CTA text | Rating číslo (4,9/5) |
| Speech bubbles / recenzie | Produktový názov na etikete |
| Bullet points | |

## Spustenie

Preklad beží cez `translate_ads.py` — Python skript v `tools/image-ad-generator/BONUS/03-image-translator/`.

```bash
python translate_ads.py --image path/to/ad.png --languages hu,cz,ro,pl --provider google-batch
```

**Parametre:**

| Parameter | Popis | Default |
|-----------|-------|---------|
| `--image` | Zdrojový obrázok (PNG/JPG) | povinné |
| `--languages` | Kódy jazykov: `hu,cz,ro,pl,sk,de,...` | povinné |
| `--provider` | `fal` / `google` / `google-batch` | interaktívny výber |
| `--output-dir` | Výstupný priečinok | `translations/` vedľa zdroja |
| `--aspect-ratio` | Pomer strán (musí zodpovedať zdroju) | `9:16` |
| `--dry-run` | Ukáže prompty bez volania API | — |

**Podporované kódy jazykov:** `sk`, `hu`, `cz`/`cs`, `ro`, `pl`, `de`, `en`, `hr`, `bg`, `rs`, `si`, `uk`, `it`, `es`, `fr`, `nl`, `pt`, `sv`, `no`, `da`, `fi`, `el`, `tr`

**Default provider pre produkciu: `google-batch`** (~$0.034/img, 50% zľava, trvá až 24h).
Keys sa načítajú automaticky z `jozef/keys/.env`.

## Postup

1. Skontroluj vstupný obrázok — musí byť finálny (Output Check PASS)
2. Spýtaj sa na cieľové jazyky ak neboli zadané
3. Zisti aspect ratio zdroja (1080x1920 = 9:16, 1080x1350 = 4:5, 1080x1080 = 1:1) a použi `--aspect-ratio`
4. Spusti `translate_ads.py` s príslušnými parametrami
5. Skontroluj výstupy — texty na produkte nesmú byť zmenené
6. Ak generátor zmení produkt → pridaj do promptu: `"Do NOT change any text or design on the product packaging."`

## Output location

```
brands/{brand}/brand-dna/ads/{date}-{format}/translations/
├── {slug}-hu.png
├── {slug}-cz.png
├── {slug}-ro.png
└── {slug}-pl.png
└── gallery.html        ← automaticky vygenerovaná galéria
```

## Poznámky

- Skript posiela obrázok ako `inlineData` (image-to-image) — nie len text prompt
- Rating číslo (napr. 4,9/5) — zachovaj formát, neprekladaj
- Pre iný výstupný priečinok (napr. pri produkte): `--output-dir brands/{brand}/products/{product}/ads/translations/`
