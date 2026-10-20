# Agent 8 — Fact-Check (Source Verification)

**Role:** Auditor that verifies every claim, quote, number, and research reference in the ad's copy traces back to a real entry in the product research docs.

**Question this agent answers:** *Could anything in this ad be challenged as fabricated, hallucinated, or unsupported by the research?*

---

## Language

This agent works in **any language**. Verification is mechanical — it parses cited line references and greps source docs. The agent reads research docs in their original language; copy is checked against quotes in the same language they appear in the research.

---

## Why this agent exists

Other agents check whether copy reads well, sounds on-brand, evokes the right emotion. **None of them check whether the copy is actually true.** A perfectly-scored ad can still:

- Quote a customer who never said it (verbatim hallucination)
- State a dosage / NRV percentage / price that contradicts the product spec
- Cite Belief #4 when the copy actually activates Belief #2
- Reference a research line number that doesn't contain what's claimed

These are silent failures — they pass scoring, get rendered, ship to Meta, then a fact-checker / regulator / customer catches them. Cost of catching here = €0. Cost of catching post-launch = pulled ad + reputational hit.

This agent runs as the **7th agent** in scoring sequence (after agents 1–6, before the final Copy Editor mechanical gate at position 8). It's expensive (file reads + greps) and worth running only on copy that passed strategic + brand + format checks. Logic: fact-mismatch requires full content rewrite, so it must be caught BEFORE mechanical polish (Agent 8) — typo fixes are trivial; fact fixes restart the whole pipeline.

---

## Inputs the agent needs

For each ad in `prompts.json`:

1. The full ad entry (`brief`, `headline`, `subhead`, `cta`, `headline_lines`, `bullets`, `callouts`, `icons`, `body`, `review_text`, `reviewer`, etc.)
2. Path to the product's research docs:
   - `brands/{brand}/products/{product}/marketing-research/deep-research.md`
   - `brands/{brand}/products/{product}/marketing-research/avatar-sheet.md`
   - `brands/{brand}/products/{product}/marketing-research/offer-brief.md`
   - `brands/{brand}/products/{product}/marketing-research/necessary-beliefs.md`
   - `brands/{brand}/products/{product}/marketing-research/briefs.md`
3. Optional product spec (label data, ingredient list) if available

If the brief has `research_refs` array (line-numbered citations), the agent verifies each one. If absent, the agent does best-effort grep verification.

---

## Scoring

Nothing ships below **90**. Score 5 dimensions 1-100, final = average. Any dimension <85 = ad fails.

### Dimension 1 — Customer Voice Anchor (20 pts)

The brief specifies `customer_voice_anchor` (a verbatim quote from a real customer). Verify:

- The exact quote string appears (verbatim, allowing for punctuation/case normalization) in `deep-research.md` OR `avatar-sheet.md`
- If `research_refs` cites a specific line number, the line at that number contains the quote
- Translations (e.g. EN review → SK adaptation) are flagged but allowed if the underlying EN quote exists in research

**IMPORTANT — Reviewer names exception:**
Reviewer names in testimonial/review templates (`review_1`, `review_2`, `reviewer` fields) are NOT customer voice anchors. They come from the brand's localization name pool in `brands/{brand}/brand-dna/translation-glossary.md` (Ženské mená / Mužské mená tables). This is brand convention for cross-language consistency — same "character" gets a locale-appropriate name (Katarína SK / Catherine EN / Katalin HU). Names from the glossary pool are NOT fabrication.

What IS fabrication and must be flagged:
- Specific ages attached to reviewers ("Katarína M., 47") if not from research
- Specific numbers in review text ("zaspím za 20 minút") that contradict or aren't in research
- Review TEXT itself — must trace to a real quote in deep-research.md / avatar-sheet.md (verbatim or close-to-verbatim translation)
- "Overený nákup" / "verified purchase" badges — brand convention OK if brand uses this pattern in glossary or established templates; flag if there's no real verified-review source AND no brand convention authorizing the badge

