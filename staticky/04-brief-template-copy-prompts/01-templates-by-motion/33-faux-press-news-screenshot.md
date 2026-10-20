# 33 — Faux Press / News Article Screenshot

🏷️ Looks like a real news article screenshot. Publication masthead on top, UGC-style photos below. Borrowed authority via press mimicry.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350)
- **needs_product_images:** false (product appears in the UGC photos, held by models)
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 340px (scaled for aspect)
- **bottom_safe_zone:** 430px (scaled for aspect)

## Product reference rule (CRITICAL)

Product must be visible in the UGC photos, held by models. Every image prompt MUST include: *"Use the attached product image as the primary reference — the product held in the UGC photos must be reproduced EXACTLY as it appears, do not invent or alter shape, color, labels, or design."*

## What this format is

Designed to look like a real online news article screenshot someone would share to their story. Top 25%: publication masthead (bold black serif "Daily Mail" / "TODAY" / "INSIDER" style), thin gray rule, "Latest Headlines" label, then a bold serif headline spanning full width. Bottom 60%: two side-by-side casual UGC selfies of different people holding the product. Borrows the authority of press without naming a real outlet.

## Copy template

```
[PUBLICATION NAME]     - 1-3 words. Fictional or category-adjacent.
                         e.g., "Daily Mail" / "TODAY" / "INSIDER" / "The Edit"

{{headline}}             - 15-25 words. Classic editorial style with quote + claim.
                         e.g., "'It's my holy grail product': The $[PRICE] [CATEGORY]
                                with over [NUMBER] five-star reviews"

No subhead. No CTA on the "article." No brand logo. Should look like an organic article
screenshot, not a designed ad.
```

## Image generation prompt

```
Use the attached product image as the primary reference — the product held in the UGC photos must be reproduced EXACTLY as it appears, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for color and tone only.

Create a faux press / news article screenshot ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350, 4:5 vertical].

COMPOSITION:
One continuous image filling the entire frame, designed to look like a screenshot of an online news article.

Top 25%: white background. Large bold black serif masthead "[PUBLICATION NAME]" centered or left-aligned, in a recognizable news-site typographic style. Below: thin gray horizontal rule spanning full width. Small gray sans-serif text "Latest Headlines" left-aligned below the rule. Below that: bold black serif article headline spanning full width, 2-3 lines: "{{headline}}".

Bottom 60%: two side-by-side casual UGC-style photos separated by a thin white gutter. Each photo shows [PEOPLE — e.g., two different young women, one brunette, one blonde / a young man and a young woman / two friends of different ages] each holding the product (reproduced exactly from reference) in a casual selfie pose.
- Left photo: [LIGHTING 1 — natural daylight, outdoor or near-window]
- Right photo: [LIGHTING 2 — warm indoor evening light]

Photos should look like real customer submissions, not studio shots. iPhone-quality, slight grain, casual framing. Product label clearly visible in both.

No brand logo on the layout. No CTA button. No call-out badges. Must look like an organic article someone screenshotted and shared.

TYPOGRAPHY:
Masthead in a news-site-style heavy serif (Times-like, Playfair, or similar). Headline in matching heavy serif. "Latest Headlines" in a small neutral sans-serif.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
White background in the article zone. Photos warm and natural, not retouched-perfect.

MOOD:
Editorial, borrowed-authority, shareable. "Did you see this article?"
```

## Variation vectors

**Publication style**: tabloid masthead (Daily Mail-style, default) | clean modern outlet (TODAY / INSIDER-style) | glossy magazine (Vogue-style) | niche vertical ("The Edit" / "Well+Good"-style)

**Photo count**: 2 side-by-side (default) | 1 large hero photo | 3 stacked thumbnails

**Person combo**: two women different hair (default) | man + woman | friend group | older customer testimonial

**Headline angle**: 'holy grail' quote | price + review count | "I tried it for 30 days" | "The product every [AUDIENCE] is buying"

**Lighting mix**: day + evening (default) | both daytime | both indoor warm | outdoor + bathroom-mirror

**Energy**: breathless tabloid | credible editorial | aspirational glossy | insidery vertical

## Format-specific rules

- **Never use a real publication name or logo.** "Forbes," "Vogue," real mastheads = legal liability. Use fictional-but-plausible names or category-adjacent alternatives.
- **Headline must reflect real product claims.** The article format borrows authority — fabricated review counts or fake price points break it.
- **UGC photos must feel real.** Studio polish kills the format. iPhone casual + varied lighting is the credibility.
- **Product visible and on-reference in both photos.** If the product isn't clearly readable in the photos, the ad fails.
- **Legal / disclosure.** Mimicking press without clear sponsored-content disclosure may violate ad rules in many markets. Verify compliance.
- **No CTA, no logo overlay.** The whole format dies if it looks designed.

See `headline_template.md` for shared Global rules. See #10 for a more explicit press/editorial variant and #20 for advertorial.
