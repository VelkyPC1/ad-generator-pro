# Copy Generation — 40 Templates

Návod na vypĺňanie promptov zo sady 40 generických ad templates (krok 4 workflow).

## Vstup

**Copy polia** (headline, subhead, cta):
- `brands/{brand}/products/{product}/marketing-research/avatar-sheet.md` — jazyk zákazníka, pain points, citáty
- `brands/{brand}/products/{product}/marketing-research/deep-research.md` — overené claims, specs

**Image direction** (background, farby, brand name, product name, setting):
- `brands/{brand}/brand-dna/brand-research-brief.json` — visual_system, primary_color_hex, offer_details
- `brands/{brand}/brand-dna/brand-spec-card.html` — typografia, logo, CTA štýl
- `brands/{brand}/brand-dna/visual-style-card.html` — photography direction, setting, mood

**Template:**
- `template-prompts.md` — zdrojový súbor so všetkými 40 promptmi

## Proces

### 1. Vyber template

Z `template-prompts.md` vyber číslo formátu (01–40). Skopíruj celý prompt pre daný formát.

### 2. Vyplň placeholders

Nahraď všetky `[BRACKETED PLACEHOLDERS]` konkrétnymi hodnotami:

| Placeholder | Zdroj |
|-------------|-------|
| `[YOUR HEADLINE]` | `avatar-sheet.md` — jazyk zákazníka, pain points |
| `[YOUR SUBHEAD]` | `deep-research.md` alebo `brand-research-brief.json` |
| `[YOUR OFFER]` | `brand-research-brief.json` — offer_details |
| `[BACKGROUND]` | `brand-research-brief.json` — visual_system |
| `[PRIMARY BRAND COLOR]` | `brand-research-brief.json` — primary_color_hex |
| `[CONTRAST COLOR]` | `brand-research-brief.json` — secondary_color_hex |
| `[BRAND]` | názov brandu |
| `[YOUR PRODUCT]` | názov produktu |
| `[SETTING]` | `visual-style-card.html` — photography direction |
| `[NAME]`, `[CREDENTIAL]` | `avatar-sheet.md` — reálne citáty zákazníkov |

**Pravidlá:**
- Jazyk zákazníka z `avatar-sheet.md` — nie generický marketing
- Claims overené z `deep-research.md` — nikdy vymyslené specs alebo čísla
- Produkt vždy cez referenčný obrázok — nikdy nepopisuj vzhľad z textu
- Žiadne em dash (—), en dash (–) v renderovanom texte

### 3. Zostav JSON output

Výstup musí byť vždy platný JSON. Copy polia sú **single source of truth** — prompt string odkazuje na ne cez `{{placeholder}}`, nikdy neobsahuje text natvrdo.

```json
{
  "template_number": "[01–40]",
  "template_name": "[názov formátu]",
  "aspect_ratio": "[napr. 4:5]",
  "needs_product_images": true,
  "headline": "[text]",
  "subhead": "[text alebo null]",
  "cta": "[text alebo null]",
  "prompt": "[prompt z template-prompts.md s už použitými {{headline}}, {{subhead}}, {{cta}} placeholdermi — ostatné [BRACKETED] hodnoty vyplnené priamo]"
}
```

**Pravidlo pre prompt string:** Vezmi prompt pre daný formát z `template-prompts.md`. Templaty už používajú `{{headline}}`, `{{subhead}}`, `{{cta}}` syntax priamo — copy-paste **bez transformácie**.

Ostatné `[BRACKETED]` hodnoty (farby, brand name, product name, setting, aspect ratio) vyplň priamo z brand-research-brief.json + format spec.

**Konvencia:**
- `{{x}}` = runtime substitúcia z copy fields (generate_ads.py to nahradí)
- `[X]` = build-time fill (Claude vyplňuje pri builde)

**KRITICKÉ — žiadne sample copy texty v prompt body (language-agnostic):**

Prompt string MUSÍ ostať jazykovo-neutrálny. NIKDY nevkladaj konkrétne hodnoty z `headline` / `subhead` / `cta` / `bullets` / `headline_lines` polí do prompt instructions ako "ukážku" alebo "popis layoutu". AI dostane konfliktný signál (placeholder + hardcoded sample) a niekedy renderuje hardcoded sample namiesto preloženého placeholderu.

❌ Anti-pattern: `HEADLINE: "{{headline}}" — first line "Rýchlo." medium weight, second "Jednoducho." heavier.`

✅ Správny pattern: `HEADLINE: "{{headline}}" — first line medium weight, second line heavier (split on newline character in {{headline}} value). Render ONLY the {{headline}} value — do not invent or substitute alternate text.`

Layout descriptions (font weight, position, color, line count) sú OK. Konkrétne sample texty z copy fields sú NIKDY OK. Pravidlo: pred uložením `prompts-{lang}.json` (default `prompts-sk.json` pre SK source) greppni prompt body na slová z copy fields → ak nájdeš match → refactor.

JSON ide do kroku 5 (Scoring) — Agent 07 číta len copy polia, prompt string neotvára.
