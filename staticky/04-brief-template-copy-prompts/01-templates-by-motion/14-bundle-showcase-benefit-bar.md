# 14 — Bundle Showcase + Benefit Bar

🏷️ Sells the system, not the SKU. The open box is the hero. The benefit bar handles the "what's in it for me."

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image (bundle / multi-SKU)
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

An open bundle/gift box as the hero, photographed slightly overhead, revealing multiple products nested inside. A horizontal benefit bar (5 segments) sits above the product. A lifestyle prop (hand, dumbbell, flower) enters from the foreground. Gradient background. Works for bundle SKUs, gift sets, routine kits, or any product sold as a system.

## Copy template

```
{{headline}}           - 3-6 words, all caps. Bold claim about the system.
                       e.g., "24/7 PEAK FEMALE PERFORMANCE" / "THE COMPLETE MORNING ROUTINE"

[BENEFIT 1-5]        - Each 1-3 words (strict). In a horizontal banner bar.
                       e.g., "Morning Energy" / "Focus Amplifier" / "Deep Sleep" /
                             "Ultimate Beauty" / "Metabolism Booster"

{{cta}}                - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a bundle showcase ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: [BACKGROUND from variation — soft pink-to-hot-pink gradient / brand pastel-to-saturated gradient / brand solid] flowing from top to bottom.

Top: oversized bold white all-caps sans-serif headline "{{headline}}".

Below the headline: a horizontal [ACCENT COLOR from spec card — purple/violet/brand contrast] banner bar divided into [NUMBER — 3 to 5] equal segments separated by thin vertical lines. Each segment contains one 1-3 word benefit label in white text: "[BENEFIT 1]", "[BENEFIT 2]", "[BENEFIT 3]", "[BENEFIT 4]", "[BENEFIT 5]".

Center-to-bottom: an open [PACKAGING — branded gift box / kit tray / bundle sleeve] photographed at a slight overhead angle, revealing [NUMBER — 2 to 4] [PRODUCTS — supplement jars, skincare bottles, SKUs] nested inside. Each product a different color-coded variant reproduced exactly from reference.

Lower foreground: a [LIFESTYLE PROP — woman's hand holding a pastel dumbbell / fresh flowers / a glass of water] entering the frame from the bottom edge.

[BRAND] logo bottom-left corner per brand spec card.

[If CTA]: "{{cta}}" styled per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Headline maximum scale all-caps. Benefit bar text bold and compact.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Gradient background saturated and energetic. Benefit bar in sharp accent color. Products studio-lit with visible color variation.

BRAND IDENTITY:
[BRAND] logo bottom-left.

MOOD:
Bright, energetic, empowering. Feeling: "this is a whole system, not a single bottle."
```

## Variation vectors

**Background gradient**: pink-to-hot-pink | brand pastel-to-saturated | deep brand primary solid | warm-to-cool diagonal

**Bundle packaging**: open gift box (default) | flat lay of SKUs | open drawer reveal | kit tray with cut-outs

**Product count**: 2 SKUs | 3 SKUs (default) | 4-5 SKUs (larger bundles)

**Benefit bar count**: 3 segments | 5 segments (default) | 4 segments

**Foreground prop**: hand + dumbbell (fitness) | fresh flowers (beauty) | coffee cup (morning) | water glass (wellness) | no prop (cleaner)

**Camera angle**: slight overhead (default) | straight-on | 45° three-quarter

## Format-specific rules

- **Benefit labels must be compact.** 1-3 words max per segment. "Morning Energy" works; "Supports morning energy levels" breaks the bar.
- **Parallel structure across labels.** All five follow the same grammatical shape — all noun phrases or all verb phrases, not mixed.
- **Bundle must be real.** Don't show 4 SKUs if the bundle only ships 3. Agent 4 and Agent 7 both flag fabricated contents.
- **Color variation across SKUs is visual.** If all products in the bundle are identical in color, the format fails — use a template where the single SKU is hero instead.
- **Prop must match audience.** Dumbbell for fitness, flowers for beauty, water for wellness. A mismatched prop tells the viewer this is stock.

See `headline_template.md` for shared Global rules.
