# 07 — Us vs Them

🏷️ Side-by-side comparison. Photography quality gap IS the argument.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for 4:5)
- **bottom_safe_zone:** 340px (scaled for 4:5)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Side-by-side vertical split. Left: muted/gray "them" column with a generic competitor and a list of weaknesses marked with X. Right: brand-color "us" column with your product and a list of strengths marked with checkmarks. A "VS" badge at the top center. The visual quality gap between sides reinforces the argument.

## Copy template

```
[COMPETITOR LABEL]   - 2-4 words. Category name, not a specific competitor.
                       e.g., "Regular shampoos" / "Generic multivitamins"

[YOUR BRAND LABEL]   - 1-3 words. The brand name or category-defining phrase.

[WEAKNESS 1-5]       - Each 2-6 words. Parallel structure.
                       e.g., "Full of parabens" / "Loaded with sugar"

[STRENGTH 1-5]       - Each 2-6 words. Direct opposite of the weakness.
                       e.g., "Paraben-free formula" / "Zero added sugar"

{{cta}}                - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a side-by-side comparison ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame, divided vertically into two equal halves.

Left half: muted gray-blue or cool-neutral background. Top header: "[COMPETITOR LABEL]" in dark text. Below: a generic, unbranded competitor product (no real competitor identification) shot with flat, unflattering lighting — deliberately plain. Below the product: vertical stack of 5 weakness lines, each with a red X mark: "[WEAKNESS 1-5]".

Right half: [PRIMARY BRAND COLOR from spec card] background. Top header: "[YOUR BRAND LABEL]" in contrasting text. Below: the product (reproduced exactly from reference), shot with premium commercial lighting — clearly the hero. Below the product: vertical stack of 5 strength lines, each with a green or brand-color checkmark: "[STRENGTH 1-5]".

Center top: a white circle with "VS" in bold dark sans-serif, straddling the dividing line.

[If CTA]: "{{cta}}" at bottom per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Both halves use the same font system but the left side reads as deliberately flatter, the right as richer. Headers at primary hierarchy, lists at tertiary.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Gray-blue or muted gray on the left, saturated brand color on the right. Photography quality gap is intentional — left side looks like it was shot on a table, right side looks like a studio hero.

BRAND IDENTITY:
[BRAND] logo bottom right per spec card.

MOOD:
Confident, direct-response. "The choice is obvious."
```

## Variation vectors

**Left side tone**: muted gray-blue | flat gray | cool neutral | dim warm gray

**Right side tone**: primary brand color | brand accent color | brand gradient

**Divider style**: thin vertical line | hard color split | diagonal split | center VS badge only (no line)

**Marker style**: X + checkmark (default) | red circle + green circle | crossed-out text on left, bold on right

**Competitor framing**: category-neutral ("Regular shampoos") | specific weakness-named ("Parabens-loaded brands") | cost-framed ("Cheap alternatives")

**List length**: 3 points each (tight) | 5 points each (default) | 4 points each (balanced)

## Format-specific rules

- **Never name real competitors.** Use category labels ("Regular shampoos," "Mainstream brands"). Naming a competitor creates legal risk and usually backfires.
- **Parallel structure.** Every strength is the direct opposite of its weakness. "Full of sugar" ↔ "Zero added sugar" — not "Full of sugar" ↔ "Tastes better."
- **Weaknesses must be true of the category.** Don't invent a fake weakness for a straw-man competitor. Agent 7 will flag fabricated claims.
- **Photography gap is the argument.** If both sides look equally good, the visual case falls apart. The competitor side must look deliberately less inviting — but not absurdly bad (parody weakens credibility).

See `headline_template.md` for shared Global rules.
