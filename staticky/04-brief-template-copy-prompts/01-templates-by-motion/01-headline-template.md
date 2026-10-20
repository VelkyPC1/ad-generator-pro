# Headline

## Metadata

- **aspect_ratio:** 9:16 default (1080x1920) | 4:5 alt (1080x1350) | 1:1 alt (1080x1080)
- **needs_product_images:** true (Style A, B) | false (Style C typography-dominant)
- **reference_uploads:** brand-spec-card.png + visual-style-card.png + product image
- **top_safe_zone:** 270px (for 9:16)
- **bottom_safe_zone:** 340px (for 9:16)

## Product reference rule (CRITICAL)

Never describe the product appearance from text assumptions. Every image prompt MUST include: *"Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design."* This rule is non-negotiable across all styles.

## What this format is

The most common static format. A single dominant headline carries the entire message. The visual and the headline work together as equal partners -- neither makes sense without the other. This format wins through compression: one idea, stated perfectly, with an image that amplifies it.

## Styles

### Style A: Product hero with headline

The product commands the frame. The headline gives the viewer a reason to care about what they're looking at. Clean, direct, commercial.

#### Copy template
```
{{headline}}    - 3-12 words. One core idea. Must work as a standalone statement.
                If you covered the image, the headline alone should make someone curious.

{{subhead}}     - Optional. 5-15 words. Adds a new dimension: proof, specificity, or urgency.
                Must not repeat the headline.

{{cta}}         - Optional. 2-5 words.
```

#### Image generation prompt
```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a static ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO].

COMPOSITION:
One continuous image filling the entire frame. The product (reproduced exactly from the reference image) is the visual hero, positioned [PRODUCT POSITION from variation selection] and occupying roughly 40-60% of the visual frame. Shot at [FOCAL LENGTH from variation selection, e.g., 50mm f/2.8] for a premium commercial feel.

The headline "{{headline}}" is rendered as the dominant text element, positioned [TEXT POSITION from variation selection]. Headline and product should feel in conversation — headline explains what the product delivers, product proves it's real.

[If SUBHEAD present]: Render "{{subhead}}" directly below or near the headline at ~40-50% of the headline's visual weight. Natural continuation, not a separate element.

[If CTA present]: Render "{{cta}}" styled per brand spec card CTA treatment at the bottom.

TYPOGRAPHY:
Per uploaded brand spec card — all fonts, weights, and colors. Headline at a scale that balances with the product (first or second thing the eye reads).

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px kept clear of critical content (platform UI overlap zones).

COLOR AND TREATMENT:
Background from brand spec card palette. Product and headline need clear contrast. [BACKGROUND from variation selection]. Lighting: [LIGHTING from variation selection].

BRAND IDENTITY:
Logo per brand spec card rules (optional — only when the ad needs brand ID at first glance).

PHOTOGRAPHY DIRECTION:
Per visual style card. The product must look premium and desirable. Commercial-grade image.

MOOD:
[ENERGY from variation selection]. Feeling: one idea, perfectly executed.
```

#### Variation vectors
**Product position**: center with headline above | left side with headline right | bottom half with headline top | angled/dynamic positioning | flat lay from above

**Text position**: top third of frame | overlaid on a clean area of the image | bottom third above CTA | centered vertically beside product

**Background**: solid brand color | lifestyle context related to the persona | clean white/neutral surface | textured surface from brand world | environmental setting

**Lighting**: soft natural light with gentle shadows | studio lighting, clean and commercial | warm golden hour | bright and even | dramatic with contrast

**Focal length**: 50mm f/2.8 (clean commercial) | 85mm f/2.8 (compressed hero) | 35mm f/2.0 (environmental) | 100mm macro (texture-focused)

**Energy**: confident and direct | warm and inviting | bold and attention-grabbing | premium and restrained | playful and energetic

---

### Style B: Lifestyle context with headline

A person or scene using/experiencing the product. The headline provides the meaning layer that turns a lifestyle image into an argument. The viewer sees themselves in the scene; the headline tells them why they should want to be there.

#### Copy template
```
{{headline}}    - 3-12 words. Should resonate with the persona's identity or desire.
                The "photograph test" applies: if you read this headline, you should
                picture the exact person it's for.

{{subhead}}     - Optional. 5-15 words.

{{cta}}         - Optional. 2-5 words.
```

