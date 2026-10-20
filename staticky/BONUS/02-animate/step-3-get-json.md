# Step 3 — Get the Veo 3.1 JSON Prompt

## What this step does

Upload both frames to the same Claude window (that ran Step 1). Claude writes the Veo 3.1 JSON prompt that describes the motion between them, with all text frozen.

## Prerequisites

- [x] Start frame PNG (from Step 1 decision + Step 2 output)
- [x] End frame PNG (from Step 1 decision + Step 2 output)
- [x] Same Claude conversation as Step 1 (for context continuity)

## Prompt

Paste into the same Claude window with both frames uploaded:

---

I'm uploading two frames for a video animation.

IMAGE 1 is the START frame.
IMAGE 2 is the END frame.

The animation concept: [describe your concept, e.g. "gummy bears march into frame and lift the product up into its final position."]

Write me a comprehensive Veo 3.1 JSON prompt that creates a smooth 8 second animation from the start frame to the end frame.

The prompt MUST include:
- Every piece of text from both frames reproduced verbatim so the fonts don't degrade during generation
- Explicit instruction that ALL text stays completely frozen in place throughout — no movement, no warping, no fading
- No camera movement whatsoever
- The background stays perfectly still
- A detailed description of the motion: what enters, from where, how it moves, the physics and easing
- The animation must resolve cleanly into the end frame as its final resting state
- Describe what stays still and what moves — be explicit about both

Format as a ready-to-paste JSON prompt for Veo 3.1.

---

> **Pozn.:** prompt hovorí "8 second animation", ale overview sekcia na Motion Foundations stránke uvádza 3-4s. Pôvodný prompt počíta s 8 s — ak chceš kratšie Reels/Stories (3-4s), priamo v prompte zmeň číslo pred tým, než ho pošleš Claudovi.

## Output

Save the JSON to:
```
brands/{brand}/brand-dna/animations/{date}-{winner-slug}/veo-prompt.json
```

## Why JSON

Veo 3.1 responds more reliably to structured JSON than to prose. Each field maps to a control the model actually uses, so you get predictable motion instead of creative reinterpretation.
