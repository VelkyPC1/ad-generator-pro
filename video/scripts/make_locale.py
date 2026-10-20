#!/usr/bin/env python3
"""Vyrobí lokalizovaný script_<id>-<lang>.json zo slovenského originálu.

Klipy (seq_main, seq_outro), poradie aj téma sa preberajú 1:1 zo SK scriptu —
mení sa výhradne text: hook, segmenty, CTA, overlay karty a display_replacements.

Preklady sú v locales/<lang>.json vo formáte:
    { "<sk_id>": { "hook": ..., "voice_hook": ..., "segments": [...],
                   "cta": ..., "voice_cta": ..., "display_replacements": [...],
                   "overlay": {...} } }

Použitie:
    python3 scripts/make_locale.py cz            # všetky preložené v locales/cz.json
    python3 scripts/make_locale.py cz vz-6voni-b # len jedno video
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
LOCALES = ROOT / "locales"

# polia, ktoré sa preberajú zo SK originálu bez zmeny (obraz, nie text)
KEEP = ("seq_main", "seq_outro", "clips", "outro_clips")


def build(lang, only=None):
    tr = json.loads((LOCALES / f"{lang}.json").read_text())
    # "_common" nie je video — drží display_replacements spoločné pre celý jazyk
    common_reps = tr.get("_common", {}).get("display_replacements", [])
    ids = [only] if only else [k for k in tr if not k.startswith("_")]
    out = []

    for sk_id in ids:
        if sk_id not in tr:
            print(f"CHYBA: {sk_id} nie je v locales/{lang}.json", file=sys.stderr)
            sys.exit(1)
        src_path = CACHE / f"script_{sk_id}.json"
        if not src_path.exists():
            print(f"CHYBA: chýba SK originál {src_path}", file=sys.stderr)
            sys.exit(1)

        sk = json.loads(src_path.read_text())
        loc = tr[sk_id]
        new_id = f"{sk_id}-{lang}"

        doc = {"id": new_id}
        doc["hook"] = loc.get("hook", sk.get("hook", ""))
        doc["voice_hook"] = loc.get("voice_hook", doc["hook"])

        # menej segmentov = zámerné vypustenie (nahlásime); viac = takmer isto omyl
        n_loc, n_sk = len(loc["segments"]), len(sk["segments"])
        if n_loc > n_sk:
            print(f"CHYBA: {sk_id} — {n_loc} preložených segmentov "
                  f"vs. {n_sk} v SK origináli", file=sys.stderr)
            sys.exit(1)
        note = f"  [o {n_sk - n_loc} segment(ov) menej než SK]" if n_loc < n_sk else ""
        doc["segments"] = [
            {"text": s["text"], "voice": s.get("voice", s["text"])}
            for s in loc["segments"]
        ]

        doc["cta"] = loc.get("cta", sk.get("cta", ""))
        doc["voice_cta"] = loc.get("voice_cta", doc["cta"])

        # obraz preberáme zo SK — rovnaké klipy, rovnaké poradie
        for k in KEEP:
            if k in sk:
                doc[k] = sk[k]

        # hook klip pre hook videá: lokalizovaný dabing = SK hook_clip + "-<lang>"
        # (alebo explicitný override v locale JSON)
        if "hook_clip" in sk:
            doc["hook_clip"] = loc.get("hook_clip", f"{sk['hook_clip']}-{lang}")

        # spoločné pre jazyk + per-video; zahodíme tie, čo sa vo voiceoveri nevyskytujú
        reps = common_reps + loc.get("display_replacements", [])
        voice_toks = [
            w.lower().strip(".,!?…—")
            for w in " ".join(
                [doc["voice_hook"]] + [s["voice"] for s in doc["segments"]] + [doc["voice_cta"]]
            ).split()
        ]
        used = []
        for rep in reps:
            rt = [w.lower().strip(".,!?…—") for w in rep["voice"].split()]
            n = len(rt)
            if any(voice_toks[i:i + n] == rt for i in range(len(voice_toks) - n + 1)):
                used.append(rep)
        doc["display_replacements"] = used

        # overlay: SK základ (theme, price_from) prepísaný lokálnymi hodnotami
        ov = dict(sk.get("overlay", {}))
        ov.update(loc.get("overlay", {}))
        doc["overlay"] = ov

        dst = CACHE / f"script_{new_id}.json"
        dst.write_text(json.dumps(doc, ensure_ascii=False, indent=2))
        out.append(new_id)
        print(f"OK -> {dst.name}  (klipy zo {sk_id}: {len(doc.get('seq_main', []))} main "
              f"+ {len(doc.get('seq_outro', []))} outro){note}")

    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("použitie: make_locale.py <lang> [sk_id]", file=sys.stderr)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
