# 09 — Negative Marketing (Bait & Switch)

🏷️ Fake bad review that's actually a rave. Scroll-stopper.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (scaled for 4:5)
- **bottom_safe_zone:** 340px (scaled for 4:5)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A fake one-star review card over a product background. The review text LOOKS negative at first glance ("I can't believe this," "I was so annoyed") but actually resolves into a positive reveal ("...that no one told me about this sooner"). A punchline at the bottom reframes it: "THE REVIEWS ARE IN." The bait-and-switch is the hook — the viewer stops to read what the "problem" is.

## Copy template

```
{{reviewer}}   - First name + last initial. e.g., "Sarah M."

[BAIT HEADLINE]   - 6-12 words. Sounds negative on first read, positive on second.
                    Must resolve into a compliment when fully understood.
                    e.g., "I can't stop using this and it's ruining my mornings — I'm waking up too fast."
                          "Worst decision I've made — now I can't go back to normal coffee."

[PUNCHLINE]       - 3-6 words. Reframes the bait.
                    e.g., "THE REVIEWS ARE IN." / "VERDICT: GUILTY AS CHARGED."

{{verified_tag}}    - "Verified Purchase" in orange pill style (mimicking Amazon UI).

{{cta}}             - Optional. 2-5 words.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a negative-marketing bait-and-switch ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350 / 1080x1080].

COMPOSITION:
One continuous image filling the entire frame. Background: close-up macro shot of the product (reproduced exactly from reference), slightly blurred to create depth, filling the entire frame as a soft backdrop.

Center: a white rounded-rectangle review card in Amazon-style layout, overlaid on the product background. Card contents:
- Top left: small gray circular default user-icon avatar
- Name: "{{reviewer}}" in bold dark sans-serif
- Rating: one gold filled star + four empty gray stars (one-star rating)
- Orange rounded-pill badge reading "Verified Purchase" in white text
- Bold dark sans-serif review text: "[BAIT HEADLINE]"

Bottom of frame (on the product backdrop, below the card): oversized bold white sans-serif "[PUNCHLINE]" in the brand's headline font, shadowed slightly for contrast against the product background.

[If CTA]: "{{cta}}" styled per brand spec card.

TYPOGRAPHY:
Review card mimics Amazon / marketplace UI — default sans-serif, not brand fonts. Punchline uses brand headline font at maximum scale.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White card with slight drop shadow. Orange verified pill (marketplace standard). One gold star, four gray. Product background in shallow-depth blur.

BRAND IDENTITY:
[BRAND] logo bottom right per spec card.

MOOD:
Provocative, clever, scroll-stopping. The viewer stops to figure out whether it's real.
```

## Variation vectors

**Review platform mimicry**: Amazon-style (default) | Google Reviews style | App Store review card style | generic minimal card

**Product background**: macro close-up of product (default) | product flat lay blurred | lifestyle scene blurred | solid brand color with product small

**Punchline framing**: "THE REVIEWS ARE IN." | "VERDICT: GUILTY AS CHARGED." | "CUSTOMERS WARNED US" | brand-specific phrase

**Bait angle**: "too good" complaint (product so good it creates a new problem) | "can't go back" regret framing | mock-accusation ("You knew and didn't tell me")

**Star count**: one filled + four empty (default) | zero filled (harder read) | all filled gold (punchline-first variant)

**Energy**: cheeky and clever | dry and deadpan | warm and self-aware

## Format-specific rules

- **The bait must resolve positively.** Cold read: sounds like a complaint. Second read: it's a compliment. If the text actually sounds negative after the reveal, it's broken.
- **Don't be cruel.** The joke is on the idea that the product is TOO good, not on the reviewer. No mockery of real consumer concerns.
- **Verified Purchase pill is orange, marketplace-standard.** Don't change the color — the familiarity of the UI is part of the trust mechanic.
- **Agent 4 may down-score this for premium brands.** This format reads as casual / community / D2C, not luxury. Check brand spec before using.
- **Disclosure rules.** In some markets (US FTC, EU consumer law), fake reviews are illegal even when "obviously ironic." If the format could be read as a real one-star review, include a small "Ad" or "Sponsored" tag to stay safe. Consult legal before production.

See `headline_template.md` for shared Global rules.
