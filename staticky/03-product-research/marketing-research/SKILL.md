---
name: marketing-research
description: "Deep marketing research a tvorba foundational dokumentov pre brand/produkt/službu. Použij keď používateľ chce pripraviť research základ pred tvorbou reklám, advertoriálov, landing pages, emailov alebo akéhokoľvek marketingového obsahu. Vstup je produktová stránka, brand alebo služba. Výstup sú 4 foundational dokumenty."
---

# Marketing Research

## Ako to funguje

Skill vytvorí kompletný research základ pre značku alebo produkt — 4 foundational dokumenty z ktorých sa dá písať akýkoľvek marketingový obsah (reklamy, advertoriály, landing pages, emaily, videá).

**Flow:**
1. Zadáš URL produktovej/brand stránky
2. Skill analyzuje stránku a opýta sa: research pre značku alebo produkt?
3. Vygeneruje špecifický prompt pre ChatGPT Deep Research — skopíruješ ho do ChatGPT
4. Medzitým Claude robí vlastný doplnkový research cez WebSearch
5. Vložíš výstup z ChatGPT späť — skill skombinuje oba zdroje do `deep-research.md`
6. Na základe researchu automaticky vytvorí `avatar-sheet.md`, `offer-brief.md`, `necessary-beliefs.md`
7. Prezentuje summary všetkých dokumentov na validáciu

**Filozofický základ:** Marketing nie je o "magnificent words" ale o "magnificent arguments" (Agora approach). Najprv postav rock-solid argument, potom ho obleč do slov. Necessary beliefs sú North Star — každý kus obsahu vedie prospecta k týmto beliefs.

**Ukladanie výstupov:**
- Značka → `brands/{brand}/brand-dna/`
- Produkt → `brands/{brand}/products/{product}/marketing-research/`

---

## Vstup

Produktová stránka, brand stránka, alebo popis služby (URL, PDF, screenshot, alebo text).

## Výstup

Na začiatku sa opýtaj: robíš research pre **značku** alebo pre **produkt**?

- **Značka** → ukladaj do `brands/{brand}/brand-dna/`
- **Produkt** → ukladaj do `brands/{brand}/products/{product}/marketing-research/`

4 samostatné dokumenty:

1. `deep-research.md` — research na trhu (min 6 strán)
2. `avatar-sheet.md` — profil ideálneho zákazníka
3. `offer-brief.md` — ponuka a jej positioning
4. `necessary-beliefs.md` — beliefs pred nákupom

---

## Proces

### Step 0: Načítaj referencie

```
cat <skill_path>/references/argument-first-transcript.md
cat <skill_path>/references/deep-research-methodology.md
cat <skill_path>/references/avatar-sheet-template.md
cat <skill_path>/references/offer-brief-template.md
```

### Step 1: Research

#### 1.1 Analýza produktovej stránky

Analyzuj vstup (URL/PDF/text produktovej stránky). Identifikuj:
- Čo sa predáva a komu
- Aký problém to rieši
- Unique mechanism / proprietary solution
- Aktuálny messaging a positioning
- Silné a slabé stránky aktuálnej prezentácie

Prezentuj analýzu používateľovi.

#### 1.2 Deep Research Prompt (pre ChatGPT Deep Research)

Na základe analýzy z kroku 1.1 vygeneruj špecifický prompt pre ChatGPT Deep Research.

**Metodológia (povinná — podľa Mark Builds Brands Research Part 1 & 2):**

Prompt musí nariadiť ChatGPT aby postupoval presne takto — v tomto poradí zdrojov:

**ZDROJ 1 — FÓRA (primárny):**
- Vyhľadaj "[topic] forum" + "[problem] reddit" + "[product category] forum"
- Otvor vlákna s NAJVIAC odpoveďami (sort by replies = najangažovanejšie témy)
- Choď hlboko do JEDNÉHO dobrého vlákna — nechoď plytko po mnohých
- Jedno dobré vlákno = väčšina celého researchu
- Copy-paste PRESNÉ citáty zákazníkov verbatim v ich pôvodnom jazyku

