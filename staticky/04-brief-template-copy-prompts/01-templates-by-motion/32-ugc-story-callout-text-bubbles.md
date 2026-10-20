# 32 — UGC Story Callout / Text Bubble Explainer

🏷️ Casual iPhone photo holding the product. 5 Instagram-Story text bubbles scattered across it. Reads like a real story, not an ad.

## Metadata

- **aspect_ratio:** 9:16 default (1080x1920)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px
- **bottom_safe_zone:** 340px

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. This must look like a real person's Instagram Story, NOT an ad layout."*

## What this format is

A casual iPhone overhead photo of a hand holding the product over a lifestyle surface (desk, counter, nightstand). Scattered across the frame: 5 Instagram-Story highlighted text bubbles in varied colors — topic + educational hook + why this product + personal result + brand endorsement. Zero ad polish. The story-native typography and hand-placed feel IS the format.

## Copy template

```
[BUBBLE 1 — TOPIC + EMOJI]    - 2-4 words. Large bold.
                                e.g., "gut health 🌱" / "clear skin ✨" / "real energy ⚡"

[BUBBLE 2 — EDUCATIONAL HOOK] - 10-20 words. Surprising stat or mechanism.
                                e.g., "Did you know 70% of your immune system lives in your gut?"

[BUBBLE 3 — WHY THIS PRODUCT] - 8-15 words. Excited informal tone.
                                e.g., "this one has 50 billion CFU + prebiotics in one scoop 🤯"

[BUBBLE 4 — PERSONAL RESULT]  - 8-15 words. First-person, early experience.
                                e.g., "been on it 2 weeks and my bloating is GONE 😭"

[BUBBLE 5 — BRAND ENDORSEMENT]- 3-6 words. One short line of approval.
                                e.g., "[BRAND] you did it again ❤️"

No headline. No CTA. No brand logo overlay. The story-native bubbles ARE the ad.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Use the brand spec card and visual style card for color reference only. This must look like a real person's Instagram Story, NOT an ad layout.

Create a UGC Story callout ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1920, 9:16 vertical].

COMPOSITION:
One continuous image filling the entire frame. A casual iPhone overhead photo of [PERSON DESCRIPTION — e.g., a woman's hand with clean natural nails / a young man's hand with a simple watch] holding the product (reproduced exactly from reference) at a slight angle over [SURFACE — a clean white desk / marble counter / wooden nightstand] with [LIFESTYLE PROPS — a coffee mug / open journal / keys / earbuds] nearby. Natural overhead daylight, slightly warm, iPhone 15 quality. Slight sensor grain.

Scattered across the frame: 5 Instagram Story text bubbles using the native Story highlighted text tool. Each bubble has a highlighted background rectangle for readability. Vary highlight colors across the 5 bubbles (white, black, [BRAND COLOR], soft pastel, etc.) so they don't feel designed as a set:

- Bubble 1 (upper area, large and bold): "[TOPIC + EMOJI]"
- Bubble 2 (mid-upper): "[EDUCATIONAL HOOK]"
- Bubble 3 (mid, near product): "[WHY THIS PRODUCT]"
- Bubble 4 (mid-lower): "[PERSONAL RESULT]"
- Bubble 5 (lower area, small): "[BRAND ENDORSEMENT]"

Bubbles feel casual and hand-placed at slightly off angles, not aligned to a grid.

TYPOGRAPHY:
Instagram Story native fonts (Classic / Modern / Neon / Typewriter). NOT brand typography. Platform authenticity IS the format.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Photo looks iPhone-casual — slightly warm, subtle grain, not studio-lit. Bubble highlight colors varied, not matching any design system.

MOOD:
Native, organic, "my friend just posted this." Zero ad energy.
```

## Variation vectors

**Surface / setting**: clean white desk (default) | marble counter | wooden nightstand | café table | bed with rumpled sheets

**Person description**: woman's hand natural nails (default) | man's hand casual watch | hand with rings | older hand with wedding band

**Lifestyle props**: coffee + journal (default) | keys + earbuds | plant + book | skincare bottles | breakfast items

**Bubble color scheme**: varied mix (default) | all white | brand-color highlights | pastel set | monochrome with one accent

**Story font**: Instagram Classic (default) | Modern | Neon | Typewriter | Strong

**Energy**: casual and warm | excited early-user | calm matter-of-fact | enthusiastic fan

## Format-specific rules

- **Must not look like an ad.** Drop shadows, brand typography, logo overlays = death. The whole format lives on platform-native styling.
- **Bubbles hand-placed, not gridded.** Slightly off-angle, uneven spacing, some bubbles overlapping photo elements.
- **Use real Instagram Story fonts.** Classic / Modern / Neon / Typewriter / Strong. Not Helvetica or a brand font.
- **Emojis feel natural, not decorative.** One emoji per bubble where appropriate. Don't stack emojis for visual energy.
- **Personal result must be realistic.** "Lost 30 lbs in a week" breaks trust. Early-user honest tone wins.
- **Legal / disclosure.** Most markets require sponsored content disclosure — this format hides the ad. Verify compliance.

See `headline_template.md` for shared Global rules. See #29 for another organic-post format.
