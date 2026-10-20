# 11 — Pull-Quote Review Card

🏷️ Emotional quote headline over a truncated review card on a color block. The "...Read more" creates an open loop.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A big emotional pull-quote in italic serif sits over the top half. Below, a white rounded review card with a truncated "...Read more" cliffhanger. The product sits bottom-right, overlapping the card. The truncation is the hook — the viewer's brain wants to complete the sentence.

## Copy template

```
[PULL-QUOTE]        - 4-8 words, the most emotional fragment of the review.
                      e.g., "I finally found something that works!"

{{reviewer}}     - First name + last initial. Optional flag emoji.

{{verified_tag}}      - "Verified Reviewer" / "Verified Buyer" per brand convention.

{{review_text}}       - 4-6 lines of authentic-sounding review, ending mid-sentence.
                      Last visible line must trail off naturally before "...Read more".

[HELPFULNESS COUNT] - "150" or "2.4K" next to a thumbs-up icon.

No headline above. The pull-quote IS the headline.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a pull-quote review ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: solid [BRAND COLOR from spec card — soft, muted tone works best, hex value per spec] color block edge-to-edge.

Top half: oversized bold italic serif pull-quote in white with curly quotation marks: "[PULL-QUOTE]". Centered. Directly below the quote: five large filled gold/yellow star icons in a horizontal row.

Bottom-left, overlapping the color background: a white rounded-corner review card with subtle shadow, containing:
- Small gray circular default avatar icon
- "{{reviewer}}" in bold dark sans-serif with optional [FLAG EMOJI]
- Below the name: blue checkmark icon + "{{verified_tag}}" in small blue text
- Review body text in medium-weight dark sans-serif, 4-6 lines of authentic-sounding customer voice trailing off mid-sentence, ending with "...Read more" in bold [BRAND COLOR]
- Bottom of card: "Was this review helpful?" in small gray + thumbs-up icon + "[HELPFULNESS COUNT]"

Bottom-right, overlapping both the card and the color background: the product (reproduced exactly from reference) angled slightly toward the viewer, sitting on the color block surface with a subtle shadow.

No brand logo — the product packaging carries the identity.

TYPOGRAPHY:
Pull-quote: italic serif at maximum scale. Review card: default marketplace sans-serif (not brand font) to mimic real review UI. "...Read more" in brand color, bold.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Solid muted brand color background. White card with slight drop shadow. Gold stars. Blue verified checkmark. Product with natural shadow grounding.

MOOD:
Emotional, honest, curiosity-inducing. The viewer wants to tap "...Read more."
```

## Variation vectors

**Background color**: soft muted brand primary | pastel brand accent | warm terracotta / sage (per spec) | deep saturated brand tone

**Quote position**: top half centered (default) | top-left aligned | diagonal positioning

**Card position**: bottom-left (default) | bottom-centered | bottom-right (mirrored product)

**Product placement**: bottom-right overlap (default) | top-right small | full-bottom band

**Verified element**: blue checkmark (default) | orange "Verified Purchase" pill | green "Verified Buyer" tag

**Review tone**: emotional first-person (default) | practical-review ("I was skeptical but...") | story-arc ("My mom told me about this...")

## Format-specific rules

- **Truncation is the hook.** The last visible line MUST trail off mid-sentence before "...Read more". Don't let the review complete itself.
- **One pull-quote, not a headline.** No separate headline above. The quote is the headline.
- **Real review truth.** Pull the quote from an actual customer review. Fabrication breaks Agent 4 and Agent 7.
- **No brand logo overlay.** The product packaging carries identity. A logo in the corner cheapens the format.
- **Five gold stars are standard.** Don't swap to brand-color stars here — gold reads as platform-universal trust.

See `headline_template.md` for shared Global rules.