**ZDROJ 2 — AMAZON REVIEWS (primárny):**
- Hľadaj produkty z danej kategórie s čo najväčším počtom recenzií
- Čítaj 5-hviezdičkové (čo milujú, aké výsledky dostali) A 1-hviezdičkové (horror stories, čo nenávidia)
- Copy-paste presné vety zákazníkov — nie parafrázu

**ZDROJ 3 — GOOGLE (len pre Curiosity + Corruption sekcie):**
- "[problém] horror story"
- "popular [riešenie] history" / "popular [riešenie] 1900s"
- "places where [problém] doesn't exist"
- Tento zdroj je TRETÍ — nie na zákazníkov, len na historický kontext a corruption angles

**Čo prompt NESMIE nariadiť:**
- Akademické štúdie a vedecké prehľady ako primárny zdroj
- Demografické správy a market research reports
- Rozkladanie researchu naprieč 10 rôznymi fórami plytko
- Parafrázu — vždy verbatim citáty

**Výstup ktorý prompt požaduje:**
- Jeden kompilovaný dokument, minimum 6 strán
- Každá sekcia plná verbatim citátov zákazníkov v ich vlastnom jazyku
- Konkrétne, nie generické — nie "chcú schudnúť" ale "chcem aby sa na mňa manžel pozrel s hrdosťou"

**4 sekcie ktoré prompt musí pokryť:**

**Sekcia 1: Demografické insights**
- Kto je zákazník (vek, pohlavie, príjem, lokalita)
- Aké postoje majú (náboženské, politické, sociálne, ekonomické)
- Nádeje a sny — konkrétne, nie generické
- Víťazstvá a zlyhania s ich problémom
- Vonkajšie sily ktoré im bránia žiť najlepší život (naratívy ktoré si hovoria)
- Predsudky a stereotypy (signalizujú "som jeden z vás")
- Core beliefs o živote, láske a rodine (1-3 vety kto je táto osoba)

**Sekcia 2: Existujúce riešenia**
- Čo trh už používa (suplementy, diéty, kurzy, appky...)
- Aká bola ich skúsenosť (používajú veľa/málo, prestali, prečo)
- Čo sa im páči na existujúcich riešeniach
- Čo sa im nepáči
- Horror stories o existujúcich riešeniach (pravdivé príbehy kde niečo šlo zle)
- Verí trh že existujúce riešenia fungujú? Ak áno → viac diferenciácie. Ak nie → prečo?

**Sekcia 3: Curiosity (Zvedavosť)**
- Stratené objavy — riešenia ktoré boli zabudnuté
- Potlačené riešenia — niekto mal odpoveď ale bola skrytá/pochovaná
- Staré unikátne pokusy (pre-1960) — inherentne odlišné od dnešných riešení
- Čo sa s nimi stalo? Boli úspešné ale zabudnuté? Zlyhali a prečo?

**Sekcia 4: Corruption (Korupcia / Pád z raja)**
- Existoval pain point trhu vždy, alebo sa zhoršil?
- "Fall from Eden" — bývali jednoduchšie časy, teraz je to horšie kvôli vonkajšej sile
- Izolované skupiny ľudí ktoré NEMAJÚ tento problém — prečo?

Prezentuj vygenerovaný prompt používateľovi. Používateľ ho skopíruje do ChatGPT Deep Research.

#### 1.3 Claude Research (doplnkový zdroj)

Paralelne s čakaním na ChatGPT výstup vykonaj vlastný research cez WebSearch. Rovnaká metodológia ako pre ChatGPT — primárne fóra a Amazon, nie akademické zdroje:

- **Fóra** — nájdi 1-2 vlákna s najviac odpoveďami, choď do hĺbky, copy-paste verbatim citáty
- **Amazon/Heureka reviews** — 5-star + 1-star, presné vety zákazníkov
- **Konkurenčný landscape** — hlavní hráči, ich positioning a unique mechanisms (stačí povrchovo)
- **Corruption/curiosity angles** — historické kontexty, potlačené riešenia (Google ako zdroj)

Sekundárne (nie customer voice, ale užitočné pre UMS a claims):
- Vedecké štúdie — pre health produkty: pochopenie mechanizmu, backing pre claims, suppressed research angles
- Regulačné obmedzenia — len ak je produkt v regulovanej kategórii (napr. zdravotné claims v EÚ)

