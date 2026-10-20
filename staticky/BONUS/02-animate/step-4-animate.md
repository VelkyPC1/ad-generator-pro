# Step 4 — Animate with Veo 3.1 Fast

## What this step does

Runs the Veo 3.1 JSON prompt in Flow (labs.google/flow) to generate the actual animation. Generate 4-8 variations, pick the cleanest one.

## Prerequisites

- [x] Veo JSON prompt (from Step 3)
- [x] Start frame + End frame PNG (from Step 2)
- [x] Flow access at [labs.google/flow](https://labs.google/flow)

## How to run

1. Open Flow → new Veo 3.1 generation.
2. **Mode:** always **Fast / Lower Priority** (cheaper, good enough for 3-4s ad).
3. Upload `start-frame.png` and `end-frame.png`.
4. Paste the JSON from Step 3.
5. Set duration to 3-4 seconds, aspect ratio to match frames.
6. Generate **4-8 variations** — motion quality varies run to run, you want options.
7. Preview each. Pick the variation where:
   - Text stays stable (no warping, no flicker)
   - Product shape/labels stay consistent
   - Motion serves the angle (dramatizes pain / reveals benefit / builds tension)
   - No platform-UI intrusion in safe zones

## Output

Save all variations + the winner to:
```
brands/{brand}/brand-dna/animations/{date}-{winner-slug}/variations/
├── v1.mp4
├── v2.mp4
├── ...
└── WINNER-v{N}.mp4
```

## Rules

- **Always Fast mode.** Save Pro runs for hero assets only.
- **If 8 variations all fail the same way** (e.g., text warps in every run), the problem is the JSON or the frames, not Veo. Go back to Step 2 or Step 3.
- **Don't cherry-pick subtle differences.** If you can't tell which variation is best in 10 seconds, they're all equivalent — pick any and ship.
