"""Rozšíri hotový 1:1 banner na 9:16 (outpaint) cez Gemini — zachová celú pôvodnú kreatívu.
Použitie: GEMINI_API_KEY=... python3 tools/extend_to_9x16.py <vstup.png> <vystup.png>
"""
import os, sys
from google import genai
from google.genai import types

MODEL = "gemini-3.1-flash-image-preview"
PROMPT = (
    "You are given a FINISHED square 1:1 advertising creative. Produce a VERTICAL 9:16 (1080x1920) "
    "version of THE SAME ad, FULL-BLEED. Keep the ENTIRE original composition — every product bottle, "
    "ALL text, badges, price and CTA button — completely UNCHANGED, identical, same wording, spelling, "
    "colours, fonts and positions relative to each other. Do NOT re-render, re-type, translate, garble, "
    "move, duplicate, add or remove ANY text or product. ONLY naturally EXTEND the existing background / "
    "scene upward and downward so it fills the ENTIRE 1080x1920 canvas edge to edge as ONE continuous, "
    "photorealistic, seamless scene — same colours, same gradient/room, same lighting and perspective. "
    "Absolutely NO border, NO frame, NO card, NO colour band, NO blur strip, NO stretched/streaky pixels, "
    "NO seam anywhere. The extended top and bottom must look like a real continuation of the same scene, "
    "not a stretched copy. The result must look like the original ad was natively shot/designed as 9:16."
)

def extend(inp: str, out: str):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("Chýba GEMINI_API_KEY v prostredí")
    client = genai.Client(api_key=key)
    with open(inp, "rb") as f:
        part = types.Part.from_bytes(data=f.read(), mime_type="image/png")
    resp = client.models.generate_content(
        model=MODEL,
        contents=[part, types.Part.from_text(text=PROMPT)],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16"),
        ),
    )
    for p in resp.candidates[0].content.parts:
        if p.inline_data:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as g:
                g.write(p.inline_data.data)
            print("OK:", out)
            return
    sys.exit("Gemini nevrátil obrázok")

if __name__ == "__main__":
    extend(sys.argv[1], sys.argv[2])
