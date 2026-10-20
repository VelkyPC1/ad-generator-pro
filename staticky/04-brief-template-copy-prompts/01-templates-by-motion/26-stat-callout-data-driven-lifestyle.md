# 26 — Stat Callout (Data-Driven Lifestyle)

🏷️ Lifestyle photography on top. Stat-led headline on the dark overlay bottom. The statistic IS the argument.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 9:16 alt (1080x1920)
- **needs_product_images:** false (product visible in lifestyle photo only)
- **reference_uploads:** product image (for brand color reference + to show product in lifestyle scene)
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Product visible in the lifestyle photo must be reproduced exactly per reference image. The image prompt should say: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo (visible in the lifestyle scene), do not invent or alter shape, color, labels, or design."*

## What this format is

Top 50%: lifestyle photography in a warm skin-toned palette — hands holding or using the product. Brand logo on a thin divider. Bottom 50%: dark gradient overlay with a huge stat-led headline ("AFTER SWITCHING, 87% OF USERS [RESULT]"). Key stats highlighted in accent color. The statistic is the whole pitch.

## Copy template

```
[STAT-DRIVEN HEADLINE]   - 12-25 words. Statistic-led claim.
                           Key percentage / number phrases highlighted in accent color.
                           e.g., "AFTER SWITCHING TO [BRAND], 87% OF USERS REPORTED
                                  BETTER SLEEP, WHILE 72% FELT MORE RESTED IN THE MORNING."

[BRAND LOGO]             - Centered on the divider between zones.

No CTA. No stars. The stat carries the ad.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo (visible in the lifestyle scene), do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a stat callout data-driven lifestyle ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1920].

COMPOSITION:
One continuous image filling the entire frame, divided horizontally.

Top 50%: lifestyle product photography — [SCENE — a woman's hands holding the product pad / person using the product in morning routine context / product visible in hand mid-use] on a [MOOD — warm skin-toned / soft golden / cool calm] background. Shot on 50mm f/2.8, shallow depth of field. Product packaging clearly visible in the frame (reproduced exactly per reference image).

Middle (divider line): [BRAND] logo centered, with thin horizontal rules on either side.

Bottom 50%: dark gradient overlay (fading from transparent at the top to [DARK COLOR — deep brown / black / deep navy] at the bottom). Large bold uppercase sans-serif text "[STAT-DRIVEN HEADLINE]" in white.

Key result phrases highlighted in [ACCENT COLOR — soft pink / brand secondary / accent yellow]. The statistic is the headline — no separate subhead needed.

TYPOGRAPHY:
Per uploaded brand spec card. Stat headline dominates the bottom half. Brand logo thin divider serves as visual break. All-caps headline reinforces data authority.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Warm lifestyle photography on top. Dark gradient on bottom. Key stats in accent color for eye-pop. Brand logo neutral.

MOOD:
Evidence-based, calm, confident. "This is what the data says."
```

## Variation vectors

**Top photo mood**: warm skin-tone (default) | cool calm studio | golden hour natural | moody intimate

**Bottom overlay color**: deep brown/warm dark | pure black | deep navy | brand dark saturated

**Stat focus**: user outcome (%) | time-based improvement | clinical / medical result | before-after delta

**Accent color for stats**: soft pink | brand secondary | neon yellow | bright cyan

**Lifestyle action**: hands holding product | product mid-apply | product in-use context | product on surface with implied use

**Energy**: calm evidence-based | confident clinical | warm and relatable | premium and restrained

## Format-specific rules

- **Stats must be verifiable.** Every percentage or number cited must have a source. Agent 4 and Agent 7 flag fabricated stats.
- **Stats require asterisk/source line in most markets.** Consumer protection rules (US FTC, EU consumer law) often require disclosure of the study or source. Add a tiny footnote if the category demands it.
- **Headline reads as data.** Use exact percentages ("87%") not vague claims ("most"). Specificity IS the credibility.
- **Lifestyle shot must match the claim.** If the headline is about sleep, the photo is about morning / bed / nighttime — not generic lifestyle.
- **One stat headline, not three.** Don't stack multiple claims in one frame. Pick the strongest.

See `headline_template.md` for shared Global rules.
