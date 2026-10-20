#!/usr/bin/env python3
"""
Ad Image Translator — translates texts in an ad image into multiple languages.

Product/packaging texts are preserved. Visual, layout, and brand elements unchanged.
Uses Nano Banana 2 (gemini-3.1-flash-image-preview) via Google API or FAL.

Usage:
    python translate_ads.py --image ad.png --languages hu,cz,ro,pl
    python translate_ads.py --image ad.png --languages hu,cz,ro,pl --provider google-batch
    python translate_ads.py --image ad.png --languages sk --output-dir path/to/out
    python translate_ads.py --image ad.png --languages hu --dry-run
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' required. pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _load_env():
    d = Path(__file__).resolve().parent
    for _ in range(10):
        env_file = d / "jozef" / "keys" / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break
        d = d.parent

_load_env()

FAL_KEY = os.environ.get("FAL_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL_ID = "gemini-3.1-flash-image-preview"
FAL_EDIT_ENDPOINT = "fal-ai/nano-banana-2/edit"

LANGUAGE_NAMES = {
    "sk": "Slovak",
    "hu": "Hungarian",
    "cz": "Czech",
    "cs": "Czech",
    "ro": "Romanian",
    "pl": "Polish",
    "de": "German",
    "en": "English",
    "hr": "Croatian",
    "bg": "Bulgarian",
    "rs": "Serbian",
    "si": "Slovenian",
    "uk": "Ukrainian",
    "it": "Italian",
    "es": "Spanish",
    "fr": "French",
    "nl": "Dutch",
    "pt": "Portuguese",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "el": "Greek",
    "tr": "Turkish",
    "at": "German",
}

BRAND = "the brand"   # nastaví --brand

TRANSLATION_PROMPT = (
    "Role: Professional Multilingual Graphic Designer & Translator for the brand {brand}.\n\n"
    "Task: Replace ALL text in this image with its {language} translation, maintaining 100% visual identity.\n\n"
    "Translation Rules:\n"
    "1. TARGET: Translate all headlines, benefits, ingredient lists (outside the product), and CTAs.\n"
    "2. TERMINOLOGY: Use the established terminology of the product's category in {language} (the words real customers and shops use), not literal translations.\n"
    "3. EXCLUSIONS:\n"
    "   - Do NOT translate or modify text on the product packaging, labels, or bottle.\n"
    "   - BRAND WORDMARK: The brand logo/wordmark is a visual element — preserve it EXACTLY as it appears in the original image (same position, same styling, same text). Do NOT replace it with translated text, do NOT write 'Prezentované' or any other phrase in its place.\n"
    "   - Keep the brand name {brand} unchanged everywhere it appears.\n"
    "   - Keep numerical values and ratings (e.g., 4.9/5) in their original format.\n"
    "4. TONE: Keep the tone of the original copy.\n\n"
    "Visual Consistency Rules:\n"
    "- POSITION: Place translated text at the EXACT coordinates of the original text.\n"
    "- STYLE: Match font family, weight (bold/italic), and color perfectly.\n"
    "- SPACING: If {language} text is longer, use tighter kerning or slightly smaller font size. "
    "Do NOT overlap other visual elements.\n"
    "- QUALITY: No blurring or artifacts around the text. The background must remain untouched.\n\n"
    "Double-check: Ensure even the small text at the bottom is translated. "
    "CRITICAL: Each product / ingredient name must appear exactly ONCE. "
    "Do NOT repeat any word within the same name (e.g., write 'Korálovec ježatý', NOT 'Korálovec ježatý ježatý')."
)


# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------

def select_provider():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║         Ad Image Translator — Provider                ║")
    print("╠════════════════════════════════════════════════════════╣")
    print("║  1. FAL AI                  (~$0.06/img, okamžite)    ║")
    print("║  2. Google — Nano Banana 2  (~$0.067/img, okamžite)   ║")
    print("║  3. Google Batch — NB2      (~$0.034/img, do 24h)     ║")
    print("╚════════════════════════════════════════════════════════╝")
    while True:
        choice = input("\nVyber provider [1/2/3]: ").strip()
        if choice == "1":
            return "fal"
        elif choice == "2":
            return "google"
        elif choice == "3":
            return "google-batch"
        else:
            print("Zadaj 1, 2 alebo 3.")


# ---------------------------------------------------------------------------
# Google helpers
# ---------------------------------------------------------------------------

def load_image_part_google(image_path: str):
    try:
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' required. pip install google-genai")
        sys.exit(1)
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(data=data, mime_type=mime)


def translate_google_realtime(image_part, prompt_text: str, aspect_ratio: str) -> bytes:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' required. pip install google-genai")
        sys.exit(1)
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL_ID,
        contents=[image_part, types.Part.from_text(text=prompt_text)],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise ValueError("No image returned in response")


# ---------------------------------------------------------------------------
# Google Batch
# ---------------------------------------------------------------------------

def translate_google_batch(image_path: str, jobs: list, aspect_ratio: str) -> list:
    """
    jobs: list of {"lang_code": "hu", "lang_name": "Hungarian", "output_path": Path}
    Returns list of result dicts.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' required. pip install google-genai")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)

    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    jsonl_lines = []
    key_map = {}

    for job in jobs:
        key = job["lang_code"]
        key_map[key] = job
        prompt_text = TRANSLATION_PROMPT.format(language=job["lang_name"], brand=BRAND)
        jsonl_lines.append(json.dumps({
            "key": key,
            "request": {
                "contents": [{
                    "parts": [
                        {"inlineData": {"mimeType": mime, "data": image_b64}},
                        {"text": prompt_text},
                    ]
                }],
                "generation_config": {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {"aspectRatio": aspect_ratio},
                }
            }
        }))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(jsonl_lines))
        jsonl_path = f.name

    slug = Path(image_path).stem
    print(f"Uploading batch ({len(jsonl_lines)} languages)...")
    uploaded = client.files.upload(
        file=jsonl_path,
        config=types.UploadFileConfig(display_name=f"{slug}-translate-batch", mime_type="jsonl"),
    )

    print("Submitting batch job...")
    batch_job = client.batches.create(
        model=GEMINI_MODEL_ID,
        src=uploaded.name,
        config={"display_name": f"{slug}-translate"},
    )
    print(f"Batch job: {batch_job.name}")
    print("Čakám na výsledky (môže trvať až 24h, kontrolujem každých 30s)...\n")

    done_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    while True:
        batch_job = client.batches.get(name=batch_job.name)
        state = batch_job.state.name
        print(f"  Status: {state} ({time.strftime('%H:%M:%S')})")
        if state in done_states:
            break
        time.sleep(30)

    if batch_job.state.name != "JOB_STATE_SUCCEEDED":
        print(f"✗ Batch failed: {batch_job.state.name}")
        return []

    result_file = batch_job.dest.file_name
    file_content = client.files.download(file=result_file)

    results = []
    for line in file_content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        resp = json.loads(line)
        key = resp.get("key", "")
        if key not in key_map:
            continue
        job = key_map[key]
        try:
            candidates = resp.get("response", {}).get("candidates", [])
            if not candidates:
                print(f"  ✗ {key}: no candidates — {str(resp.get('response', {}))[:300]}")
                continue
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                finish = candidates[0].get("finishReason", "unknown")
                print(f"  ✗ {key}: no parts (finishReason={finish}) — {str(content)[:200]}")
                continue
            img_bytes = None
            for part in parts:
                if "inlineData" in part:
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    break
            if not img_bytes:
                print(f"  ✗ {key}: no image in response")
                continue
            with open(job["output_path"], "wb") as f:
                f.write(img_bytes)
            print(f"  ✓ {key}: {job['output_path'].name}")
            results.append({"lang": key, "file": str(job["output_path"])})
        except Exception as e:
            print(f"  ✗ {key}: {e}")

    os.unlink(jsonl_path)
    return results


