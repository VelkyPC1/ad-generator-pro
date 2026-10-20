# AdGenerator Pro — pravidlá pre Claude

Jazyk práce: slovenčina so správnou diakritikou. Detailný popis nástroja: `README.md`, `staticky/METODIKA.md`,
`staticky/visual-styles/README.md`, `video/README.md`, `video/RULES.md`.

## Peniaze a kľúče
- **Pred každým plateným generovaním** (Gemini obrázky, Veo / Omni klipy, ElevenLabs voiceover) ukáž súhrn:
  čo sa vygeneruje, koľko kusov, odhad ceny (`staticky/tools/pricing.py`) a ktorý kľúč (`.env`) sa použije.
  Spusti až po výslovnom potvrdení. Kľúč nikdy nevyberaj sám — opýtaj sa.
- Kľúče nevypisuj, nekopíruj do iných súborov a nedávaj do gitu.
- Najprv vždy kontrola zadarmo: `generate_ads.py … --dry-run`, `vyrob_video.py <id> --skusobne`.

## Statické bannery
- Klient = `staticky/brands/<klient>/` (brand-dna s `brand-spec-card.png` + `visual-style-card.png`, fotky produktu,
  `products/<produkt>/product-image-ads/<ad-set>/prompts-<jazyk>.json`, voliteľne vlastný `.env`).
- Každý prompt musí obsahovať frázu „reproduce the product exactly from the reference image" (inak validácia zlyhá).
- Art direction nepíš do promptu — vyber štýl z `staticky/visual-styles/` (`_meta.visual_style` alebo `--visual-style`).
- `--images-dir` vždy ako **absolútna** cesta.
- Logo do bannera negeneruj AI-čkom (komolí ho) — nechaj miesto a prilep PNG dodatočne.
- Pri opravách pregeneruj **iba** bannery označené v dashboarde (✕ FAIL / ✎ drobná oprava) podľa poznámky —
  `staticky/flagged.json`; schválené (`approved.json`) nikdy nepregeneruj.

## Videá
- Celé video: `cd video && python3 vyrob_video.py <id>` zo scriptu `cache/script_<id>.json`.
  Existujúci voiceover sa neopakuje (nový len `--novy-hlas`, platené).
- Pred prácou na videu si prečítaj `video/RULES.md` (každý klip beží raz, bez loopu; koniec = produktový záber;
  všetko v 9:16 safezone).
- Render vždy cez sandbox (`video/security/render-sandbox.sb`).

## Dashboard
- `bash staticky/tools/serve_dashboard.sh` → http://localhost:8077/dashboard.html, obnova tlačidlom „⟳ Úplná obnova".
- Nespúšťaj nič, čo by bežalo stále na pozadí.
