#!/usr/bin/env python3
"""
Video Factory — jeden príkaz na celé video.

    python3 vyrob_video.py <id>                    # v2: voiceover → props → render Ad → dashboard
    python3 vyrob_video.py <id> --styl vyrazny     # štýl prechodov/strihu (make_ad_props.py STYLES)
    python3 vyrob_video.py <id> --hook             # hook video (UGC hook + produktová sekcia) → *_FINAL.mp4
    python3 vyrob_video.py <id> --legacy           # starý v1 postup (silent sekvencia + overlay)
    python3 vyrob_video.py <id> --novy-hlas        # vynúti nový voiceover (ElevenLabs = platené)
    python3 vyrob_video.py <id> --skusobne         # len vypíše kroky, nič nespustí

Vstup: cache/script_<id>.json. Výstup: remotion/out[/<JAZYK>]/<id>_REMOTION.mp4 (hook: _FINAL.mp4).
Config sa vyberie sám: config_<klient>.json podľa začiatku ID (napr. config_moja-znacka.json pre ID moja-znacka-…),
inak podľa jazyka (…-hu / de- / pl- / ro-), inak config.json.
Voiceover sa NEROBÍ znova, ak cache/voice_<id>.mp3 už existuje (šetrí ElevenLabs kredity).
Render beží vždy v sandboxe (security/render-sandbox.sb). Po renderi sa prestaví dashboard AdGenerator Pro.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent              # AdGenerator-Pro/video
REMOTION = ROOT / "remotion"
CACHE = ROOT / "cache"
DASHBOARD_BUILD = ROOT.parent / "staticky" / "tools" / "build_dashboard.py"
LANG_CONFIG = {"hu": "config_hu.json", "de": "config_de.json", "pl": "config_pl.json", "ro": "config_ro.json"}


def video_lang(vid: str) -> str:
    """Jazyk podľa ID — rovnaká logika ako render_overlay.sh (…-cz / …-hu, de- / pl- / ro-)."""
    for suf in ("cz", "hu", "de", "pl", "ro"):
        if vid.endswith(f"-{suf}"):
            return suf
    for pre in ("de", "pl", "ro"):
        if vid.startswith(f"{pre}-"):
            return pre
    return "sk"


def pick_config(vid: str) -> Path:
    best = None
    for cfg in ROOT.glob("config_*.json"):
        key = cfg.stem[len("config_"):]
        if key in LANG_CONFIG.values() or key in ("hu", "de", "pl", "ro"):
            continue
        if vid == key or vid.startswith(key + "-") or vid.startswith(key.replace("_", "-") + "-"):
            if not best or len(key) > len(best.stem):
                best = cfg
    if best:
        return best
    lang = video_lang(vid)
    if lang in LANG_CONFIG and (ROOT / LANG_CONFIG[lang]).exists():
        return ROOT / LANG_CONFIG[lang]
    return ROOT / "config.json"


def out_dir(vid: str) -> Path:
    lang = video_lang(vid)
    return REMOTION / "out" / (lang.upper() if lang != "sk" else "")


def step(title: str, cmd: list, dry: bool, cwd: Path = ROOT, env: dict = None):
    print(f"\n▶ {title}\n  $ {' '.join(str(c) for c in cmd)}")
    if dry:
        return
    t = time.time()
    r = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env={**os.environ, **(env or {})})
    if r.returncode != 0:
        sys.exit(f"✗ Krok zlyhal ({title}) — kód {r.returncode}")
    print(f"  ✓ {time.time() - t:.0f} s")


def main():
    ap = argparse.ArgumentParser(description="Video Factory — celé video jedným príkazom")
    ap.add_argument("id", help="ID videa = cache/script_<id>.json")
    ap.add_argument("--styl", default="stredny", help="štýl v2 (make_ad_props.py --style), default stredny")
    ap.add_argument("--hudba", default="auto", help="music/<súbor>.mp3 alebo 'auto' (náhodná z music)")
    ap.add_argument("--cta-bottom", default="0.22", help="odsadenie CTA zdola — 0,22 = v safezone (RULES #15)")
    ap.add_argument("--hook", action="store_true", help="hook video → scripts/build_hookvideo.sh")
    ap.add_argument("--legacy", action="store_true", help="v1: build_silent_seq + render_overlay.sh")
    ap.add_argument("--novy-hlas", action="store_true", help="vždy nový voiceover (platené ElevenLabs)")
    ap.add_argument("--bez-dashboardu", action="store_true", help="neprestavovať dashboard po renderi")
    ap.add_argument("--skusobne", action="store_true", help="len vypíše kroky")
    ap.add_argument("--extra", default="", help="ďalšie prepínače pre make_ad_props.py, napr. \"--fancy --no-blur\"")
    a = ap.parse_args()

    vid = a.id
    script = CACHE / f"script_{vid}.json"
    if not script.exists():
        sys.exit(f"✗ Chýba {script.relative_to(ROOT)} — najprv priprav script (step1_script.py alebo make_locale.py)")
    cfg = pick_config(vid)
    env = {"FF_CONFIG": cfg.name} if cfg.name != "config.json" else {}
    print(f"Video: {vid} · jazyk {video_lang(vid).upper()} · config {cfg.name}"
          + (" · hook" if a.hook else " · legacy" if a.legacy else f" · v2 štýl {a.styl}"))

    if a.hook:
        step("Hook video (voiceover → sekvencia → overlay → spojenie)", ["bash", "scripts/build_hookvideo.sh", vid], a.skusobne, env=env)
    else:
        voice = CACHE / f"voice_{vid}.mp3"
        if a.novy_hlas or not voice.exists():
            step("Voiceover (ElevenLabs, zapíše sa do denníka cien)", [sys.executable, "scripts/step2_voice.py", script], a.skusobne, env=env)
        else:
            print(f"\n▶ Voiceover — používam existujúci {voice.relative_to(ROOT)} (nový: --novy-hlas)")

        if a.legacy:
            step("Silent sekvencia klipov", [sys.executable, "scripts/build_silent_seq.py", vid], a.skusobne, env=env)
            step("Remotion overlay (titulky + karty + hudba)", ["bash", "render_overlay.sh", vid], a.skusobne, cwd=REMOTION, env=env)
        else:
            props = f"props_{vid}.json"
            cmd = [sys.executable, "make_ad_props.py", vid, "--style", a.styl, "--cta-bottom", a.cta_bottom, "--out", props]
            if a.hudba:
                cmd += ["--music", a.hudba]
            cmd += a.extra.split()
            step("Props pre Remotion (strih, prechody, titulky)", cmd, a.skusobne, cwd=REMOTION, env=env)
            dest = out_dir(vid)
            if not a.skusobne:
                dest.mkdir(parents=True, exist_ok=True)
            target = dest / f"{vid}_REMOTION.mp4"
            render = ["npx", "remotion", "render", "src/index.ts", "Ad", target.relative_to(REMOTION), f"--props={props}", "--gl=angle"]
            sandbox = REMOTION.parent / "security" / "render-sandbox.sb"
            if shutil.which("sandbox-exec") and sandbox.exists():
                render = ["sandbox-exec", "-f", "../security/render-sandbox.sb"] + render
                title = "Render v sandboxe (Remotion Ad)"
            else:
                title = "Render (Remotion Ad) — ⚠ bez sandboxu (sandbox-exec je len na macOS; spusti setup.sh)"
            step(title, render, a.skusobne, cwd=REMOTION, env=env)
            if not a.skusobne:
                print(f"\n✓ Hotovo: {target.relative_to(ROOT)}")

    if not a.bez_dashboardu and DASHBOARD_BUILD.exists():
        step("Dashboard AdGenerator Pro (video + výstupy)", [sys.executable, DASHBOARD_BUILD], a.skusobne, cwd=DASHBOARD_BUILD.parent.parent)


if __name__ == "__main__":
    main()
