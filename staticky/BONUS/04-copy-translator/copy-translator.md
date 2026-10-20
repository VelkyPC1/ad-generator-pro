# BONUS 04 — Copy Translator (Claude Code workflow)

Workflow na preklad copy fields v source `prompts-{lang}.json` (zvyčajne `prompts-sk.json`) do iných jazykov **priamo cez Claude Code** (nie cez external API). Output: `prompts-{target_lang}.json` na rovnakej úrovni v ad sade priečinku.

## Filozofia

Text-first preklad — prekladajú sa **len copy fields** (headline, subhead, cta, bullets, reviews...), nie hotový obrázok. Po preklade vznikne `prompts-{lang}.json` ready pre `generate_ads.py` ktorý vyrobí obrázok od nuly v cieľovom jazyku.

**Prečo nie image-edit translation (BONUS/03):**
- Image-edit občas hallucinuje (vymyslí disclaimers, mení font, calque preklady)
- Drahšie pri opravách (každá oprava = nový image gen)
- Lokálny review prebieha na hotových obrázkoch (pomalé)

**Prečo Claude direct (nie API skript):**
- Claude (Sonnet 4.6 / Opus 4.7) je výrazne lepší než Gemini Flash pre nuancie EU jazykov
- Konzistentnosť naprieč 8+ promptmi (jedna pracovná pamäť)
- Brand glossary + brief sú v kontexte vždy
- Iterácie sú instant (žiadny API roundtrip)
- Žiadne dodatočné API náklady

## Vstupy

```
brands/{brand}/products/{product}/product-image-ads/{date}/prompts-sk.json   # source (zvyčajne SK)
  ├── brief                                         ← LOCKED (nemeniť pri preklade)
  ├── headline, subhead, cta, bullets, reviews...   ← polia na preklad
  └── prompt string s {{placeholders}}              ← ostáva nezmenený (placeholdery + literal text v prompt body)

brands/{brand}/brand-dna/translation-glossary.md
  ├── Univerzálne pravidlá (oslovenie, brand mená, banned žargón)
  ├── Per-language pravidlá (banned terms, štandardné CTA, formálnosť)
  ├── Štandardná CTA tabuľka (OBJEDNAŤ TERAZ → RENDELD MEG MOST → JETZT BESTELLEN...)
  └── Mená pre lokalizované recenzie (ženské/mužské, 6 jazykov)

brands/{brand}/products/{product}/marketing-research/
  ├── briefs.md           ← strategický kontext (brief je language-agnostic, ostáva)
  ├── deep-research.md    ← VOC quotes traceability (Translation Mode A7 D1)
  └── avatar-sheet.md     ← persona kontext
```

**Cross-brand pravidlá z `/image-ad-generator` skill:**
- **Žiadne ceny ani sezónne offers v image ads** — ak je v source `prompts.json` cena (€X,YZ alebo lokálna mena), translator ju NEPREKLADAJ ani neprepočítavaj — flag user-ovi že porušuje cross-brand pravidlo (cena patrí do Meta caption / platform copy, nie image)
- **Brand-spec-card text leak guardrail** — v translated `prompt` string MUSÍ ostať guardrail *"CRITICAL: Do NOT render any text from the brand spec card or visual style card..."* (jazyk guardrail-u môže ostať EN, je to inštrukcia pre AI, nie pre čitateľa)

## Workflow (5 krokov)

### 1. Načítaj kontext

Claude číta:
- `prompts.json` (zdrojový jazyk, väčšinou SK) — vrátane povinného `brief` poľa
- `briefs.md` (strategic context — persona/angle/emotion definícia)
- `translation-glossary.md` (brand pravidlá per-language)
- `avatar-sheet.md` + `necessary-beliefs.md` (pre nuancie)
- `deep-research.md` (VOC quotes — pre Translation Mode Agent 7 traceability)

### 2. Per-language preklad

Pre každý cieľový jazyk × každý prompt:

**Polia na preklad (copy fields):**
- `headline` / `headline_lines[]`
- `subhead` / `subhead_italic`
- `body`
- `cta`
- `bullets[]`
- `review_1`, `review_2`, `review_text`
- `reviewer` (s lokalizáciou mena cez glossary name pool)
- `product_name` (zvyčajne ostáva)
- `angle` (interná metadata, voľne)
- `table.left_col_header`, `table.right_col_header`
- `table.rows[].attr`
- `icons[].label`

