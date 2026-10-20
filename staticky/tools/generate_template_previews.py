#!/usr/bin/env python3
"""
AI ukážky 40 Motion templatov pre tab „Templaty a štýly" (PLATENÉ — Gemini, ~0,07 $ / obrázok pri 1K).

    python3 tools/generate_template_previews.py --env brands/<brand>/.env --dry-run   # len vypíše prompty
    python3 tools/generate_template_previews.py --env brands/<brand>/.env             # vygeneruje chýbajúce
    python3 tools/generate_template_previews.py --env … --only 07,17 --force          # konkrétne, aj prepísať

Každá ukážka je fiktívna značka „Lumen" s neutrálnym produktom a slovenským textom — ukazuje FORMÁT, nie klienta.
Výstup: template-previews/<NN>.png s pásikom „UKÁŽKA" (pridaný cez PIL, nie AI). Cena ide do cost-log.jsonl.
Token sa nikdy nevyberá automaticky — vždy explicitne cez --env.
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import pricing  # noqa: E402

TEMPLATES = ROOT / "04-brief-template-copy-prompts" / "01-templates-by-motion"
OUT = ROOT / "template-previews"
MODEL = pricing.IMAGE_MODEL
ALLOWED_AR = {"1:1", "4:5", "9:16", "16:9", "3:4", "2:3"}


def load_env(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^GEMINI_API_KEY\s*=\s*(.+)$", line.strip())
        if m:
            return m.group(1).strip().strip("'\"")
    sys.exit(f"✗ V {path} nie je GEMINI_API_KEY")


def parse(md: Path) -> dict:
    text = md.read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    num, _, name = title.partition("—")
    if not name:
        num, name = md.name[:2], title
    what = ""
    m = re.search(r"## What this format is\s*\n+(.+?)(?:\n\s*\n|\n#)", text, re.S)
    if m:
        what = " ".join(m.group(1).split())
    ar = re.search(r"\*\*aspect_ratio:\*\*\s*(\d+:\d+)", text)
    ratio = ar.group(1) if ar and ar.group(1) in ALLOWED_AR else "4:5"
    return {"num": int(num.strip()), "name": name.strip(), "what": what, "ratio": ratio}


def prompt_for(t: dict) -> str:
    return (
        f"Create a polished, realistic example of a static paid-social ad that clearly demonstrates the ad format "
        f"\"{t['name']}\". How this format works: {t['what']}\n\n"
        "Use a FICTIONAL neutral brand called \"Lumen\" selling a minimalist home-care product: a clean white bottle "
        "with a soft lavender label and the word Lumen on it. No real brands, no real logos, no real people's names.\n"
        "All visible text must be short, natural SLOVAK sample copy with correct diacritics (headline, supporting line, "
        "price or offer where the format needs it, CTA where the format needs it). Render ONLY the ad copy — never "
        "render font names, sizes, colour codes, percentages, layout instructions or the format name as text.\n"
        "Premium, modern, well-crafted layout with clear hierarchy, generous spacing and a coherent palette of "
        "lavender, warm off-white and one confident accent. Keep the top ~8% and bottom ~10% calm (no tiny text there). "
        "The composition must make the structure of this ad format obvious at a glance."
    )


def watermark(path: Path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = max(14, int(w * 0.026))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
    except Exception:
        font = ImageFont.load_default()
    label = "UKÁŽKA FORMÁTU"
    tw = d.textlength(label, font=font)
    pad = int(size * 0.7)
    x0, y0 = w - tw - pad * 3, int(h * 0.02)
    d.rounded_rectangle((x0, y0, x0 + tw + pad * 2, y0 + size + pad), radius=(size + pad) // 2, fill=(20, 20, 26, 170))
    d.text((x0 + pad, y0 + pad // 2), label, font=font, fill=(255, 255, 255, 235))
    Image.alpha_composite(im, layer).convert("RGB").save(path, "PNG")


def generate(api_key: str, prompt: str, ratio: str) -> bytes:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    for attempt in range(3):
        try:
            r = client.models.generate_content(
                model=MODEL, contents=[types.Part.from_text(text=prompt)],
                config=types.GenerateContentConfig(response_modalities=["IMAGE"],
                                                   image_config=types.ImageConfig(aspect_ratio=ratio)))
            for part in r.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data
            raise ValueError("bez obrázka v odpovedi")
        except Exception as e:
            if attempt == 2:
                raise
            print(f"    ↻ pokus {attempt + 2} ({e})")
            time.sleep(6 * (attempt + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True, help="cesta k .env s GEMINI_API_KEY (token si vždy vyberá používateľ)")
    ap.add_argument("--only", default="", help="čísla templatov, napr. 07,17")
    ap.add_argument("--force", action="store_true", help="prepísať existujúce ukážky")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    only = {int(x) for x in a.only.split(",") if x.strip()}
    todo = []
    for md in sorted(TEMPLATES.glob("[0-9][0-9]-*.md")):
        t = parse(md)
        if only and t["num"] not in only:
            continue
        if not a.force and (OUT / f"{t['num']:02d}.png").exists():
            continue
        todo.append(t)
    est = len(todo) * pricing.image_cost("google", "1K", 0)["total"]
    print(f"Ukážok na vygenerovanie: {len(todo)} · model {MODEL} · odhad ≈ {est:.2f} $")
    if a.dry_run:
        for t in todo:
            print(f"\n[{t['num']:02d}] {t['name']} · {t['ratio']}\n{prompt_for(t)[:300]}…")
        return
    key = load_env(Path(a.env))
    OUT.mkdir(exist_ok=True)
    ok = fail = 0
    for t in todo:
        path = OUT / f"{t['num']:02d}.png"
        print(f"[{t['num']:02d}] {t['name']} ({t['ratio']})…")
        try:
            path.write_bytes(generate(key, prompt_for(t), t["ratio"]))
            watermark(path)
            cost = pricing.image_cost("google", "1K", 0)
            pricing.log_generation({"kind": "image", "brand": "template-previews", "file": str(path.relative_to(ROOT)),
                                    "model": MODEL, "provider": "google", "tier": "1K", "inputs": 0,
                                    "cost_output": cost["output"], "cost_input": cost["input"], "cost_usd": cost["total"],
                                    "prices_checked": pricing.PRICES_CHECKED})
            ok += 1
            print("    ✓")
        except Exception as e:
            fail += 1
            print(f"    ✗ {e}")
    print(f"\nHotovo: {ok} ✓ · {fail} ✗ — v dashboarde klikni „⟳ Úplná obnova\"")


if __name__ == "__main__":
    main()
