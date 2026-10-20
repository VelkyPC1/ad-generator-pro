# AdGenerator Pro

**Create more. Design less.** — lokálny nástroj na výrobu reklamných kreatív pre Meta a Google:

- **Statické bannery** cez Google Gemini (model Nano Banana 2) — 40 osvedčených formátov reklám, knižnica
  vizuálnych štýlov, brand karty, preklady do ďalších jazykov.
- **Videá (Reels 9:16)** z vlastných klipov — voiceover (ElevenLabs), karaoke titulky, animované karty,
  prechody a hudba, všetko renderované v Remotion jedným príkazom.
- **Dashboard** v prehliadači — prezeranie a hodnotenie kreatív (PASS / drobná oprava / FAIL s poznámkou),
  porovnanie vedľa seba, PDF na schvaľovanie, sťahovanie, štatistiky nákladov, knižnica footage,
  pokrytie jazykov, templaty a štýly.

Všetko beží lokálne na tvojom počítači. Platíš len za to, čo naozaj vygeneruješ (Gemini, ElevenLabs).

---

## 1. Čo potrebuješ

| Čo | Prečo | Ako získať |
|---|---|---|
| **macOS** (odporúčané) alebo Linux | sandbox pre render videí je pre macOS; na Linuxe render beží bez neho | — |
| **Python 3.9+** | generátor, dashboard, Video Factory | `python3 --version` · macOS: `xcode-select --install` alebo python.org |
| **Node.js 18+** a npm | Remotion render videí | nodejs.org alebo `brew install node` |
| **ffmpeg** | náhľady videí, strih, zvuk | `brew install ffmpeg` (Linux: `apt install ffmpeg`) |
| **Google Gemini API kľúč** | generovanie bannerov (a voliteľne AI video klipy Veo / Omni) | aistudio.google.com → Get API key (zapni billing) |
| **ElevenLabs API kľúč** *(len pre videá)* | voiceover s presným časovaním titulkov | elevenlabs.io → Profile → API Keys (bez neho fallback na edge-tts zadarmo) |
| **Claude Code** *(odporúčané)* | píše prompty, copy a scripty videí, spúšťa nástroje | claude.com/claude-code |

Orientačné ceny (USD, bez DPH): banner 1K ≈ 0,07 $ (Batch API ≈ 0,035 $) · voiceover ≈ 0,08 $ / 1 000 znakov
(~0,03 $ na video) · AI video klip Veo ≈ 0,12–0,15 $ / s. Render videí a dashboard sú zadarmo.

---

## 2. Inštalácia

### Rýchlo — s Claude Code
Otvor priečinok `AdGenerator-Pro` v Claude Code a vlož mu prompt zo súboru **`NASTAVENIE-S-CLAUDE.md`**.
Claude skontroluje požiadavky, nainštaluje závislosti, opýta sa ťa na kľúče a overí, že všetko funguje.

### Ručne
```bash
cd AdGenerator-Pro
bash setup.sh                       # závislosti (pip + npm), sandbox, symlinky, prvý dashboard
```
Potom doplň kľúče (nikdy ich nikomu neposielaj, nepatria do gitu):
- `staticky/.env` → `GEMINI_API_KEY=...` (vzor `staticky/.env.example`)
- voliteľne vlastný kľúč pre každého klienta: `staticky/brands/<klient>/.env` (oddelené účtovanie)
- `video/config.json` → `elevenlabs_api_key` a `elevenlabs_voice_id` (vytvorí ho `setup.sh` z `config.example.json`)

---

## 3. Prvé spustenie

```bash
bash staticky/tools/serve_dashboard.sh      # → http://localhost:8077/dashboard.html
```
Dashboard je zo začiatku prázdny — kreatívy pribudnú po prvom generovaní. Nové bannery, videá, štýly či templaty
načítaš tlačidlom **⟳ Úplná obnova** (nič nebeží na pozadí).

### Statické bannery
1. **Nový klient:** skopíruj `staticky/brands/_priklad/` na `staticky/brands/<klient>/`, doplň brand DNA
   (postup v `staticky/01-brand-research-prompt/` a `02-brand-cards/` → `brand-spec-card.png` + `visual-style-card.png`)
   a fotky produktu (`source-product-images/`).
2. **Prompty:** vyber formát v dashboarde (tab 🎨 Templaty a štýly) a priprav `prompts-sk.json` v ad-sete
   (vzor v `_priklad`). S Claude Code stačí povedať: *„priprav 4 bannery pre <klient>, formát Us vs Them, štýl vibrant"*.
3. **Kontrola zadarmo:** `python3 staticky/06-image-generation/generate_ads.py --provider google --brand-dir <abs. cesta k ad-setu> --images-dir <abs. cesta k fotkám> --lang sk --dry-run`
4. **Generovanie (platené):**
   ```bash
   cd staticky
   ./run.sh <klient> --provider google --brand-dir <abs. cesta k ad-setu> \
     --images-dir <abs. cesta k fotkám> --output-dir <ad-set>/outputs --lang sk --templates 1,2
   ```
   Po generovaní sa dashboard prestaví sám a bannery sú aj v `vystupy/statiky/`.

### Videá
1. Vlož svoje klipy do `video/assets/footage/` (`seq_*` = sekvencie, `product_*` = záver s produktom,
   `hook_*` = UGC hook s vlastným zvukom) a hudbu do `video/assets/music/`.
2. Priprav script `video/cache/script_<id>.json` (hook, segmenty, CTA, poradie klipov) — `scripts/step1_script.py`
   ho napíše cez Claude, alebo ho pripravíte spolu v chate. Vzor polí: `video/README.md`.
3. **Celé video jedným príkazom:** `cd video && python3 vyrob_video.py <id>` (najprv môžeš `--skusobne`).

---

## 4. Štruktúra

```
AdGenerator-Pro/
├── setup.sh · README.md · NASTAVENIE-S-CLAUDE.md · CLAUDE.md · requirements.txt
├── staticky/                    generátor bannerov + dashboard
│   ├── 01–05 …                  metodika: brand research, brand karty, produktový research, 40 formátov, hodnotenie copy
│   ├── 06-image-generation/     generate_ads.py — generátor (Gemini realtime / batch, FAL)
│   ├── 07-video-generation/     AI video klipy (Veo, Gemini Omni) do footage
│   ├── visual-styles/           knižnica vizuálnych štýlov (art direction)
│   ├── brands/_priklad/         vzor klienta (tvoje klientske dáta ostávajú len u teba)
│   ├── tools/                   dashboard, cenník (pricing.py), štatistiky, náčrty templatov, ukážky
│   └── run.sh                   generovanie s kľúčom konkrétneho klienta
├── video/                       Video Factory — vyrob_video.py, scripts/, remotion/, assets/, cache/
└── vystupy/                     zrkadlo hotových súborov (statiky/<klient>/…, videa/<klient>/…), vznikne samo
```

## 5. Bezpečnosť a súkromie
- Kľúče sú len v `.env` / `config.json` na tvojom počítači; dashboard ukazuje iba **či** je kľúč nastavený.
- Server dashboardu počúva len na `127.0.0.1` (nie je dostupný zvonku).
- Render videí beží v macOS sandboxe — Node / Chromium nevidí `~/.ssh`, `~/.aws`, Keychain ani nastavenia Claude.
- Každé platené generovanie sa zapisuje do `staticky/cost-log.jsonl` → tab 📊 Štatistiky.
