# Step 7 (Bonus) — Animate Your Statics

Turn a winning static ad into a 3-4 second animation in ~15 minutes.

**Key insight:** You're not asking AI to "animate your ad." You create a **start frame** and an **end frame**, then let AI interpolate between them.

## 5-step workflow

1. **Ideate** (`step-1-ideate.md`) — Upload static to Claude. Get 5 animation concepts + Nano Banana prompt for the missing frame.
2. **Create Frame** (`step-2-create-frame.md`) — Run Nano Banana prompt. Now you have start + end frames. Cap at 3-4 iterations.
3. **Get JSON** (`step-3-get-json.md`) — Same Claude window. Upload both frames. Get Veo 3.1 JSON prompt. All text frozen.
4. **Animate** (`step-4-animate.md`) — Veo 3.1 Fast via Flow (labs.google/flow). Generate 4-8 variations. Always use Fast/Lower Priority mode.
5. **Iterate** (`step-5-iterate.md`) — Download GIF. Upload to Claude. Describe problems. Get updated prompt.

## Prerequisites

- Validated winning static ad (ideally from steps 1-5 or a multiplied winner from step 6)
- Access to Nano Banana 2 (fal.ai or Gemini API)
- Access to Flow (labs.google/flow) for Veo 3.1

## Output location

```
brands/{brand}/brand-dna/animations/{date}-{winner-slug}/
├── source-static.png          # the winning static ad
├── start-frame.png            # often = source static
├── end-frame.png              # generated via Nano Banana (step 2)
├── animation-concepts.md      # 5 ideate concepts (step 1)
├── veo-prompt.json            # Veo 3.1 JSON (step 3)
├── variations/                # 4-8 Veo outputs (step 4)
│   ├── v1.mp4
│   └── ...
├── winner.gif                 # chosen animation
└── iterations.md              # iteration log (step 5)
```

## Rules

- **Cap frame generation at 3-4 iterations.** If you can't nail the end frame in 4 tries, rethink the concept.
- **Text stays frozen.** All copy renders identically in start and end frames; Veo interpolates the scene, not the text.
- **Always use Fast/Lower Priority mode** in Flow — it's cheaper and good enough for 3-4s ads.
- **Iterate on the prompt, not the frames.** If Veo output is off, fix the JSON prompt and re-run; don't keep regenerating frames.
