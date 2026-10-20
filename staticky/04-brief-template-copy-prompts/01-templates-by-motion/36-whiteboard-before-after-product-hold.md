# 36 — Whiteboard Before / After + Product Hold

🏷️ Casual kitchen photo. Hand-drawn whiteboard shows before/after outlines with an arrow. Hand holds the product in the foreground. Homemade educational feel.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 340px (scaled for aspect)
- **bottom_safe_zone:** 430px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. This should look like a real person's casual photo, NOT an ad."*

## What this format is

A lifestyle photo in a bright everyday setting (kitchen, living room). In the background: a small whiteboard propped on the counter with two hand-drawn marker illustrations side by side — a "before" outline and an "after" outline with an arrow between them — plus a handwritten CTA below. In the foreground: a person's hand holding the product up next to the whiteboard. Feels homemade, educational, earnest. Works for transformation / health / body categories.

## Copy template

```
[BEFORE LABEL]      - 1-3 words. Handwritten on whiteboard above drawing.
                      e.g., "De esto..." / "Before." / "Week 1"

[AFTER LABEL]       - 1-3 words. Handwritten on whiteboard above drawing.
                      e.g., "A esto!" / "After." / "Week 8"

[HANDWRITTEN CTA]   - 6-15 words. One hand-written line below the drawings.
                      e.g., "If you want progress during menopause, you need this!"

No typeset headline. No designed CTA button. No brand logo overlay. Everything on the
whiteboard is handwritten marker. The product packaging in the foreground carries the brand.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. This should look like a real person's casual photo, NOT an ad.

Create a whiteboard before/after + product hold ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350, 4:5].

COMPOSITION:
One continuous image filling the entire frame. Setting: [SETTING — a bright modern kitchen / a sunny living room / a minimalist home office] with natural daylight.

Background plane: a small tabletop dry-erase whiteboard or flip-chart propped up on [SURFACE — a marble countertop / a wooden shelf / a kitchen island]. On the whiteboard, two simple hand-drawn black marker line illustrations side by side:
- Left drawing labeled "[BEFORE LABEL]" showing [BEFORE STATE — a bloated midsection outline with dots / a tired-looking figure / a rough skin texture diagram]
- Arrow drawn from left to right between the drawings
- Right drawing labeled "[AFTER LABEL]" showing [AFTER STATE — a flatter smoother midsection outline / an energized figure / smooth skin diagram]

Below the drawings on the whiteboard: a handwritten black marker line "[HANDWRITTEN CTA]". Natural marker strokes, slightly uneven, not perfect calligraphy.

Foreground: [PERSON'S HAND — a woman's hand / a man's hand, natural skin, no polish] holding the product (reproduced exactly from reference) up next to the whiteboard, positioned in the lower-right (or lower-left) of the frame at a natural angle. Product label clearly visible. Hand relaxed, not posed.

Shot on iPhone-quality camera, natural [SETTING] lighting, casual and educational. Slight sensor grain. Depth-of-field shallow enough that the whiteboard is readable but soft in the background, product and hand sharp in the foreground.

TYPOGRAPHY:
Whiteboard text is all handwritten marker — NO typeset fonts. Brand spec card typography does not appear in this ad.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Natural iPhone photo palette. Whiteboard marker in black only (one marker color). Product in its natural packaging colors.

MOOD:
Educational, homemade, earnest. "A friend is explaining this to you in her kitchen."
```

## Variation vectors

**Setting**: modern kitchen (default) | bright living room | home office | bathroom counter | bedroom vanity

**Before/after subject**: body outline (default) | skin close-up | hair texture | energy-level figure | posture diagram

**Whiteboard type**: small dry-erase board (default) | flip-chart pad | chalkboard | paper pad on easel | notebook page

**Marker style**: black single-marker (default) | black + one brand-color accent | full chalk | pencil sketch feel

**Hand placement**: lower-right (default) | lower-left | center holding toward camera | upper-corner casual

**Energy**: educational and earnest | casual and friendly | warm and confident | "mom explaining" tone

## Format-specific rules

- **Must not look designed.** Typeset fonts, clean vectors, designed arrows = broken format. Everything on the whiteboard is imperfect marker.
- **Before / after must be category-appropriate.** Body-transformation imagery triggers platform ad rules in many markets. Verify compliance before shipping (Meta, TikTok, Google all restrict this).
- **One marker color.** Mixing marker colors on the whiteboard makes it feel designed. One black marker (plus optional one accent) looks real.
- **Hand is natural, not prop-staged.** Loose grip, relaxed fingers. Not a "product shot with hand glued on."
- **Product label must be readable.** If the packaging is blurred or angled wrong, the ad fails to brand.
- **Handwriting style consistent.** All labels + CTA look like the same person's writing.

See `headline_template.md` for shared Global rules. See #08 for UGC-native before/after variant.
