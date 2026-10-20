# 21 — Bold Statement / Reaction Headline

🏷️ Pure brand energy. No stats. No reviews. Just a provocative line, a hot gradient, and the product. The copy IS the ad.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Vibrant diagonal gradient background. Oversized playful headline in the upper-left (Cooper Black / rounded retro feel). A hand reaching into the product from the upper right. The product sits center-right. No stats, no reviews, no badges. Pure brand voice and personality. Works for brands with strong character where the line alone can carry the ad.

## Copy template

```
[BOLD STATEMENT]   - 4-10 words. Playful, expressive, voice-forward.
                     Can include mild profanity if brand allows (or self-censor with *****).
                     e.g., "This popcorn is so f*****g delicious."
                           "Smells like clean laundry. Tastes like candy."
                           "We said what we said."

[PRODUCT DESCRIPTOR] - Smaller text beneath logo at bottom.
                       e.g., "Flavor Wrapped Popcorn Kernels"

No headline + subhead hierarchy. One statement does everything.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a bold statement ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: vibrant [GRADIENT from variation — coral-pink to golden-yellow / sunset orange to purple / brand primary to accent] flowing diagonally from upper left to lower right.

Upper-left: oversized playful [FONT STYLE from variation — rounded retro serif / Cooper Black / heavy italic / brand display font] white headline "[BOLD STATEMENT]". Text feels loose, fun, expressive — not rigid or corporate.

Right side: [PERSON DETAIL — a hand reaching down from upper right / a hand grabbing from below] engaging with [YOUR PRODUCT — the signature packaging / signature bowl / product display]. Product sits center-right, slightly below the midline, reproduced exactly from reference.

Bottom-left: [BRAND] logo in [LOGO COLOR from spec card — black / white / accent] with "[PRODUCT DESCRIPTOR]" in smaller text below.

No stats. No reviews. No badges. Gradient and headline carry the whole ad.

TYPOGRAPHY:
Per brand spec card. Use brand's display/personality font (not a clean sans-serif). Headline weight and scale dominate. The font choice IS the energy.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Saturated diagonal gradient. White headline for contrast. Product naturally lit with subtle shadow. Hand comes in from frame edge, partially cropped.

BRAND IDENTITY:
[BRAND] logo bottom-left per spec card.

MOOD:
Loose, fun, confident. The brand is cracking a joke and doesn't need to explain it.
```

## Variation vectors

**Gradient**: coral-to-yellow (default) | sunset orange-to-purple | pink-to-red | brand primary-to-accent | two-tone hard split

**Font personality**: Cooper Black / rounded retro | italic bold script | heavy condensed sans | brand display

**Hand position**: upper-right reaching down (default) | lower-left reaching up | bottom reaching up | no hand (product alone)

**Product position**: center-right (default) | center-left | bottom-centered | floating upper-right

**Profanity level**: explicit (brand allows) | censored with asterisks | implied without profanity | safe confident line

**Energy**: playful and irreverent | confident and bold | warm and friendly | cheeky and knowing

## Format-specific rules

- **Brand voice must be on-brand.** Irreverent headlines require a brand with established irreverent voice. Don't bolt this format onto a premium/clinical brand.
- **Gradient must match brand palette.** If the brand uses muted earth tones, a hot coral gradient breaks identity. Use gradients from the brand spec card.
- **Font personality is non-negotiable.** A clean Helvetica headline kills the format. Use a display / personality font.
- **Profanity rule.** Follow brand guidelines. Censor with asterisks if platform or market requires it.
- **Agent 4 flags this for luxury / clinical / medical brands.** Know your brand fit before using.

See `headline_template.md` for shared Global rules.
