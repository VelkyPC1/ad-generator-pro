# 22 — Flavor Story / "Tastes Like"

🏷️ The food is the hero. The product is the payoff. Photorealistic flavor visualization.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A photorealistic close-up food scene fills the entire background (raspberry donuts, chocolate cake, caramel drip). A headline at the top promises "Tastes like [indulgence]". The product sits casually dropped into the scene at a tilt. A stat bar at the bottom handles nutrition compliance ("15g protein / 2g sugar / 180 cal"). Works for health-forward food / supplement brands that taste indulgent.

## Copy template

```
{{headline}}              - 8-16 words. "[Product category] that tastes like [indulgence]."
                          One key word bold-italic for emphasis.
                          e.g., "A protein bar that tastes like freshly baked raspberry donuts"

[STAT 1 / STAT 2 / STAT 3] - Short nutrition stats in a bar.
                             e.g., "15g PROTEIN" | "2g SUGAR" | "180 CALORIES"

[CLEAN LABEL CLAIM]    - Optional tagline at bottom.
                         e.g., "NO ARTIFICIAL SWEETENERS"

No CTA. The flavor is the pitch.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a flavor-story ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: photorealistic close-up food scene of [INDULGENT FOOD — freshly baked raspberry donuts dusted with powdered sugar on a gray stone surface / warm chocolate cake with fudge drip / stack of pancakes with maple syrup]. Shot at 50mm f/2.8, shallow depth of field, warm bakery lighting.

Top third: large bold white sans-serif headline "{{headline}}" with one key word in bold italic for emphasis.

Bottom-right: the product (reproduced exactly from reference) placed at a 15° angle as if casually laid into the scene — not centered, not perfectly placed. Should look dropped into the food shot, not composed.

Bottom: a semi-transparent white bar spanning full width with three stat columns separated by thin vertical lines: "[STAT 1]" | "[STAT 2]" | "[STAT 3]".

Very bottom edge: smaller bold sans-serif "[CLEAN LABEL CLAIM]".

TYPOGRAPHY:
Per uploaded brand spec card. Headline bold white against food scene — if contrast fails, use subtle shadow. Bold italic emphasis on one key word.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Warm bakery / food-forward lighting. Product integrates into scene but remains recognizable.

MOOD:
Indulgent, craveable, permissive. "It tastes like you want it to."
```

## Variation vectors

**Food scene**: raspberry donuts | chocolate cake with drip | pancakes with syrup | cereal with milk splash | ice cream sundae | cinnamon rolls | brownie stack

**Product integration**: casually angled on food surface (default) | partially buried in food | held by hand reaching in | centered in scene

**Headline emphasis**: one bold italic word (default) | two words emphasized | underline accent on key word | color accent on key word

**Stat bar style**: semi-transparent white (default) | solid brand color | dark overlay | no stat bar (flavor-only)

**Lighting**: warm bakery (default) | bright daylight | golden hour | moody evening

**Energy**: indulgent-permissive | fresh-energizing | cozy-comforting | bold-assertive

## Format-specific rules

- **Food must be photorealistic and appetizing.** Stylized food illustrations kill the craveability. Real food photography only.
- **Food must actually reflect the flavor claim.** If the bar claims "tastes like raspberry donut," the background is raspberry donuts — not generic pastries.
- **Product is casual, not hero-lit.** Don't add a spotlight to the product. It sits in the scene like it belongs.
- **Stat bar is compliance, not pitch.** Keep it light, non-aggressive. Nutrition panels are legally required; don't turn them into a second headline.
- **Health claims discipline.** "Healthy" or "guilt-free" may trigger category regulations (US FDA, EU EFSA). Stick to verified claims.

See `headline_template.md` for shared Global rules.
