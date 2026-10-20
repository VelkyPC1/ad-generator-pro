# 18 — Stat Surround / Callout Radial (Lifestyle Flatlay)

🏷️ Same stat-radial format as #13, but lifestyle flatlay background and hand-held product sell the experience, not just the specs.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Stat radial like #13, but the hero is a hand holding the product mid-use within a lifestyle flatlay scene. Background is white with scattered lifestyle props filling the corners and edges (food plates, fruit, accessories) slightly out of focus. A filled banner headline runs across the top. Works when the product is experiential (food, drinks, wellness items you use daily).

## Copy template

```
{{headline}}     - 5-10 words all-caps in a colored banner bar.
                 e.g., "INCREDIBLY TASTY BREAKFAST IN 30 SECONDS"

[STAT 1-4]     - Each: big number + 1-2 word caps label.
                 e.g., "20g PROTEIN" / "900K HAPPY CUSTOMERS" /
                       "20+ FLAVORS" / "30K 5-STAR REVIEWS"

No CTA. Info-led format.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a stat-surround lifestyle flatlay ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: clean white surface shot from slightly overhead.

Top: bold [ACCENT COLOR from spec card — purple / brand contrast] filled banner bar spanning full width, with white all-caps sans-serif "{{headline}}".

Center: a [PERSON DETAIL — woman's hand / man's hand] holding the product (reproduced exactly from reference) in mid-frame at a natural mid-use angle (sipping a shaker, opening packaging, holding a jar).

Scattered around the edges: [FLATLAY PROPS — product sachets, pancakes on plates, blueberries, muffins, fruit, relevant lifestyle items] arranged organically to fill corners and edges. Props slightly out of focus to create depth.

Four stat callouts with curved [ACCENT COLOR] arrows pointing toward the held product (top-left, top-right, bottom-left, bottom-right):
- "[STAT 1]" big bold number / "[LABEL 1]" all-caps regular weight below
- "[STAT 2]" / "[LABEL 2]"
- "[STAT 3]" / "[LABEL 3]"
- "[STAT 4]" / "[LABEL 4]" with five small filled gold stars beneath if review-related

Arrows feel hand-drawn / editorial.

TYPOGRAPHY:
Per uploaded brand spec card. Headline bold banner. Stats oversized. Labels small caps.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White background for scannability. Banner and arrows in sharp accent color. Props naturally lit, slightly out of focus.

MOOD:
Energetic, appetizing, information-dense but scannable. Lifestyle authenticity + stat authority in one frame.
```

## Variation vectors

**Banner color**: brand accent | brand primary | saturated contrast (coral, mint, purple)

**Hand type / gesture**: holding upright | pouring | mid-sip / mid-scoop | mid-apply / mid-open

**Prop theme**: food/breakfast | supplements/morning routine | beauty/self-care | workout/gym | coffee/desk

**Stat focus**: nutrition (protein, sugar, calories) | social proof (customers, reviews) | variety (flavors, SKUs) | mixed

**Arrow style**: hand-drawn curved | straight angled | dotted curved

**Prop density**: sparse (3-4 props) | medium (default, 5-7 props) | heavy (8-10+ for abundance feel)

## Format-specific rules

- **Flatlay coherence.** All props come from the same "world." Pancakes + dumbbells in the same frame = chaos. Pick a scene (morning breakfast / workout prep / self-care routine) and stay there.
- **Hand must interact with the product naturally.** A frozen hand "holding" a product at arm's length reads as fake. The gesture should match the product use.
- **Stats parallel structure.** Same as #13 — all four callouts in the same format.
- **Overhead or slightly tilted.** Flat lay works; eye-level doesn't. The format depends on the top-down perspective.
- **Props must NOT obscure the product or the stats.** Props frame, they don't dominate.

See `headline_template.md` for shared Global rules. See #13 for the parent stat-radial format.
