# 03 — Testimonials

🏷️ Real environments + text overlays. Tests composition depth.

## Metadata

- **aspect_ratio:** 9:16 default (1080x1920) | 4:5 alt (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (for 9:16)
- **bottom_safe_zone:** 340px (for 9:16)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."* Non-negotiable.

## What this format is

A testimonial set in the persona's real environment — bathroom, kitchen, desk, gym bag. The product sits naturally in that scene (slightly out of focus). The quote is the hero: a short pull-line, a longer quote body, attribution with credential, and a star rating. Works because the setting makes the endorsement feel real, not staged.

## Copy template

```
[SHORT HEADLINE]   - 3-8 words. The pull-line distilled from the full quote.
                     The most emotional / specific fragment of the testimonial.

{{review_text}}       - 2-3 sentences. First-person, conversational, specific.
                     Avoid marketing language — it should sound like how a real person talks.

{{reviewer}}      - Name + credential. e.g., "Dr. Lisa M., Dermatologist" / "Anna K., mama 3 detí".

[STAR RATING]      - 5 filled brand-color stars. Not optional in this format.

{{cta}}              - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a testimonial ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO].

COMPOSITION:
One continuous image filling the entire frame. Scene: [SETTING from variation selection — bright bathroom / modern kitchen / sunlit desk / gym bag on bench / morning nightstand] with warm natural light from a window. The product (reproduced exactly from reference) rests on [SURFACE — marble counter / wood desk / tile / soft fabric], slightly out of focus in the background third of the frame. The persona is implied, not shown — this is their environment captured honestly.

Overlaid text:
- Large bold white sans-serif "[SHORT HEADLINE]" in the brand's headline font, positioned [TEXT POSITION — upper third | centered | bottom above CTA].
- Below: "{{review_text}}" in smaller weight, 2-3 lines wrapping naturally.
- Below the quote: "{{reviewer}}" in smaller italic or light weight.
- Five filled [BRAND COLOR] star icons in a horizontal row, placed between the pull-line and the body quote OR below the attribution.

[If CTA]: "{{cta}}" styled per brand spec card at the bottom.

TYPOGRAPHY:
Per uploaded brand spec card. Pull-line holds primary hierarchy. Quote body readable against the lifestyle backdrop — if the background behind text is busy, use subtle shadow or semi-transparent backing, not a heavy overlay. Shot on 35mm f/2.0 for environmental authenticity.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Scene color-graded per visual style card. Natural, not stock-photo generic. Product recognizable but not artificially highlighted.

BRAND IDENTITY:
[BRAND] logo bottom right in white or brand color per spec card.

MOOD:
[ENERGY — warm and trustworthy | confident and clinical | aspirational and elevated | relatable and casual]. Feeling: a real person saying something real.
```

## Variation vectors

**Setting**: bright bathroom morning | warm kitchen with coffee | sunlit desk | gym bag on bench | bedside nightstand | outdoor patio

**Text position**: top third (quote above product) | centered overlay | bottom third (product leads, quote below) | left-aligned with product on the right

**Quote length**: pull-line only (fragment, most emotional 4-6 words) | short body (1 sentence) | full body (2-3 sentences)

**Credential weight**: first name + last initial only | full name + role | full name + role + location | anonymous with persona tag (e.g., "Mama 2 detí, 34")

**Lighting**: soft natural from window | warm golden hour indoor | bright even daylight | late-afternoon slanted

**Energy**: warm and trustworthy | clinical and confident | aspirational | relatable casual

## Format-specific rules

- **Setting must match the persona.** A bathroom testimonial for a hair brand, a kitchen for a supplement, a desk for productivity. Mismatched setting breaks the trust effect instantly.
- **Attribution is non-optional.** A quote without a name reads as manufactured. Always give the testimonial a face, even if it's just a first name + last initial.
- **No stock-photo smiles.** The scene should feel captured, not posed. If you must show a person, they're mid-task, not looking at the camera.
- **Stars are part of the format.** If brand guidelines don't allow star ratings, switch to a different template — this format needs them.

See `headline_template.md` for shared Global rules (visual-copy coherence, Agent 7 checklist, price-is-not-default).