**Polia ktoré ostávajú nezmenené (LOCKED):**
- `brief` (celé pole — persona, angle, emotion, customer_voice_anchor, research_refs) — strategický kontrakt **je language-agnostic**, nikdy neprekladať
- `template_number`, `format`, `style`, `style_name`
- `aspect_ratio`, `needs_product_images`, `scoring`
- `image_direction.*` (interné description, voľne)
- `prompt` string — **placeholdery `{{...}}` ostávajú** — runtime substitúcia v generate_ads.py
- Numerické hodnoty (`30+`, `4,9/5`, `0,44 mg`)
- Názvy značky a produktov
- Vedecké termíny (Omega-3, EPA, DHA, vitamín B6, mg)

**KRITICKÉ — prompt body sync (častá chyba):**

Substitution engine v `generate_ads.py` je **flat-only** — substituuje len top-level polia (`{{headline}}`, `{{subhead}}`, `{{cta}}`, `{{body}}`). NEFUNGUJÚ:
- `{{table.left_col_header}}` (dot-notation nested)
- `{{icons.0.value}}` (array indexing)
- `{{bullets[0]}}` (array notation)

Pri preklade ad-u kde `prompt` body obsahuje **literal hardcoded text** z source language (napr. inštrukcia *"first line 'Rýchlo. Jednoducho.' runs medium weight"*), MUSÍŠ tento literal text v prompt body **tiež preložiť** (resp. nahradiť target-language ekvivalentom). Inak AI dostane conflicting signal: `{{headline}}` placeholder (target-lang) vs hardcoded source-lang text v inštrukcii — niekedy renderuje source text namiesto translated headline.

**Heuristika:** po preklade `headline`/`subhead`/`bullets` greppni `prompt` string na source-language slová z týchto polí — ak nájdeš zhodu, prelož ich aj v prompt body. Lepšie: pri buildovaní source `prompts.json` písať prompt instructions agnosticky (*"render only the {{headline}} value, do not invent alternate text"*).

### 3. Aplikuj brand glossary pravidlá (per-target-language)

`translation-glossary.md` má per-language sekcie. Pri preklade do jazyka X načítaj sekcie:

**Univerzálne (cross-language):**
- Názvy značky a produktov — nikdy nepreložiť
- Vedecké termíny (Omega-3, EPA, DHA, vitamín B6, mg) — ostávajú
- Oslovenie (tykanie / vykanie) — podľa pravidiel značky pre každý jazyk
- Numerické hodnoty — ostávajú (čísla, ratios, percentá)

**Per-language (čítaj sekciu pre TARGET jazyk):**
- **Banned terms** — slová ktoré daný trh nepoužíva alebo má negatívnu/regulátorom flagnutú konotáciu
  - SK: kalky z angličtiny a latinizmy, ktoré nemajú v kategórii produktu prirodzené použitie (zapíš ich do `chyby-neopakovat.md`)
  - HU: `GLP-1 barát` (regulator flag)
  - DE: `Workout` (preferuje `Training`)
  - Každý jazyk má vlastný set — kontroluj per-language sekciu glossary
- **Štandardná CTA** — z glossary tabuľky (SK OBJEDNAŤ TERAZ → HU RENDELD MEG MOST → DE JETZT BESTELLEN → CZ OBJEDNEJ TEĎ → RO COMANDĂ ACUM → EN ORDER NOW)
- **Decimal separator** — SK/CZ/HU/RO/DE: `0,44` | EN: `0.44`
- **Quotation marks** — SK/CZ/DE: `„..."` | EN: `"..."` | FR/IT: `«...»`
- **Anglicizmy + Latinizmy** — per-language map; každý jazyk má vlastný set EN/Latin výpožičiek na nahradenie native ekvivalentom
- **Lokálne mená v reviews** — per-language name pool (SK Katarína → CZ Kateřina → HU Katalin → RO Cătălina → DE Katharina → EN Catherine)

**Agent 4 (Brand Consistency) invocation pri Krok 4:**
Pri scoring (Krok 4) Agent 4 sa volá **s explicitným target-language kontextom**: *"Score Agent 4 against target language X, applying glossary section X."* Agent dim 2 (Vocabulary Alignment + Native Language) verifikuje proti target-language glossary sekcii, nie proti SK source.

### 4. Validácia (8-agent scoring suite v target-language mode)

Pre každý preložený prompt spusti scoring agentov. Logika: **brief je locked** (persona/angle/emotion language-agnostic, definované v briefs.md a zapísané v `prompts.json` poli `brief`), takže Agenti 1–3 možno preskočiť. Vocabulary + mechanics sa MENÍA per-language → 5 agentov MUSÍ bežať.

