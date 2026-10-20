#!/usr/bin/env python3
"""Sekvenčný builder silent.mp4 — BEZ loopu, BEZ opakovania záberov.

Nahrádza step3_local + vizuálnu časť step4 pre "sekvenčné" videá, kde je veľa
krátkych klipov. Každý klip beží raz, na svoju PLNÚ dĺžku (žiadny loop/freeze);
oreže sa len úplne posledný klip videa, aby dĺžka sedela na voiceover.

Script JSON musí mať:
  "seq_main":  [poradie main klipov — dá sa uviesť viac, builder zoberie koľko treba]
  "seq_outro": [produktové/outro klipy (koniec videa, počas CTA)]

Vstup:  cache/script_<id>.json, cache/words_<id>.json, cache/voice_<id>.mp3
Výstup: cache/work_<id>/silent.mp4  (pripravené pre remotion/render_overlay.sh)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"


def load_config():
    return json.loads((ROOT / os.environ.get("FF_CONFIG", "config.json")).read_text())


def run_ff(args, cwd=None):
    res = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
                         capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg zlyhal:\n{res.stderr.strip()}")


def clip_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def resolve(name, footage):
    for c in [footage / name, footage / (name + ".mp4")]:
        if c.exists():
            return c.resolve()
    raise FileNotFoundError(f"Klip nenájdený: {name} (v {footage})")


# posledný main klip po oreze nesmie byť kratší (inak len "blikne" pred outrom)
MIN_TAIL_CLIP = 1.2

# výrazné kľúčové slová na hrubú kategóriu klipu (poradie = priorita zhody)
_CAT_KEYS = (
    # doplň kľúčové slová z názvov svojich klipov (napr. "balenie", "detail", "ruka") — inak sa
    # kategória berie z prvého slova názvu klipu
)


def _category(name):
    """Hrubá kategória klipu z názvu — na detekciu dvoch príbuzných záberov za sebou."""
    base = Path(name).stem.replace("seq_", "").replace("product_", "")
    for key in _CAT_KEYS:
        if key in base:
            return key
    return base.split("-")[0]


def validate_sequence(seq, outro_names):
    """Poistka pred zostavením (RULES #2, #11). Tvrdé chyby zastavia build,
    mäkké (príbuzné zábery za sebou) len upozornia."""
    names = [s[2] for s in seq]
    # TVRDÉ: žiadny identický záber 2× za sebou
    for i in range(len(names) - 1):
        if Path(names[i]).name == Path(names[i + 1]).name:
            raise RuntimeError(
                f"rovnaký záber 2× za sebou: '{names[i]}' (poz. {i} a {i+1}) — vymeň jeden")
    # TVRDÉ: koniec videa = produktový záber
    if not outro_names:
        raise RuntimeError("chýba seq_outro — koniec videa musí byť produktový záber (product_*)")
    for n in outro_names:
        if not Path(n).name.startswith("product_"):
            raise RuntimeError(f"outro nie je produktový záber: '{n}' — musí začínať 'product_'")
    # MÄKKÉ: dva príbuzné zábery za sebou (varovanie, build pokračuje)
    main_names = names[: len(names) - len(outro_names)]
    for i in range(len(main_names) - 1):
        if _category(main_names[i]) == _category(main_names[i + 1]):
            print(f"  ⚠️  príbuzné zábery za sebou: '{main_names[i]}' + '{main_names[i+1]}' "
                  f"(kat. '{_category(main_names[i])}') — zváž preskupenie", file=sys.stderr)


def pick_sequence(main, outro, footage, cta_start, total, tail=0.35):
    """Vyskladaj (path, use_dur, name) sekvenciu. Produktový outro klip beží ako
    POSLEDNÝ a dobehne CELÝ (koniec videa = produkt, RULES #11); main sekvencia
    vyplní zvyšok bez loopu. Oreže sa posledný MAIN klip; ak by z neho ostalo
    menej než MIN_TAIL_CLIP, zahodí sa celý a orezanie sa prenesie na predošlý."""
    target = total + tail
    outro_paths = [(resolve(n, footage), n) for n in outro]
    outro_full = sum(clip_dur(p) for p, _ in outro_paths)
    main_target = max(0.0, target - outro_full)

    main_seq, acc = [], 0.0
    for name in main:
        if acc >= main_target:
            break
        p = resolve(name, footage)
        d = clip_dur(p)
        main_seq.append([p, d, name])
        acc += d

    # orež posledný main na main_target; ak by z neho ostal krátky útržok, radšej ho
    # zahoď celý (žiadne "bliknutie") — ale len ak aj bez neho pokryjeme voiceover.
    overshoot = acc - main_target
    while len(main_seq) > 1 and overshoot > 0 and (main_seq[-1][1] - overshoot) < MIN_TAIL_CLIP:
        cand_acc = acc - main_seq[-1][1]
        if cand_acc + outro_full < total - 0.1:
            break  # bez tohto klipu by video nepokrylo VO → nechaj ho (orež nižšie)
        main_seq.pop()
        acc = cand_acc
        overshoot = acc - main_target  # môže byť ≤ 0 (video ~ presne VO, outro celý)
    if main_seq and overshoot > 0:
        main_seq[-1][1] = max(MIN_TAIL_CLIP, main_seq[-1][1] - overshoot)

    seq = main_seq + [[p, clip_dur(p), name] for p, name in outro_paths]
    if not seq:
        raise RuntimeError("prázdna sekvencia")

    validate_sequence(seq, [n for _, n in outro_paths])

    covered = sum(s[1] for s in seq)
    if covered < total - 0.1:
        raise RuntimeError(
            f"seq klipy ({covered:.1f}s) nepokryjú voiceover ({total:.1f}s) — "
            f"pridaj viac klipov do seq_main/seq_outro")
    return seq


def run(vid):
    cfg = load_config()
    script = json.loads((CACHE / f"script_{vid}.json").read_text())
    words = json.loads((CACHE / f"words_{vid}.json").read_text())
    footage = (ROOT / cfg.get("footage_dir", "assets/footage")).resolve()

    total = words[-1]["end"]
    cta_n = len((script.get("voice_cta") or "").split())
    cta_start = words[-cta_n]["start"] if 0 < cta_n <= len(words) else total - 2.5

    main = script.get("seq_main") or script.get("clips") or []
    outro = script.get("seq_outro") or script.get("outro_clips") or []
    seq = pick_sequence(main, outro, footage, cta_start, total)

    w, h, fps = cfg["resolution"]["w"], cfg["resolution"]["h"], cfg["fps"]
    grade = cfg.get("color_grade", "")
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,"
          f"crop={w}:{h},setsar=1,fps={fps}" + (("," + grade) if grade else ""))

    work = CACHE / f"work_{vid}"
    work.mkdir(exist_ok=True)
    print(f"  VO total={total:.1f}s  CTA@{cta_start:.1f}s  klipov={len(seq)} (bez loopu)")
    norm = []
    for i, (p, d, name) in enumerate(seq):
        dest = work / f"s{i:02d}.mp4"
        # žiadny -stream_loop; -t oreže len ak je klip dlhší (posledný orezaný)
        run_ff(["-i", str(p), "-t", f"{d:.3f}", "-an", "-vf", vf,
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(dest)])
        norm.append(dest)
        print(f"    [{i}] {d:4.1f}s  {name}")

    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{p.name}'\n" for p in norm))
    silent = work / "silent.mp4"
    run_ff(["-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "silent.mp4"],
           cwd=str(work))
    print(f"  -> {silent}  ({clip_dur(silent):.1f}s)")
    return silent


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("použitie: build_silent_seq.py <id>", file=sys.stderr)
        sys.exit(1)
    try:
        run(sys.argv[1])
    except Exception as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        sys.exit(1)