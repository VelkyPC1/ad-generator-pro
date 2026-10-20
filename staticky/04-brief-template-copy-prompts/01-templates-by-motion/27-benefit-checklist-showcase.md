# 27 — Benefit Checklist Showcase (Split Product + Info)

🏷️ Split composition. Product reveal on the left (overhead). Review count + benefit checklist + CTA on the right.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Split 45/55 composition. Left: overhead product reveal (e.g., bowl divided into labeled sections, box opened to reveal contents). Right: star rating + review count, brand logo, brand-color headline, 3 checkmark benefit rows, and a rounded CTA button. Works for products with multiple visible variants or compartmentalized offerings.

## Copy template

```
[STAR RATING + REVIEW COUNT]   - 5 gold stars + "[X]+ REVIEWS"
                                 e.g., "10,000+ REVIEWS"

{{headline}}                      - 3-6 words. Brand-color serif or sans.
                                  e.g., "Made for the pickiest dogs" /
                                        "Everything your skin needs"

[BENEFIT 1-3]                   - Each 3-8 words. Bold, parallel structure.
                                  e.g., "Head-turning aroma"
                                        "No additives, flavors, or preservatives"
                                        "Ready to serve from the pouch"

{{cta}}                           - 2-4 words. In a rounded button.
                                  e.g., "SHOP NOW" / "START YOUR TRIAL"

[VARIETY LABELS 1-4]            - If product shows compartments, each section labeled.
                                  e.g., "CHICKEN & YAMS / BEEF N' RICE / SALMON N' RICE"
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a benefit checklist showcase ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Split composition.

Left 45%: overhead product shot — [PRODUCT DISPLAY — a white bowl filled with fresh dog food divided into labeled sections by thin white lines, each section labeled in curved white text "[VARIETY 1]" / "[VARIETY 2]" / "[VARIETY 3]" / "[VARIETY 4]" — OR a product box opened to reveal contents — OR a jar with lid off showing texture]. Shot on 50mm f/4, clean white surface, even studio lighting.

Right 55%: white background. Top: [STAR RATING — five filled gold stars] with "[REVIEW COUNT]" in [BRAND COLOR from spec card]. Below: [BRAND] logo.

Below the logo: [BRAND COLOR] serif or sans-serif headline "{{headline}}".

Below the headline: 3 checkmark benefit rows, each with a filled [BRAND COLOR] circle checkmark + bold text:
- "[BENEFIT 1]"
- "[BENEFIT 2]"
- "[BENEFIT 3]"

Bottom right: large rounded [ACCENT COLOR from spec card] CTA button with white text "{{cta}}".

TYPOGRAPHY:
Per uploaded brand spec card. Headline serif for warmth (or sans for modern), benefits in bold sans. CTA button white text on accent color.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Clean white background throughout. Product reveal hero-lit. Benefits in brand primary color, CTA in accent.

BRAND IDENTITY:
[BRAND] logo top-right of the info zone.

MOOD:
Informational, trustworthy, shop-ready. "Here's what it is, here's why, here's how to buy."
```

## Variation vectors

**Product reveal style**: divided bowl / sections (default, for food) | box open showing contents | jar with lid off | flat lay of variety pack | product with cap removed

**Variety / label count**: 3 labels | 4 labels (default) | 5 labels | no labels (single-variant product)

**Headline font**: brand serif (warm) | brand sans (modern) | italic (elevated)

**Benefit count**: 3 rows (default) | 4 rows | 5 rows (info-dense)

**CTA button style**: rounded filled (default) | outlined | full-width bar | pill-shaped

**Energy**: warm and trustworthy | clean and clinical | premium and elevated | friendly and accessible

## Format-specific rules

- **Overhead reveal is the hero.** If the product can't be shown overhead with visible contents, use a different format.
- **Parallel structure across benefits.** All three benefits follow the same grammatical pattern.
- **Review count must be real.** Don't fabricate "10,000+ reviews" if the brand has 500.
- **CTA button is functional, not decorative.** In real campaigns this is the click target — style it clearly.
- **Variety labels must match brand SKUs.** If the bowl is divided into 4 flavors but only 2 exist, the format lies.

See `headline_template.md` for shared Global rules.
