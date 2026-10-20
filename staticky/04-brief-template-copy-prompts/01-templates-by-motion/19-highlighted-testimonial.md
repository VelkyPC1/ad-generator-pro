# 19 — Highlighted / Annotated Testimonial

🏷️ The highlighter pen does the work. Long-form review text with key phrases visually emphasized. Directs the eye to the money lines.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Long-form customer quote set in large body copy across most of the frame. Key phrases are highlighted in neon-yellow / lime-green rectangular backgrounds (like a physical highlighter marker). Customer headshot + name top-left. Product bottom-right with a trust badge. The highlighter directs the eye to the "money lines" while the surrounding body provides full context.

## Copy template

```
{{reviewer}}         - First name + last initial, bold. Verified checkmark.

{{review_text}}            - 3-5 sentences of customer voice. Long-form, specific, emotional.

[HIGHLIGHT PHRASE 1]    - Key phrase from inside the quote. 2-5 words.
                          e.g., "changed my life" / "thyroid removed"

[HIGHLIGHT PHRASE 2]    - Second key phrase. 2-7 words.
                          e.g., "This is the best product I have found."

[TRUST BADGE]           - Circular seal.
                          e.g., "100% MONEY BACK / 90 DAYS / 100% GUARANTEE"
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a highlighted testimonial ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: clean white throughout.

Top-left: circular customer headshot photo of [PERSON DESCRIPTION — age, hair, wearing]. To the right of the photo: bold name "{{reviewer}}" with a [VERIFIED ICON — blue checkmark].

Below (spanning most of the frame): a long-form customer quote in large regular-weight black sans-serif: "{{review_text}}". Use real sentence rhythm and line breaks for readability.

Key phrases within the quote are highlighted with [HIGHLIGHT COLOR — bright lime green / neon yellow] rectangular background fills behind the text:
- "[HIGHLIGHT PHRASE 1]"
- "[HIGHLIGHT PHRASE 2]"

Highlights look like real marker-pen rectangles with slight irregularity (not perfect rectangles — imperfect as if hand-highlighted).

Bottom-right: the product (reproduced exactly from reference) at a slight angle, partially cropped at the bottom edge.

To the left of the product: a circular [TRUST BADGE — "100% MONEY BACK / 90 DAYS / 100% GUARANTEE"] seal in [BADGE COLOR — lime green / brand seal color] with dark text.

[BRAND] logo bottom-left corner, small.

TYPOGRAPHY:
Per uploaded brand spec card. Quote body at readable hero scale. Bold name secondary. Highlighter adds visual emphasis, not scale change.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Clean white background. Highlighter phrases in bright neon yellow or lime green. Photo realistic. Product color-graded per visual style card.

MOOD:
Honest, considered, evidence-based. "Here's someone's real story — the parts that matter are highlighted."
```

## Variation vectors

**Highlight color**: neon yellow (default) | lime green | pastel pink | brand accent color

**Highlight phrase count**: 1 phrase (focused) | 2 phrases (default) | 3 phrases (heavier emphasis)

**Headshot style**: circular crop photo (default) | square crop | initials-only if no headshot | illustrated avatar

**Trust badge type**: money-back guarantee (default) | certification seal | category award | brand-specific badge

**Quote length**: 3 sentences (tight) | 4-5 sentences (default) | 6+ sentences (info-dense but risks bloat)

**Quote tone**: emotional story arc | practical-skeptical conversion | medical/clinical with specifics | community-voice casual

## Format-specific rules

- **Highlights must land on the strongest phrases.** The reader's eye jumps to highlights first — so highlights carry the ad on their own. Test: if you only read the highlighted phrases, is the argument still clear?
- **Highlighter imperfection is the point.** Perfect rectangles read as design. Slight rotation, slight over/under reach feels real.
- **Quote must be real.** Agent 4 and Agent 7 both flag invented testimonials. Pull from actual customer reviews with permission.
- **Headshot must match persona.** If your persona is 65-year-old women but the headshot is 25-year-old woman, the format breaks trust.
- **Trust badge + product overlap is the closer.** Don't place them in separate quadrants — they should be a visual unit at the bottom-right.

See `headline_template.md` for shared Global rules.