#### Image generation prompt
```
Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for all typography, colors, and photography direction.

Create a static ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO].

COMPOSITION:
One continuous image filling the entire frame. Scene the target persona ([PERSONA SUMMARY]) would immediately recognize as their life or aspiration. The product (reproduced exactly from reference) is present naturally — being used, held, or visible in context. Never staged or forced. Shot at [FOCAL LENGTH from variation selection, e.g., 35mm f/2.0] for environmental authenticity.

The headline "{{headline}}" rendered as text overlay, positioned [TEXT POSITION from variation selection] in a visually calm area for legibility. Speaks directly to the person in the scene (or the viewer who sees themselves in it).

[If SUBHEAD present]: "{{subhead}}" below the headline at secondary scale.

[If CTA present]: "{{cta}}" styled per brand spec card at the bottom.

TYPOGRAPHY:
Per brand spec card. Headline font/color must hold legibility against lifestyle imagery. If background behind text is busy: subtle shadow, semi-transparent backing, or place text in naturally calm area. No heavy graphic overlays.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear. Headlines avoid extreme edges.

COLOR AND TREATMENT:
Scene feels authentic and aspirational, never stock-photo generic. Color grading aligned with brand visual style card. Product recognizable but not artificially highlighted.

BRAND IDENTITY:
Logo per brand spec card (optional).

PHOTOGRAPHY DIRECTION:
Per visual style card. Candid and real, captured-in-the-moment feel. Persona ([PERSONA SUMMARY]) should think "that's me" or "that's who I want to be."

MOOD:
[ENERGY from variation selection].
```

#### Variation vectors
**Text position**: top third | bottom third | left-aligned with image right | centered overlay on calm area

**Scene context**: morning routine | outdoor/active | social gathering | quiet personal moment | work/productivity

**Focal length**: 35mm f/2.0 (environmental) | 50mm f/1.8 (natural perspective) | 85mm f/2.8 (subject compression)

**Energy**: aspirational and warm | confident and direct | relatable and casual | premium and elevated | energetic and dynamic

---

### Style C: Typography-dominant

Minimal or no imagery. The headline IS the creative. The words, set in the brand's typography at scale, are the visual. Works when the headline is strong enough to carry the entire ad alone.

#### Copy template
```
{{headline}}    - 3-10 words. Must be powerful enough to be the entire visual.
                Short, punchy, and rhythmic. Every word earns its place.

{{subhead}}     - Optional. 5-15 words. Secondary scale.

{{cta}}         - Optional. 2-5 words.
```

#### Image generation prompt
```
[If product appears]: Use the attached product image as the primary reference — reproduce the product EXACTLY as it appears in the photo, do not invent or alter shape, color, labels, or design. Reference the attached brand spec card and visual style card for typography and colors.

Create a static ad for [BRAND NAME]'s [PRODUCT NAME]. [ASPECT RATIO].

COMPOSITION:
One continuous image filling the entire frame. Typography-driven — the headline "{{headline}}" is the dominant visual, centered at maximum scale. Words ARE the creative — bold statement, declaration, or provocation.

The product (reproduced exactly from reference) may appear [PRODUCT TREATMENT from variation selection] — small in a corner, at the bottom, or absent entirely if the headline carries the message alone.

[If SUBHEAD present]: "{{subhead}}" below the headline at clearly secondary scale.

[If CTA present]: "{{cta}}" at bottom per brand spec card.

TYPOGRAPHY:
Per brand spec card. Headline in the brand's most impactful headline font at the largest feasible scale. [TYPE TREATMENT from variation selection]. Typography should feel intentional and designed — not text on a background.

SAFE ZONES:
Top [TOP SAFE ZONE]px and bottom [BOTTOM SAFE ZONE]px clear.

COLOR AND TREATMENT:
Background: [BACKGROUND from variation selection]. Headline color creates maximum contrast. Tight palette — power of words + brand identity, not decoration.

BRAND IDENTITY:
Logo per brand spec card (optional).

MOOD:
[ENERGY from variation selection]. Feeling: these words demanded to be said this way.
```

#### Variation vectors
**Product treatment**: small in bottom-right corner | small centered below headline | absent entirely | subtly integrated into background

