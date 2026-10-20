# 13 — Stat Surround / Callout Radial (Product Hero)

🏷️ Product is the sun. Stats are the planets. Arrows make it scannable in under 2 seconds.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Product centered in a clean gradient frame. Four stat callouts (big number + small label) float in the corners, each connected to the product with a hand-drawn curved arrow. A price badge near the product. Scattered "appetite appeal" props (food crumbs, ingredient bits) at the base. Works for info-dense products (food, supplements, personal care) where multiple stats compete for attention.

## Copy template

```
{{headline}}         - 6-12 words. Top of frame.
                     e.g., "So tasty you'll forget it's actually healthy."

[STAT 1-4]         - Each: big number + 1-2 word label in caps.
                     e.g., "20g" + "PROTEIN" / "280" + "CALORIES" /
                           "900k+" + "HAPPY CUSTOMERS" / "30k+" + "5-STAR REVIEWS"

[PRICE BADGE]      - Optional. Small circular badge floating near the product.
                     e.g., "AS LOW AS $2.63 PER MEAL!"

No CTA by default — format is info-first.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a stat-surround product hero ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: white-to-[LIGHT GRADIENT COLOR from variation — warm golden beige / pale blush / mint cream] gradient, fading top to bottom.

Top: large bold [TEXT COLOR — dark brown or brand dark] sans-serif headline "{{headline}}" centered.

Center: the product (reproduced exactly from reference) photographed on the gradient surface, soft studio lighting, occupying ~35% of the frame. Treated as the "sun" of the composition.

Floating near the product: a small circular badge "[PRICE BADGE]" in [BADGE COLOR from spec card] with bold text. Positioned to not block the product silhouette.

Four stat callouts around the product (top-left / top-right / bottom-left / bottom-right). Each callout:
- Big oversized bold "[STAT N]" number in dark bold
- Small "[LABEL N]" in all-caps regular weight below the number
- A hand-drawn-style curved arrow in [ARROW COLOR — black or brand dark] connecting the callout to a point on the product

Bottom-right stat includes five small filled gold/brand stars beneath the label.

Bottom foreground: [FLAVOR/INGREDIENT PROPS — scattered food bits like cookie dough balls, chocolate chips, ingredient crumbs, or relevant props] adding texture and appetite appeal.

No brand logo. The product packaging carries identity.

TYPOGRAPHY:
Per uploaded brand spec card. Headline dominant. Stats oversized bold. Labels small caps. Arrows feel hand-drawn / editorial, not rigid mechanical.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Soft gradient background. Arrows and stats in dark contrast color. Price badge in bold brand color. Appetite props naturally lit on the surface.

MOOD:
Clean, informational, appetizing. Info-dense but scannable in under 2 seconds.
```

## Variation vectors

**Gradient color**: warm beige (default) | pale blush pink | mint cream | soft lavender | brand-tinted pale

**Stat focus**: nutrition (protein, calories, sugar) | social proof (customers, reviews, stars) | performance (results, hours, uses) | mixed (2 nutrition + 2 social proof)

**Arrow style**: hand-drawn curved (default) | straight thin lines | dotted curved | bracket-style

**Product angle**: straight-on front (default) | slight 15° three-quarter | flat lay

**Props type**: food crumbs/ingredients | texture sprinkles (oats, herbs, dust) | packaging bits | no props (cleaner minimal)

**Energy**: appetizing and energetic | clean and clinical | warm and indulgent | confident and evidence-based

## Format-specific rules

- **Stats must be true.** Every number is verified against brand source. Agent 4 and Agent 7 both flag invented stats.
- **Parallel structure across stats.** All four follow the same format: big number + all-caps label. Don't mix "20g PROTEIN" with "Rated 4.9 stars."
- **Arrows connect to real points.** Nutrition stats arrow to the label area. Review stats arrow to a visible badge or just out from the product. Arbitrary arrows read as placeholder design.
- **Props must match product.** Cookie crumbs for a cookie; ingredient bits for a supplement; steam/mist for a beverage. Mismatched props look like stock library.
- **No brand logo overlay — product carries identity.** Adding a logo clutters the radial composition.

See `headline_template.md` for shared Global rules.
