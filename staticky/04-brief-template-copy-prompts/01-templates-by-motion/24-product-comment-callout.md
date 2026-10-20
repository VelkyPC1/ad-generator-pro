# 24 — Product + Comment Callout (Faux Social Proof)

🏷️ Clean product hero on top. Realistic Facebook-style comment card below. Looks like a screenshot, not an ad.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Two-zone layout. Top 55%: clean studio product shot with the cap slightly open or product-in-use detail. Bottom 45%: realistic Facebook-style comment card with profile photo, name, testimonial body, timestamp, and emoji reactions. The comment looks like a genuine screenshot someone dropped below a product photo. Works as social proof when UGC-feel is preferred over studio polish.

## Copy template

```
{{reviewer}}     - First name + last initial. e.g., "Alan R."

[TESTIMONIAL]       - 2-3 sentences. Specific, first-person, game-changer framing.
                      e.g., "Been using this for 3 weeks. My sleep has completely
                             changed. Never going back."

[TIMEFRAME]         - "4w" / "2d" / "3m". Small gray.

[REACTION COUNT]    - e.g., "33" with thumbs-up + heart emojis.

No headline. No stars. No CTA.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a product + comment callout social proof ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame.

Top 55%: the product (reproduced exactly from reference) centered on a clean white background, studio-lit at 85mm f/2.8 with soft shadow grounding it. Product cap/lid slightly open or with a [DETAIL — a dropper visible / gummies spilling / tablets exposed]. A few [LOOSE UNITS — gummies / capsules / scoops] spilling casually at the base.

Bottom 45%: a realistic Facebook-style comment card on light gray background. Card contents:
- Small circular profile photo of [PERSON DESCRIPTION — man in 30s, friendly casual smile / woman in 40s, warm expression]
- Bold name "{{reviewer}}" above the comment
- Comment text in regular weight: "[TESTIMONIAL]" (2-3 sentences)
- Below comment: "[TIMEFRAME]" · Like · Reply in small gray text
- Bottom right: Facebook-style reaction emojis (thumbs-up + heart icons) with "[REACTION COUNT]"

Should look like an organic screenshot, not a designed ad.

TYPOGRAPHY:
Product zone uses brand styling. Comment card uses Facebook-standard sans-serif (default platform font), NOT brand font — platform-authenticity is the trust mechanic.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Product zone: clean white. Comment card: light gray platform background with white comment bubble. Profile photo realistic.

MOOD:
Raw, conversational, organic. Product looks catalog. Comment looks screenshotted. Juxtaposition is the point.
```

## Variation vectors

**Platform mimicry**: Facebook (default) | Instagram comment | TikTok comment | Reddit comment | generic social

**Product detail**: cap open with dropper | gummies/tablets spilling | product mid-use | partial unwrap

**Comment tone**: first-person game-changer | skeptic-converted | community recommendation | husband/wife endorsement

**Photo style (avatar)**: realistic headshot (default) | illustrated avatar | default platform silhouette | candid low-res

**Reaction count**: double digits (20-99, realistic small-circle) | triple digits (100+, viral) | single digit (intimate, rare)

**Product angle**: straight-on (default) | slight 15° tilt | flat lay top-down

## Format-specific rules

- **Comment card MUST mimic the real platform.** Facebook uses a specific sans-serif, a specific gray, a specific spacing. Get the details right or the format fails.
- **Comment voice must be authentic.** Specific details, natural sentence fragments, no marketing language.
- **Product zone is polished; comment zone is raw.** Don't harmonize them — the contrast is the format.
- **Legal / authenticity.** Fake reviews are illegal in many markets. Pull from real customer comments with permission, or use clear "sponsored content" disclosure.
- **No brand logo overlay.** Product packaging carries identity in the top zone.

See `headline_template.md` for shared Global rules. See #15 (Social Comment Screenshot) for the comment-first variant.
