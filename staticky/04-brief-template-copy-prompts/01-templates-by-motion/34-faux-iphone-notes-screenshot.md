# 34 — Faux iPhone Notes / App Screenshot

🏷️ Disguised as an iPhone Notes screenshot. Headline + 3 food-equivalency benefits with checkmarks. Product casually overlaps the note. Info-dense in a native UI.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

The ad mimics an iPhone Notes app screenshot. Top: iOS status bar + Notes nav bar + timestamp. Main area: bold serif headline + 3 benefit rows with brand-color checkmarks and food-equivalency copy ("More Vitamin D than 800 mushrooms"). The product breaks into the note from the right edge with spilled pieces at its base. Feels like a note someone jotted — which is exactly the trick.

## Copy template

```
{{headline}}                - 4-8 words. Bold black serif.
                            e.g., "In Just 2 Gummies A Day" / "One Scoop. Every Nutrient."

[BENEFIT 1-3]             - Each in food-equivalency format: "More [X] than [Y]".
                            Use vivid comparisons that evoke volume / absurdity.
                            e.g., "More Vitamin D than 800 mushrooms"
                                  "More Folate than 4 cups of spinach"
                                  "More Vitamin B1 than 7 cups of broccoli"

[DATE + TIME]             - Small gray metadata, looks like a real note.
                            e.g., "13 July 2023   10:44"

No headline outside the note. No CTA button. No brand logo overlay. The note IS the ad.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for color and tone only.

Create a faux iPhone Notes screenshot ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame, designed to look like an iPhone Notes app screenshot.

Top: realistic iOS status bar — time "[TIME — e.g., 10:45]" left, signal bars / wifi icon / battery icon right, all in black on white.

Below: iOS Notes navigation bar — blue "< All iCloud" back arrow on the left, small share icon and three-dot menu icon on the right. Thin gray hairline below the nav.

Below the nav: small gray sans-serif timestamp text "[DATE + TIME — e.g., 13 July 2023  10:44]" left-aligned.

Main content area on white background:
- Bold black serif headline "{{headline}}" — large, 2 lines max.
- Below: 3 benefit rows, vertical stack, generous line spacing. Each row: a filled [BRAND COLOR from spec card] circle checkmark + [EMOJI matching the benefit] + bold black serif text:
  * "[BENEFIT 1 — food-equivalency format]"
  * "[BENEFIT 2 — food-equivalency format]"
  * "[BENEFIT 3 — food-equivalency format]"

Right side of the content area, overlapping the benefit text slightly and breaking out of the note's right edge: the product (reproduced exactly from reference) at a slight angle, with [DETAILS — e.g., a few gummies / capsules / powder / drops] spilling out at the base onto the white surface. Product casually placed, breaking the note frame.

Clean white background throughout the note area. Subtle iOS UI details (rounded corners, thin separators) feel authentic.

TYPOGRAPHY:
iOS native fonts for UI elements (status bar, nav, timestamp). Content headline + benefits in a warm black serif (Georgia / Charter / New York-style). Brand typography is secondary here — Notes UI authenticity is primary.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Pure white background. Black serif text. Brand color reserved for checkmarks only.

MOOD:
Personal, jotted-down, "I made this note for myself." Info-dense but native.
```

## Variation vectors

**App style**: iOS Notes (default) | iOS Reminders (checkbox list) | Apple Mail draft | Google Keep note | simple notepad app

**Benefit format**: food equivalency (default) | stat + unit ("12g protein per scoop") | "No [X], no [Y]" | ingredient callout with dose

**Product placement**: breaking from right edge (default) | from bottom edge | overlapping upper-right | floating mid-note

**Spilled detail**: gummies (default) | capsules | powder scoop | drops / droplets | product pieces

**Emoji use**: one emoji per row (default) | no emoji (cleaner) | mix of emoji + symbols

**Energy**: warm and personal | clinical and credible | playful with emoji | minimal and calm

## Format-specific rules

- **iOS UI must be convincing.** Wrong time format, wrong battery icon, wrong nav color = ad feels fake. Reference real iOS Notes screenshots.
- **Food equivalencies must be true.** "More Vitamin D than 800 mushrooms" gets fact-checked. Use real math from the product's nutrition panel.
- **Product breaks the frame.** If the product sits neatly inside the note, the ad looks designed. Spilling out = native feel.
- **Checkmarks stay brand-color.** The one splash of brand color cues the viewer this is branded, even though the layout is app-native.
- **Headline stays in the note.** Never put a headline outside the note area — breaks the Notes illusion.
- **No CTA, no logo overlay.** Same reason as #29 and #32.

See `headline_template.md` for shared Global rules. See #29 / #32 / #33 for other native-looking formats.
