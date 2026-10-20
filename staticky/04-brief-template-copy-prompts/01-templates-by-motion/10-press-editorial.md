# 10 — Press / Editorial

🏷️ Authority play. Vogue back-page energy.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for 4:5)
- **bottom_safe_zone:** 340px (scaled for 4:5)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A full-page magazine editorial layout. Small "As Featured In" tag at the top, a horizontal row of grayscale press-style mastheads, a large italic serif pull-quote with attribution in the center, and a premium product shot in the lower third. Generous white space. Linen or off-white background. Reads like a back-page ad in Vogue, Kinfolk, or a high-end editorial.

## Copy template

```
[AS FEATURED IN TAG]   - "As Featured In" (or localized equivalent, e.g., "O nás píšu").
                         Small caps, wide-tracked.

[PRESS QUOTE]          - 8-20 words. Italic serif, the best available press line.
                         Must be a real quote from a real publication.

{{reviewer}}          - Publication name + optional date. e.g., "— Vogue, 2025"

{{cta}}                  - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create an editorial press ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame. Background: off-white linen or soft cream texture, evenly lit, generous negative space.

Top: small [BRAND COLOR from spec card] uppercase wide-tracked text "[AS FEATURED IN TAG]" centered.

Below the tag: a horizontal row of five grayscale publication-style mastheads (generic editorial word-marks — do not reproduce real publication logos without documented press placements and rights).

Center: italic serif pull-quote in [BRAND COLOR] or dark charcoal: "[PRESS QUOTE]". Set large, centered, with soft curly quotation marks. Below the quote: "{{reviewer}}" in smaller regular weight italic.

Lower third: the product (reproduced exactly from reference) at 85mm f/2.8, soft side light, sitting on the linen surface with subtle shadow. Occupies ~25% of the frame, off-centered slightly to feel editorial rather than catalog.

[BRAND] logo bottom left in small wide-tracked caps per brand spec card.

[If CTA]: "{{cta}}" styled per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Editorial serif for the pull-quote. Sans-serif small caps for the tag and attribution. Generous line-height. Everything feels considered, not busy.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Off-white or cream linen. Brand color used sparingly (tag, pull-quote, logo). Product color-graded warm.

BRAND IDENTITY:
[BRAND] logo bottom left, small.

PHOTOGRAPHY DIRECTION:
Per visual style card. Product shot like a magazine product-placement page — not a catalog.

MOOD:
Established, elevated, quiet authority. "We don't need to shout."
```

## Variation vectors

**Background**: off-white linen (default) | warm cream | pale gray-beige | soft paper texture

**Masthead row**: 5 grayscale word-marks (default) | 3 prominent | single hero masthead ("ELLE calls it...") | text-only publication names

**Product position**: lower third centered | lower right corner | lower left with quote right | flat lay top-down in lower third

**Quote style**: italic serif (default) | bold serif (louder) | light regular serif (minimal)

**Lighting**: soft side light (default) | overhead diffused | warm window light | muted studio

**Energy**: quiet authority | elevated and aspirational | confident and refined

## Format-specific rules

- **Real press only.** Do not fabricate quotes, publications, or coverage. Agent 4 and Agent 7 both veto invented press.
- **Rights to logos.** Real publication masthead reproduction requires rights. Default to generic editorial word-marks unless the brand has documented permission.
- **One quote per ad.** Layering three press quotes clutters the editorial feel. If the brand has multiple press hits, either pick the strongest or rotate variants.
- **Negative space is structural.** Don't fill corners. The format earns its authority from confident emptiness.
- **Brand must actually be premium.** A value brand using this format reads as inauthentic. Check brand spec before using.

See `headline_template.md` for shared Global rules.
