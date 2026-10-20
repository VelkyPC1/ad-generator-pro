# 20 — Advertorial / Editorial Content Card

🏷️ Looks like a news post, not an ad. The editorial framing creates curiosity and authority. Designed to blend into feed.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 9:16 alt (1080x1920)
- **needs_product_images:** false
- **reference_uploads:** product image (brand tone reference only — NOT rendered as hero)
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

This format does NOT render the product. The product image is uploaded only for brand-tone reference (color palette, mood). The image prompt should say: *"Use the attached product image as tone reference only. Do NOT render the product in this ad — it's intentionally absent for organic editorial feel."*

## What this format is

Full-bleed moody portrait photo. Editorial framing: a category tag pill ("HOT TOPIC"), a massive condensed all-caps headline spanning full width, and a social-handle signature at the bottom. No product, no CTA, no stars. Designed to read like a culture/news post, not a paid ad. Works in awareness campaigns where the goal is to earn the click, not close the sale.

## Copy template

```
[CATEGORY TAG]   - 1-3 words in all caps, inside a pill label.
                   e.g., "HOT TOPIC" / "MUST READ" / "BREAKING" / "TREND ALERT"

{{headline}}       - 12-25 words. Dominant. Condensed all-caps bold sans.
                   Tabloid / culture-blog energy.
                   Key words can be highlighted in accent color.
                   e.g., "[BRAND] IS BLOWING UP ON TIKTOK — HERE'S WHY EVERYONE'S
                          USING IT TO [ACTION]"

[HANDLE]         - @username or publication handle at bottom.
                   e.g., "@waveform.watch"

No product. No CTA. No stars. No logo overlay.
```

## Image generation prompt

```
Use the attached product image as tone reference ONLY. Do NOT render the product in this ad. Reference the attached brand spec card for accent color.

Create an advertorial editorial content card ad for [BRAND NAME]. [ASPECT RATIO — 1080x1350 / 1080x1920].

COMPOSITION:
One continuous image filling the entire frame. Full-bleed moody portrait photo of [PERSON DESCRIPTION + ACTION — e.g., "a young man in dark textured sweater holding an electric guitar / a woman in a knit cardigan at golden hour by a window"], shot on 50mm f/1.8 with shallow depth of field. Cinematic color grade with warm highlights and cool shadows. Photo should feel editorial, not ad-polished.

Lower 45% of the frame: a text overlay zone.

Top of that zone: a prominent white rounded-rectangle pill label reading "[CATEGORY TAG]" in centered uppercase sans-serif. Pill spans roughly one-third of the frame width.

Below the pill: very large, dominant, bold all-caps condensed sans-serif headline filling the width: "{{headline}}". White text with key words in [HIGHLIGHT COLOR — brand accent / neon yellow]. Headline at least 35% of the total frame height.

Bottom center: "[HANDLE]" in small white text.

No product shot. No CTA button. No stars. No logo overlay.

TYPOGRAPHY:
Per uploaded brand spec card for accent color ONLY. Typography is editorial/tabloid — condensed all-caps bold sans, tight leading, bold word-weight emphasis. Not brand-polished.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Cinematic photography grade. Overlay text in white. Pill label bright white. Key highlight words in brand accent.

MOOD:
Editorial, cultural, organic. "Music blog post, not paid ad." The ad should feel like feed content.
```

## Variation vectors

**Category tag**: "HOT TOPIC" | "MUST READ" | "BREAKING" | "TREND ALERT" | "DON'T SLEEP ON THIS" | localized equivalents

**Headline tone**: breathless tabloid ("...HERE'S WHY EVERYONE'S USING IT") | academic-editorial ("NEW DATA SUGGESTS...") | shocked-insider ("WAIT UNTIL YOU SEE THIS...")

**Photo mood**: moody portrait (default) | lifestyle candid | atmospheric environment | detail macro

**Highlight color for key words**: neon yellow | brand accent | bright coral | muted highlighter

**Handle / attribution**: @handle | "via publication name" | "reported by X" | blank (no attribution)

**Portrait subject**: person alone | hands / object | detail shot of the subject area | environment without person

## Format-specific rules

- **Looks like an ad → fails.** If the viewer clocks this as branded content in the first 0.5s, the format breaks. Make the photo cinematic, not commercial.
- **No product. No logo. No CTA.** The whole conversion job is "earn the click." Brand reveal happens after.
- **Handle / attribution is the low-key brand signal.** The handle can be the brand's TikTok or a partner publication's.
- **Headline must tease, not sell.** "[BRAND] IS BLOWING UP" works; "BUY [BRAND] NOW" kills the format.
- **Legal / disclosure.** In most markets, sponsored content requires an "Ad" or "Sponsored" label. This format intentionally hides the ad nature, so check legal compliance before shipping.
- **Agent 4 often flags this format for premium brands.** The tabloid energy can undermine luxury positioning. Works best for D2C / DTC / challenger brands.

See `headline_template.md` for shared Global rules.
