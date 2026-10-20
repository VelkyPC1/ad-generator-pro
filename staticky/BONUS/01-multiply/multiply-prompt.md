# Step 6 — Multiply One Winning Ad Across All Format Templates

Use this after you have a **validated winner** — an ad that has real campaign signal (CTR, ROAS, proven performance). Multiplies the winner's strategic DNA across every other format template in the library.

## When to use

- [x] Ad from steps 1-5 ran in market
- [x] Performance data confirms it's a winner (not just your opinion — actual signal)
- [x] You want to scale its DNA across 39 other format structures to systematically test what else works

**Do NOT use this step on an unvalidated ad.** Multiplying a mediocre ad produces 40 mediocre ads.

---

## The prompt

Paste this into Claude. Upload your format template `.md` files first.

---

**Multiply one winning ad across all your format templates**

I have a winning ad brief that I want to multiply across different format templates. The original brief is below.

Here are my format templates: [upload or list your .md template files]

For EACH format template, rewrite the brief to fit that format exactly:
- Keep the same persona, angle, emotion, and core product truth
- Rewrite the copy to match the new format's structure (headline lengths, copy slots, required elements)
- Follow the format template's copy rules and variation vectors
- Adjust the creative direction to match the new format's visual requirements
- Write a complete Nano Banana 2 image generation prompt for each

**Do not change the strategic foundation. Only change the packaging.**

The original brief:
[paste your winning brief here]

---

## What travels across formats (DNA)

- **Persona** — same target audience
- **Angle** — same strategic wedge
- **Emotion** — same target emotional response
- **Core product truth** — same claim/promise/proof
- **Voice** — same brand fingerprint

## What changes per format (packaging)

- Copy structure (word counts, slots, required elements)
- Visual composition (product position, text position, background)
- Typography scale and placement
- Supporting elements (stats, badges, quotes, icons)
- Variation vectors (per format template)

## Governance

Every multiplied variation passes through:
- **Agent 2 (Angle Execution)** — DNA preserved across packaging?
- **Agent 4 (Brand Consistency)** — fingerprint intact?
- **Agent 6 (Format Compliance)** — new format's structural spec met?
- **Agent 7 (Copy Editor)** — mechanical correctness

Other agents (Persona Fit, Emotion, Copy Excellence) re-score since copy is new.

Thresholds unchanged: 90+ on all scored agents, Agent 7 PASS, otherwise iterate.

## Output location

```
brands/{brand}/brand-dna/multiplied-winners/{date}-{winner-slug}/
├── original-winner.md          # the validated winner brief
├── original-performance.md     # signal data (CTR, ROAS, why it won)
├── variations/
│   ├── {format-name}-brief.md         # multiplied copy brief
│   ├── {format-name}-scoring.md       # 7-agent scores
│   ├── {format-name}-generation.md    # Nano Banana prompt
│   └── {format-name}-output.png       # generated image
└── README.md                   # index of all variations with status
```

## Rules

1. **Validated winner only.** If there's no real signal, go back to steps 1-5 first.
2. **DNA is non-negotiable.** Persona, angle, emotion, product truth stay fixed.
3. **Skip incompatible formats.** If the winner's angle doesn't translate to a given format (e.g., a long-form manifesto angle won't fit a pure Headline format), flag it and skip rather than force.
4. **Re-score every variation.** Don't assume "it worked once, it'll work again" — each format change re-opens the scoring door.
5. **Track which variations win.** The multiplication tree becomes your format-strength matrix for this persona + angle combination.