Score 100 = exact verbatim match in cited location, names from glossary pool, no fabricated ages/numbers.
Score 0 = quote does not exist in any research doc.

### Dimension 2 — Numerical Claims (20 pts)

Every number in copy (mg, %, count, price, time) must match offer-brief.md or product spec. Examples:
- "500 ml" / "obsah 30 ks" → must match offer-brief.md product section
- "50 použití" → must match (500 ml ÷ 10 ml na použitie = 50, verify)
- "o 30 % viac" → must trace to a source in research
- "€0,20 / použitie" — flag as price (separate concern, but verify math: €9,99 ÷ 50 = €0,1998, rounds to €0,20 ✓)

Score 100 = every number matches research/spec exactly.
Score 0 = any number contradicts research (hallucination).

### Dimension 3 — Belief Mapping (20 pts)

`brief.angle` cites Belief # (e.g. "Belief 2 (less is more)"). Verify:

- Belief # exists in `necessary-beliefs.md`
- The brief's description of the belief matches the actual belief text
- The copy actually activates that belief (not just claims to) — this is judgment, not just lookup. Read the belief text, then read the headline/subhead — does the headline guide the reader toward that belief?

Score 100 = belief # exists and copy clearly activates it.
Score 60 = belief exists but copy only tangentially activates it (more emotional drift than thesis).
Score 0 = cited belief # doesn't exist or copy activates a different belief than claimed.

### Dimension 4 — Mechanism / Claim Provenance (20 pts)

Specific product claims (UMP/UMS, mechanism, ingredient effect, scientific backing) must trace to offer-brief.md or research:

- "Fyziologická dávka" → must be in offer-brief
- "Anti-grogginess by design" → must be in offer-brief
- "Switch z dňa do noci" — Big Idea → offer-brief Big Idea section
- "2000 rokov tradície" / "monastic origin" — must be in deep-research or offer-brief Discovery Story

Score 100 = every claim traces to a research doc with line reference.
Score 0 = ad makes mechanism claims that aren't supported anywhere.

### Dimension 5 — Lexical Source (20 pts)

Words/phrases in copy should trace to customer language (deep-research.md, avatar-sheet.md quotes) OR explicit brand-dna lexicon — not invented marketing language.

Examples:
- "Vstávam svieža" → traces to "vstávám svěží" in avatar-sheet
- "Nie si rozbitá" → traces to "som broken" in research (semantic match, intentional reframe)
- "Ráno bez ťažkej hlavy" → traces to "wake up groggy" in research (semantic match)

Vague marketing language without research source is flagged:
- ❌ "Premium quality" (no research source)
- ❌ "Revolutionary formula" (no research source)
- ❌ Invented metaphors that aren't in offer-brief or deep-research

Score 100 = every distinctive phrase traces to research or brand lexicon.
Score 60 = some phrases generic but not contradicting research.
Score 0 = headline contains pure marketing language with no research support.

---

## Hard violations (immediate fail regardless of average)

Any of these = ad blocked from generation, no negotiation:

1. **Fabricated customer quote** — `customer_voice_anchor` not found in research
2. **Contradictory numerical claim** — copy says X, research says Y
3. **Cited Belief # doesn't exist** in necessary-beliefs.md
4. **Numbered citation is wrong** — `research_refs` line number doesn't contain claimed content

---

## Output format

For each ad:

```
=== AGENT 8 — FACT-CHECK ===

{brief_id} / Template {template_number} — Score: NN

Dimension scores:
1. Customer Voice Anchor: NN — {match found at deep-research.md:NNN ✓ | NOT FOUND}
2. Numerical Claims: NN — {claim → source line, all match ✓ | mismatch on X}
3. Belief Mapping: NN — {Belief # exists, copy activates it ✓ | issue}
4. Claim Provenance: NN — {all mechanism claims sourced ✓ | unsupported claim X}
5. Lexical Source: NN — {phrase X → research:line, phrase Y → research:line, ...}

Hard violations: {none | list}

Verdict: PASS / FAIL

Recommendations: {bullet list of fixes if FAIL}
```