**Type treatment**: all caps (if brand guidelines allow) | mixed case with key word emphasized through size | stacked with line breaks for rhythm | single line at maximum width

**Background**: solid brand primary color | solid brand accent color | black or very dark | white or very light | textured surface

**Energy**: bold and declarative | quiet and confident | provocative and edgy | warm and personal | minimal and sophisticated

---

## Global rules for headline format

### Visual-headline coherence (CRITICAL)

The image must visually reinforce the headline's concept — not just accompany it. If the headline makes a claim, paints a picture, or names a scenario, the image must SHOW that claim, picture, or scenario. A generic product-on-dark-background shot fails this test unless the headline is itself generic (which it shouldn't be).

**The coherence test:** Cover the headline. Does the image alone hint at the same idea? Cover the image. Does the headline alone conjure a visual that matches? If both answers are yes, the ad has coherence. If either answer is no, the visual and headline are working independently — which means the ad is working at half power.

**Examples:**
- Headline: "Your Morning Shouldn't Start with a Fight." (coffee brand) → Image must show the frustrating morning scenario, not just a coffee cup on marble. The "fight" is the concept and it must be visible.
- Headline: "Finally, a Bag You Don't Hide at Check-In." (luggage brand) → Image should show the bag in an airport or travel context as a statement piece, not on a white studio backdrop.
- Headline: "10,000 Five-Star Reviews. Zero Returns." → Image should emphasize durability or satisfaction -- the product in pristine condition after visible use, or multiple happy contexts.
- Headline: "Stop Rebooking. Start Arriving." (travel brand) → Image should show the contrast between chaos and calm -- not just a destination photo.

**When the headline contains a metaphor, scene, or narrative (e.g., "graveyard," "fight," "stop rebooking"), the image must stage that metaphor, scene, or narrative literally.** The visual is not a decoration — it is the other half of the argument.

### Agent 7: Copy Editor / Proofreader (REQUIRED)

Every ad brief must pass through a dedicated copy-editing agent before final approval. This agent checks ONLY for mechanical correctness -- it is not a strategy or creative review. It has veto power: any error it finds blocks approval regardless of other agents' scores.

**Checklist:**
1. **Grammar**: Subject-verb agreement, tense consistency, dangling modifiers, pronoun-antecedent agreement. Every headline is a sentence -- it must be grammatically correct even if it uses fragments for style.
2. **Spelling**: Every word checked. Brand names verified against official capitalization and spacing (e.g., if the brand uses "ProCook" not "Procook" or "pro-cook").
3. **Punctuation**: Periods, commas, apostrophes, quotation marks. Verify possessives vs. plurals. Verify contractions.
4. **Banned characters**: NO em dashes (--). Use hyphens (-) for compound words only. If a pause is needed, use a period, comma, or ellipsis. NO en dashes. NO semicolons in headlines.
5. **Number consistency**: Dollar signs, decimals, and commas in numbers must follow a single convention throughout the brief. Use whole dollars (e.g., "$49") not "$49.00" unless cents matter.
6. **Duplicate content**: The same data point (price, stat, claim) must not appear in more than one text element. If the price is in the headline, it cannot also appear as a separate price display.
7. **Word count compliance**: Every text element must be recounted against the format spec limits. No rounding, no "close enough."
8. **Brand name capitalization**: Verified against the brand's official usage in every instance.

**Scoring**: Pass/Fail. Any single error is a fail. The agent must list every error found with the exact text, the rule violated, and the corrected version.

### Price is not a default element

Price is not a default element. Include price only when the context makes sense for the specific execution. Not every ad needs a price. Adding price to every ad dilutes its impact and adds unnecessary copy.

### Fewer elements by default

Default to fewer elements, not more. Every text element must earn its place. If removing an element does not weaken the ad, remove it. Optional slots (CTA, headline, price, logo) should be left empty unless they meaningfully strengthen the specific execution.

### What to avoid
- Headlines that could apply to any product in the category
- Product and headline fighting for attention (one leads, one supports)
- Text placed over busy image areas without sufficient contrast
- Subheads that repeat the headline in different words
- Generic lifestyle imagery that doesn't connect to the specific persona
- **Product-on-dark-background shots that could work with ANY headline (visual-headline disconnect)**
- **Visuals that illustrate the product but not the headline's concept**
