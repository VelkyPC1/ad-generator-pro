# 30 — Hero Statement + Icon Benefit Bar

🏷️ Bold 2-3 word power statement. Lifestyle product shot in the middle. 3 icon+label benefits at the bottom. Scrolling social-proof ticker.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** false (product in lifestyle scene only)
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Product visible in the lifestyle scene must be reproduced exactly per reference. The image prompt should say: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo (visible in the lifestyle scene), do not invent or alter shape, color, labels, or design."*

## What this format is

Three-zone layout. Top 15%: massive 2-3 word power statement in a white banner ("APPETITE KILLER."). Middle 55%: lifestyle product shot (hand holding a capsule above a supplement jar). Bottom 25%: light brand-color zone with 3 icon+label benefits in columns. Very bottom: scrolling ticker bar with social proof. Works for weight-loss / performance / functional products where the claim needs bluntness.

## Copy template

```
{{headline}}   - 1-3 words + a period. All caps, massive.
                      e.g., "APPETITE KILLER." / "INSTANT ENERGY." / "DEEP SLEEP."

[ICON + LABEL 1-3]  - Each 2-4 words next to a simple line-drawn icon.
                      e.g., "(crossed-out burger) CURB APPETITE"
                            "(lightning bolt) BURN CALORIES"
                            "(heart + body) LOSE WEIGHT"

[SOCIAL PROOF]      - Repeating ticker text.
                      e.g., "OVER 300K+ LIVES CHANGED" (repeating across the bar)

No CTA. Power statement + benefits + social proof ticker.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo (visible in the lifestyle scene), do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a hero statement + icon benefit bar ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame, divided into three horizontal zones.

Top 15%: white banner overlay with massive bold [BRAND COLOR from spec card — dark purple / brand dark] uppercase sans-serif headline "{{headline}}" with a period for punch.

Middle 55%: lifestyle product photo — [SCENE — a woman's hand holding a capsule above an open supplement jar on a clean surface / a person pouring product onto breakfast / product in natural use context]. Soft natural light. Product label and branding clearly visible (reproduced exactly per reference image).

Bottom 25%: [SOFT BRAND COLOR — lavender / light purple / pastel brand] background. Three evenly spaced icon-and-text benefit columns:
- Column 1: [ICON 1 — crossed-out burger icon] / "[LABEL 1 — CURB APPETITE]"
- Column 2: [ICON 2 — lightning bolt icon] / "[LABEL 2 — BURN CALORIES]"
- Column 3: [ICON 3 — heart + body icon] / "[LABEL 3 — LOSE WEIGHT]"

Icons are simple line-drawn in [BRAND COLOR] circles. Labels in all-caps bold dark text.

Very bottom edge: scrolling ticker bar in [DARK BRAND COLOR] with repeating text "[SOCIAL PROOF]" (repeating multiple times across the bar).

TYPOGRAPHY:
Per uploaded brand spec card. Power statement at maximum scale all-caps. Icon labels bold caps. Ticker text smaller caps repeating.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White banner on top. Lifestyle photo mid. Light brand-color bottom zone. Dark ticker at the very bottom.

MOOD:
Blunt, confident, evidence-stacked. "Here's what it does. Here are the proofs."
```

## Variation vectors

**Power statement style**: 1 word + period (e.g., "FUEL.") | 2 words + period (default) | 3 words + period

**Lifestyle action**: hand holding capsule above jar | pouring powder | applying topically | mid-swallow shot

**Icon style**: simple line-drawn in circles (default) | filled brand-color icons | flat emoji-style | minimal geometric

**Bottom zone color**: soft lavender / pastel | brand pastel | warm cream | off-white

**Ticker content**: social proof count (300K+ lives) | review count (10K+ 5-star) | press accolades | category rank

**Energy**: blunt and confident | clinical and direct | warm and reassuring

## Format-specific rules

- **Power statement must end with a period.** The period IS the format. "APPETITE KILLER" without the period reads as mid-sentence. With it, it's a verdict.
- **Icons must be consistent in style.** Don't mix line-drawn with filled; don't mix geometric with emoji-style.
- **Parallel structure for labels.** All 3 benefits in the same grammatical pattern (verb-object, verb-object, verb-object).
- **Social proof ticker must be truthful.** Fabricated numbers break trust and law.
- **Category compliance.** Weight-loss / supplement claims require legal review in most markets. Power statements like "APPETITE KILLER" may trigger health-claim rules.

See `headline_template.md` for shared Global rules.
