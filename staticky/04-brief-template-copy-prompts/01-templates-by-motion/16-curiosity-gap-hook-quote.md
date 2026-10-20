# 16 — Curiosity Gap / Hook Quote Testimonial

🏷️ The bait-and-switch testimonial. Provocative headline forces the double-take. The reveal reframes it. Scroll-stop machine.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Mixed typography testimonial. A small italic setup line at the top. A massive provocative bait phrase in the middle ("FAKING IT WITH MY HUSBAND"). A smaller reveal line that reframes it ("since perimenopause — with [BRAND] I don't have to"). Bottom third: product + trust badge + star-count card. The double-take is the hook.

## Copy template

```
[SETUP LINE]       - 2-5 words. Italic serif or semi-bold small.
                     e.g., "I've been" / "For years" / "Nobody knew"

[BAIT PHRASE]      - 3-7 words across 1-2 lines. Huge all-caps heavy weight.
                     Sounds alarming, suggestive, or taboo on first read.
                     e.g., "FAKING IT / WITH MY HUSBAND"

[REVEAL]           - 6-15 words. Smaller sentence-case. Reframes the bait.
                     e.g., "since perimenopause — with [BRAND] I don't have to"

{{reviewer}}      - "- First name + last initial"

[TRUST BADGE]      - Circular seal. e.g., "60 Day Guarantee" / "100% Money Back"

[REVIEW COUNT]     - e.g., "3,600+ 5-Star Reviews"

[DISCLAIMER]       - Optional small text. e.g., "Results may vary. No results guaranteed."
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a curiosity-gap hook testimonial ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: clean white throughout.

Top center: large [ACCENT COLOR — periwinkle blue / brand accent] opening curly quotation marks.

Below: mixed-weight headline in black:
- First line: "[SETUP LINE]" in italic serif or semi-bold small
- Next 1-2 lines: "[BAIT PHRASE]" in enormous heavy-weight bold all-caps sans-serif
- Below: "[REVEAL]" in smaller sentence-case regular weight

Closing curly quotation marks. Below: "{{reviewer}}" in regular weight italic.

Left side bottom third: the product (reproduced exactly from reference) at a slight angle with [PRODUCT DETAILS — capsules / product loose / accessory] scattered nearby.

To the left of the product: a circular [TRUST BADGE — "60 Day Guarantee" / "100% Money Back" / brand-specific seal] in [BADGE COLOR] with dark text.

Right side bottom third: five large filled [ACCENT COLOR] stars and bold text "[REVIEW COUNT]" with a small brand icon.

Bottom edge: small disclaimer text "[DISCLAIMER]" in regular weight gray.

TYPOGRAPHY:
Per uploaded brand spec card. Bait phrase dominates. Setup italic secondary. Reveal tertiary. Typography weight contrast IS the scroll-stop.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White background. Accent color used on quotation marks + stars. Badge in brand-appropriate seal color.

MOOD:
Provocative, clever, earned. The bait makes you stop. The reveal makes you respect the brand.
```

## Variation vectors

**Bait direction**: taboo/suggestive ("FAKING IT") | mock-confession ("LYING TO MY KIDS") | shocking claim ("I HATED THIS") that reveals positive | authority provocation ("MY DOCTOR WAS WRONG")

**Setup style**: italic serif | semi-bold sans | all-caps small | handwritten script

**Bait weight**: ultra-black all-caps (default) | bold italic | condensed bold all-caps

**Product side**: left bottom (default) | right bottom (mirrored) | centered below text

**Trust badge position**: next to product (default) | top right corner | integrated into review block

**Review count format**: "3,600+ 5-Star Reviews" | "Rated 4.9/5" | "Trusted by X customers"

## Format-specific rules

- **The reveal must reframe positively.** First read alarms the viewer. Second read makes them nod. If the reveal doesn't land, the format is doing harm.
- **Bait must not be cruel or exploit protected categories.** No fat-shaming, no medical-gaslighting, no offensive stereotypes. Cleverness, not cruelty.
- **Truth in the claim.** Agent 4 and Agent 7 both flag if the reveal promises something the brand can't deliver. The bait may be dramatic but the reveal must be honest.
- **Typography hierarchy is the whole trick.** If the setup, bait, and reveal are all the same size, the format collapses. Weight contrast is non-negotiable.
- **Disclaimer is often legally required** for categories like supplements, skincare, weight-related products, finance. Check category rules before shipping.

See `headline_template.md` for shared Global rules.
