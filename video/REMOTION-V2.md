# Video Factory v2 — celé video v Remotion („cesta B")

*Zavedené 2026-09-19.*

## Čo sa zmenilo oproti v1

| | v1 (ffmpeg) | v2 (Remotion) |
|---|---|---|
| Strih klipov | `concat` = tvrdý strih, nula prechodov | `TransitionSeries`, 19 prechodov na výber |
| Ken Burns | len na statických obrázkoch, ffmpeg `zoompan` (jittery) | na všetkom vrátane videa, `interpolate` s easingom |
| Titulky | priehľadný ProRes 4444 overlay, 130–160 MB medzikrok | v tej istej kompozícii |
| Audio | ffmpeg mux | `<Audio>` v Remotion |
| Počet renderov | 2 (silent + overlay) + mux | **1** |
| Remotion | 4.0.290 | **4.0.520** |

## Spustenie

```bash
cd AdGenerator-Pro/video/remotion

# 1) props (rieši aj kompenzáciu timeline)
python3 make_ad_props.py moje-video --style stredny

# 2) render v sandboxe
sandbox-exec -f ../security/render-sandbox.sb \
  npx remotion render src/index.ts Ad out/moje-video.mp4 \
  --props=props_ad.json --gl=angle
```

### Animované scény
Časť scén nie je len footage. `make_ad_props.py` z `overlay` v script JSON poskladá panely a rozdá ich rovnomerne po strednej časti videa (nikdy na hook, nikdy na outro):

- **counter** — veľké minimalistické číslo, ktoré sa odpočíta (napr. cena za kus)
- **bullets** — benefity, nabiehajú staggerovane s odrazom
- **headline** — claim na farebnej ploche

Panel zaberá hornú časť, footage dolnú (`split-bottom`, 42/58). Titulky sa preto posúvajú na `y_position 0.64`.

⚠️ **Farby panelu sa berú z témy** (`cardBg`/`cardColor`), nie natvrdo — svetlá téma `cream` má tmavý text a biely by na krémovom pozadí zmizol.

Horné karty z v1 sa pri zapnutých scénach **vypínajú** (okrem social proof) — ich obsah prevzali panely a inak by sa prekrývali.

**Emoji** (`FloatingEmojis`) stúpajú cez vybrané scény, na outre vystrelia z centra. Deterministické cez `random(seed)` — inak by Remotion nevedel renderovať snímky paralelne.

**CTA** (`CtaLanding`) spadne zhora, dosadne s odrazom, pri dopade rozostrí a stmaví pozadie, potom jemne dýcha.

Vypnúť: `--no-scenes`.

### Rytmus
Záber dlhší než `--cut-long` (default 2,6 s) sa **rozsekne na dva** — ten istý súbor, druhá časť pokračuje cez `trimBefore`, takže footage beží plynulo, ale divák vidí strih a zmenu pohybu kamery. Vypnúť `--no-cuts`.

### Štýly prechodov
- `--style jemny` — fade, dissolve (8f)
- `--style stredny` — dreamyZoom, fade, linearBlur (10f) ← default
- `--style vyrazny` — dreamyZoom, zoomBlur, crossZoom, filmBurn (12f)
- `--no-transitions` — tvrdé strihy všade, ako v1
- `--no-kenburns` — statické klipy
- `--no-audio` — bez VO a hudby, ak si chceš audio domuxovať sám

**Prvý strih (hook → prvý segment) je vždy tvrdý cut**, bez ohľadu na štýl. Hook potrebuje plnú pozornosť, prechod ju kradne.

## ⚠️ Zásek: 24 fps footage na 30 fps timeline

Niektoré AI klipy (napr. `product_*`) sú **24 fps**, timeline beží na **30 fps**. Bez zásahu Remotion duplikuje 6 snímok za sekundu → **20,3 % snímok je duplicitných** a video viditeľne seká.

`make_ad_props.py` to rieši `playbackRate = fps / src_fps` (24 → 1,25×). Každá zdrojová snímka potom padne presne na jednu snímku timeline. **Nameraný výsledok: 20,3 % → 0 %.** Bonus: o 25 % svižnejší pohyb, čo produktovým záberom sedí.