Čo NIE je prioritou:
- Demografické správy a market research documents
- Akademické prehľady ako náhrada za customer voice

#### 1.4 Kompilácia

Keď používateľ dodá výstup z ChatGPT Deep Research:

1. Skombinuj oba zdroje (ChatGPT + Claude research) do jedného dokumentu
2. Odstráň duplicity, zachovaj najlepšie citáty a insights z oboch zdrojov
3. Štruktúruj podľa 4 sekcií + doplnkové zistenia

**Princíp:** Copy-paste presné slová zákazníkov. Nehádam čo chcú počuť — oni ti to povedia. Jedno dobré vlákno na fóre = väčšina researchu.

Výstup: `deep-research.md` — minimum 6 strán, dva zdroje skombinované.

### Step 2: Foundational Documents

#### 2.1 Avatar Sheet

Na základe researchu vyplň avatar sheet template. Pokry:

- Demografia a psychografia
- Denný život a rutina
- Hlavné bolesti a frustrácie (vlastnými slovami zákazníka)
- Túžby a sny
- Strachy a obavy
- Čo už skúsili a prečo to nefungovalo
- Kde sa zdržiavajú online
- Kto ich ovplyvňuje
- Trigger momenty kedy hľadajú riešenie

Výstup: `avatar-sheet.md`

#### 2.2 Offer Brief

Na základe researchu a avatar sheetu vyplň offer brief template. Pokry:

- Potential product name ideas
- Level of consciousness (Low/High)
- Level of awareness (Unaware → Most Aware)
- Stage of sophistication (Level 1-5)
- Big Idea
- Metaphor
- UMP — Unique Mechanism of the Problem (prečo majú tento problém)
- UMS — Unique Mechanism of the Solution (nový, odlišný a lepší spôsob)
- Guru — autorita/expert za produktom
- Discovery Story — ako bolo riešenie objavené
- Product — čo presne je produkt
- Potential headline/subheadline ideas
- All objections
- Belief chains — čo musí prospect veriť aby kúpil
- Funnel architecture
- Examples/Swipes

Výstup: `offer-brief.md`

#### 2.3 Necessary Beliefs

Toto je kľúčový krok. Marketing at its core is simply about changing the existing beliefs of a customer into beliefs that align with them and empower them to purchase.

Na základe VŠETKÝCH predošlých dokumentov (deep-research.md, avatar-sheet.md, offer-brief.md) analyzuj:

1. Aké beliefs prospect aktuálne má (existujúce presvedčenia)
2. Aké beliefs MUSÍ mať PRED tým ako uvidí ponuku (max 6)
3. Štruktúruj ako "I believe that..." statements

Tieto beliefs sú North Star pre VŠETOK budúci content — každý kus marketingu (reklama, advertoriál, email, landing page) musí viesť prospecta krok za krokom k týmto beliefs. Bez nich ponuka nedáva zmysel.

Výstup: `necessary-beliefs.md`

### Step 3: Validácia

Po vytvorení všetkých 4 dokumentov znovu prečítaj každý jeden a urob brief summary. Cieľ: potvrdiť že máš phenomenal understanding of the prospect, the market, the offer, and the necessary beliefs.

Prezentuj používateľovi:
- **Deep Research** — kľúčové zistenia o trhu, zákazníkovi, konkurencii, curiosity/corruption angles
- **Avatar Sheet** — kto je zákazník, čo ho trápi, čo chce, ako hovorí (vrátane kľúčových citátov)
- **Offer Brief** — čo predávame, UMP/UMS, big idea, stage of sophistication
- **Necessary Beliefs** — aké beliefs musí mať pred nákupom a prečo práve tieto

Opýtaj sa používateľa či chce niečo upraviť pred finalizáciou.

---

## Pravidlá

- Jazyk: slovenčina (ak nie je špecifikované inak)
- Vždy hľadaj UNIQUE MECHANISM — proprietary solution, nie komoditu
- Argument first, words second — najprv logika a emócia, potom jazyk
- Review mining — používaj jazyk zákazníkov, nie marketingový žargón
- Beliefs sú North Star — všetko vedie k nim
- Dokumenty ukladaj do `brands/{brand}/brand-dna/` (značka) alebo `brands/{brand}/products/{product}/marketing-research/` (produkt)
