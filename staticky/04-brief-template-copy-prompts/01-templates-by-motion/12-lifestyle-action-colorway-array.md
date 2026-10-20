# 12 — Lifestyle Action + Product Colorway Array

🏷️ Action hero shot sells the use case. Fanned product lineup sells the range. Two conversion jobs in one frame.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image (multiple colorways ideally)
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A lifestyle action shot (person mid-use) occupies the left two-thirds. Product colorway array (3+ variants fanned) overlays the bottom-right foreground. An endorsement-style quote headline sits prominently. Works for products that sell in multiple colors/flavors/variants where the use case needs to be shown AND the range needs to be communicated.

## Copy template

```
[ENDORSEMENT HEADLINE]   - 4-10 words in quotation marks.
                           A bold endorsement or category-defining claim.
                           e.g., "THE GREATEST PANTS IN GOLF" / "THE ONLY COFFEE I DRINK"

[BRAND LOGO]             - Top center. Bold sans-serif.

{{cta}}                    - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a lifestyle action + colorway array ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Left two-thirds: a lifestyle photo of [PERSON DESCRIPTION + ACTION — e.g., "man mid-golf-swing in a tropical patterned polo and khaki pants"] shot outdoors in [SETTING — e.g., "golf course with palm trees / beach boardwalk / urban rooftop"]. Bright natural daylight. Shot on 50mm f/2.0 with lifestyle background slightly softer than the foreground product.

Top center: [BRAND] logo in bold sans-serif white or brand-color.

Below logo: large bold sans-serif quote text "[ENDORSEMENT HEADLINE]" in [TEXT COLOR — white or black per contrast with the background]. The quote reads as an endorsement from the implied person in the scene or from category authority.

Bottom-right foreground: three (or four) [PRODUCT VARIANTS — folded pairs, lined bottles, stacked boxes] fanned in an overlapping arrangement showing [COLOR 1], [COLOR 2], [COLOR 3]. Products crisp and studio-lit against the lifestyle background — not color-graded to match the scene.

[If CTA]: "{{cta}}" styled per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Endorsement headline dominant. Logo wordmark next. Quote reads like a magazine caption, not a sales headline.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Lifestyle scene color-graded per visual style card. Product array stays studio-clean — the color variants should POP visually against the lifestyle backdrop.

BRAND IDENTITY:
[BRAND] logo top center, bold.

MOOD:
[ENERGY — confident, athletic, aspirational but accessible | premium and refined | casual and fun | adventurous].
```

## Variation vectors

**Action type**: mid-motion sport (swing, run, jump) | mid-use (sipping, applying, wearing) | social scene (group, couple, family)

**Variant count**: 3 variants (default) | 4 variants | 5+ variants (for ranges with many SKUs)

**Array arrangement**: fanned overlap (default) | linear horizontal | stacked vertical | spiral/radial fan

**Setting**: outdoor natural | urban/architectural | beach/travel | domestic interior | sports venue

**Endorsement framing**: quoted pull-line with attribution implied | unattributed declaration | category-defining ("THE ONLY X I DRINK")

**Energy**: confident and athletic | aspirational lifestyle | casual and warm | premium refined

## Format-specific rules

- **Action must be real.** If the brand is about golf, the swing must look like a golfer's swing. Generic posed shots kill the format.
- **Variants must be distinct.** If your product comes in 3 shades of beige, the array fails visually. Use variants with clear color differences.
- **Product wins the foreground.** Even though the action is left, the product array must read as the hero when the viewer's eye lands. Studio-light the products harder than the scene.
- **Endorsement headline must NOT overlap the person's face.** Place it in negative space above or beside the subject.
- **Brand must sell in true variants.** Don't fake a colorway array when the product only comes in one version — Agent 4 flags inauthentic range claims.

See `headline_template.md` for shared Global rules.
