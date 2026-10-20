# 25 — Us vs Them Color Split

🏷️ Bold saturated color split comparison. Dynamic action product photography. Comic-style VS burst. Meme energy.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Sibling of #07 but with saturated color block split and dynamic product photography (chocolate dripping, liquid pouring). Left: vibrant brand color with your product in action + 4 strengths with green checks. Right: pale/cream background with a generic competitor + 4 weaknesses with red Xs. Comic-style VS burst in the center. Meme-format energy that could go viral on social.

## Copy template

```
[COMPETITOR CATEGORY]   - 2-4 words. Category name, not specific competitor.
                          e.g., "Other chocolate bars" / "Big Pharma brands"

[YOUR BRAND LOGO]       - Top-left of left half in bold white caps.

[STRENGTH 1-4]          - Each 2-6 words. All-caps. Parallel with weaknesses.
                          e.g., "≤2G SUGAR / ALL NATURAL INGREDIENTS / ≥6G FIBRE / 12G PROTEIN"

[WEAKNESS 1-4]          - Each 2-6 words. Direct opposites.
                          e.g., "29G SUGAR / FULL OF FRUCTOSE CORN SYRUP / 1G FIBRE / 2G PROTEIN"

{{cta}}                   - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create an us-vs-them color split ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame, divided vertically into two equal halves.

Left half: [PRIMARY BRAND COLOR from spec card — vibrant teal / saturated brand] background. The product (reproduced exactly from reference) photographed with dynamic energy — [ACTION DETAIL — chocolate dripping / liquid pouring / melt shot / splash motion] to convey indulgence and vitality.

Top-left: [BRAND] logo in bold white caps.
Below the product: vertical stack of 4 benefits, each with a green filled circle checkmark emoji: "[STRENGTH 1]", "[STRENGTH 2]", "[STRENGTH 3]", "[STRENGTH 4]" in bold white uppercase.

Right half: [CONTRAST COLOR — pale cream / muted beige / soft neutral] background. A generic unbranded competitor product [DESCRIPTION — crumpled foil-wrapped chocolate bar / generic plain packaging], shot in flat unflattering lighting.

Top-right: "[COMPETITOR CATEGORY]" header in dark text.
Below the competitor product: vertical stack of 4 weaknesses, each with a red filled circle X emoji: "[WEAKNESS 1]", "[WEAKNESS 2]", "[WEAKNESS 3]", "[WEAKNESS 4]" in bold dark uppercase.

Center divider: a comic-style "VS" burst graphic in [ACCENT COLOR — coral / red / brand accent] spanning the split line.

[If CTA]: "{{cta}}" at bottom per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Both sides use bold all-caps for parallel rhythm. Logo + VS burst in loud accent styling.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Saturated brand color on left, muted neutral on right. Product on left shot with action/energy lighting. Competitor on right shot flat. Center burst in contrast color that pops against both halves.

MOOD:
Loud, confident, meme-worthy. "The difference is obvious."
```

## Variation vectors

**Left color**: vibrant teal | brand primary saturated | hot pink | deep brand color

**Right color**: pale cream (default) | muted beige | flat light gray | pale warm neutral

**Action detail**: chocolate drip | liquid pour | splash motion | crumble burst | powder scatter

**VS burst style**: comic burst (default) | circular red badge | lightning bolt graphic | diagonal slash with VS text

**Check / X style**: emoji-style filled circles (default) | drawn checkmarks and Xs | minimalist dots (harder read)

**Strength/weakness framing**: nutrition stats (default) | ingredient callouts | process claims | ethical claims

## Format-specific rules

- **Never name real competitors.** Use category labels. Naming specific competitors creates legal risk.
- **Weaknesses must be true of the category.** Agent 4 and Agent 7 flag fabricated claims.
- **Parallel stats.** Every strength has a direct numeric opposite weakness. "12G PROTEIN" pairs with "2G PROTEIN," not with "Boring."
- **Action photography on the left is non-negotiable.** If your product looks flat, this format fails. Use drip, pour, splash, or motion.
- **Comic VS burst is the brand moment.** Don't replace with minimal text. The burst signals meme-format playfulness.
- **Agent 4 flags for luxury / clinical brands.** Meme energy works for D2C / community / playful brands.

See `headline_template.md` for shared Global rules. See #07 (Us vs Them) for the restrained variant.
