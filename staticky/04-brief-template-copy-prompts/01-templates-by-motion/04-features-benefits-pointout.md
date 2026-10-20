# 04 — Features / Benefits Point-Out

🏷️ Educational diagram-style layout.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for 4:5)
- **bottom_safe_zone:** 340px (scaled for 4:5)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

An educational, diagram-style ad. The product sits centered like a specimen. Four callout boxes with connecting lines fan out, each naming one feature-to-benefit. Clean white background. Looks like a luxury-agency redesign of a scientific diagram. Works when the product has concrete, nameable features that translate to benefits (ingredient X → benefit Y).

## Copy template

```
[HEADER]        - 4-8 words. The overarching claim that frames the diagram.
                  e.g., "What Makes [PRODUCT] Different" / "Engineered for [BENEFIT]"

[BENEFIT 1-4]   - Each 2-6 words. Feature → benefit, one per callout.
                  Parallel structure across all four.
                  e.g., "Ceramides repair barrier" / "pH 5.5 balances skin"

[WEBSITE]       - Optional. Bottom center. "brand.com"

{{cta}}           - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a diagram-style educational ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame. Clean white background throughout. Top: bold [BRAND COLOR from spec card] sans-serif header "[HEADER]" centered, at clear primary hierarchy.

Center: the product (reproduced exactly from reference) photographed centered, even studio lighting with minimal shadow, occupying roughly 35% of the visual frame. Product should read as the "specimen" under inspection.

Four callout boxes fan out from the product (top-left / top-right / bottom-left / bottom-right). Each callout:
- A thin [BRAND COLOR] line connecting from a precise point on the product to the callout text
- A small [BRAND COLOR] filled circle at the product-side end of the line
- Callout text "[BENEFIT N]" in bold dark sans-serif, left-aligned

"[WEBSITE]" in small text centered at the very bottom of the frame.

TYPOGRAPHY:
Per uploaded brand spec card. Header dominates. Callout labels at tertiary scale — readable but clearly subordinate to the product.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White background, brand color for header + lines + circles. No decorative colors. Clean, informational, clinical.

BRAND IDENTITY:
[BRAND] logo bottom right per spec card.

PHOTOGRAPHY DIRECTION:
Product shot at 50mm f/4, even studio lighting, minimal shadow. This is a specimen shot — crisp, honest, clinical.

MOOD:
Scientific diagram redesigned by a luxury agency. Authoritative. Educational.
```

## Variation vectors

**Callout count**: 3 callouts (simpler) | 4 callouts (default) | 5 callouts (complex product)

**Callout position**: four corners (default) | all left side (list-style) | top-and-bottom only | radial 360°

**Line style**: straight with right angle | gently curved | diagonal straight

**Product angle**: straight-on front | slight 15° three-quarter | flat lay from above

**Benefit framing**: feature-led ("Ceramides repair barrier") | benefit-led ("Barrier-repairing formula") | mechanism-led ("Clinically proven pH 5.5")

**Background**: pure white | off-white/cream | pale brand-tinted | subtle texture (linen, paper)

## Format-specific rules

- **Parallel structure.** All callouts follow the same grammatical pattern. Mixing "Repairs barrier" with "For deeper hydration" breaks scanability.
- **One concept per callout.** Don't cram two benefits into one line — use a separate callout.
- **Lines must connect to real product points.** An ingredient callout should originate from the label; a texture callout from the visible texture. Arbitrary lines break credibility.
- **White space is structural.** Don't fill the corners — negative space signals authority in this format.

See `headline_template.md` for shared Global rules.
