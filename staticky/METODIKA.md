# Generátor statických bannerov — metodika

Systém na produkciu AI statických reklám (Meta / Google). Vstupom je značka + produkt, výstupom hotový banner
(default 4:5, 1080×1350) s copy a vizuálom v štýle značky, voliteľne preložený do ďalších jazykov.
Formáty vychádzajú z verejnej metodiky Motion Foundations (40 recipe cards v `04-brief-template-copy-prompts/`).

> **Kľúčový princíp:** *Brand DNA prvé, AI druhé. Stratégia raz, execution často. Text-first lokalizácia.*

---

## 4 vrstvy systému

| Vrstva | Čo to je | Ako často sa mení |
|---|---|---|
| **1. Brand DNA** | tón, vizuálny štýl, glosár, „chyby neopakovať" | raz na značku |
| **2. Produktový research** | 5 základných dokumentov vrátane `briefs.md` (10–15 strategických briefov) | raz na produkt |
| **3. Ad-set** | brief → template → copy → hodnotenie → generovanie → vizuálna kontrola | často |
| **4. Jazyky** | `prompts-{jazyk}.json` + kratšie hodnotenie + review lokálnym tímom | voliteľne |

Vrstvy 1 a 2 sú jednorazová investícia, vrstva 3 je rýchla opakovaná výroba, vrstva 4 lacné škálovanie na ďalšie trhy.

---

## Postup

### Krok 0 — Kontext
Zisti značku, produkt a úlohu (nový banner / ad-swipe / multiply / animácia) a načítaj `brands/{značka}/brand-dna/`
(tón, glosár, `chyby-neopakovat.md`).

### Krok 1 — Brand research
Ak chýba `brand-dna/brand-research-brief.json`, spusti prompt z `01-brand-research-prompt/`.

### Krok 2 — Brand karty
Ak chýbajú `brand-spec-card.png` a `visual-style-card.png`, vyplň HTML šablóny z `02-brand-cards/` a ulož ich ako PNG.
Karty sa posielajú AI ako referenčné obrázky pri **každom** generovaní — bez nich nie je značka konzistentná.

### Krok 3 — Produktový research
`brands/{značka}/products/{produkt}/marketing-research/`:

| Súbor | Účel |
|---|---|
| `deep-research.md` | doslovné citáty zákazníkov (review mining) |
| `avatar-sheet.md` | kto je zákazník — problémy, túžby, jazyk |
| `offer-brief.md` | unikátny mechanizmus, big idea, ponuka |
| `necessary-beliefs.md` | presvedčenia, ktoré zákazník potrebuje pred nákupom |
| `briefs.md` | **10–15 strategických briefov** (persona × presvedčenie × emócia) |

Ak chýbajú, použi postup z `03-product-research/marketing-research/`.

### Krok 4 — Brief → template → copy

**4a — Brief.** Z `briefs.md` vyber brief (alebo definuj vlastný). Brief zamkne: personu, uhol (presvedčenie),
emóciu a citát zákazníka. Brief je nezávislý od jazyka — pri preklade sa nemení.

**4b — Template.** Vyber formát:

| Zdroj | Kedy |
|---|---|
| `04-brief-template-copy-prompts/01-templates-by-motion/` | 40 recipe cards s copy šablónou, promptom a safe zónami |
| `04-brief-template-copy-prompts/02-40-templates/` | tie isté formáty ako rýchle prompty s `[PLACEHOLDERMI]` |
| `brands/{značka}/{značka}-templates/` | vlastné formáty značky (voliteľné) |
| `04-brief-template-copy-prompts/03-ad-swipe.md` | nový template z reklamy konkurencie (rozbor → nová šablóna) |

V dashboarde (tab 🎨 Templaty a štýly) vidíš každý formát ako náčrt.

**4c — Copy.** Napíš `prompts-sk.json` (vzor v `brands/_priklad/`):

```json
{
  "brand": "Moja značka",
  "_meta": { "product": "…", "visual_style": "studio-product" },
  "prompts": [
    {
      "template_number": 1,
      "template_name": "headline-hero",
      "aspect_ratio": "4:5",
      "needs_product_images": true,
      "brief": { "id": "B03", "persona": "…", "angle": "…", "emotion": "…", "customer_voice_anchor": "…" },
      "headline": "Jedna veta, ktorá predá",
      "subhead": "Krátky benefit",
      "cta": "KÚPIŤ TERAZ",
      "prompt": "Reproduce the product exactly from the reference image … HEADLINE: \"{{headline}}\" …"
    }
  ]
}
```

**Prompt musí byť nezávislý od jazyka.** Do tela promptu nikdy nevkladaj ukážkový text ako „ukážku layoutu" —
AI potom občas vyrenderuje ukážku namiesto preloženého `{{placeholderu}}`.

❌ `HEADLINE: "{{headline}}" — prvý riadok "Rýchlo." stredná hrúbka, druhý "Jednoducho." hrubší`
✅ `HEADLINE: "{{headline}}" — prvý riadok stredná hrúbka, druhý hrubší (delenie podľa \n v {{headline}}). Render ONLY the {{headline}} value.`

Každý prompt musí obsahovať frázu *„reproduce the product exactly from the reference image"* — inak ho validácia zastaví.
Art direction nepíš do promptu — vyber štýl z `visual-styles/` (`_meta.visual_style` alebo `--visual-style`).

### Krok 5 — Hodnotenie copy (8 agentov, `05-scoring-agents/`)

