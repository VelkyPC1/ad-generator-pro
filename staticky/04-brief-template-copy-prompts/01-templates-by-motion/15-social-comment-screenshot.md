# 15 — Social Comment Screenshot + Product

🏷️ Screenshotted comment = instant credibility. Looks organic. Bold hook headline does the scroll-stopping.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A bold hook headline at top. A screenshotted-style comment card in the middle (rawly laid out to look like an Instagram or Facebook comment). The product sits at the bottom. The rawness is the trust mechanic — it should look like someone screenshotted a real comment and pasted the product photo below.

## Copy template

```
{{headline}}    - 5-10 words. Bold, provocative. Optional emoji at end.
                     e.g., "IF YOU'RE GOING THROUGH PERI..." 😅
                     The "..." cliffhanger works here too.

{{reviewer}}    - Full or first-name-last-initial.
                     e.g., "Elaine McLean"

[FULL REVIEW]      - 3-4 sentences. Conversational, emotional, specific.
                     Sounds like a real comment — not marketing copy.

[TIMESTAMP]        - "2d" / "5h" / "1w". Small gray.

No brand logo. No stars. No CTA.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a social comment screenshot ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: clean white throughout.

Top: oversized bold black sans-serif headline "{{headline}}" with [EMOJI] at the end. Set at maximum scale the frame allows.

Center: a social media comment card with a light gray rounded-rectangle background containing:
- Small circular profile avatar (generic, top-left of card)
- Bold name "{{reviewer}}" in dark sans-serif
- Multi-sentence comment in regular-weight sans-serif: "[FULL REVIEW]" (3-4 conversational sentences)
- Small gray "[TIMESTAMP]" below the comment

Bottom center: the product (reproduced exactly from reference) photographed at a slight angle on white, soft studio lighting.

No brand logo. No stars. No CTA.

TYPOGRAPHY:
Headline: bold black sans-serif, dominant. Comment card: mimics platform UI — default sans-serif, not brand font. Hook headline uses brand headline font.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Pure white background. Gray comment card. Product naturally lit. The whole composition should look slightly raw — like a screenshot dropped above a product photo.

MOOD:
Organic, conversational, scroll-stopping. "Did someone really just say that?"
```

## Variation vectors

**Platform mimicry**: Instagram comment style (default) | Facebook comment | Twitter/X post | Reddit comment

**Hook headline tone**: cliffhanger with emoji (default) | question-hook | declarative bold | all-caps provocation

**Product placement**: bottom center (default) | bottom right | bottom band full-width | top corner (headline swapped to bottom)

**Comment tone**: confessional emotional | practical-review | humor / shared frustration | surprise-conversion ("I didn't expect...")

**Avatar style**: blank gray default | generic colored initial circle | small photo-looking avatar

**Background**: pure white (default) | off-white | pale brand-tinted

## Format-specific rules

- **Rawness is the feature.** Don't add drop shadows, frames, or design polish to the comment card. It should look pasted, not composed.
- **Comment voice must be authentic.** Read it out loud. If it sounds like marketing copy, it fails. Use real customer voice — specific details, natural sentence fragments.
- **Hook headline must connect to the comment.** The headline teases the problem the comment validates. Disconnected headline + comment breaks the format.
- **No stars, no CTA, no logo.** Every added element reduces credibility.
- **Legal/authenticity.** If the comment is fabricated, in some markets this is prohibited. Default to real customer comments with permission, or use clearly ironic / self-aware framing.

See `headline_template.md` for shared Global rules.
