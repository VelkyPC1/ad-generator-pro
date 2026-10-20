# 31 — Comparison Grid / Table

🏷️ Your product vs competitor. Three rows of attribute comparison in bold type. Meme-format energy — looks like a viral X or Reddit post.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Structured 2-column comparison grid on white. Top row: your product on the left, competitor product on the right. Three horizontal rows below: each compares one attribute. Bold black heavy typography. No icons, no color. Typography and contrast do all the work. Meme-format feel that can go viral organically.

## Copy template

```
[YOUR ADVANTAGE 1-3]       - Each 2-6 words. Bold declarative.
                             e.g., "Uses beef tallow." / "Organic corn." / "Tastes amazing."

[COMPETITOR WEAKNESS 1-3]  - Each 2-6 words. Direct opposites.
                             e.g., "Uses seed oils." / "Pesticide corn." /
                                   "Doesn't even taste good."

No headline. No CTA. The table IS the argument.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a comparison grid ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: clean white throughout.

Top row divided 50/50 by a thin black vertical line:
- Left: the product (reproduced exactly from reference) packaging photographed clean on white with [DETAIL — chips spilling out / product mid-use / cap open]. Studio lit.
- Right: [COMPETITOR PRODUCT — generic competitor packaging, unbranded, photographed flat on white]. Both products at similar scale.

Below the product row: three horizontal attribute rows spanning the full width, separated by thin black horizontal lines. Each row divided 50/50 by the same vertical line:

Row 1: Left — "[YOUR ADVANTAGE 1]" / Right — "[COMPETITOR WEAKNESS 1]"
Row 2: Left — "[YOUR ADVANTAGE 2]" / Right — "[COMPETITOR WEAKNESS 2]"
Row 3: Left — "[YOUR ADVANTAGE 3]" / Right — "[COMPETITOR WEAKNESS 3]"

All text in bold black serif or heavy sans-serif, centered in each cell. No icons. No colors. No checkmarks. Only the copy contrast.

TYPOGRAPHY:
Per uploaded brand spec card. Heavy bold for every attribute line. Parallel structure. Serif for literary bite OR heavy sans for meme energy.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Pure white background. Black text and black lines. No accent color. The minimalism IS the meme.

MOOD:
Deadpan, confident, meme-ready. "No need to decorate this argument."
```

## Variation vectors

**Type style**: heavy serif (literary meme) | heavy sans-serif (modern meme, default) | condensed bold (tabloid) | italic bold (editorial)

**Row count**: 3 rows (default) | 4 rows | 5 rows (more attributes)

**Grid style**: thin black lines (default) | thicker black lines | no lines (just space) | boxed grid

**Product shot**: straight-on front (default) | slight 15° tilt | flat lay top-down

**Competitor framing**: generic unbranded (default) | category-labeled ("Other brand") | hand-drawn placeholder

**Energy**: deadpan minimal | confident direct | playful-meme | serious-evidence

## Format-specific rules

- **Never name real competitors.** Use generic unbranded packaging or category labels. Naming competitors creates legal risk.
- **Weaknesses must be true of the category.** Every claim verifiable. Agent 4 and Agent 7 flag fabrications.
- **Parallel structure.** Every your-advantage + competitor-weakness pair follows the same grammatical pattern.
- **No color, no icons.** The format depends on the minimalist aesthetic. Adding color ruins it.
- **Three rows is the sweet spot.** More rows dilute. Fewer feel thin.
- **Serif OR heavy sans — not both.** One type family carries the whole ad.

See `headline_template.md` for shared Global rules. See #07 and #25 for other Us-vs-Them variants.
