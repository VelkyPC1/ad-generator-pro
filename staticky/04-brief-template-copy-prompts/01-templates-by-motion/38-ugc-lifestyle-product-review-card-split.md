# 38 — UGC Lifestyle + Product + Review Card (Split)

🏷️ Lifestyle UGC photo on the left, saturated brand-color zone on the right with product + 5-star review card. Social proof meets aspirational scene.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 340px (scaled for aspect)
- **bottom_safe_zone:** 430px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo (visible both in the lifestyle photo and in the product shot on the color panel), do not invent or alter shape, color, labels, or design."*

## What this format is

Vertical split social proof ad. Left 55%: casual UGC photo of a person enjoying the product in context (sipping, applying, eating). Right 45%: solid brand-color panel with the product studio-lit and a white rounded review card below — 5 stars + short quote + brand logo at the bottom. Small sparkle/star decorative accents. Warm social proof meets design polish.

## Copy template

```
[REVIEW QUOTE]      - 6-12 words in quotes. Italic or casual serif.
                      e.g., "I will never get drive-thru coffee again" /
                            "This replaced five products in my routine"

[STAR RATING]       - 5 filled accent-color stars above the quote.

[BRAND LOGO]        - Lockup at bottom-center in white on the brand-color panel.

No headline. No CTA. The lifestyle photo + review card do the selling.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo (visible both in the lifestyle photo and in the product shot on the color panel), do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a UGC lifestyle + product + review card split ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350, 4:5].

COMPOSITION:
One continuous image filling the entire frame. Vertical split.

Left 55%: casual UGC-style photo of [PERSON — e.g., a blonde woman in her early 30s in a casual zip-up sweater / a young man in a linen shirt / a friend group at a café] enjoying the product in real context. [ACTION — sipping an iced drink through a gold metal straw in a bright café / applying skincare in a bathroom mirror / eating the product at a breakfast table]. Natural lighting, warm and inviting, iPhone-quality casual feel. Person looks genuinely happy — not posed smile. Product (reproduced exactly from reference) visible and readable in their hand or on the surface.

Right 45%: solid [PRIMARY BRAND COLOR — deep indigo / purple / brand saturated] background. Top-right: small decorative sparkle / star accents in [ACCENT COLOR — gold / yellow / brand accent].

Floating center-right: the product (reproduced exactly from reference) at a slight angle, studio-lit on the colored background. Clean shadow underneath grounding it.

Below the product: a white rounded-rectangle review card with:
- Five filled [ACCENT COLOR] stars at the top, centered.
- Italic or casual serif review text in [BRAND DARK COLOR]: "[REVIEW QUOTE]"

Bottom center of the right panel: [BRAND LOGO] in white, small, with tiny sparkle accents on either side.

TYPOGRAPHY:
Per uploaded brand spec card. Review text italic serif or soft casual serif for warmth. Brand logo per lockup.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Left panel warm and natural. Right panel saturated brand color with accent sparkles. White review card floats crisply.

MOOD:
Aspirational meets credible. "A real person loves this, and it looks beautiful."
```

## Variation vectors

**Lifestyle action**: sipping drink (default) | applying skincare | eating the product | cooking with it | wearing / using it

**Person description**: woman early 30s casual (default) | man in casual wear | friend group | older customer | mom with child

**Setting**: bright café (default) | home bathroom / mirror | kitchen counter | outdoor patio | bedroom morning light

**Brand color saturation**: deep indigo (default) | saturated brand primary | pastel brand | jewel-tone

**Decorative accents**: sparkles + stars (default) | small hand-drawn doodles | confetti specks | none (cleaner)

**Review tone**: casual first-person | premium editorial | funny / memorable | specific problem-solved

**Energy**: warm aspirational | crisp premium | friendly casual | editorial confident

## Format-specific rules

- **Person must look happy naturally.** Posed smiles = ad energy. Candid enjoyment = UGC energy.
- **Product readable in both zones.** If the left-photo product is blurred or too small, the brand-recognition fails.
- **Review must be real or paraphrased from real feedback.** Fabricated quotes break trust and law.
- **Stars and logo use accent colors consistently.** Don't have gold stars with a silver logo — one accent language.
- **Color panel saturation matters.** Muted = boring. Too neon = cheap. Hit the brand's saturated primary.
- **Review card floats.** If the card is flush with panel edges, it looks like a banner. Give it breathing room.

See `headline_template.md` for shared Global rules. See #11 and #17 for review-card variants.