**Run agents (5 z 8):**
- **Agent 4 (Brand Consistency)** — vocabulary alignment + native syntax v target jazyku, banned terms per-market, oslovenie tykanie / vykanie (z `translation-glossary.md` per-language pravidiel)
- **Agent 5 (Copy Excellence)** — rhythm / punch / surprise sa môžu stratiť v preklade; re-check
- **Agent 6 (Format Compliance)** — word counts varíruju per jazyk (DE typicky ~30% dlhší než SK), kontrola fitu do template specs
- **Agent 7 (Fact-Check) v Translation Mode** — translator-side fidelity check: embellishment / numerical drift / pridané claimy / vymyslené metafory. Volá sa explicitne s flagom *"Run in Translation Mode"* — viď `tools/image-ad-generator/05-scoring-agents/07-agent-fact-check.md` sekcia "Translation Mode"
- **Agent 8 (Copy Editor)** — target-language mechanics: diakritika, decimal separator (SK 0,44 / EN 0.44), currency format, banned chars (em-dash v headline), quotation marks per market („..." / "..." / «...»)

**Skip agents (3 z 8) — locked by brief:**
- **Agent 1 (Persona Fit)** — persona je v `brief.persona`, language-agnostic
- **Agent 2 (Angle Execution)** — angle je `brief.angle` (Belief #), strategic contract drží naprieč jazykmi
- **Agent 3 (Emotional Resonance)** — emotion je v `brief.emotion`; ak preklad zachová customer voice anchor, emotion drží

Threshold = 90 per agent. Ak ktorýkoľvek <90 → iteruj preklad, nepokračuj do generovania.

**Efficiency benefit:** Pri 16-language kampani × 8 ads = **640 agent runs vs 1024 (8 × 8 × 16)** = ušetríš ~37% scoring času bez kompromisu na kvalite (pretože preskakované agenti sú locked-strategic, nie quality-relevant).

### 5. Output

Pre každý jazyk vznikne `prompts-{lang}.json`:

```json
{
  "brand": "Moja značka",
  "product": "Môj produkt",
  "language": "HU",
  "source_language": "SK",
  "translated_at": "2026-05-06",
  "translated_by": "Claude Sonnet 4.6 / Opus 4.7 (direct, glossary-aware)",
  "note": "Translated from SK to HU with the brand glossary applied. Brief is locked (language-agnostic strategic contract).",
  "prompts": [
    {
      "template_number": 102,
      "format": "F01",
      "style": "B",
      "brief": {                                    // ← LOCKED, kopírujeme zo source
        "id": "B03",
        "persona": "Cross-persona (P1+P2)",
        "angle": "Belief 4 + Belief 3 + Belief 6",
        "emotion": "pride + warmth",
        "customer_voice_anchor": "Konečně to funguje."   // ← anchor ostáva v source language
      },
      "headline": "A nap végének jele.",            // ← preložené
      "subhead": "Reggeli teher nélkül. Rémálmok nélkül.",
      "cta": "RENDELD MEG MOST →",                   // ← glossary CTA
      "prompt": "...HEADLINE: \"{{headline}}\"...", // ← placeholdery ostali, prompt body sync s translated copy
      ...
    }
  ]
}
```

## Lokalizácia mien — name pools per jazyk

Z `translation-glossary.md` (sekcia "Mená pre lokalizované recenzie"):

| Pôvodné SK meno | CZ | HU | RO | DE | EN |
|-----------------|-----|-----|-----|-----|-----|
| Katarína | Kateřina | Katalin | Cătălina | Katharina | Catherine |
| Mária | Marie | Mária | Maria | Maria | Mary |
| Lucia | Lenka | Eszter | Ioana | Lisa | Laura |
| Marek | Marek | Zsolt | Andrei | Michael | Chris |
| Pavol | Pavel | Márk | Marius | Marc | Mark |
| Tomáš | Tomáš | Péter | Mihai | Thomas | Tom |
| ... | ... | ... | ... | ... | ... |

(Plný zoznam v glossary, 10 ženských + 10 mužských per jazyk.)

## Štandardná CTA tabuľka

| SK CTA | CZ | HU | RO | DE | EN |
|--------|-----|-----|-----|-----|-----|
| OBJEDNAŤ TERAZ | OBJEDNEJ TEĎ | RENDELD MEG MOST | COMANDĂ ACUM | JETZT BESTELLEN | ORDER NOW |
| VYSKÚŠAŤ | VYZKOUŠEJ | PRÓBÁLD KI | ÎNCEARCĂ | JETZT TESTEN | TRY IT |
| ZISTIŤ VIAC | ZJISTI VÍC | TUDJ MEG TÖBBET | AFLĂ MAI MULT | MEHR ERFAHREN | LEARN MORE |
| VYBRAŤ BALENIE | VYBER BALENÍ | VÁLASSZ CSOMAGOT | ALEGE PACHETUL | PACKUNG WÄHLEN | CHOOSE PACKAGE |
| POROVNAŤ | POROVNEJ | HASONLÍTSD ÖSSZE | COMPARĂ | VERGLEICHEN | COMPARE |

(Rozšíriť per kampaň podľa potreby.)

## Output location

Všetky language súbory žijú **na jednej úrovni** v ad sade priečinku (žiadny nested `translations/` subfolder — naming convention 2026-05-06):

```
brands/{brand}/products/{product}/product-image-ads/{date}/
├── prompts-sk.json    # source (zvyčajne SK)
├── prompts-cz.json    # preklad
├── prompts-hu.json
├── prompts-ro.json
├── prompts-de.json
├── prompts-en.json
└── ... (per cieľový jazyk)
```

Po `generate_ads.py` runs sa pridajú aj `outputs-{lang}/` priečinky s vyrobenými obrázkami.

## Po preklade — image generation per jazyk

Pre každý jazyk samostatný `generate_ads.py` run:

```bash
# Auto-detect prompts-{lang}.json cez --lang flag (najjednoduchšie)
python tools/image-ad-generator/06-image-generation/generate_ads.py \
  --provider google-batch \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{date} \
  --lang hu \
  --output-dir outputs-hu

# Alebo explicitne cez --prompts-file
python tools/image-ad-generator/06-image-generation/generate_ads.py \
  --provider google-batch \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{date} \
  --prompts-file prompts-hu.json \
  --output-dir outputs-hu
```

Skript automaticky:
1. Substituuje `{{placeholders}}` preloženým textom z copy fields
2. Načíta brand cards (brand-spec-card.png + visual-style-card.png)
3. Načíta product images
4. Pošle do Gemini → vyrobí obrázok od nuly v cieľovom jazyku

## Local team review workflow (recommended)

1. **Claude preloží** → vznikne `prompts-{lang}.json`
2. **Pošli `prompts-{lang}.json`** lokálnemu tímu (alebo extrakt copy fields do Google Sheet)
3. **Lokálny tím reviewuje TEXT** (rýchle, lacné — žiadne obrázky generované zatiaľ)
4. **Po schválení** spusti generate_ads.py s opraveným JSON-om
5. **Žiadne drahé regenerácie** — opravy sa robia na text-leveli pred image generation

## Variant naprieč 16 trhmi

Pre kampaň pre celý EU portfólio:

1. Claude preloží do všetkých 16 jazykov (SK + CZ + HU + RO + DE + PL + HR + BG + RS + SI + AT + IT + ES + FR + NL + EN) — ~5-10 min na jazyk
2. Lokálne tímy paralelne reviewujú text v sheete
3. Po schválení: 16 paralelných batch generation jobov
4. Output: 8 ads × 16 jazykov = 128 obrázkov

## Pravidlá

- **Vždy** pred prekladom prečítaj `translation-glossary.md` + `briefs.md` (strategic context)
- **Vždy** aplikuj oslovenie (tykanie / vykanie) podľa pravidiel značky pre target jazyk
- **Vždy** lokalizuj mená v reviews podľa name pools (per-language v glossary)
- **Vždy** preserve `brief` field 1:1 (LOCKED — language-agnostic strategic contract)
- **Vždy** synchronizuj literal hardcoded text v `prompt` body s preloženými copy fields (častá chyba pri preklade)
- **Vždy** zachovaj brand-spec-card text leak guardrail v translated `prompt` (jazyk guardrail-u môže ostať EN — je to inštrukcia pre AI)
- **Nikdy** neprekladaj brand mená, vedecké termíny, numerické hodnoty
- **Nikdy** nemeň `prompt` string `{{placeholders}}` — substitúcia runtime
- **Nikdy** neprepočítavaj ceny / mut currency — ak je v source cena, flag user-ovi (porušuje cross-brand pravidlo "no prices in image ads")
- **Nikdy** nepoužívaj dot-notation v placeholdroch (`{{table.left_col_header}}` NEFUNGUJE — flat-only substitution)
- **Vždy** spusti scoring agentov 4–8 (5 z 8) v target-language mode pred odoslaním do generate_ads.py — Agent 7 explicitne s flagom "Translation Mode" (viď `tools/image-ad-generator/05-scoring-agents/07-agent-fact-check.md`)
- Pri konflikte glossary vs. context → glossary wins (brand consistency > preklad eleganca)