| # | Agent | Kontroluje |
|---|---|---|
| 1 | Persona Fit | hovorí to k persone z briefu? |
| 2 | Angle Execution | aktivuje uhol (presvedčenie)? |
| 3 | Emotional Resonance | vyvolá cieľovú emóciu? |
| 4 | Brand Consistency | tón, prirodzená slovná zásoba, oslovenie podľa značky, glosár |
| 5 | Copy Excellence | rytmus, úspornosť, prekvapenie, sila hooku |
| 6 | Format Compliance | počty slov, štruktúra, súlad s templatom |
| 7 | Fact-Check | každé tvrdenie, číslo a citát má zdroj v researchi (proti halucináciám) |
| 8 | Copy Editor | gramatika, diakritika, desatinné čiarky, zakázané znaky |

Prah 90 na agenta. Pod 90 → uprav copy a hodnoť znova. Potom **tabuľka všetkých textov** na schválenie človekom —
bez „OK" sa negeneruje.

### Krok 6 — Generovanie

```bash
cd staticky
./run.sh <značka> --provider google \
  --brand-dir <abs. cesta k ad-setu> --images-dir <abs. cesta k fotkám> \
  --output-dir <ad-set>/outputs --lang sk --templates 1,7 --resolution 1K
```

Provider: `google` (okamžite, ~0,07 $ / 1K obrázok) · `google-batch` (polovičná cena, do 24 h) · `fal` (fal.ai).
Najprv vždy `--dry-run` (zadarmo). Skript sám:
1. načíta `prompts-{jazyk}.json` podľa `--lang` a pridá brand karty ako referencie,
2. pridá ochranu proti vyrenderovaniu názvov fontov z brand kariet,
3. skontroluje nevyriešené `{{placeholdery}}`, ceny v copy (prepni `--allow-prices`, ak cena patrí do bannera)
   a zabudnuté `[ZÁTVORKY]`,
4. vygeneruje bannery, zapíše cenu do `cost-log.jsonl` a prestaví dashboard.

### Krok 6.1 — Vizuálna kontrola (povinná)
V dashboarde over každý banner: texty sedia s JSON, žiadny vyrenderovaný názov fontu ani hex kód, správne logo,
žiadny vymyslený text navyše. Hodnotenie: ✓ PASS / ✎ drobná oprava / ✕ FAIL + poznámka. Pregeneruj iba označené.

---

## Jazyky (voliteľné)

1. **Preklad copy** — `BONUS/04-copy-translator/` (Claude číta zdrojový `prompts-sk.json`, glosár a research,
   píše `prompts-{jazyk}.json` vedľa neho).
2. **Kratšie hodnotenie** — agenti 4–8 (1–3 sú zamknuté briefom).
3. **Review lokálnym tímom** — voliteľne cez TSV / Google Sheets.
4. **Generovanie** — `--lang hu --output-dir <ad-set>/outputs-hu`.

Hotový banner sa dá preložiť aj priamo: `BONUS/03-image-translator/translate_ads.py --brand "<značka>" --image … --languages cz,hu`.

---

## Štruktúra klienta

```
brands/{značka}/
├── .env                              voliteľne vlastný GEMINI_API_KEY
├── brand-dna/                        brand-research-brief.json, brand-spec-card.png, visual-style-card.png,
│                                     voice / glosár, chyby-neopakovat.md, logos/
├── {značka}-templates/               voliteľné vlastné formáty
└── products/{produkt}/
    ├── marketing-research/           deep-research, avatar-sheet, offer-brief, necessary-beliefs, briefs
    ├── source-product-images/        čisté fotky produktu
    └── product-image-ads/{YYYY-MM-DD}-{názov}/
        ├── prompts-sk.json  (+ prompts-cz.json, prompts-hu.json …)
        └── outputs/  outputs-cz/  outputs-hu/ …
```

## Overené pravidlá (zapisuj ich do `chyby-neopakovat.md` každej značky)

| Pravidlo | Prečo |
|---|---|
| Žiadne anglicizmy, ak existuje domáci výraz | text pôsobí prirodzene |
| Prirodzený slovosled, žiadne kalky z angličtiny | „Bez starosti dňa" → „Bez denných starostí" |
| Žiadne ceny v banneri, ak tam nepatria (`--allow-prices` na výnimky) | ceny sa menia, banner nie |
| Žiadne zámená bez jasného antecedentu | čitateľ nevie, o čom je reč |
| Názvy fontov, veľkosti a hex kódy nikdy nepísať hneď za text v úvodzovkách | AI ich vyrenderuje ako text |
| Prompt bez ukážkového textu | jeden template = N jazykov |
| Žiadne vymyslené recenzie (mená, veky, citáty bez zdroja) | agent 7 to zastaví |
| Logo negenerovať AI — nechať voľný roh a prilepiť PNG | AI logo komolí |

## Problémy a riešenia

| Problém | Príčina | Riešenie |
|---|---|---|
| Banner má pôvodný slovenský text namiesto prekladu | ukážkový text v tele promptu | prompt prerobiť na inštrukciu bez textu |
| Na banneri je názov fontu („Montserrat 400") | únik z brand karty | slovný popis namiesto názvu fontu, „render EXACTLY these texts" |
| Validácia: „cena v copy" | cena v texte | odstrániť alebo `--allow-prices` |
| Validácia: „unresolved {{…}}" | placeholder bez poľa | doplniť pole (vnorené: `{{tabulka.stlpec}}`) |
| Validácia: „chýba reference image" | prompt bez frázy o referencii | doplniť „reproduce the product exactly from the reference image" |
| AI si vymyslí produkt | `--images-dir` relatívna cesta | vždy absolútna cesta |
