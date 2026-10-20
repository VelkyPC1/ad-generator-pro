# 40 — Native / Ugly Post-It Note Style (Product Hero)

🏷️ Casual lifestyle product photo. A real yellow post-it stuck on the packaging with handwritten marker copy. Brand carried entirely by the product. Maximum organic energy.

## Metadata

- **aspect_ratio:** 4:5 default (1080x1350)
- **needs_product_images:** true
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 340px (scaled for aspect)
- **bottom_safe_zone:** 430px (scaled for aspect)

## Product reference rule (CRITICAL)

Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."*

## What this format is

A lifestyle product photo shot in a real-life setting (kitchen floor, bathroom counter, coffee table). Product centered but slightly off-axis — feels found, not composed. A yellow post-it note stuck directly onto the product face with tape, slightly crooked, with 3-4 lines of handwritten marker text (the hook / argument / punchline). No logo overlay, no designed text — the product packaging IS the brand, the post-it IS the copy. Below the photo: a small plain caption line. Maximum "ugly ad" energy.

## Copy template

```
[POST-IT LINE 1]    - Short, lowercase, setup or hook.
                      e.g., "ok so" / "hear me out" / "not even kidding"

[POST-IT LINE 2]    - Continuation or turn.
                      e.g., "my dog won't eat anything else" / "replaced my whole cabinet"

[POST-IT LINE 3]    - Punchline, result, or kicker.
                      e.g., "and he's the pickiest eater ever" / "skin is unreal now"

[POST-IT LINE 4]    - Optional final beat or emoji.
                      e.g., "10/10 🐶" / "just try it" / "😭❤️"

[CAPTION]           - Below the photo on a plain strip.
                      e.g., "brandname.com — the one that actually works"

No headline. No CTA button. No logo overlay. Brand identity = product packaging only.
```

## Image generation prompt

```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for product color accuracy only.

Create a native / ugly post-it note style product hero ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO — 1080x1350, 4:5].

COMPOSITION:
One continuous image filling the entire frame. A lifestyle product photo set in [REAL-LIFE SETTING — a warm kitchen floor / a bathroom counter / a living room coffee table / a bedroom nightstand] with [LIGHTING — soft natural daylight from a nearby window / warm diffused morning light]. Naturally blurred background showing [BACKGROUND DETAILS — lower kitchen cabinets and a dog bowl / mirror edge and toiletries / couch cushions and a throw blanket].

Frame very slightly off-center — product not perfectly centered, [LEFT / BOTTOM / RIGHT] edge of product very slightly cropped. Feels found, not composed. Slight natural sensor grain consistent with a phone camera in indoor daylight. Subtle natural vignette at frame corners.

Center of frame, large and dominant: the product (reproduced exactly from reference) sitting on [SURFACE — light wood floor / raw wood shelf / marble counter / linen cloth], slightly angled toward the viewer. [SCATTERED SURFACE DETAIL — a few scattered kibble pieces / sea salt crystals / product crumbs / sprinkled powder] on the surface around the base of the product for casual realism.

Stuck directly onto the front face of the product: a [POST-IT COLOR — yellow] square post-it note, slightly crooked and not perfectly straight — slightly trapezoid from the angle it was pressed on. Realistic paper texture with a horizontal crease across the middle as if it was folded once. Subtle curl at the bottom-right corner only. Held at the top by a small piece of [TAPE COLOR — clear / yellow / white] tape, slightly wrinkled.

Handwritten on the post-it in thick black marker-style lettering, imperfect and uneven, lowercase natural writing — not formatted, not centered, not evenly spaced:
"[LINE 1]"
"[LINE 2]"
"[LINE 3]"
"[LINE 4]"

One word is slightly heavier-inked or underlined from natural pen pressure. No attribution line. No signature.

Bottom center of frame, outside the photo on a plain white or off-white strip: small plain lowercase sans-serif caption text: "[BRAND URL] — [CAPTION]"

No logo overlay anywhere. Brand identity carried entirely by the product packaging visible in the photo. No border.

TYPOGRAPHY:
Post-it text: handwritten black marker, imperfect and uneven. NOT a handwriting font — actual marker lettering. Caption below: small plain sans-serif (system font feel).

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Natural indoor photo. Yellow post-it with black marker. Product in its real packaging colors. Caption strip plain white.

MOOD:
[MOOD — e.g., casual, earnest, homemade / messy, honest, scroll-stopping / warm, funny, real]. "Someone stuck a note on their product and took a photo."
```

## Variation vectors

**Setting**: kitchen floor (default) | bathroom counter | coffee table | bedroom nightstand | outdoor porch step

**Post-it color**: classic yellow (default) | neon pink | pastel blue | neon green | white

**Tape style**: clear tape slightly wrinkled (default) | yellow masking tape | white washi tape | no tape (self-adhesive)

**Marker style**: thick black marker (default) | thin black pen | blue pen | brown marker

**Scattered detail**: kibble / product pieces (default) | powder / crumbs | liquid drops | botanical bits | nothing

**Caption style**: "url — short tagline" (default) | url only | no caption | longer casual sentence

**Mood**: casual and earnest | funny and warm | messy and honest | minimal and cool

## Format-specific rules

- **Post-it must look physically real.** Slight crookedness, tape wrinkle, paper crease, corner curl. Perfect placement = graphic design, not a post-it.
- **Handwriting must be imperfect.** Uneven letter size, slightly off-baseline, varied pen pressure. Handwriting fonts look fake — describe actual marker strokes.
- **Product is NOT perfectly centered.** Slight off-center framing, slight crop at one edge. Perfect centering = product shot, not "found photo."
- **No logo overlay, no designed text.** The whole format depends on the brand being carried by the packaging. Adding a logo on top breaks it.
- **Post-it copy is short.** 3-4 lines of handwritten text is the max. Paragraphs don't fit a post-it — and they break the casual energy.
- **Caption is lowercase and plain.** Uppercase or styled caption = ad. Lowercase system font = organic post.

See `headline_template.md` for shared Global rules. See #29, #32, and #36 for other organic / native-format variants.
