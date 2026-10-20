#!/usr/bin/env python3
"""Vizuálny kontaktný list footage klipov — 1 miniatúra (stredný frame) na klip
s názvom pod ňou, poskladané do mriežky. Pomáha vyberať klipy podľa OBRAZU,
nie len podľa názvu.

Použitie:
    python3 scripts/make_contact_sheet.py            # všetky seq_* + product_*
    python3 scripts/make_contact_sheet.py --filter produkt   # len klipy s podreťazcom

Výstup: clip_previews/sheet_NN.jpg  (viac strán, ~48 klipov na stranu)
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FOOTAGE = ROOT / "assets" / "footage"
OUTDIR = ROOT / "clip_previews"

COLS, PER_PAGE = 6, 48          # 6×8 klipov na stranu
TW, TH = 300, 533               # miniatúra 9:16
PAD, LABEL_H = 16, 40
BG, FG = (18, 12, 25), (240, 240, 240)


def clip_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 2.0


def grab_frame(clip, dst):
    """Stredný frame klipu ako JPG (scale na šírku miniatúry)."""
    t = max(0.1, clip_dur(clip) * 0.5)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", f"{t:.2f}", "-i", str(clip), "-frames:v", "1",
                    "-vf", f"scale={TW}:{TH}:force_original_aspect_ratio=increase,crop={TW}:{TH}",
                    str(dst)], check=False)
    return dst.exists()


def load_font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def build(clips):
    OUTDIR.mkdir(exist_ok=True)
    font = load_font(19)
    tmp = Path(tempfile.mkdtemp())
    pages = [clips[i:i + PER_PAGE] for i in range(0, len(clips), PER_PAGE)]
    made = []
    for pi, page in enumerate(pages, 1):
        rows = (len(page) + COLS - 1) // COLS
        cw = TW + PAD
        ch = TH + LABEL_H + PAD
        W = COLS * cw + PAD
        H = rows * ch + PAD
        sheet = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(sheet)
        for idx, clip in enumerate(page):
            r, c = divmod(idx, COLS)
            x = PAD + c * cw
            y = PAD + r * ch
            fr = tmp / f"{pi}_{idx}.jpg"
            if grab_frame(clip, fr):
                try:
                    sheet.paste(Image.open(fr), (x, y))
                except Exception:
                    pass
            name = clip.stem.replace("seq_", "").replace("product_", "★")
            # zalom dlhý názov na 2 riadky
            label = name if len(name) <= 34 else name[:33] + "…"
            draw.text((x, y + TH + 6), label, fill=FG, font=font)
            print(f"  [{pi}] {clip.stem}")
        out = OUTDIR / f"sheet_{pi:02d}.jpg"
        sheet.save(out, quality=85)
        made.append(out)
    return made


def main():
    filt = None
    if "--filter" in sys.argv:
        filt = sys.argv[sys.argv.index("--filter") + 1].lower()
    clips = sorted([p for p in FOOTAGE.glob("*.mp4")
                    if (p.name.startswith("seq_") or p.name.startswith("product_"))
                    and (filt is None or filt in p.name.lower())])
    if not clips:
        print("Žiadne klipy.", file=sys.stderr)
        sys.exit(1)
    print(f"Klipov: {len(clips)}")
    made = build(clips)
    print("\nHOTOVO:")
    for m in made:
        print(f"  {m}")


if __name__ == "__main__":
    main()
