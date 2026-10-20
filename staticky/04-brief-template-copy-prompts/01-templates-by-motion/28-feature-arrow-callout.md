# 28 — Feature Arrow Callout / Product Annotation

🏷️ Product held by hand. Hand-drawn arrows point to 4 benefit callouts around it. Editorial feel with a promo banner at the bottom.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Italic serif headline at top, then a massive bold value prop ("ALL IN ONE"). Center: a hand holding the product with 4 curved arrows pointing to benefit callouts arranged around it. Bottom: full-width contrast banner with a promo/CTA. Works for products with multiple named benefits that need to be called out visually.

## Copy template

```
[BENEFIT STATEMENT]    - 5-10 words. Italic serif. Dark navy or brand dark.
                         e.g., "Barista grade coffee. Instant. Affordable."

[VALUE PROP]           - 2-3 words. Massive bold sans-serif.
                         e.g., "ALL IN ONE" / "MADE SIMPLE" / "EVERYTHING INSIDE"

[CALLOUT 1-4]          - Each 2-4 words. Bold brand color.
                         e.g., "NO sugar or calories"
                               "Multiple Flavors"
                               "Iced, cold or hot"
                               "Smooth and delicious"

[PROMO TEXT]           - Bottom banner. Bold gold/accent on contrast.
                         e.g., "HUGE SALE + FREE GIFTS" / "BUY 2 GET 1 FREE"

{{cta}}                  - Optional, integrated with promo. 2-4 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a feature arrow callout product annotation ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: [BACKGROUND from variation — warm cream / light yellow textured / soft brand-tinted neutral].

Top: italic serif headline "[BENEFIT STATEMENT]" in [BRAND COLOR — dark navy / brand dark].

Below: massive bold sans-serif "[VALUE PROP]" in [BRAND COLOR] at maximum scale.

Center: [PERSON'S HAND — realistic hand reaching from bottom or side] holding the product (reproduced exactly from reference) at a natural mid-use angle.

Four curved arrows in [BRAND COLOR] pointing from the product outward to four benefit callout labels arranged around it:
- Top-left: "[CALLOUT 1]"
- Top-right: "[CALLOUT 2]"
- Bottom-left: "[CALLOUT 3]"
- Bottom-right: "[CALLOUT 4]"

Callouts in bold [BRAND COLOR] text. Arrows feel hand-drawn or editorial, not rigid mechanical.

Bottom: full-width [CONTRAST COLOR — deep navy / dark brand] banner with "[PROMO TEXT]" in bold [ACCENT COLOR — gold / white] with optional emoji accents.

TYPOGRAPHY:
Per uploaded brand spec card. Italic serif for elevated headline. Massive sans for value prop. Bold for callouts. Contrast banner grabs attention at the bottom.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Warm textured background. Brand color for headline + callouts + arrows. Contrast banner saturated with accent text.

MOOD:
Editorial but promo-forward. "Here's what you get, and here's the deal."
```

## Variation vectors

**Background**: warm cream (default) | light yellow textured | soft brand-tinted | off-white linen

**Hand position**: hand reaching from bottom (default) | hand from left side | hand from right side | hand from upper-right

**Arrow style**: hand-drawn curved (default) | slight squiggle | clean curved | bracket-pointer

**Callout count**: 3 callouts | 4 callouts (default) | 5 callouts | 6 callouts (max info density)

**Promo banner style**: full-width solid (default) | pill at bottom | ribbon wrap | bright burst badge

**Energy**: editorial and inviting | bold and promo-driven | elegant and elevated

## Format-specific rules

- **Hand must look natural, not prop-staged.** Product held loosely, fingers relaxed. Mannequin-style grips kill the format.
- **Arrows connect to real product features.** Each arrow originates from the specific visible element it's calling out (ingredient label, cap, texture).
- **Parallel structure across callouts.** All 4 follow the same pattern — don't mix "NO sugar" with "For your morning routine."
- **Promo banner must have a real offer.** "HUGE SALE" without a real campaign = lost trust. Only use when there's a real promotion.
- **Italic serif + bold sans combination carries the format.** Replacing both with the same font flattens it.

See `headline_template.md` for shared Global rules.
