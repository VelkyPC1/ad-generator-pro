# Video Factory — AdGenerator Pro

Reklamné Reels 9:16 z **vlastných klipov** (+ voliteľne AI klipy): voiceover (ElevenLabs, záložne edge-tts zadarmo),
karaoke titulky, animované karty (cena, benefity, social proof, CTA), prechody, Ken Burns a hudba —
celé v **Remotion** v jednom renderi. Hotové videá sú v dashboarde (tab 🎬 Video) a vo `vystupy/videa/`.

## Jeden príkaz

```bash
cd video
python3 vyrob_video.py <id> --skusobne       # len vypíše kroky, nič nespustí
python3 vyrob_video.py <id>                  # voiceover (ak chýba) → props → render → dashboard
python3 vyrob_video.py <id> --styl vyrazny   # iný štýl strihu a prechodov (make_ad_props.py STYLES)
python3 vyrob_video.py <id> --hook           # UGC hook klip (s vlastným zvukom) + produktová sekcia → *_FINAL.mp4
python3 vyrob_video.py <id> --novy-hlas      # vynúti nový voiceover (platené)
python3 vyrob_video.py <id> --legacy         # starší postup: sekvencia klipov + titulkový overlay
```

- **Vstup:** `cache/script_<id>.json` · **výstup:** `remotion/out/<id>_REMOTION.mp4` (lokalizácie v `out/CZ|HU|DE|PL|RO/`).
- **Config:** `config.json`; pre klienta `config_<klient>.json` (použije sa pre ID `<klient>-…`), pre jazyk
  `config_hu.json` / `config_de.json` / … (ID končí `-hu` alebo začína `de-`, `pl-`, `ro-`).
- Voiceover sa **neopakuje**, ak `cache/voice_<id>.mp3` existuje. Render beží v sandboxe (macOS).

## Script videa — `cache/script_<id>.json`

```jsonc
{
  "id": "moja-znacka-leto-a",
  "title": "…",                                  // názov pre dashboard
  "hook": "Text titulku hooku",  "voice_hook": "Čítaná verzia hooku",
  "segments": [ { "text": "Titulok segmentu", "voice": "Čítaná verzia" } ],
  "cta": "Objednajte teraz za 9,99 €.",
  "voice_cta": "Objednajte teraz za deväť eur deväťdesiatdeväť.",
  "seq_main":  [ "seq_klip-1", "seq_klip-2", "…" ],   // poradie klipov z assets/footage (uveď viac, zoberie koľko treba)
  "seq_outro": [ "product_zaver" ],                     // koniec = produktový záber, beží celý
  "display_replacements": [ { "voice": "deväť eur deväťdesiatdeväť", "display": "9,99 €" } ],
  "overlay": {                                    // karty na obrazovke (číta make_ad_props.py)
    "price_label": "cena za kus", "price_to": 0.99,
    "benefits": ["…", "…", "…"],
    "social": "konkrétny, pravdivý social proof",
    "cta": "KÚPIŤ TERAZ"
  }
}
```
Pre hook video navyše `"hook_clip": "hook_<názov>"` a prázdne `hook` / `voice_hook`.

Script ti napíše `python3 scripts/step1_script.py` (cez `claude -p` alebo `ANTHROPIC_API_KEY`) podľa `brand_name`,
`brief` a voliteľného `copy_playbook` v configu — alebo ho pripravíš s Claude v chate. Preklad:
`python3 scripts/make_locale.py <jazyk> [id]` (preklady v `locales/<jazyk>.json`, klipy ostávajú rovnaké).

## Nastavenie (`config.json`)

| Kľúč | Význam |
|---|---|
| `brand_name`, `language`, `brief`, `copy_playbook` | značka, jazyk VO, zadanie, cesta k tvojmu copy playbooku (.md) |
| `voice_provider` | `elevenlabs` (presné titulky) alebo `edge` (zadarmo) |
| `elevenlabs_api_key`, `elevenlabs_voice_id`, `elevenlabs_model` | ElevenLabs prístup, hlas, model (`eleven_multilingual_v2`) |
| `voice` | hlas pre edge-tts (napr. `sk-SK-ViktoriaNeural`) |
| `target_seconds`, `segments_per_video` | dĺžka VO a počet segmentov |
| `captions.highlight_color` | farba zvýrazneného slova v titulkoch |
| `footage_dir`, `music_dir`, `music_volume` | klipy, hudba, hlasitosť podmazu |

## Štruktúra

| Súbor / priečinok | Účel |
|---|---|
| `vyrob_video.py` | jeden príkaz na celé video |
| `scripts/step1_script.py` · `step2_voice.py` · `make_locale.py` | script, voiceover s časovaním slov, lokalizácia |
| `scripts/build_hookvideo.sh` · `build_silent_seq.py` | hook video, sekvencia klipov (legacy) |
| `remotion/src/Ad.tsx` | kompozícia: footage + prechody + Ken Burns + titulky + karty + audio |
| `remotion/make_ad_props.py` | props pre render (strih, prechody, kompenzácia 24→30 fps, štýly) |
| `assets/footage/` · `assets/music/` | tvoje klipy a hudba (nie sú súčasťou balíka) |
| `security/render-sandbox.sb` | sandbox pre render (vytvorí `setup.sh`) |
| `RULES.md` · `REMOTION-V2.md` | pravidlá skladania videí a technická dokumentácia |

AI klipy (Veo / Gemini Omni) do footage: `staticky/07-video-generation/generate_videos.py` a `generate_omni.py`
(platené, zapisujú sa do denníka nákladov).
