# Step 1 — Ideate (animation concepts + missing frame prompt)

## What this step does

Takes a validated static ad and generates 5 animation concepts. For each concept, identifies whether the static is the start frame or end frame, then writes a Nano Banana 2 prompt to generate the missing frame.

## Prerequisites

- [x] Winning static ad as PNG
- [x] Brand Spec Card + Visual Style Card (for brand consistency)

## Prompt

Paste into Claude with your static ad uploaded:

---

I want to animate this static ad. Give me 5 animation concepts. For each one tell me: (1) Is my static the START or END frame? (2) What does the other frame look like — describe it in detail? (3) What motion happens between the two frames? (4) Why does this motion make sense for the product? Rules: all text must stay frozen in place throughout the animation, no camera movement, 3-4 seconds max

---

## Output

Save Claude's response to:
```
brands/{brand}/brand-dna/animations/{date}-{winner-slug}/animation-concepts.md
```

Pick the concept that best serves the winning ad's angle. Move to Step 2 with that concept's Nano Banana prompt.
