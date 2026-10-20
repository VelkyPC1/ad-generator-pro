# Format Template Structure (vzor)

Referenčná štruktúra pre všetkých 15 format templates. Vzorom je `headline_template.md` (hybrid verzia — Motion štruktúra + tactical detaily zo skills-databaza).

## Povinná štruktúra každého template

```markdown
# [Format Name]

## Metadata
- aspect_ratio: default + alternatives
- needs_product_images: true / false (per style)
- reference_uploads: brand-spec-card.png + visual-style-card.png + product image
- top_safe_zone / bottom_safe_zone

## Product reference rule (CRITICAL)
Never describe product from text. Always: "Use attached product image as primary reference — reproduce EXACTLY, do not invent or alter shape, color, labels, or design."

## What this format is
[1-2 odseky — čo formát je, prečo funguje, kedy vyhráva]

## Styles

### Style A: [názov]
[popis štýlu]

#### Copy template
{{headline}}  - word count + guidance (čo musí splniť)
{{subhead}}   - optional, word count + guidance
{{cta}}       - optional, word count

#### Image generation prompt
(plný prompt s placeholdermi)
PREFIX: "Use attached product image as primary reference — reproduce EXACTLY..."
COMPOSITION: (include FOCAL LENGTH, e.g., 50mm f/2.8)
TYPOGRAPHY: per brand spec card
SAFE ZONES: top [TOP SAFE ZONE]px, bottom [BOTTOM SAFE ZONE]px clear
COLOR AND TREATMENT: ...
BRAND IDENTITY: logo per brand spec card (optional)
PHOTOGRAPHY DIRECTION: per visual style card
MOOD: [from variation]

#### Variation vectors
- Product position: options separated by |
- Text position: options
- Background: options
- Lighting: options
- Focal length: options (50mm f/2.8, 85mm f/2.8, 35mm f/2.0, 100mm macro)
- Energy: options

### Style B: [variant — napr. lifestyle/context]
(rovnaká štruktúra)

### Style C: [variant — napr. typography-dominant]
(rovnaká štruktúra)

---

## Global rules for [format] format

### Visual-[format] coherence (CRITICAL)
[test: cover text — image conjures idea? cover image — text conjures visual? oba yes = coherence]

### Agent 7: Copy Editor / Proofreader (REQUIRED)
Checklist:
1. Grammar
2. Spelling (brand names verified)
3. Punctuation
4. Banned characters: NO em dashes (--), NO en dashes, NO semicolons in headlines
5. Number consistency
6. No duplicate content (stat/price/claim once)
7. Word count compliance per spec
8. Brand name capitalization
Scoring: Pass/Fail — single error = fail.

### Price is not a default element
Include only when contextually relevant.

### Fewer elements by default
Empty optional slots unless they strengthen the execution.

### What to avoid
- Generic headlines that fit any product
- Text fighting image (one leads, one supports)
- Low-contrast text placement
- Subheads repeating headline
- Generic lifestyle unrelated to persona
- Product-on-dark-background disconnected from headline concept
- Visuals illustrating product, not headline idea
```

## Kľúčové princípy (platia pre všetky formáty)

1. **Jeden súvislý image po okraje** — žiadne panely/boxy/rámy
2. **Copy verbatim v obrázku** — nie v overlay vrstve
3. **Safe zones:** top 270px, bottom 340px bez textu (kvôli platform UI)
4. **Aspect ratio:** 1080x1920 (9:16) default
5. **Brand spec sheet + visual style card** sú uploadované ako reference images pre každú generáciu
6. **Product reference image** je tretí vstup do generácie
7. **Visual–copy coherence test** — ak zakryjem jedno, druhé musí evokovať rovnaký nápad

## 15 formátov (status)

- [x] Headline (`headline_template.md` — vzor)
- [ ] Before & After
- [ ] Bullet Points
- [ ] Carousel
- [ ] Features & Benefits
- [ ] Founder Story
- [ ] Handwriting
- [ ] Negative Marketing
- [ ] New Creative Formats
- [ ] News
- [ ] Press
- [ ] Social Proof
- [ ] Statistics
- [ ] Testimonial
- [ ] UGC
- [ ] Us vs Them

Každý ďalší template dodržuje štruktúru vyššie, prispôsobuje obsah špecifike formátu.
