# 03 — Product Research Check

Kontrola či existuje marketing research pre zvolený produkt. Spúšťa sa po nastavení brand cards (krok 02), pred výberom template a písaním copy (krok 04).

## Čo skontrolovať

Skontroluj existenciu týchto súborov:

```
brands/{brand}/products/{product}/marketing-research/
├── deep-research.md       — POVINNÝ
├── avatar-sheet.md        — POVINNÝ
├── necessary-beliefs.md   — POVINNÝ
└── offer-brief.md         — odporúčaný
```

## Výsledok kontroly

### Všetky povinné súbory existujú → pokračuj do kroku 04

Načítaj:
- `deep-research.md`
- `avatar-sheet.md`
- `necessary-beliefs.md`
- `offer-brief.md` (ak existuje)
- `reviews-verbatim.md` (ak existuje)

### Niektorý povinný súbor chýba → spusti research

Informuj usera:

> Marketing research pre produkt **{product}** nie je kompletný. Chýbajúce súbory: [zoznam].
> Spúšťam research proces.

Pokračuj podľa `product-research-process.md` v tomto priečinku — kompletný postup od analýzy produktu po všetky 4 dokumenty.

**Nepokračuj do kroku 04 kým research nie je kompletný** — bez neho nie je možné napísať copy z reálnych dát.
