# 23 — Long-Form Manifesto / Letter Ad

🏷️ Copy-only manifesto. The writing IS the ad. No imagery, just a considered argument.

## Metadata

- **aspect_ratio:** 1:1 default (1080x1080) | 4:5 alt (1080x1350)
- **needs_product_images:** true (product at bottom only)
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for aspect)
- **bottom_safe_zone:** 340px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

Clean white background. A provocative short headline spans the top. Below it, a manifesto-style body in short punchy sentences (not paragraphs) — acknowledges an objection, reframes it, closes with a confident brand statement. The product sits small at the bottom as a closer. No icons, no badges, no CTA. The writing is the creative.

## Copy template

```
[PROVOCATIVE HEADLINE]   - 3-6 words. Short and declarative.
                           e.g., "They're not cheap." / "This isn't for everyone." / "We said no."

[MANIFESTO BODY]         - 12-18 short lines. Line breaks, not paragraphs.
                           Structure:
                           1-3 lines: acknowledge the objection / tension
                           4-8 lines: list what you'd lose if corners were cut
                           9-14 lines: reframe as a positive
                           15-18 lines: confident brand close

No CTA. No icons. No stats.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for typography and colors.

Create a long-form manifesto ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1080 / 1080x1350].

COMPOSITION:
One continuous image filling the entire frame. Background: clean white throughout. No background imagery. Text IS the creative.

Top (spans top 12-15% of frame): oversized bold black serif or sans-serif headline "[PROVOCATIVE HEADLINE]".

Below (spans middle 65-70% of frame): left-aligned body copy in smaller regular-weight black text, structured as short punchy sentences with line breaks between each (NOT paragraphs). Approximately 12-18 lines.

"[MANIFESTO BODY]"

Bottom 15-20%: the product (reproduced exactly from reference) centered or slightly right, product-only on white, clean studio shot angle. No props, no scene.

No icons, no badges, no CTA button, no stars.

TYPOGRAPHY:
Per uploaded brand spec card. Headline in a serif for literary weight (or sans for editorial modernism). Body in readable regular weight. Line-height generous. Line breaks are the pacing — each line hits a beat.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Pure white background. Black text. Product naturally lit. No color accents.

BRAND IDENTITY:
Product carries identity — no logo overlay.

MOOD:
Considered, confident, literary. "We have something to say, and we'll take the space to say it."
```

## Variation vectors

**Headline tone**: provocative objection ("They're not cheap") | declarative boundary ("We said no") | brand philosophy ("Quality is not a feature") | confessional ("We failed once. Never again.")

**Body structure**: objection → list → reframe → close (default) | story arc | principle-driven list | Q&A rhythm

**Body length**: 12 lines (tight) | 16-18 lines (default) | 20+ lines (dense, for patient audiences)

**Headline weight**: serif for literary feel | heavy sans-serif for modern editorial | italic for confessional

**Product treatment**: small centered at bottom (default) | small right-aligned | small in-text inline | flat lay small

**Energy**: literary and considered | confrontational and direct | warm and confessional | principled and quiet

## Format-specific rules

- **Short lines, not paragraphs.** The visual rhythm is the pacing. Paragraphs feel dense; line breaks feel musical.
- **Every line must earn its place.** Cut filler. If a line doesn't advance the argument, delete it.
- **No em dashes, no semicolons.** Use periods. The format is about rhythm, and punctuation that breaks the rhythm is wrong.
- **Product closes the ad — doesn't sell it.** The product appears at the end as "here's what we make." Not "buy now."
- **Brand voice carries.** This format fails for brands without strong voice. Works best for brands with editorial / considered / principled identity.
- **Agent 5 (Copy Excellence) is the critical scorer here.** This format stands or falls on copy quality.

See `headline_template.md` for shared Global rules.
