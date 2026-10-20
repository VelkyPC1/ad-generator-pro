# 37 — Hero Statement + Icon Bar + Offer Burst (Promo Variant)

🏷️ Dark moody promo. Power statement headline, starburst discount badge, hand lifting the product, icon benefit bar. Black Friday / sale-season energy.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Promo variant of #30. Dark moody background. Top banner: massive power statement with a period. Upper product zone: starburst badge with a % OFF discount rotated slightly. Center: a hand gripping the product from above, lifting it out of its retail packaging. Bottom: 3-icon benefit bar on a semi-transparent dark strip. Very bottom: bright accent promo banner. Sale-season vibe.

## Copy template

```
{{headline}}     - 1-3 words + period. All caps, massive.
                        e.g., "FUPA KILLER." / "GUT RESET." / "PAIN GONE."

[DISCOUNT BURST]      - "GET UP TO [X]% OFF" or similar short promo.
                        e.g., "GET UP TO 40% OFF" / "50% OFF TODAY"

[ICON + LABEL 1-3]    - Each 2-4 words + simple icon.
                        e.g., "(crossed burger) CURB APPETITE" /
                              "(bolt) BURN CALORIES" / "(heart) LOSE WEIGHT"

[PROMO BANNER]        - Very bottom bar. 2-5 words bold.
                        e.g., "BLACK FRIDAY SPECIAL" / "SITEWIDE 48 HOURS ONLY"

No long copy. Statement + price + 3 benefits + sale bar.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a promo-variant hero statement + icon bar ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: [DARK BACKGROUND — charcoal / moody gray / near-black brand dark]. Moody slightly dramatic lighting throughout.

Top 12%: white or light banner with massive bold [DARK BRAND COLOR] uppercase sans-serif headline "{{headline}}" ending with a period for punch.

Upper-left of the product area: a [BRIGHT ACCENT COLOR — neon green / lime / electric yellow] comic-style starburst badge rotated slightly (approx. -8°), reading "[DISCOUNT BURST]" in bold black uppercase text. The badge breaks into the product zone for energy.

Center 55%: [PERSON'S HAND — realistic hand reaching from above] gripping the product (reproduced exactly from reference) from the top, lifting it slightly off its [PACKAGING — retail box / canister base / jar lid] visible below. Product label and branding clearly visible. Moody rim lighting on the product edge, slight shadow from the hand.

Bottom 20%: semi-transparent dark strip overlaying the background. Three evenly spaced icon-and-text benefit columns:
- Column 1: [ICON 1 — simple line art] / "[LABEL 1]"
- Column 2: [ICON 2 — simple line art] / "[LABEL 2]"
- Column 3: [ICON 3 — simple line art] / "[LABEL 3]"

Icons in line-art circles with [ACCENT COLOR] highlights. Labels in white bold uppercase sans.

Very bottom edge: full-width [BRIGHT ACCENT COLOR] banner with bold black uppercase text "[PROMO BANNER]".

TYPOGRAPHY:
Per uploaded brand spec card. Power statement massive all-caps. Discount burst in chunky comic-style caps. Icon labels uppercase bold. Promo banner dense bold caps.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Dark moody background. White banner on top. Bright accent for burst + bottom banner creates promo pop. Product dramatically lit.

MOOD:
Aggressive, sale-driven, urgent. "This is the deal. Don't scroll past."
```

## Variation vectors

**Background**: charcoal (default) | near-black | moody brand dark | deep navy

**Burst style**: comic starburst (default) | jagged star | sunburst rays | pill badge with strike-through price

**Accent color**: neon green (default) | electric yellow | hot pink | bright orange

**Hand position**: gripping from above (default) | pulling from side | holding mid-air | two hands presenting

**Icon style**: line-art in circles (default) | filled accent-color icons | outlined geometric | emoji-style

**Promo intensity**: single-line bar (default) | stacked banner with urgency ("48 HRS ONLY") | gift-with-purchase callout

**Energy**: Black Friday aggressive | everyday-promo confident | seasonal celebration | flash-sale urgent

## Format-specific rules

- **Period on power statement is mandatory.** Same rule as #30 — "FUPA KILLER" reads mid-sentence; "FUPA KILLER." is a verdict.
- **Discount must be real.** "40% OFF" without a live promo = false advertising. Only use when the campaign is actually running.
- **Category compliance.** Health / weight-loss / supplement power statements may violate ad-platform claim rules. Verify before shipping (Meta + TikTok enforce strictly).
- **Icons consistent in style.** Don't mix line-art with emoji-style. Pick one visual language.
- **Hand looks natural.** Gripping the product like a tool, not like a display. Realistic tension in fingers.
- **Accent color is loud on purpose.** Muting it for "brand safety" kills the sale energy — either commit or use #30 instead.

See `headline_template.md` for shared Global rules. See #30 for the non-promo hero statement version.
