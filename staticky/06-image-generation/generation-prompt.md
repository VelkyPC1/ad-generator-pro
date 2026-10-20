# Step 7 — Image Generation Prompt Template

Vezme finálny prompt string z kroku 6 (po substitúcii placeholderov) a odošle ho do generátora spolu s reference images.

## When to use

After:
- [x] Krok 1 — Brand Research Brief uložený
- [x] Krok 2 — Brand Spec Card + Visual Style Card uložené ako PNG
- [x] Krok 3 — Product research kompletný (deep-research, avatar-sheet, necessary-beliefs)
- [x] Krok 3b — **Vizuálny štýl vybraný** z `visual-styles/` (`--list-styles`) a zapísaný
      do `_meta.visual_style` (ad-set) alebo `prompts[].visual_style` (banner)
- [x] Krok 4 — Template vybraný, copy napísaný, `prompt.json` uložený
- [x] Krok 5 — Všetci 7 agenti ≥90, Agent 7 PASS
- [x] Krok 6 — Placeholdery nahradené, finálny prompt string bez `{{}}`, reference images pripravené

## 10 universal rules (enforced in every generation prompt)

Every generated prompt must include these rules verbatim so the generator respects them:

1. **Exact dimensions:** 1080x1920 pixels, 9:16 vertical aspect ratio (unless format template specifies otherwise — 4:5 = 1080x1350, 1:1 = 1080x1080).
2. **One continuous image.** No panels, borders, split frames, grid lines, collages, or multi-cell compositions. The image fills the entire frame edge to edge.
3. **All copy rendered verbatim in the image.** Every word from the approved brief appears exactly as written — no paraphrasing, no extra words, no missing words.
4. **No text smaller than 24px** at 1080px width. Fine print must still be legible.
5. **Sufficient contrast** between text and background. If the background behind text is busy or low-contrast, use a subtle text treatment (slight shadow or semi-transparent backing) rather than heavy graphic overlays.
6. **Photorealistic product representation.** Reproduce the product EXACTLY as it appears in the uploaded product reference image — do not invent, alter, or idealize shape, color, labels, typography, or design details.
7. **Safe zones respected:** top 270px and bottom 340px clear of critical content (platform UI overlap zones for Stories, Reels, TikTok).
8. **No em dashes (—), en dashes (–), or semicolons** in any rendered copy.
9. **Every data point appears once.** No duplicate prices, stats, claims, or badges across elements.
10. **Brand fingerprint dominates.** Final output must look like this brand's ad — typography, colors, photography direction all sourced from the brand spec card and visual style card, not from generic stock conventions.

## Reference upload checklist

Before sending the prompt to Nano Banana 2 / fal.ai, upload:

- [ ] **Brand Spec Card** (PNG) — `brands/{brand}/brand-dna/brand-spec-card.png`
- [ ] **Visual Style Card** (PNG) — `brands/{brand}/brand-dna/visual-style-card.png`
- [ ] **Product photo** — authoritative reference for product visual
- [ ] **Style reference** (voliteľné) — `ref_images` vybraného štýlu, posiela sa automaticky (max 2)

## Generation prompt template

```
Create a static ad for [BRAND NAME]'s [PRODUCT NAME].

DIMENSIONS: [1080x1920, 9:16 vertical] — [or 1080x1350 4:5 / 1080x1080 1:1 per format template].

REFERENCE IMAGES (uploaded):
1. Brand Spec Card — authoritative source for fonts, colors, logo, CTA styling, typography rules
2. Visual Style Card — authoritative source for photography direction, mood, product styling, always/never rules
3. Product photo — reproduce the product EXACTLY as shown; do not invent or alter shape, color, labels, or design

COPY (render verbatim in the image):
[Vložiť finálny prompt string z kroku 6 — všetky {{placeholdery}} sú už nahradené]

UNIVERSAL RULES (enforce all):
1. Exact dimensions [1080x1920 / 1080x1350 / 1080x1080].
2. One continuous image — no panels, borders, split frames, grid lines, or collages.
3. All copy rendered verbatim — no paraphrasing, no extras.
4. No text smaller than 24px at 1080px width.
5. Sufficient contrast between text and background.
6. Photorealistic product per uploaded reference — do not alter shape, color, labels, or design.
7. Top 270px and bottom 340px clear of critical content.
8. No em dashes (—), en dashes (–), or semicolons in rendered copy.
9. Every data point appears exactly once.
10. Output must look like [BRAND]'s ad — brand fingerprint dominates generic ad conventions.
```

## Execution

Generovanie prebieha cez `generate_ads.py` — Python skript v `brands/{brand}/products/{product}/product-image-ads/`.

```bash
python generate_ads.py --provider google-batch --prompts-file prompts/file.json
```

**Vizuálny štýl** sa pripojí automaticky na koniec promptu podľa `visual_style` v prompts JSON.
Prebiť celý beh: `--visual-style <id>`. Knižnica a schéma: `visual-styles/README.md`.

**3 provideri:**

| Provider | Cena/img | Čas | Použitie |
|----------|----------|-----|---------|
| `fal` | ~$0.06 | sekundy | testy |
| `google` | ~$0.067 | sekundy | real-time |
| `google-batch` | ~$0.034 | až 24h | **produkcia (default)** |

- **Model:** `gemini-3.1-flash-image-preview` = **Nano Banana 2**
- **Keys:** `jozef/keys/.env` → `FAL_KEY`, `GEMINI_API_KEY`
- **Reference images:** skript posiela brand-spec-card + visual-style-card + product photo automaticky ako `inlineData`

## Output location

```
brands/{brand}/brand-dna/ads/{date}-{format}/
├── prompt.json        # krok 4 — copy polia + prompt string s {{placeholdermi}}
├── scoring.md         # krok 5 — výsledky 7 agentov
├── output.png         # krok 7 — vygenerovaný obrázok
└── output-check.md    # krok 8 — výsledok vizuálnej kontroly
```
