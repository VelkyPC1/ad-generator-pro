#!/usr/bin/env python3
"""make_ad_props.py — props pre kompozíciu <Ad> (PVF v2, "cesta B").

Celé video sa skladá v Remotion: footage + prechody + Ken Burns + titulky + audio.
ffmpeg už netreba.

Titulkovú časť NEDUPLIKUJE — volá make_props.build(), ktorý je odladený.
Tento skript rieši navyše footage vrstvu a hlavne KOMPENZÁCIU TIMELINE.

⚠️ Prečo kompenzácia:
   TransitionSeries má dĺžku = Σ(klipy) − Σ(prechody). Prechody sa prekrývajú,
   takže video SKRACUJÚ. Keby sme dĺžky klipov nechali tak, ako ich počíta
   step4, video by skončilo skôr než voiceover. Preto klipy dopredu nafukujeme
   o Σ(prechody), rozdelené proporčne.

Použitie:
   python3 make_ad_props.py moje-video
   python3 make_ad_props.py moje-video --style vyrazny --no-transitions
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import make_props

ROOT = Path(__file__).resolve().parent
PVF = ROOT.parent
CACHE = PVF / "cache"
PUBLIC = ROOT / "public"

# Ken Burns smery — striedajú sa, aby dva susedné klipy nešli rovnako.
PANEL_TIME_FACTOR = 1.9   # o koľko dlhšie trvá scéna s panelom

KEN_CYCLE = ["in", "left", "out", "right", "in", "up"]

# Štýly prechodov. Kľúč = ako agresívne.
#   Pozícia 0 (hook -> prvý segment) je VŽDY "none":
#   prvé sekundy potrebujú tvrdý cut, prechod tam kradne pozornosť z hooku.
# Štýly prechodov. Kľúč = ako agresívne.
#   Pozícia 0 (hook -> prvý segment) je VŽDY "none":
#   prvé sekundy potrebujú tvrdý cut, prechod tam kradne pozornosť.
#
# ⚠️ POUŽÍVAJÚ SA LEN DOM/CSS PRECHODY.
# Overené A/B testom 2026-09-19: HTML-in-canvas prechody (dreamyZoom, linearBlur,
# zoomBlur, filmBurn, crossZoom, dissolve, crosswarp, ripple, bookFlip, blurSlide,
# zoomInOut) spôsobujú, že hotové video pri prehrávaní laguje. To isté video
# s vypnutými prechodmi je plynulé. Bežia cez experimentálne Chrome API
# (canvas-draw-element) a do výstupu sa premietnu nekonzistentne.
# Sú dostupné cez --fancy, ale na ostré kreatívy ich NEPOUŽÍVAŤ.
STYLES = {
    # nepoužívať (2026-09-19): clockWipe (hodinky), iris (kruh),
    # slide a wipe (posúvanie do boku = "vyzerá ako PowerPoint").
    # punch/flash sú vlastné CSS prechody zo src/Punch.tsx.
    "jemny":   {"mid": ["fade"],                    "outro": "fade",  "frames": 9},
    "stredny": {"mid": ["punch", "fade"],           "outro": "fade",  "frames": 10},
    "vyrazny": {"mid": ["punch", "flash", "punch"], "outro": "flash", "frames": 12},
}

# Efektné prechody — LEN cez --fancy. Pozri varovanie vyššie.
FANCY_STYLES = {
    "jemny":   {"mid": ["dissolve"],                            "outro": "fade",       "frames": 8},
    "stredny": {"mid": ["dreamyZoom", "fade", "linearBlur"],    "outro": "dreamyZoom", "frames": 10},
    "vyrazny": {"mid": ["dreamyZoom", "zoomBlur", "crossZoom"], "outro": "filmBurn",   "frames": 12},
}


VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def resolve_clips_from_script(script, cfg, skip_hook=False):
    """Zoznam klipov zo script JSON (hook_clip + seq_main + seq_outro).
    Rovnaká logika hľadania ako step3_local.resolve_clip.

    ⚠️ skip_hook: keď je zadané vlastné intro, hook_clip sa vynechá.
    hook_* klipy majú vlastný hovorený VO a do tela videa nepatria
    (pravidlo #14) — inak by po intre nasledoval druhý hook."""
    fdir = PVF / cfg.get("footage_dir", "assets/footage")
    names = []
    if script.get("hook_clip") and not skip_hook:
        names.append(script["hook_clip"])
    names += list(script.get("seq_main", []))
    names += list(script.get("seq_outro", []))

    out = []
    for name in names:
        found = None
        for ext in ("",) + VIDEO_EXTS + IMG_EXTS:
            cand = fdir / (name + ext)
            if cand.exists():
                found = cand.resolve()
                break
        if not found:
            raise SystemExit(f"❌ Klip nenájdený: '{name}' v {fdir}")
        out.append(str(found))
    return out


def probe_fps(path: str) -> float:
    """fps zdrojového klipu. Niektoré AI klipy majú 24, timeline beží na 30 —
    bez zarovnania Remotion duplikuje každú 5. snímku a video sa VIDITEĽNE seká."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    try:
        num, den = r.stdout.strip().split("/")
        return float(num) / float(den)
    except Exception:
        return 0.0


def probe_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def audio_duration(path: Path) -> float:
    return probe_duration(str(path))


def segment_durations(script, words, total):
    """Rozdelí `total` medzi vizuálne segmenty. Rovnaká logika ako step4_compose,
    aby sa video strihalo na tých istých miestach ako doteraz."""
    visual_texts = [script.get("hook") or script.get("hook_clip_line", "")] + \
                   [s["text"] for s in script["segments"]]
    counts = [max(1, len(t.split())) for t in visual_texts]

    if words:
        n = len(words)
        cum, idx = 0, []
        for c in counts:
            cum += c
            idx.append(min(n - 1, round(cum / sum(counts) * n) - 1))
        durs, prev_t = [], 0.0
        for i, wi in enumerate(idx):
            end_t = total if i == len(idx) - 1 else words[max(0, wi)]["end"]
            durs.append(max(0.8, round(end_t - prev_t, 3)))
            prev_t = end_t
        return durs

    tot = sum(counts)
    return [max(0.8, round(total * c / tot, 3)) for c in counts]


def public_rel(abs_path: str) -> str:
    """Prevedie absolútnu cestu klipu na cestu vnútri public/ (cez symlinky
    footage/ music/ voice/, ktoré ukazujú do assets/ a cache/)."""
    p = Path(abs_path).resolve()
    for link, prefix in (("footage", "footage"), ("music", "music"), ("voice", "voice")):
        target = (PUBLIC / link).resolve()
        try:
            return f"{prefix}/{p.relative_to(target)}"
        except ValueError:
            continue
    raise SystemExit(
        f"❌ Klip je mimo public/: {p}\n"
        f"   Symlinky: {PUBLIC}/footage -> assets/footage_*, music -> assets/music_*, voice -> cache")


def build_transitions(n_clips, style, enabled, fancy=False):
    """Prechod medzi každou dvojicou klipov. Vracia n_clips-1 položiek."""
    st = (FANCY_STYLES if fancy else STYLES)[style]
    out = []
    for i in range(max(0, n_clips - 1)):
        if not enabled or i == 0:
            # i == 0 je strih hook -> prvý segment: tvrdý cut, vždy.
            out.append({"type": "none", "durationInFrames": 0})
        elif i == n_clips - 2:
            out.append({"type": st["outro"], "durationInFrames": st["frames"]})
        else:
            out.append({"type": st["mid"][(i - 1) % len(st["mid"])],
                        "durationInFrames": st["frames"]})
    return out


def compensate(base_frames, trans, total_frames):
    """⚠️ JADRO. Nafúkne dĺžky klipov tak, aby po odčítaní prechodov
    vyšla presne `total_frames`.

       Σd − Σt = T   →   Σd = T + Σt
    """
    sum_t = sum(t["durationInFrames"] for t in trans)
    target_sum = total_frames + sum_t
    cur = sum(base_frames)
    if cur <= 0:
        raise SystemExit("❌ Nulová dĺžka klipov.")

    # proporčné nafúknutie
    scaled = [max(1, round(f * target_sum / cur)) for f in base_frames]

    # zaokrúhľovací zvyšok hodíme na najdlhší klip
    diff = target_sum - sum(scaled)
    if diff:
        scaled[scaled.index(max(scaled))] += diff

    # constraint: prechod nesmie byť dlhší než ktorákoľvek susedná sekvencia
    for i, t in enumerate(trans):
        d = t["durationInFrames"]
        if d and d > min(scaled[i], scaled[i + 1]):
            t["durationInFrames"] = max(0, min(scaled[i], scaled[i + 1]) - 1)

    # prechody sa mohli skrátiť -> prepočítaj, aby súčet zase sedel
    sum_t2 = sum(t["durationInFrames"] for t in trans)
    if sum_t2 != sum_t:
        delta = (total_frames + sum_t2) - sum(scaled)
        scaled[scaled.index(max(scaled))] += delta

    return scaled, trans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--style", choices=list(STYLES), default="stredny")
    ap.add_argument("--no-transitions", action="store_true",
                    help="tvrdé strihy všade (ako v1)")
    ap.add_argument("--no-kenburns", action="store_true")
    ap.add_argument("--no-cuts", action="store_true",
                    help="nerozsekávať dlhé zábery na kratšie")
    ap.add_argument("--cut-long", type=float, default=2.6,
                    help="záber dlhší než N sekúnd rozsekni na dva (default 2.6)")
    ap.add_argument("--intro", default=None,
                    help="klip na začiatok (názov vo footage_dir). Má vlastný zvuk, "
                         "voiceover a titulky začnú až za ním.")
    ap.add_argument("--min-clip", type=float, default=1.5,
                    help="minimálna dĺžka záberu v sekundách; pri menšej sa počet klipov zredukuje")
    ap.add_argument("--fancy", action="store_true",
                    help="⚠️ HTML-in-canvas prechody (dreamyZoom, filmBurn...). "
                         "Overené, že spôsobujú lagovanie pri prehrávaní — nepoužívať na ostré kreatívy.")
    ap.add_argument("--headline-panel", action="store_true",
                    help="pridá panel s claimom zo set_text (default vypnuté)")
    ap.add_argument("--no-blur", action="store_true",
                    help="vypne backdrop-filter blur (podozrivý z blikania)")
    ap.add_argument("--no-scenes", action="store_true",
                    help="bez animovaných panelov a emoji")
    ap.add_argument("--no-audio", action="store_true",
                    help="bez VO a hudby — video nechať domuxovať ffmpegom")
    ap.add_argument("--music", default=None, help="cesta k hudbe v public/ (napr. music/x.mp3), alebo 'auto'")
    ap.add_argument("--music-volume", type=float, default=0.07,
                    help="hlasitosť podkresu (default 0.07)")
    ap.add_argument("--cta-bottom", type=float, default=None,
                    help="odsadenie CTA zdola ako podiel výšky (default 0.13; safezone 0.22)")
    ap.add_argument("--out", default="props_ad.json")
    args = ap.parse_args()
    vid = args.id

    script = json.loads((CACHE / f"script_{vid}.json").read_text())
    words_raw = json.loads((CACHE / f"words_{vid}.json").read_text())
    cfg = json.loads((PVF / "config.json").read_text())
    clips_json = CACHE / f"clips_{vid}.json"
    if clips_json.exists():
        clips = json.loads(clips_json.read_text())
        if args.intro and script.get("hook_clip"):
            hk = script["hook_clip"]
            clips = [c for c in clips if Path(c).stem != hk]
    else:
        # fallback: odvodíme priamo zo scriptu, nech nezávisíme na poradí krokov
        clips = resolve_clips_from_script(script, cfg, skip_hook=bool(args.intro))
        print(f"   (clips_{vid}.json chýbal — klipy odvodené zo script JSON)")
    voice_path = CACHE / f"voice_{vid}.mp3"

    fps = cfg.get("fps", 30)
    W, H = cfg["resolution"]["w"], cfg["resolution"]["h"]
    total = audio_duration(voice_path)
    if total <= 0:
        raise SystemExit(f"❌ Nepodarilo sa zistiť dĺžku {voice_path}")

    # titulky + karty + CTA z odladeného make_props
    captions = make_props.build(vid, 0.0, 0.33, "", [], "", "", write=False)

    # kde začína CTA (outro klipy ho pokrývajú)
    voice_cta = script.get("voice_cta") or script.get("cta") or ""
    cta_n = len(voice_cta.split())
    cta_start = words_raw[-cta_n]["start"] if 0 < cta_n <= len(words_raw) else total

    words_main = words_raw[:-cta_n] if 0 < cta_n <= len(words_raw) else words_raw
    durs = segment_durations(script, words_main, cta_start)

    # Rozdelenie času medzi klipy.
    # POZOR: segmentov (hook + segments) je typicky menej než klipov
    # (seq_main ich má viac), takže sa NEDÁ mapovať 1:1 — inak posledné
    # klipy dostanú zvyškových pár snímok.
    n_seq_main = len(script.get("seq_main", []))
    n_outro = len(script.get("seq_outro", []))
    n_main = (1 + n_seq_main if (script.get("hook_clip") and not args.intro)
              else max(1, n_seq_main))

    # Keď intro nahradilo hook, prvý segment nepatrí žiadnemu hook klipu —
    # jeho čas sa rozdelí medzi bežné zábery.
    hook_dur = 0.0 if args.intro else (durs[0] if durs else 1.5)

    # Outro (CTA fáza). Keď video nemá CTA vo voiceoveri, cta_start == total
    # a outru by neostal čas — preto minimum z configu, rovnako ako step4_compose.
    outro_time = max(0.5, (total + 0.3) - cta_start)
    if n_outro:
        outro_time = max(cfg.get("outro_seconds", 2.5), outro_time)

    content_time = max(0.5, (total + 0.3) - hook_dur - (outro_time if n_outro else 0.0))

    durs = [] if args.intro else [hook_dur]
    if n_seq_main:
        durs += [round(content_time / n_seq_main, 3)] * n_seq_main
    if n_outro:
        durs += [round(outro_time / n_outro, 3)] * n_outro

    # zarovnaj na skutočný počet klipov
    if len(durs) > len(clips):
        durs = durs[:len(clips)]
    while len(durs) < len(clips):
        durs.append(round(outro_time / max(1, len(clips) - len(durs)), 3))

    # ── Intro klip ──
    # Má vlastný hovorený part, takže si berie svoj zvuk a celé ostatné
    # časovanie (voiceover, titulky, karty, CTA) sa posunie za neho.
    intro_frames = 0
    intro_obj = None
    if args.intro:
        fdir = PVF / cfg.get("footage_dir", "assets/footage")
        ipath = None
        for ext in ("",) + VIDEO_EXTS:
            cand = fdir / (args.intro + ext)
            if cand.exists():
                ipath = cand.resolve(); break
        if not ipath:
            raise SystemExit(f"❌ Intro klip nenájdený: '{args.intro}' v {fdir}")
        idur = probe_duration(str(ipath))
        ifps = probe_fps(str(ipath))
        # intro sa NEZRÝCHĽUJE — má hovorené slovo, zmena tempa by skreslila hlas
        intro_frames = max(1, round(idur * fps))
        intro_obj = {"src": public_rel(str(ipath)), "kind": "video",
                     "durationInFrames": intro_frames, "ken": "none",
                     "keepAudio": True}
        if ifps and abs(ifps - fps) > 0.5:
            print(f"   intro: {idur:.2f}s @ {ifps:.0f} fps (necháva sa v pôvodnom tempe kvôli hlasu)")

    total_frames = max(1, round((total + 0.3) * fps))
    base_frames = [max(1, round(d * fps)) for d in durs]

    # ── Pomalšie tempo ──
    # Keď by zábery vychádzali kratšie než --min-clip, radšej ich použijeme menej
    # a dáme im viac času, než aby to rýchlo preskakovalo.
    min_f = args.min_clip * fps
    while len(base_frames) > 3 and (total_frames / len(base_frames)) < min_f:
        # zahodíme najkratší zo strednej časti (hook a outro ostávajú)
        mid_idx = range(1, len(base_frames) - 1)
        drop = min(mid_idx, key=lambda i: base_frames[i])
        base_frames.pop(drop)
        clips.pop(drop)
    # čas prerozdelíme rovnomerne na zostávajúce
    scale_up = total_frames / max(1, sum(base_frames))
    base_frames = [max(1, round(f * scale_up)) for f in base_frames]

    # ── 1) Rozhodni rozsekanie dlhých záberov (PRED prechodmi, lebo mení počet klipov) ──
    # Dlhý statický záber uspí rytmus. Rozsekneme ho na dva: je to ten istý súbor,
    # druhá časť pokračuje cez trimBefore, takže footage beží plynulo ďalej,
    # ale divák vidí strih a zmenu pohybu kamery.
    units = []   # (index_zdroja, cesta, base_frames, je_druhá_polovica)
    for i, (path, f) in enumerate(zip(clips, base_frames)):
        is_img = Path(path).suffix.lower() in IMG_EXTS
        if not is_img and not args.no_cuts and f > args.cut_long * fps:
            units.append((i, path, f // 2, False))
            units.append((i, path, f - f // 2, True))   # nadviaže cez kenPhase
        else:
            units.append((i, path, f, False))

    # ── 2) Panely a ich rozmiestnenie (musí byť PRED kompenzáciou,
    #       lebo scény s panelom dostávajú viac času) ──
    ov = script.get("overlay", {})
    theme = captions.get("theme", {})
    accent = theme.get("accent", "#4F52F7")
    card_bg = theme.get("cardBg", "#13161D")
    # ⚠️ farbu textu panelu ber z témy — svetlé témy (cream) majú tmavý text,
    # natvrdo biela by na krémovom pozadí zmizla
    card_fg = theme.get("cardColor", "#ffffff")
    on_accent = theme.get("onAccent", "#ffffff")

    panels = []
    if ov.get("price_to") is not None and ov.get("price_from") is not None:
        panels.append({
            "kind": "counter", "bg": card_bg, "color": card_fg, "accent": accent,
            "counter": {"from": ov.get("price_from", 0.0), "to": ov.get("price_to", 0.0),
                        "unit": ov.get("unit", "€/ks"),
                        "decimals": ov.get("decimals", 2),
                        "label": ov.get("price_label", "cena za kus")},
        })
    if ov.get("benefits"):
        panels.append({"kind": "bullets", "bg": card_bg, "color": card_fg,
                       "accent": accent, "bullets": ov["benefits"][:3]})
    # headline panel (set_text, napr. dlhý slogan) nepoužívať — 2026-09-19.
    # Zapnúť sa dá cez --headline-panel.
    if ov.get("set_text") and args.headline_panel:
        panels.append({"kind": "headline", "bg": accent, "color": on_accent,
                       "headline": ov["set_text"]})

    EMOJI_SETS = [
        {"chars": ["💚", "✨"], "count": 10, "mode": "up", "size": 58},
        {"chars": ["❤️", "💚", "✨"], "count": 12, "mode": "up", "size": 62},
    ]

    n_units = len(units)
    # panely rozhádž rovnomerne po strednej časti videa (nikdy hook, nikdy outro)
    mid = list(range(1 if args.intro else 2, max(2, n_units - 1)))
    if panels and mid:
        # rozprestri ich cez celý rozsah, nech nie sú tri za sebou
        if len(panels) == 1:
            panel_slots = [mid[len(mid) // 2]]
        else:
            panel_slots = sorted({
                mid[round(i * (len(mid) - 1) / (len(panels) - 1))]
                for i in range(len(panels))
            })
    else:
        panel_slots = []
    emoji_slots = [i for i in mid if i not in panel_slots][:len(EMOJI_SETS)]

    # Scéna s panelom dostane viac času — text v nej treba stihnúť prečítať.
    weighted = [max(1, round(u[2] * (PANEL_TIME_FACTOR if i in panel_slots else 1.0)))
                for i, u in enumerate(units)]

    # ── 3) Prechody a kompenzácia ──
    trans = build_transitions(len(units), args.style, not args.no_transitions, args.fancy)
    frames, trans = compensate(weighted, trans, total_frames)

    clip_objs = []
    pi = 0
    for idx, ((src_i, abs_path, _, is_second), f) in enumerate(zip(units, frames)):
        rel = public_rel(abs_path)
        is_img = Path(abs_path).suffix.lower() in IMG_EXTS
        obj = {
            "src": rel,
            "kind": "image" if is_img else "video",
            "durationInFrames": f,
            "ken": "none" if args.no_kenburns else KEN_CYCLE[idx % len(KEN_CYCLE)],
        }

        rate = None
        # voliteľný orez začiatku zdroja (script "clip_trim": {"<klip>": sekundy}),
        # napr. keď klip začína prázdnym záberom
        trim_s = float(script.get("clip_trim", {}).get(Path(abs_path).stem, 0.0))
        if not is_img:
            src_fps = probe_fps(abs_path)
            src_dur = probe_duration(abs_path)
            # ⚠️ ZÁSEK: zdroj 24 fps na 30 fps timeline = duplikovaná každá 5. snímka.
            # Prehratím na fps/src_fps (24 -> 1.25x) padne každá zdrojová snímka
            # presne na jednu snímku timeline. Bonus: o 25 % svižnejší pohyb.
            if src_fps and abs(src_fps - fps) > 0.5:
                rate = round(fps / src_fps, 4)
            need = f / fps
            eff = max(0.0, src_dur - trim_s) / (rate or 1.0)
            if 0 < eff < need:
                rate = round(max(0.5, (rate or 1.0) * eff / need), 4)
            if rate:
                obj["playbackRate"] = rate

        if trim_s and not is_img and not is_second:
            obj["trimBefore"] = int(round(trim_s * fps))
        if is_second:
            # Druhá polovica pokračuje tam, kde prvá skončila — a to v oboch
            # osiach: vo footage (trimBefore) aj v pohybe kamery (kenPhase).
            # Bez kenPhase sa zoom na strihu resetuje z 1.10 na 1.0 a vidno skok.
            prev = clip_objs[-1]["durationInFrames"] if clip_objs else 0
            obj["trimBefore"] = int(round(trim_s * fps) + prev * (rate or 1.0))
            obj["ken"] = clip_objs[-1]["ken"] if clip_objs else obj["ken"]
            obj["kenPhaseFrom"] = 0.5
            obj["kenPhaseTo"] = 1.0
        elif idx + 1 < len(units) and units[idx + 1][3]:
            obj["kenPhaseFrom"] = 0.0
            obj["kenPhaseTo"] = 0.5

        if not args.no_scenes:
            if idx in panel_slots and pi < len(panels):
                obj["layout"] = "split-bottom"    # panel hore, footage dole
                obj["splitRatio"] = 0.58
                obj["panel"] = panels[pi]
                pi += 1
            if idx in emoji_slots:
                obj["emojis"] = EMOJI_SETS[emoji_slots.index(idx) % len(EMOJI_SETS)]

        clip_objs.append(obj)

    # posledná scéna: emoji výstrel pod CTA
    if not args.no_scenes and clip_objs:
        clip_objs[-1]["emojis"] = {"chars": ["💚", "✨", "❤️"], "count": 14,
                                   "mode": "burst", "size": 64, "seed": "outro"}

    # ── 4) Titulky: čo sa presunulo do panelov, nech sa neopakuje hore ──
    if not args.no_scenes:
        # Horné karty sa vypínajú úplne — ich obsah prevzali panely.
        # Keby ostali, prekrývali by panel v hornej polovici. Výnimka: social proof,
        # ten beží cez outro, kde panel nie je.
        captions["topCards"] = [c for c in captions.get("topCards", [])
                                if c["kind"] == "social"]
        # CTA prevzala vrstva CtaLanding (pristátie + rozostrenie)
        cta_cfg = captions.get("cta")
        captions["cta"] = None
        # titulky nižšie, nech nekolidujú s panelom v hornej polovici
        captions["y_position"] = 0.64

    if intro_obj:
        clip_objs.insert(0, intro_obj)
        trans.insert(0, {"type": "none", "durationInFrames": 0})

    props = {
        "clips": clip_objs,
        "transitions": trans,
        "captions": captions,
        "fps": fps,
        "width": W,
        "height": H,
        "totalDurationInFrames": total_frames + intro_frames,
        "introFrames": intro_frames,
    }

    if not args.no_scenes:
        cta_text = ov.get("cta") or (cta_cfg or {}).get("text") or "NAKUPOVAŤ"
        cta_at = (cta_cfg or {}).get("start", cta_start)
        props["cta"] = {
            "text": cta_text,
            "bg": accent,
            "color": "#ffffff",
            "landFrame": max(0, round(cta_at * fps) - 6) + intro_frames,
            "from": "right",     # z boku, zhora prekrývalo titulky
        }
        if args.cta_bottom is not None:
            props["cta"]["bottomPct"] = args.cta_bottom

    if args.no_blur:
        props["noBackdropBlur"] = True

    if not args.no_audio:
        props["voice"] = public_rel(str(voice_path))
        if args.music == "auto":
            mdir = PVF / cfg.get("music_dir", "assets/music")
            tracks = sorted(f for f in mdir.iterdir()
                            if f.suffix.lower() in (".mp3", ".m4a", ".wav"))
            if tracks:
                args.music = f"music/{tracks[len(vid) % len(tracks)].name}"
                print(f"   hudba: {Path(args.music).name}")
        if args.music:
            props["music"] = args.music
            props["musicVolume"] = args.music_volume
            # hudba nabehne až za introm/hookom, nech neprekrýva hovorené slovo
            props["musicFrom"] = intro_frames

    out = ROOT / args.out
    out.write_text(json.dumps(props, ensure_ascii=False, indent=2))

    # kontrola: sedí timeline?
    check = sum(c["durationInFrames"] for c in clip_objs) - sum(t["durationInFrames"] for t in trans)
    target = total_frames + intro_frames
    used = [t["type"] for t in trans if t["type"] != "none"]
    print(f"OK -> {out}")
    print(f"   klipy={len(clip_objs)}  VO={total:.2f}s  intro={intro_frames}f  "
          f"timeline={check}f (cieľ+intro={target}f)  "
          f"{'✓ sedí' if check == target else '❌ NESEDÍ'}")
    print(f"   prechody: {', '.join(used) if used else 'žiadne (tvrdé strihy)'}")
    print(f"   kompenzácia: +{sum(t['durationInFrames'] for t in trans)}f rozdelených do klipov")
    n_panels = sum(1 for c in clip_objs if c.get("panel"))
    n_emoji = sum(1 for c in clip_objs if c.get("emojis"))
    n_rate = sum(1 for c in clip_objs if c.get("playbackRate"))
    print(f"   scény: {len(clip_objs)} (z {len(clips)} zdrojov, rozsekané +{len(clip_objs)-len(clips)})"
          f" · panely={n_panels} · emoji={n_emoji} · fps-zarovnané={n_rate}")


if __name__ == "__main__":
    main()
