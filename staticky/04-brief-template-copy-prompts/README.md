# 04 — Format Templates + Copy

Tri zdroje šablón pre generovanie static ads + workflow na výrobu vlastných z konkurencie. Každý zdroj má vlastný `copy-prompt.md` s inštrukciami na zostavenie JSON outputu s placeholdermi.

---

## 01-templates-by-motion/

**40 Motion Foundations recipe cards** — jeden súbor = jeden formát.

Každá šablóna obsahuje:
- Metadata (aspect ratio, safe zones, reference uploads)
- 2–3 štýly s vlastnou copy template + image generation promptom
- Presné word counts pre headline / subhead / CTA
- Variation vectors (BG, lighting, product position, color)
- Scoring kritériá pre 7 agentov

Vhodné pre: **plný Motion workflow** (copy → scoring → generácia). Vyššia kvalita, viac iterácií.

Postup písania copy: `01-templates-by-motion/copy-prompt.md`

---

## 02-40-templates/

**40 generických ad formátov** — všetky v jednom súbore `template-prompts.md`.

Každý formát obsahuje:
- Hotový prompt s [BRACKETED PLACEHOLDERS] na vyplnenie
- Aspect ratio + needs_product_images flag

Vhodné pre: **rýchle prototypy**.

Postup písania copy: `02-40-templates/copy-prompt.md`

---

## 03-ad-swipe.md

**Výroba šablóny z konkurenčnej reklamy** — 3-fázový proces:

1. **Deconstruct** — JSON extrakcia zo screenshotu konkurenčného adu
2. **Rebuild** — mapovanie na štruktúru format template
3. **Copy generation** — prepísanie copy pre vlastný brand + Agent 7 sign-off

Výstup: nový template pripravený na scoring a generáciu.

---

## Kedy čo použiť

| Situácia | Zdroj |
|----------|-------|
| Chcem kvalitný ad s plným workflow | `01-templates-by-motion/` |
| Chcem rýchly prototyp | `02-40-templates/` |
| Videl som dobrý ad konkurencie | `03-ad-swipe.md` |
| Mám brand-špecifický formát | `brands/{brand}/{brand}-templates/` |