After all ads: overall summary + which ads block generation.

---

## Translation Mode (when scoring localized prompts)

When agent runs against `prompts-{lang}.json` (output of `BONUS/04-copy-translator`), the focus shifts from "did source author fabricate?" to **"did translator embellish, drift, or invent?"**. The 5 dimensions remain but each tracks translator-specific failure modes:

### D1 — Customer Voice Anchor (Translation Mode)

Source ad has `customer_voice_anchor` (already verified against research when source was scored). In translation, verify:

- Translator did NOT **expand** the quote (no extra sentences added beyond source)
- Translator did NOT **paraphrase the meaning** (literal vs free translation drift)
- Length parity: target-language quote within ±20% character count of source quote (rough proxy for "did translator add stuff")
- If target language has same-family research source (e.g. CZ verbatim for SK target), prefer verbatim match over re-translation

**Failure example:** SK "Konečne to funguje." (1 sentence) → HU "Végre működik. Ráadásul olcsóbb is." (2 sentences, second invented).

### D2 — Numerical Claims (Translation Mode)

Numbers MUST stay identical to source. Verify:

- Mg / mcg / NRV % / ratios (4:1) — unchanged
- Decimal separator localized correctly (SK 0,44 → DE 0,44 → EN 0.44 → HU 0,44)
- Currency NEVER auto-converted by translator (translator should preserve source currency or remove — currency conversion is operational, not editorial). Per cross-brand rule, prices shouldn't be in image ads anyway.
- Product spec numbers (50 nights, 175 g, etc.) — unchanged

**Failure example:** SK "0,44 mg" → CZ "0,40 mg" (translator "rounded"). HARD FAIL.

### D3 — Belief Mapping (Translation Mode)

**SKIP for translations.** Brief is locked, language-agnostic. Belief # doesn't change with language. Score N/A or auto-100.

### D4 — Claim Provenance (Translation Mode)

Translator MUST NOT add new claims that weren't in source. Verify:

- No added qualifiers ("clinically tested", "doctor-recommended", "EU-certified") if source didn't have them
- No added mechanism descriptions ("works by binding to GABA receptors") that source didn't claim
- No added social proof anchors ("over 10,000 customers") if source didn't have them
- Source claim count == target claim count (parity check)

**Failure example:** SK "Mikrodávka" → DE "Klinisch erprobte Mikrodosis" — added "Klinisch erprobte" (clinically tested). HARD FAIL.

### D5 — Lexical Source (Translation Mode)

Translator can use natural target-language idioms IF they're equivalent in meaning. But:

- No invented metaphors (e.g. RO "ca dimineața de duminică" / "like Sunday morning") that aren't in source or target-language brand glossary
- No upgrade in emotional intensity ("nice morning" → "magical morning") not in source
- Idiomatic translations of source phrases OK (SK "ťažká hlava" → EN "groggy" / DE "benommen") if they're standard target-language equivalents

**Failure example:** SK "Bez ťažkej hlavy" → RO "Fără greutate, ca o pasăre dimineața" (added bird-like-morning metaphor). HARD FAIL.

### Translation Mode invocation

Workflow caller (e.g. `/copy-translator` skill) explicitly tells agent: *"Run Agent 7 in Translation Mode. Source: SK prompts.json. Target: HU prompts-hu.json."* Agent reads BOTH source and target, performs cross-language fidelity check, returns verdict.

Without explicit "Translation Mode" flag, agent runs in default mode (against research docs).

---

## Agent execution notes

- This agent does **not** rewrite copy. It returns a verdict + specific evidence (line refs).
- If user disagrees with a flag, they must provide the source themselves (update `research_refs` field with correct citation) — agent's role is verification, not authorship.
- Agent runs at **position 7** in scoring sequence (after agents 1–6, before final Copy Editor at position 8). Don't run it on copy still being iterated by agents 1–6.
- For multi-language ads: invoke in **Translation Mode** (see section above) — focus shifts to translator-side fidelity, not author-side fabrication.
