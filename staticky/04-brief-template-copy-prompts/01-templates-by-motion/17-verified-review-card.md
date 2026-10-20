# 17 — Verified Review Card

🏷️ Mimics real review platform UI. The verified badge and helpfulness count do the trust-building work.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Solid brand-color background. A big pull-quote headline at top with five gold stars. A white review card containing full review UI (avatar, name, verified badge, body, "Read more" link, helpfulness counter). Product overlaps the card edge on the right. No brand logo — the review UI is the whole trust mechanic.

## Copy template

```
[HEADLINE QUOTE]    - 4-10 words in quotation marks.
                      e.g., "I finally found something that works!"

{{reviewer}}     - First name + last initial. Optional flag emoji.

{{verified_tag}}      - "Verified Reviewer" / "Verified Buyer"

{{review_text}}       - 3-4 sentences. Full review that extends beyond the pull-quote.

[READ MORE]         - "...Read more" link (blue).

[HELPFULNESS]       - "Was this review helpful? 👍 150"

No CTA needed — review card IS the proof.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a verified review card ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: solid [BRAND COLOR from spec card — periwinkle / lavender blue / brand primary].

Top: large bold white serif or semi-bold sans-serif pull-quote with curly quotation marks "[HEADLINE QUOTE]".

Below the quote: five filled large gold stars in a horizontal row.

Center-left: a white rounded-rectangle review card with subtle shadow. Card contents:
- Gray circular avatar icon (top-left)
- "{{reviewer}}" in bold dark sans-serif with [FLAG EMOJI]
- Blue checkmark + "{{verified_tag}}" in small blue or brand-color text
- "{{review_text}}" in regular weight dark text, 3-4 sentences
- "[READ MORE]" in blue link text at bottom of card
- "[HELPFULNESS]" below the link

Right side, overlapping the card edge: the product (reproduced exactly from reference) photographed at a slight angle, soft studio lighting, casting a gentle shadow on the background.

No brand logo.

TYPOGRAPHY:
Pull-quote: serif or semi-bold at maximum scale. Review card: default marketplace sans-serif (not brand font) to mimic real review UI.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Solid brand-color background. White review card. Gold stars. Blue checkmark and link text (platform-standard). Product with natural shadow.

MOOD:
Trusted, earned, quiet confidence. "Real people say this works."
```

## Variation vectors

**Background color**: brand primary saturated | brand accent pastel | deep brand dark | soft brand-tinted mid-tone

**Quote font**: serif italic (default) | semi-bold sans-serif | bold sans-serif | condensed bold caps

**Card position**: left-center overlapping product right (default) | centered with product bottom | right with product left

**Verified tag style**: blue checkmark (default) | orange "Verified Purchase" pill | green badge | brand-color accent

**Star color**: gold (default, universal) | brand-color stars (only if brand is famous for a specific color)

**Helpfulness count**: 50-200 realistic range | 1K-10K range (for big-brand social proof) | no count (tighter)

## Format-specific rules

- **Marketplace UI feel is the trust mechanic.** Use default sans-serif in the card, not brand fonts. Blue checkmark is platform-standard.
- **Truthful reviews only.** Pull from real customer reviews. Agent 4 and Agent 7 flag fabricated UI.
- **No brand logo.** The review card IS the identity. A logo overlay cheapens it.
- **Product overlap on the card is the composition trick.** It says "this is the thing being reviewed" without needing a caption. Don't break the overlap.
- **Gold stars, not brand-color stars** — unless the brand's entire identity revolves around a specific color (then still consider gold for universal trust reads).

See `headline_template.md` for shared Global rules.
