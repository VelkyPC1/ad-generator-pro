# 05 — Bullet-Points

🏷️ Split composition. Product left, benefits right.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for 4:5)
- **bottom_safe_zone:** 340px (scaled for 4:5)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A split composition: product on the left (40%), a vertical stack of 5 benefit bullets on the right (60%). Each bullet is preceded by a filled brand-color dot. Generous spacing. Works when the product has 5 clear, parallel benefits you want the viewer to scan in 3 seconds.

## Copy template

```
[BENEFIT 1-5]   - Each 2-7 words. Parallel structure.
                  e.g., "Cold-pressed in small batches"
                        "Zero added sugar"
                        "Shelf-stable for 12 months"
                        "Single-farm sourcing"
                        "Compostable packaging"

{{headline}}      - Optional, above bullets. 3-8 words.

{{cta}}           - Optional. 2-5 words, bottom right.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a benefit-list ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame. Split composition on [BACKGROUND from variation — solid brand color / cream / light neutral / textured surface].

Left 40%: the product (reproduced exactly from reference) centered in that column, shot at 85mm f/2.8, clean commercial lighting, subtle shadow grounding the product on the surface.

Right 60%: vertical stack of five benefit lines. Each line:
- Filled [BRAND COLOR from spec card] circle (dot) on the left
- "[BENEFIT N]" in clean sans-serif immediately to the right of the dot
- Generous vertical spacing between lines

[If HEADLINE]: "{{headline}}" at top of the right column, above the bullets, in a clearly larger weight.

[If CTA]: "{{cta}}" bottom right per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Bullets at consistent size — do NOT vary weight or size across the five lines. All five read as equals.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Background aligned with brand palette. Product and text contrast clearly. Dots in brand primary color, text in brand's primary text color.

BRAND IDENTITY:
[BRAND] logo bottom right per spec card.

MOOD:
Confident, scannable, evidence-based.
```

## Variation vectors

**Background**: solid brand color | warm cream | off-white | textured surface (linen, paper, wood) | soft gradient per spec card

**Bullet marker**: filled brand-color dot (default) | filled brand-color checkmark | small brand-color square | minimal dash

**Product angle**: straight-on front | 15° three-quarter | flat lay from above | hand-held from left

**Bullet count**: 3 bullets (punchy) | 5 bullets (default) | 7 bullets (info-dense — only if headline absent)

**Split ratio**: 40/60 product-bullets (default) | 50/50 | 35/65 (bullet-heavy)

**Energy**: confident and evidence-based | warm and inviting | premium and clinical | bold and direct

## Format-specific rules

- **Parallel structure across bullets.** All five follow the same grammatical pattern. Don't mix "Cold-pressed" with "Shelf-stable for 12 months" with "For deeper flavor" — pick one pattern and hold.
- **No redundant bullets.** "Organic" and "Certified organic" in the same stack waste a slot.
- **Bullets compress.** Every bullet is 2-7 words. If a benefit needs more, either cut it or promote it to a headline — don't let one bullet run long.
- **Visual-copy coherence.** The product shown must demonstrably support the claimed benefits. A shot of bare product without visible features contradicts "Cold-pressed in small batches" — use a shot that shows it.

See `headline_template.md` for shared Global rules.
