# 05 — Scoring Agents

7 agentov na hodnotenie copy briefu pred generáciou. Spúšťajú sa sekvenčne v poradí 01–07.

## Pravidlo

**Všetci agenti musia skórovať ≥90** (okrem Agenta 7 ktorý je pass/fail). Ak ktorýkoľvek skóruje pod 90 → iteruj copy brief, nepokračuj do generácie.

## Agenti

| # | Súbor | Hodnotí | Typ |
|---|-------|---------|-----|
| 01 | `01-agent-persona.md` | Persona Fit — rezonuje copy s cieľovým publikom? | 1–100 |
| 02 | `02-agent-angle.md` | Angle Execution — je angle dobre vykonaný? | 1–100 |
| 03 | `03-agent-emotion.md` | Emotional Resonance — emocionálny dopad | 1–100 |
| 04 | `04-agent-brand.md` | Brand Consistency — zodpovedá brand voice? | 1–100 |
| 05 | `05-agent-copy-excellence.md` | Copy Excellence — kvalita copy | 1–100 |
| 06 | `06-agent-format.md` | Format Compliance — dodržuje pravidlá formátu? | 1–100 |
| 07 | `07-agent-grammar.md` | Copy Editor — gramatika, diakritika, banned chars | PASS/FAIL |

## Postup

1. Prečítaj copy brief (headline, subhead, CTA, image direction)
2. Spusti agentov 01–06 — každý dá skóre + zdôvodnenie + návrhy na opravu
3. Spusti agenta 07 — veto právo, blokuje generáciu pri akomkoľvek mechanickom błęde
4. Ak všetci ≥90 a Agent 07 PASS → pokračuj do kroku 06 (Prompt Substitution)
5. Ak ktorýkoľvek zlyhá → oprav brief a spusti znova len zlyhaných agentov