Ak pribudne footage s iným fps, rieši sa automaticky — `probe_fps()` si ho zistí.

⚠️ **Merať duplicity sa dá len na PNG sekvencii** (`--sequence --image-format=png`). Po h264 kompresii vychádza všade 0 %, lebo enkodér aj identické snímky zakóduje mierne odlišne.

## ⚠️ Kompenzácia timeline

`TransitionSeries` má dĺžku **Σ(klipy) − Σ(prechody)**. Prechody sa prekrývajú, takže video **skracujú**. Keby sa dĺžky klipov nechali tak, video by skončilo skôr než voiceover.

`make_ad_props.py` to rieši: klipy dopredu nafúkne o Σ(prechody), rozdelené proporčne, a potom overí, že `Σd − Σt` sa presne rovná cieľu. Výpis na konci to hlási:

```
klipy=8  VO=15.23s  cieľ=466f  timeline=466f  ✓ sedí
```

**Keby tam niekedy bolo `❌ NESEDÍ`, video nepoužívaj** — titulky by sa rozišli s hlasom.

## Architektúra

| Súbor | Účel |
|---|---|
| `src/Ad.tsx` | kompozícia: footage + prechody + Ken Burns + titulky + audio |
| `src/Captions.tsx` | **nezmenený** z v1 — Ad ho znovupoužíva, neduplikuje |
| `make_ad_props.py` | generátor props, delenie času, kompenzácia timeline |
| `make_props.py` | z v1, pribudol len `write=False` (spätne kompatibilné) |
| `public/footage` | symlink → `assets/footage` |
| `public/music` | symlink → `assets/music` |
| `public/voice` | symlink → `cache` |
| `security/render-sandbox.sb` | sandbox profil pre render |

`Ad.tsx` je postavený tak, že titulkovú vrstvu nepíše znova — importuje `<Captions>`. Keď sa bude ladiť vzhľad titulkov, mení sa stále len `Captions.tsx`, tak ako doteraz.

## Bezpečnosť

Render púšťaj **vždy cez sandbox** (`sandbox-exec -f ../security/render-sandbox.sb`). Bez neho má Node a Chromium prístup ku `~/.claude`, `~/.api-keys` a Keychainu.

`.npmrc` blokuje install skripty. Nové balíčky mimo `@remotion/*` neinštalovať bez overenia.

## Čo ešte nie je hotové

- ✅ Jeden príkaz: `python3 vyrob_video.py <id>` (2026-10-16) — voiceover → props → render → dashboard.
- ✅ Hudba: `vyrob_video.py` posiela `--music auto` (náhodná), konkrétna cez `--hudba music/nazov.mp3`.
- Prechody sa vyberajú cyklicky podľa indexu, nie podľa obsahu scény.

## Úpravy 2026-10-05

- `--cta-bottom 0.22` — odsadenie CTA tlačidla zdola (podiel výšky). Default ostáva 0,13, čo je **mimo safezone**
  (RULES #15, tlačidlo sedelo na 80–87 % výšky). Pre nové videá používať **0,22**. Pri téme `cream` stačí **0,20**,
  lebo jej titulkový box má na konci 3 riadky a pri 0,22 sa dotýka CTA.
- `overlay.price_label` — popis nad počítadlom (default „cena za kus"). Pre ostatné jazyky ho treba vyplniť,
  inak bude po slovensky.
- `make_props.apply_display_replacements` už **zachová koncovú interpunkciu** („desať eur." → „10 €.").
  Predtým sa pri nahradení čísla stratila bodka a titulky spájali koniec jednej vety so začiatkom ďalšej
  Týka sa to všetkých videí, kde je číslo na konci vety.
- Voiceover v inom jazyku: `FF_CONFIG=config_<jazyk>.json python3 scripts/step2_voice.py cache/script_<id>.json`.
- `"clip_trim": {"<klip>": sekundy}` v script JSON — oreže začiatok zdrojového klipu (napr. prázdny začiatok hooku).
