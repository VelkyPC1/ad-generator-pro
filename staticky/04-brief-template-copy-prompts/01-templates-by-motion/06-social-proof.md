# 06 — Social Proof

🏷️ Member count + review card + press logos. The trust stack.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for 4:5)
- **bottom_safe_zone:** 340px (scaled for 4:5)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

The "trust stack": member count headline, star rating, product hero, review card, press logos. Four proof mechanisms layered in one frame. Works when you have multiple legitimate proof points and need to signal "this is a real, trusted brand" to a cold audience.

## Copy template

```
{{headline}}        - 4-8 words. The quantified trust claim.
                    e.g., "Join 1,000,000+ Members" / "Loved by 50,000 parents"

[RATING LINE]     - e.g., "Rated 4.9 out of 5" — below 5 filled stars.

[REVIEW TITLE]    - 3-6 words. The emotional headline of the review.
                    e.g., "Changed my morning routine"

{{review_text}}     - 2-3 sentences. Conversational, specific.

{{reviewer}}     - Name + optional credential, italic.

[PRESS TAG]       - "As Featured In" or localized equivalent.

{{cta}}             - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a social proof ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame. Background: [BACKGROUND from variation — warm cream / off-white / soft brand-tinted neutral].

Top: "{{headline}}" in bold [BRAND COLOR from spec card] sans-serif, centered. Below: five filled [BRAND COLOR] stars in a horizontal row, with "[RATING LINE]" immediately below the stars in smaller weight.

Center: the product (reproduced exactly from reference) shot at 50mm f/4, soft studio lighting, centered, occupying ~30-35% of the frame.

Below product: a frosted white rounded-rectangle card with subtle shadow, containing:
- Five small filled stars at the top
- "[REVIEW TITLE]" in bold
- "{{review_text}}" in regular weight below the title
- "{{reviewer}}" in italic at the bottom

Below the card: "[PRESS TAG]" in small [BRAND COLOR] uppercase wide-tracked text, then a horizontal row of five grayscale publication logos (generic editorial mastheads, do not reproduce real logos without rights).

[If CTA]: "{{cta}}" styled per brand spec card.

TYPOGRAPHY:
Per uploaded brand spec card. Member-count headline is primary hierarchy. Review card uses secondary scale. Press row at tertiary.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Cream or off-white background creates a "trusted publication" feel. Product color-graded per visual style card. Stars in brand color.

BRAND IDENTITY:
[BRAND] logo bottom right per spec card.

MOOD:
Established. Trusted. "Everybody's already using this."
```

## Variation vectors

**Background**: warm cream (default) | off-white | soft brand-tinted | light texture (linen)

**Headline claim**: member count ("1,000,000+ members") | rating ("4.9 stars, 12,000 reviews") | press ("As featured in X") | category rank ("#1 in [category]")

**Product position**: centered middle | upper-center with card below | left with card on right

**Review card style**: frosted white (default) | soft gray | brand-tinted pale | framed with thin brand-color border

**Press row**: 5 grayscale masthead-style generic logos | 3 prominent generic logos | text-only "As featured in X, Y, Z"

**Energy**: established and trusted | warm and community-driven | premium and exclusive

## Format-specific rules

- **Truthfulness.** Do not fabricate member counts, star ratings, or press placements. Agent 4 (Brand Consistency) and Agent 7 (Copy Editor) both veto fabricated proof.
- **No duplicate data.** If the headline claims "1,000,000+ members," the review body should not also mention "1M people" — one claim per frame.
- **Press logos must be permissioned or generic.** Do not reproduce real publication logos unless the brand has documented press placements with those outlets.
- **Every proof is a real proof.** Star rating, review, press, member count — each element should reflect actual brand truth. Otherwise this format becomes a credibility liability.

See `headline_template.md` for shared Global rules.
