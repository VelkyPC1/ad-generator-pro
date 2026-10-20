# 35 — Hero Product Showcase + Stat Bar

🏷️ Superlative headline up top. Product hero center with ingredient debris scattered radially. Stat bar with 3 metrics at the bottom. Classic premium e-comm.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Superlative claim headline at the top ("THE WORLD'S HEALTHIEST CHOCOLATE"), a rounded CTA button, product hero in the center with ingredient debris (broken pieces, cocoa dust, crumbs) scattered radially around it, and a white rounded-pill stat bar at the bottom with 3 product metrics. Classic premium e-comm layout with texture energy.

## Copy template

```
[SUPERLATIVE HEADLINE]   - 3-6 words. Uppercase bold. Brand-color sans.
                           e.g., "THE WORLD'S HEALTHIEST CHOCOLATE" /
                                 "THE LAST MULTIVITAMIN YOU'LL NEED" /
                                 "PROTEIN. PERFECTED."

{{cta}}                    - 2-4 words. In a white pill button.
                           e.g., "EXPLORE NOW" / "SHOP THE RANGE" / "TRY IT TODAY"

[STAT 1-3]               - Each is a number + short label. Bold dominant number.
                           e.g., "12G OF PROTEIN" / "≤2G OF SUGAR" / "≤3G OF NET CARBS"

No body copy. The product + stats do the argument.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a hero product showcase + stat bar ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: [BACKGROUND COLOR — warm sand / beige / cream / soft brand-tinted neutral].

Top: large bold [BRAND COLOR — chocolate brown / brand dark] uppercase sans-serif headline "[SUPERLATIVE HEADLINE]" at maximum scale. 2 lines max.

Below headline: white rounded-rectangle pill CTA button with [BRAND COLOR] uppercase bold text "{{cta}}".

Center: the product (reproduced exactly from reference) in full packaging, angled slightly, hero-lit with soft studio lighting. Product fills the vertical center zone.

Surrounding the product: [SCATTERED ELEMENTS — broken chocolate pieces / cocoa powder dust / crumbs / ingredient pieces / powder puffs / sprinkled oats] arranged in an exploded radial pattern creating visual energy and texture on the background surface. Debris looks natural — not machine-placed.

Bottom: a white (or off-white) rounded-pill stat bar spanning most of the width with three metrics separated by thin vertical [BRAND COLOR] hairlines:
- "[STAT 1]"  |  "[STAT 2]"  |  "[STAT 3]"

Numbers large and dominant, short labels smaller below or inline in bold [BRAND COLOR].

TYPOGRAPHY:
Per uploaded brand spec card. Headline at max scale, all caps. CTA pill uppercase bold. Stat numbers hero-sized, labels bold support.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Warm neutral background. Brand-color typography. Product hero-lit on the surface with realistic debris shadows.

MOOD:
Premium, abundant, craft-feel. "This is the best one. Here's proof in three numbers."
```

## Variation vectors

**Background**: warm sand (default) | cream | soft brand-tint | off-white linen | pastel accent

**Debris theme**: ingredient pieces (default) | powder dust cloud | cross-section scatter | liquid splash | natural botanicals

**CTA placement**: under headline pill (default) | floating top-right badge | integrated into stat bar | none (stats only)

**Stat count**: 3 metrics (default) | 2 metrics | 4 metrics | single hero stat

**Product angle**: slight tilt (default) | straight-on front | 3/4 angle | laying flat with props

**Energy**: premium craft | clean clinical | abundant maximalist | minimal editorial

## Format-specific rules

- **Superlative must be defensible.** "THE WORLD'S HEALTHIEST" gets flagged by Agent 4 unless verifiable. Prefer category-bounded superlatives ("THE CLEANEST PROTEIN IN [CATEGORY]") or swap to a strong declarative.
- **Stats must come from the real product panel.** Inventing "12g protein" when it's 8g breaks trust and law.
- **Debris feels natural, not machine-placed.** Random scatter, varied sizes, real shadows.
- **Product is the hero.** If the debris overpowers the product, rebalance. The packaging must be the primary read.
- **Stat bar readable at thumb-scroll scale.** Numbers dominant, labels short and bold. If labels wrap, rewrite shorter.

See `headline_template.md` for shared Global rules. See #13 and #18 for other stat-forward layouts.
