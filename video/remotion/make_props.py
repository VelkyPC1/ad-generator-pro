#!/usr/bin/env python3
"""Vygeneruje props.json pre Remotion caption overlay z dát Video Factory.

Číta z ../cache/: words_<id>.json (časovanie slov), script_<id>.json (CTA, voice_cta,
display_replacements), a ../config.json (fps, rozlíšenie, captions.highlight_color).

Použitie:
    python3 make_props.py <id>
    python3 make_props.py <id> --price-to 0.33 --set-text "Celý set len 1,99 €" \
        --benefits "6 vôní na vyskúšanie" "Dlhá sviežosť" "Vegan a bez parabénov"

Timeline horných kariet je pomerová k času, kde vo voiceoveri začína CTA
(cta_start) — funguje aj pre krátke videá. Social proof „vyskočí" raz počas
outra (nie cez celé video).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PVF = ROOT.parent
CACHE = PVF / "cache"

# Vizuálne témy — aby nevyzeralo každé video rovnako. Vyber cez overlay.theme v scripte.
THEMES = {
    "pink": {  # ružová téma
        "accent": "#E5397F", "accent2": "#ffd400", "onAccent": "#ffffff",
        "captionColor": "#ffffff", "captionStyle": "outline", "captionBg": "#000000",
        "ctaStyle": "pill", "ctaBg": "#E5397F", "ctaColor": "#ffffff",
        "cardBg": "#13161D", "cardColor": "#ffffff", "cardStyle": "pill",
        "captionPos": 0.5,
    },
    "noir": {  # tmavý luxus + spodný CTA pásik
        "accent": "#ff2e9a", "accent2": "#f5c451", "onAccent": "#ffffff",
        "captionColor": "#ffffff", "captionStyle": "block", "captionBg": "rgba(10,8,14,0.42)",
        "ctaStyle": "bar", "ctaBg": "#E5397F", "ctaColor": "#ffffff",
        "cardBg": "rgba(10,8,14,0.85)", "cardColor": "#ffffff", "cardStyle": "minimal",
        "captionPos": 0.55,
    },
    "cream": {  # svetlý, čistý, „ticket" CTA
        "accent": "#E5397F", "accent2": "#E5397F", "onAccent": "#ffffff",
        "captionColor": "#2a1520", "captionStyle": "block", "captionBg": "rgba(255,248,240,0.55)",
        "ctaStyle": "ticket", "ctaBg": "#ffffff", "ctaColor": "#E5397F",
        "cardBg": "#fff8f0", "cardColor": "#2a1520", "cardStyle": "boxed",
        "captionPos": 0.6,
    },
    "lemon": {  # žltá energia, vysoký kontrast
        "accent": "#ffd400", "accent2": "#E5397F", "onAccent": "#1a1200",
        "captionColor": "#ffffff", "captionStyle": "block", "captionBg": "rgba(20,12,6,0.45)",
        "ctaStyle": "pill", "ctaBg": "#ffd400", "ctaColor": "#1a1200",
        "cardBg": "#1a1200", "cardColor": "#ffffff", "cardStyle": "boxed",
        "captionPos": 0.52,
    },
    "mint": {  # sviežosť (tyrkys akcent + ružový sekundár)
        "accent": "#12b98a", "accent2": "#E5397F", "onAccent": "#ffffff",
        "captionColor": "#ffffff", "captionStyle": "outline", "captionBg": "#04211a",
        "ctaStyle": "pill", "ctaBg": "#12b98a", "ctaColor": "#ffffff",
        "cardBg": "#04211a", "cardColor": "#ffffff", "cardStyle": "pill",
        "captionPos": 0.5,
    },
}


def apply_display_replacements(words, replacements):
    """Nahradí sekvencie slov vo words liste display verziami (napr. 'šesť vzoriek' → '6 vzoriek').
    Rovnaká logika ako step4_compose — aby Remotion titulky ukazovali skratky, nie celé slová."""
    if not replacements:
        return words
    result = list(words)
    for rep in replacements:
        voice_tokens = rep["voice"].lower().split()
        display = rep["display"]
        n = len(voice_tokens)
        i = 0
        while i <= len(result) - n:
            if [w["word"].lower().strip(".,!?…") for w in result[i:i + n]] == voice_tokens:
                # koncovú interpunkciu ponechaj ("lei." -> "10 lei.") — podľa nej sa
                # titulky delia na konci vety (eos); bez nej sa spájali cez dve vety
                import re
                trail = re.search(r"[.,!?…]+$", result[i + n - 1]["word"])
                merged = {"word": display + (trail.group(0) if trail else ""),
                          "start": result[i]["start"], "end": result[i + n - 1]["end"]}
                result = result[:i] + [merged] + result[i + n:]
            i += 1
    return result


def build(vid, price_from, price_to, set_text, benefits, social, cta_text, write=True):
    words = json.loads((CACHE / f"words_{vid}.json").read_text())
    script = json.loads((CACHE / f"script_{vid}.json").read_text())
    cfg = json.loads((PVF / "config.json").read_text())
    cap = cfg.get("captions", {})

    words = apply_display_replacements(words, script.get("display_replacements", []))

    # koncová interpunkcia sa v titulkoch (uppercase) neukazuje — TTS ju má naďalej pre pauzy
    import re
    for w in words:
        w["eos"] = bool(re.search(r"[.!?…]\s*$", w["word"]))
        w["word"] = re.sub(r"[.,!?…]+$", "", w["word"])

    # per-video prvky zo script JSON (pole "overlay") majú prednosť pred CLI defaultmi
    ov = script.get("overlay", {})
    price_from = ov.get("price_from", price_from)
    price_to = ov.get("price_to", price_to)
    set_text = ov.get("set_text", set_text)
    benefits = ov.get("benefits", benefits)
    social = ov.get("social", social)
    cta_text = ov.get("cta", cta_text)
    # mena a počet desatinných miest — lokalizácia (€/ks · Kč/ks · Ft/db)
    unit = ov.get("unit", "€/ks")
    decimals = ov.get("decimals", 2)

    total = words[-1]["end"]
    cta_n = len((script.get("voice_cta") or "").split())
    cta_start = words[-cta_n]["start"] if 0 < cta_n <= len(words) else total - 2.5

    # Karty pomerovo k cta_start (fáza obsahu pred CTA); social „vyskočí" raz cez outro.
    cs = cta_start
    top_cards = [
        {"kind": "price_count", "from": price_from, "to": price_to, "unit": unit,
         "decimals": decimals, "start": 0.3, "end": round(cs * 0.32, 2)},
        {"kind": "text", "text": set_text,
         "start": round(cs * 0.34, 2), "end": round(cs * 0.60, 2)},
        {"kind": "benefits", "items": benefits,
         "start": round(cs * 0.62, 2), "end": round(cs * 0.99, 2)},
        {"kind": "social", "text": social,
         "start": round(cs + 0.2, 2), "end": round(total + 0.2, 2)},
    ]
    # zahoď karty, čo by po skrátení nedávali zmysel
    top_cards = [c for c in top_cards if c["end"] > c["start"] + 0.3]

    theme_name = ov.get("theme", "pink")
    theme = THEMES.get(theme_name, THEMES["pink"])

    props = {
        "words": words,
        "fps": cfg.get("fps", 30),
        "width": cfg["resolution"]["w"],
        "height": cfg["resolution"]["h"],
        "highlight_color": theme["accent"],
        "primary_color": theme["captionColor"],
        "font_size": 92,
        "y_position": theme["captionPos"],
        "topCards": top_cards,
        "cta": {"text": cta_text, "start": cta_start},
        "transitions": [],  # swipe prechody vypnuté (2026-07-07)
        "theme": theme,
    }
    if write:
        out = ROOT / "props.json"
        out.write_text(json.dumps(props, ensure_ascii=False, indent=2))
        print(f"OK -> {out} | id={vid} téma={theme_name} total={total:.2f}s CTA@{cta_start:.2f}s kariet={len(top_cards)}")
    return props


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--price-from", type=float, default=0.0)
    ap.add_argument("--price-to", type=float, default=0.33)
    ap.add_argument("--set-text", default="Celý set len 1,99 €")
    ap.add_argument("--cta", default="VYSKÚŠAŤ ZA 1,99 €")
    ap.add_argument("--social", default="tisíce spokojných zákazníkov")
    ap.add_argument("--benefits", nargs="+",
                    default=["6 vôní na vyskúšanie", "Dlhá sviežosť", "Vegan, bez parabénov"])
    args = ap.parse_args()
    build(args.id, args.price_from, args.price_to, args.set_text,
          args.benefits, args.social, args.cta)