# ---------------------------------------------------------------------------
# FAL helpers
# ---------------------------------------------------------------------------

def upload_to_fal(image_path: str) -> str:
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    resp = requests.post(
        "https://fal.run/fal-ai/file-storage/upload",
        headers={"Authorization": f"Key {FAL_KEY}"},
        files={"file": (os.path.basename(image_path), data, mime)},
    )
    if resp.status_code != 200:
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    result = resp.json()
    return result.get("url", result.get("file_url", ""))


def translate_fal(image_url: str, prompt_text: str, aspect_ratio: str) -> bytes:
    resp = requests.post(
        f"https://fal.run/{FAL_EDIT_ENDPOINT}",
        headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"},
        json={
            "prompt": prompt_text,
            "image_urls": [image_url],
            "aspect_ratio": aspect_ratio,
            "num_images": 1,
            "output_format": "png",
            "safety_tolerance": "5",
        },
        timeout=180,
    )
    resp.raise_for_status()
    result = resp.json()
    img_url = result["images"][0]["url"]
    img_resp = requests.get(img_url)
    img_resp.raise_for_status()
    return img_resp.content


# ---------------------------------------------------------------------------
# Gallery
# ---------------------------------------------------------------------------

def generate_gallery(output_dir: Path, source_name: str, results: list):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{source_name} — Translations</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; padding: 2rem; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 0.4rem; }}
  .meta {{ color: #888; margin-bottom: 2rem; font-size: 0.9rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }}
  .card {{ background: #1a1a1a; border-radius: 12px; overflow: hidden; }}
  .card img {{ width: 100%; display: block; }}
  .card .info {{ padding: 0.8rem 1rem; font-size: 0.9rem; font-weight: 600; letter-spacing: 0.05em; }}
</style>
</head>
<body>
<h1>{source_name} — Translations</h1>
<p class="meta">Generated {time.strftime("%B %d, %Y")} · {len(results)} languages</p>
<div class="grid">
"""
    for r in results:
        fname = Path(r["file"]).name
        lang = r["lang"].upper()
        html += f'  <div class="card"><img src="{fname}" alt="{lang}"><div class="info">{lang}</div></div>\n'

    html += "</div>\n</body>\n</html>"

    gallery_path = output_dir / "gallery.html"
    with open(gallery_path, "w") as f:
        f.write(html)
    print(f"Gallery: {gallery_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Translate texts in an ad image into multiple languages via Nano Banana 2"
    )
    parser.add_argument("--brand", default="the brand", help="názov značky (nebude sa prekladať)")
    parser.add_argument("--image", required=True,
        help="Source ad image (PNG/JPG)")
    parser.add_argument("--languages", required=True,
        help="Comma-separated language codes: hu,cz,ro,pl,sk,de,en,...")
    parser.add_argument("--provider", choices=["fal", "google", "google-batch"], default=None,
        help="Generation provider (default: interactive selection)")
    parser.add_argument("--output-dir", default=None,
        help="Output folder (default: translations/ next to source image)")
    parser.add_argument("--aspect-ratio", default="4:5",
        help="Output aspect ratio — must match source image (default: 4:5)")
    parser.add_argument("--dry-run", action="store_true",
        help="Show what would run without calling the API")
    args = parser.parse_args()
    global BRAND
    BRAND = args.brand

    image_path = Path(args.image).resolve()
    if not image_path.exists():
        print(f"Error: image not found: {image_path}")
        sys.exit(1)

    lang_codes = [l.strip().lower() for l in args.languages.split(",") if l.strip()]
    provider = args.provider if args.provider else select_provider()

    if not args.dry_run:
        if provider == "fal" and not FAL_KEY:
            print("Error: FAL_KEY not set. Check jozef/keys/.env")
            sys.exit(1)
        if provider in ("google", "google-batch") and not GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY not set. Check jozef/keys/.env")
            sys.exit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else image_path.parent / "translations"
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = image_path.stem
    aspect_ratio = args.aspect_ratio

    jobs = []
    unknown = []
    for code in lang_codes:
        name = LANGUAGE_NAMES.get(code)
        if not name:
            unknown.append(code)
        else:
            out_path = output_dir / f"{slug}-{code}.png"
            jobs.append({"lang_code": code, "lang_name": name, "output_path": out_path})

    if unknown:
        supported = ", ".join(sorted(LANGUAGE_NAMES.keys()))
        print(f"Warning: unknown language codes (skipped): {unknown}")
        print(f"Supported: {supported}\n")

    if not jobs:
        print("No valid languages. Exiting.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Ad Image Translator")
    print(f"  Source:       {image_path.name}")
    print(f"  Languages:    {', '.join(j['lang_name'] for j in jobs)}")
    print(f"  Provider:     {provider.upper()}")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Output:       {output_dir}/")
    print(f"{'='*60}\n")

    if args.dry_run:
        print("DRY RUN — prompts that would be sent:\n")
        for job in jobs:
            print(f"  [{job['lang_code'].upper()}] {TRANSLATION_PROMPT.format(language=job['lang_name'], brand=BRAND)}")
        print(f"\n  Output files:")
        for job in jobs:
            print(f"  → {job['output_path']}")
        return

    results = []

    if provider == "google-batch":
        results = translate_google_batch(str(image_path), jobs, aspect_ratio)

    elif provider == "google":
        image_part = load_image_part_google(str(image_path))
        for job in jobs:
            prompt_text = TRANSLATION_PROMPT.format(language=job["lang_name"], brand=BRAND)
            print(f"Translating → {job['lang_name']}...")
            try:
                img_bytes = translate_google_realtime(image_part, prompt_text, aspect_ratio)
                with open(job["output_path"], "wb") as f:
                    f.write(img_bytes)
                print(f"  ✓ {job['output_path'].name}")
                results.append({"lang": job["lang_code"], "file": str(job["output_path"])})
            except Exception as e:
                print(f"  ✗ {job['lang_name']}: {e}")

    elif provider == "fal":
        print("Uploading source image to FAL storage...")
        image_url = upload_to_fal(str(image_path))
        print("  ✓ Uploaded\n")
        for job in jobs:
            prompt_text = TRANSLATION_PROMPT.format(language=job["lang_name"], brand=BRAND)
            print(f"Translating → {job['lang_name']}...")
            try:
                img_bytes = translate_fal(image_url, prompt_text, aspect_ratio)
                with open(job["output_path"], "wb") as f:
                    f.write(img_bytes)
                print(f"  ✓ {job['output_path'].name}")
                results.append({"lang": job["lang_code"], "file": str(job["output_path"])})
            except Exception as e:
                print(f"  ✗ {job['lang_name']}: {e}")

    print(f"\n{'='*60}")
    print(f"  Done: {len(results)}/{len(jobs)} translations")
    if len(results) < len(jobs):
        failed = [j["lang_code"] for j in jobs if not any(r["lang"] == j["lang_code"] for r in results)]
        print(f"  Failed: {', '.join(failed)}")
    print(f"  Output: {output_dir}/")
    print(f"{'='*60}\n")

    if results:
        generate_gallery(output_dir, slug, results)


if __name__ == "__main__":
    main()
