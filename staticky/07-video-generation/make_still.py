#!/usr/bin/env python3
"""
Rýchly one-off generátor štartovacích snímok pre Omni (Nano Banana / gemini image).

Usage:
    python make_still.py "prompt text" out.png
    python make_still.py --model gemini-3-pro-image "prompt" out.png
    python make_still.py --ref path/to/ref.jpg "prompt" out.png      # image+text vstup

Kľúč: GEMINI_API_KEY z staticky/.env
"""
import argparse, base64, os, sys
from pathlib import Path

from dotenv import load_dotenv
_here = Path(__file__).resolve().parent
for c in (_here / "../.env", _here / ".env"):
    if c.exists():
        load_dotenv(c); break

from google import genai
from google.genai import types

ap = argparse.ArgumentParser()
ap.add_argument("prompt")
ap.add_argument("out")
ap.add_argument("--model", default="gemini-3.1-flash-image")
ap.add_argument("--ref", action="append", default=[])
args = ap.parse_args()

key = os.environ.get("GEMINI_API_KEY", "")
if not key:
    sys.exit("GEMINI_API_KEY chýba")

client = genai.Client(api_key=key)

parts = [args.prompt]
for r in args.ref:
    p = Path(r).expanduser()
    mime = "image/jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    parts.append(types.Part.from_bytes(data=p.read_bytes(), mime_type=mime))

resp = client.models.generate_content(model=args.model, contents=parts)

saved = False
for part in resp.candidates[0].content.parts:
    inline = getattr(part, "inline_data", None)
    if inline and inline.data:
        Path(args.out).write_bytes(inline.data)
        saved = True
        print(f"✅ {args.out} ({len(inline.data)/1024:.0f} KB)")
    elif getattr(part, "text", None):
        print(f"   model: {part.text[:200]}")
if not saved:
    sys.exit("❌ žiadny obrázok v odpovedi")
