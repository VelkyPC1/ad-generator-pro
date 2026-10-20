# 02 — Offer / Promotion

🏷️ The money-maker. Tests the core offer.

## Metadata

- **aspect_ratio:** 9:16 default (1080x1920) | 4:5 alt (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (for 9:16)
- **bottom_safe_zone:** 340px (for 9:16)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."* Non-negotiable.

## What this format is

A direct-response offer ad. The headline IS the offer. The product anchors the frame. A color split between primary brand color and a contrast color creates visual stopping power. Works when the offer itself is strong enough to be the whole argument — free trial, percentage off, bundle pricing, money-back guarantee.

## Copy template

```
[OFFER HEADLINE]       - 3-8 words. The offer in its clearest form.
                         e.g., "YOUR FIRST MONTH FREE" / "40% OFF THIS WEEK"

[OFFER DETAILS]        - 5-12 words. The terms, qualifier, or mechanism.
                         e.g., "No subscription required" / "On orders over $50"

[VALUE ADDS]           - Optional. 3-6 words. Secondary benefits in small text.
                         e.g., "Free shipping + free returns"

{{cta}}                  - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a promotional ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1920 / 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame. Split background: top [60%] is [PRIMARY BRAND COLOR from spec card] and bottom [40%] is [CONTRAST COLOR — warm cream / off-white / light accent]. The product (reproduced exactly from the reference image) sits centered where the two colors meet, occupying roughly 35-45% of the frame. Soft studio lighting from upper-left, subtle shadow grounding the product on the lower color.

Upper area (on primary brand color): large [CONTRAST COLOR] sans-serif headline "[OFFER HEADLINE]" in the brand's headline font, positioned in the top [TEXT POSITION — third | centered in upper half | left-aligned]. Below the headline: "[OFFER DETAILS]" at ~40-50% of the headline's visual weight.

Lower section (on contrast color): small [PRIMARY BRAND COLOR] text "[VALUE ADDS]" center or left-aligned. [If CTA]: "{{cta}}" styled per brand spec card CTA treatment at the very bottom.

TYPOGRAPHY:
Per uploaded brand spec card. Offer headline at maximum scale the frame allows while keeping safe zones. Contrast between text and background must be immediately readable even at small preview size.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear of critical content.

COLOR AND TREATMENT:
Hard color split — no gradient unless brand spec explicitly uses gradients. The split line sits roughly behind the product's midpoint. Lighting: soft studio, clean and commercial.

BRAND IDENTITY:
[BRAND] logo bottom right per spec card rules.

MOOD:
[ENERGY — confident and urgent | celebratory | premium and restrained | bold and direct]. Feeling: the offer is too good to scroll past.
```

## Variation vectors

**Color split ratio**: 60/40 top-bottom | 50/50 | 70/30 top-bottom | diagonal split | vertical split left/right

**Headline weight**: ultra-bold caps | italic serif emphasis | mixed-case with one word larger | stacked line-break rhythm

**Product angle**: straight-on hero | 15° three-quarter | flat lay from above | product-in-hand

**Offer framing**: % off | free trial / first month free | bundle price | guarantee-led (money-back, free returns) | time-limited flash

**Lighting**: soft studio commercial | bright even daylight | warm golden accent | dramatic with contrast

## Format-specific rules

- **Offer must be singular.** One headline offer. Do not stack multiple discounts in the headline ("40% OFF + FREE SHIPPING + FREE GIFT") — pick the lead offer, put the rest as value adds.
- **Price discipline.** If the offer mentions dollars, use whole dollars ($49 not $49.00) unless cents matter. Every data point appears once — no duplicate prices across elements.
- **Color split must match brand palette.** Don't invent a contrast color — use one from the brand spec card.

See `headline_template.md` for the shared Global rules section (visual-copy coherence, Agent 7 copy editor checklist, price-is-not-default, fewer-elements-by-default).
