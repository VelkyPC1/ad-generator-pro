# Step 2 — Create the Missing Frame with Nano Banana 2

## What this step does

Runs the Nano Banana 2 prompt from Step 1 to generate the missing frame (either the start or the end, depending on what Step 1 decided). Result: you now have BOTH frames ready for Veo 3.1.

## Prerequisites

- [x] Animation concept chosen from Step 1
- [x] Nano Banana prompt for the missing frame (from Step 1 output)
- [x] Source static (the winning ad)
- [x] Brand Spec Card + Visual Style Card

## Prompt

Paste into the same Claude window (with the source static uploaded as a reference):

---

I want to animate this static ad. The concept is: [describe your chosen concept from step 1, e.g. "gummy bears march into frame and lift the product up into position. My static is the END frame."]

My static is the [END] frame.

I need you to write a Nano Banana 2 prompt to generate the other frame as a still image. Based on the animation concept, figure out which elements need to be added, removed, or repositioned in the missing frame.

Every piece of text must be reproduced verbatim — same words, same position, same fonts, colors, and sizing. The background, lighting, and overall style must match my static exactly. Only change what needs to be different for the other frame of the animation.

The prompt must specify exact dimensions (1080x1920). I will upload my original static as a reference image — tell the generator to match everything from it except the elements that change between frames.

Be extremely detailed — NB2 won't guess, it only does what you tell it.

---

## Rules

- **Cap at 3-4 iterations.** If you can't nail the frame in 4 tries, the concept is probably off — go back to Step 1 and pick another concept.
- **Copy must be byte-identical** between frames. If text shifts even 2px, Veo will warp it.
- **Product must be visually identical** — Veo interpolates, so any inconsistency becomes motion artifacts.

## Output

Save both frames to:
```
brands/{brand}/brand-dna/animations/{date}-{winner-slug}/
├── start-frame.png
└── end-frame.png
```
