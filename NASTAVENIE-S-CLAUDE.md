# Nastavenie AdGenerator Pro s Claude Code

1. Rozbaľ `AdGenerator-Pro.zip` kamkoľvek (napr. do domovského priečinka).
2. V termináli: `cd AdGenerator-Pro && claude` (alebo otvor priečinok v aplikácii Claude Code).
3. Vlož celý prompt nižšie. Claude nastaví všetko a pri kľúčoch sa ťa opýta.

---

```text
Nastav mi AdGenerator Pro v tomto priečinku. Prečítaj si README.md a CLAUDE.md a postupuj takto:

1. Skontroluj požiadavky: python3 (3.9+), pip, node (18+), npm, ffmpeg + ffprobe, a na macOS sandbox-exec.
   Čo chýba, vypíš aj s presným príkazom na inštaláciu pre môj systém a opýtaj sa, či to mám nainštalovať.
   Nič neinštaluj bez môjho súhlasu.
2. Spusti `bash setup.sh` a over výstup (Python balíky, npm závislosti pre Remotion, sandbox profil, symlinky,
   prvý dashboard). Ak niečo zlyhá, oprav príčinu a skús znova.
3. Kľúče: opýtaj sa ma na GEMINI_API_KEY a zapíš ho do staticky/.env. Opýtaj sa, či chcem robiť aj videá —
   ak áno, opýtaj sa na ElevenLabs API kľúč a voice ID a zapíš ich do video/config.json.
   Kľúče nikdy nevypisuj do chatu ani do žiadneho iného súboru.
4. Over funkčnosť BEZ platených volaní:
   - python3 staticky/06-image-generation/generate_ads.py --list-styles
   - python3 staticky/tools/build_dashboard.py
   - bash staticky/tools/serve_dashboard.sh a otvor http://localhost:8077/dashboard.html
   - cd video/remotion && npx remotion compositions src/index.ts (na macOS cez sandbox-exec -f ../security/render-sandbox.sb)
5. Opýtaj sa ma na prvého klienta (názov, web, produkt) a vytvor mu staticky/brands/<klient>/ podľa staticky/brands/_priklad/.
   Brand DNA a brand karty priprav podľa staticky/01-brand-research-prompt/ a staticky/02-brand-cards/.
6. Na záver mi stručne napíš, čo je hotové, čo chýba a ako vygenerujem prvý banner a prvé video.

Pravidlá: pred akýmkoľvek plateným generovaním (Gemini, Veo, Omni, ElevenLabs) mi ukáž, čo a koľko sa vygeneruje,
odhad ceny a ktorý kľúč sa použije, a počkaj na moje „áno". Token / kľúč si vždy vyberám ja.
```

---

## Ak nepoužívaš Claude Code
Postupuj podľa `README.md` → časť 2 (Inštalácia) a 3 (Prvé spustenie). Prompty pre bannery píšeš do
`prompts-<jazyk>.json` podľa vzoru v `staticky/brands/_priklad/` a receptov v `staticky/04-brief-template-copy-prompts/`.
