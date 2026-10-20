# 39 — Curiosity Gap + Scroll-Stopper Hook

🏷️ Truncated social caption up top ("...more"). Close-up problem-visual photo below. Zero branding. Pure curiosity bait for top-of-funnel.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** false
- **reference_uploads:** brand-spec-card.png + visual-style-card.png (for visual tone reference ONLY)
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

This format does NOT render the product. The product image is uploaded for brand visual-tone reference only. The image prompt should say: *"Use the attached images as brand reference for visual tone ONLY. Do NOT include any product, logo, or branding in this ad."*

## What this format is

A scroll-stopping curiosity ad mimicking a truncated social media post. Top 35%: white background with bold black headline that cuts off with "...more" in gray — the classic Facebook/Instagram caption truncation. Bottom 65%: close-up editorial photo of the problem the product solves (the symptom, the frustration, the texture). No product, no logo, no CTA. The entire purpose is to provoke curiosity and earn the click to expand.

## Copy template

```
{{headline}}       - 12-20 words. Bold black. Ends mid-thought.
                        e.g., "Most women don't realize THIS is why their skin
                               breaks out after 30 but did you know..."
                        The "..." signals the truncation.

[TRUNCATION CTA]      - "...more" in light gray after the headline.
                        Mimics the platform "See more" / "...more" behavior.

No product name. No brand name. No CTA button. No logo. Pure curiosity.
```

## Image generation prompt

```
Use the attached images as brand reference for visual tone ONLY. Do NOT include any product, logo, or branding in this ad.

Create a curiosity gap scroll-stopper hook ad. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame.

Top 35%: clean white background with large bold black sans-serif text (heavy weight, tight leading, left-aligned): "{{headline}}". The last few words trail off followed by "...more" in lighter gray text (rgb ~180,180,180), mimicking a truncated Facebook / Instagram caption that requires clicking "more" to expand. The headline should feel mid-sentence, unfinished.

Bottom 65%: a close-up, slightly uncomfortable or attention-grabbing photo of [PROBLEM VISUAL — the specific physical symptom, texture, or problem the product solves, shown on a real person or in a real context. No product visible]. Photo should feel real and editorial — not stock-library clean. Slightly shallow depth of field, natural lighting. Shot feels candid or documentary.

No text on the photo zone. No product. No logo. No CTA button. No brand name anywhere.

TYPOGRAPHY:
Heavy bold sans-serif for the headline (Inter / Helvetica Neue / SF Pro style — platform-native feeling, NOT brand font). "...more" in the same font at lighter gray weight.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White text zone. Photo zone natural and unretouched — slightly raw.

MOOD:
Curiosity-provoking, slightly unsettling, scroll-stopping. "Wait — what? I need to read the rest."
```

## Variation vectors

**Problem visual**: skin close-up (default) | hair texture | body discomfort | food/ingredient macro | gut/digestive visual

**Headline angle**: "Most [AUDIENCE] don't realize..." (default) | "Nobody talks about THIS..." | "I was today years old when I learned..." | "Your doctor won't tell you this but..."

**Photo mood**: slightly uncomfortable (default) | raw documentary | warm editorial | clinical macro

**Truncation style**: "...more" gray text (default) | "See more" link-style | "Continue reading" | just "..." trailing off

**Depth of field**: shallow (default) | medium-sharp | very shallow (dreamy)

**Energy**: unsettling curiosity | warm "did you know" | urgent revelation | calm educational

## Format-specific rules

- **Zero branding.** Any brand element kills the format. The viewer should NOT know this is an ad until they click.
- **Headline must be genuinely curiosity-provoking.** If you can finish the sentence without clicking, the hook fails. Cut it mid-revelation.
- **Problem visual must connect to the product's category.** A skincare brand shows skin, a gut-health brand shows digestive discomfort. Random shock imagery disconnects.
- **Photo must not be gratuitous or offensive.** Slightly uncomfortable = effective. Gross or shocking = reported.
- **Legal / disclosure.** This format intentionally hides the ad nature. Most platforms and markets require sponsored-content disclosure. Verify compliance before shipping.
- **"...more" must look platform-native.** Wrong color, wrong font, wrong placement = the truncation illusion breaks.

See `headline_template.md` for shared Global rules. See #16 for another curiosity-gap format, #29 for organic-post feel.
