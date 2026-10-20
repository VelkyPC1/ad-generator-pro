# Product Research — Proces

Kompletný postup na vytvorenie marketing research dokumentov pre produkt. Spúšťa sa keď `product-research-check.md` zistí že research chýba.

## Výstup (4 dokumenty)

Ukladaj do `brands/{brand}/products/{product}/marketing-research/`:

1. `deep-research.md` — research trhu (min 6 strán)
2. `avatar-sheet.md` — profil ideálneho zákazníka
3. `offer-brief.md` — ponuka a positioning
4. `necessary-beliefs.md` — beliefs pred nákupom

Šablóny: `avatar-sheet-template.md`, `offer-brief-template.md` (v tomto priečinku)

---

## Step 1: Analýza produktu

Požiadaj usera o URL produktovej stránky alebo popis produktu. Analyzuj:
- Čo sa predáva a komu
- Aký problém to rieši
- Unique mechanism / proprietary solution
- Aktuálny messaging a positioning

---

## Step 2: Deep Research Prompt (pre ChatGPT Deep Research)

Vygeneruj prompt pre ChatGPT Deep Research prispôsobený konkrétnemu produktu. Prompt musí pokryť 4 sekcie:

**Sekcia 1: Demografické insights**
- Kto je zákazník (vek, pohlavie, príjem, lokalita)
- Nádeje a sny — konkrétne, nie generické
- Víťazstvá a zlyhania s ich problémom
- Vonkajšie sily ktoré im bránia žiť najlepší život
- Predsudky a stereotypy
- Core beliefs o živote, láske a rodine

**Sekcia 2: Existujúce riešenia**
- Čo trh už používa
- Aká bola ich skúsenosť (používajú veľa/málo, prestali, prečo)
- Čo sa im páči / nepáči
- Horror stories o existujúcich riešeniach

**Sekcia 3: Curiosity**
- Stratené/potlačené riešenia
- Staré unikátne pokusy (pre-1960)

**Sekcia 4: Corruption**
- Existoval pain point vždy alebo sa zhoršil?
- "Fall from Eden" — vonkajšia sila ktorá situáciu zhoršila
- Skupiny ľudí ktoré tento problém nemajú — prečo?

Kde hľadať: fóra, Amazon/Heureka reviews (5★ aj 1★), Google ("[problém] horror story").

Prezentuj prompt userovi — user ho skopíruje do ChatGPT Deep Research.

---

## Step 3: Claude Research (doplnkový)

Paralelne s čakaním na ChatGPT výstup urob vlastný research:
- Review mining (Heureka, Amazon, fóra) — presné citáty zákazníkov
- Konkurenčný landscape — hlavní hráči, ich positioning
- Vedecké štúdie relevantné pre produkt
- Regulačné obmedzenia v reklame pre daný segment

---

## ⛔ GATE pred Step 4+

NEPOKRAČOVAŤ na Step 4 (kompilácia) ani Step 5–7 kým nie sú splnené VŠETKY podmienky:

1. ✅ ChatGPT Deep Research output dodaný userom
2. ✅ Všetci Claude research subagenti dokončili prácu (review mining, konkurenčný landscape, veda+regulácie)
3. ✅ Chýbajúce tvrdé dáta (ceny, dávkovanie, claims) doplnené alebo explicitne označené ako gap

Ak niečo chýba → confirm-back userovi čo presne ešte chýba a čakaj. Nepokračovať „aspoň s tým čo máme" — half-finished research = half-finished hooks.

---

## Step 4: Kompilácia do deep-research.md

Keď user dodá ChatGPT výstup A všetky subagenti sú hotoví:
- Skombinuj oba zdroje (ChatGPT + Claude)
- Odstráň duplicity, zachovaj najlepšie citáty
- Štruktúruj podľa 4 sekcií
- Minimum 6 strán, copy-paste presné slová zákazníkov

Ulož: `brands/{brand}/products/{product}/marketing-research/deep-research.md`

---

## Step 5: Avatar Sheet

Vyplň `avatar-sheet-template.md` na základe deep-research.md.

Ulož: `brands/{brand}/products/{product}/marketing-research/avatar-sheet.md`

---

## Step 6: Offer Brief

Vyplň `offer-brief-template.md` na základe deep-research.md + avatar-sheet.md.

Ulož: `brands/{brand}/products/{product}/marketing-research/offer-brief.md`

---

## Step 7: Necessary Beliefs

Na základe všetkých predošlých dokumentov identifikuj max 6 beliefs ktoré musí prospect mať PRED tým ako uvidí ponuku. Štruktúruj ako "I believe that..." statements.

Tieto beliefs sú North Star pre všetok copy — každá reklama musí viesť prospecta k nim.

Ulož: `brands/{brand}/products/{product}/marketing-research/necessary-beliefs.md`

---

## Step 8: Návrat do workflow

Po uložení všetkých 4 dokumentov sa vráť do `product-research-check.md` — spusti kontrolu znova a pokračuj do kroku 04 (Template + Copy).
