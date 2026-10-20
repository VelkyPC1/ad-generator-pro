# Step 5 — Iterate on Your Animation

## What this step does

Download the winner variation as GIF. Upload it (plus both original frames) back to the Step 1 / Step 3 Claude window. Describe what's wrong. Claude rewrites the Veo JSON prompt to fix it.

## When to iterate

Iterate if you see any of these in the winner:
- Text warps, flickers, or drifts position
- Product shape/label morphs
- Motion is too fast / too slow / wrong beat
- Camera move feels unmotivated or seasick
- Safe zones get crossed mid-animation
- Background interpolation produces artifacts

## Prompt

Same Claude window as Step 1 / Step 3. Upload the GIF + both original frames:

---

I'm uploading the animation output plus my original start frame and end frame for reference.

Here's what's wrong with the animation:
[describe your issues — e.g. "no gummy bears appeared, the text warps at 3 seconds, the tube just floats up on its own instead of being lifted, there's a weird color shift in the background"]

Give me a corrected Veo 3.1 JSON prompt that fixes these issues. Keep everything that worked well.

---

## Rules

- **Iterate on the prompt, not the frames.** If frames are solid, don't regenerate — fix the JSON.
- **One issue at a time** for big problems. If you list 5 things to fix in one pass, Veo will compromise on all 5.
- **Cap iterations at 3.** If 3 JSON rewrites don't fix it, the concept or the frames are the real problem — go back to Step 1.

## Log

Append each iteration to:
```
brands/{brand}/brand-dna/animations/{date}-{winner-slug}/iterations.md
```

Format:
```
## Iteration {N} — {date}
**Problem:** [what was wrong]
**Fix in JSON:** [what changed]
**Result:** [better / same / worse]
```

This log becomes training data for future animations — over time you'll see which problems Veo can actually fix via prompt and which need frame regeneration.
