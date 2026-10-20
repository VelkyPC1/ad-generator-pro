# 29 — UGC + Viral Post Overlay

🏷️ Casual selfie doing mundane stuff. Reddit/X post screenshot overlay. The opinion is the hook. Zero selling energy.

## Metadata

- **aspect_ratio:** 9:16 default (1080x1920)
- **needs_product_images:** false (brand color reference only)
- **reference_uploads:** product image (for brand color reference ONLY — NOT as hero, product stays absent)
- **top_safe_zone:** 270px
- **bottom_safe_zone:** 340px

## Product reference rule (CRITICAL)

This format does NOT render the product. The product image is uploaded only for brand-color reference. The image prompt should say: *"Use the attached product image for brand color reference only. Do NOT render the product in this ad — it's intentionally absent. This must look completely native and organic, not branded."*

## What this format is

A casual iPhone selfie of a person doing something mundane (brushing teeth, making coffee, cooking). Overlaid in the center: a screenshot of a Reddit / X / Twitter post with a provocative opinion related to the product's problem space. The person appears to be reacting to or sharing the post. No product visible. No brand logo. No CTA. Works for awareness / hook ads where the opinion does the scroll-stopping.

## Copy template

```
[POST HEADLINE]       - 8-15 words. Provocative opinion in the product's problem space.
                        First-person or universal statement.
                        e.g., "UNPOPULAR OPINION: [category] marketing has been lying
                               to us about [specific pain point] for decades."

[POST BODY]           - 2-3 sentences expanding on the opinion.
                        Sounds like a real internet post — informal, opinionated.

[PLATFORM DETAILS]    - Subreddit / username / timestamp / upvote count.
                        e.g., "r/skincareaddiction • u/glowgetter • 2d • ⬆ 14.2k"

No headline on the ad itself. No product. No brand logo. No CTA.
```

## Image generation prompt

```
Use the attached product image for brand color reference only. Do NOT render the product in this ad. This should look completely native and organic — NOT an ad.

Create a UGC + viral post overlay ad. [ASPECT RATIO — 1080x1920, 9:16 vertical].

COMPOSITION:
One continuous image filling the entire frame. A casual iPhone-front-camera selfie of [PERSON DESCRIPTION — a man in his mid-20s, beanie, crewneck sweatshirt / a woman in her 30s, makeup-free, in pajamas] doing something mundane: [ACTION — brushing teeth / making coffee / cooking / walking a dog / getting ready in the mirror]. Slightly grainy, bathroom or kitchen lighting, no professional setup. The person is NOT looking at the camera — they're mid-task.

Overlaid in the center of the frame: a realistic screenshot of a [PLATFORM — Reddit / Twitter / X / TikTok] post:
- Small platform header with "[PLATFORM DETAILS — subreddit name, username, timestamp, upvote count]"
- Post title in bold: "[POST HEADLINE]"
- Post body in regular text: "[POST BODY]" (2-3 sentences)

The post should feel like the person is reacting to it or sharing it — NOT selling a product.

No product visible. No brand logo. No CTA. Only the natural person + the overlaid post.

TYPOGRAPHY:
The post screenshot uses the target platform's native typography (Reddit sans, Twitter/X sans, etc.). NOT brand font. This is critical — platform authenticity IS the hook.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Selfie looks raw — slightly grainy, natural light, iPhone front-camera quality. Post screenshot faithful to the target platform's UI (colors, fonts, layout).

MOOD:
Organic, opinionated, scroll-stopping. "Wait, is this even an ad?"
```

## Variation vectors

**Platform**: Reddit (default) | Twitter/X | TikTok comment | Instagram story | Facebook post

**Person action**: brushing teeth | making coffee | cooking | driving | walking | getting ready in mirror

**Person description**: young man casual | woman makeup-free | older parent | Gen Z aesthetic

**Opinion tone**: unpopular opinion | shocked-revelation ("Just learned...") | pushback ("Sorry but...") | validation ("Finally someone said it")

**Grain / polish level**: heavy grain (very raw) | medium (default) | slightly cleaner

**Selfie angle**: front-camera (default) | mirror selfie | third-person (someone else snapping)

## Format-specific rules

- **Must not look like an ad.** Drop shadows, brand overlays, polished typography = death. Keep everything raw.
- **No product, no logo, no CTA.** The WHOLE point is the post opinion — product reveal comes later in the funnel.
- **Post must connect to the category / problem space.** A skincare brand uses a skincare opinion. Random viral opinions disconnect from the brand.
- **Selfie should NOT be posed.** The person is mid-task, caught. Not looking at camera, not smiling at lens.
- **Legal / disclosure.** Most markets require sponsored content to be disclosed. This format hides the ad — verify legal compliance before shipping.
- **Opinions must not be inflammatory or offensive.** Sharp yes; cruel no. Don't use political or identity-based opinions as bait.

See `headline_template.md` for shared Global rules.
