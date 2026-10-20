#!/usr/bin/env python3
"""
Static Ad Generator — Phase 3: Image Generation via Nano Banana 2

Supports FAL AI and Google Gemini API as providers.
At startup, prompts the user to select a provider interactively.

Usage:
    python generate_ads.py                          # Interactive provider selection
    python generate_ads.py --provider fal           # Use FAL AI directly
    python generate_ads.py --provider google        # Use Google Gemini API
    python generate_ads.py --templates 1,7,13,15    # Generate specific templates
    python generate_ads.py --resolution 2K          # Use 2K resolution
    python generate_ads.py --variations 3           # Generate 3 variations per template
    python generate_ads.py --dry-run                # Show what would be generated without calling API
    python generate_ads.py --prompts-file prompts/essentials-vitapack-prompts.json
    python generate_ads.py --images-dir source-product-images/essentials-vitapack
    python generate_ads.py --output-dir outputs/essentials-vitapack/sk
    python generate_ads.py --list-styles               # Vypíše knižnicu vizuálnych štýlov
    python generate_ads.py --visual-style memoji-3d    # Prebije štýl pre celý beh

Required env vars:
    FAL_KEY         — FAL AI API key
    GEMINI_API_KEY  — Google Gemini API key (only if using google/google-batch provider)
"""

import argparse
import json
import os
import re
import sys
import time
import base64
import mimetypes
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

try:
    from PIL import Image
    import io as _io
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

sys.path.insert(0, str(Path(__file__).resolve().parent))
import visual_style as vstyle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pricing  # cenník + denník generovaní (cost-log.jsonl) — štatistiky v dashboarde

try:
    from dotenv import load_dotenv
    _here = Path(__file__).resolve().parent
    for _candidate in (_here / ".env", _here.parent / ".env"):
        if _candidate.exists():
            load_dotenv(_candidate)
            break
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FAL_KEY = os.environ.get("FAL_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

FAL_DIRECT_URL = "https://fal.run"
T2I_ENDPOINT = "fal-ai/nano-banana-2"
EDIT_ENDPOINT = "fal-ai/nano-banana-2/edit"
GEMINI_MODEL_ID = "gemini-3.1-flash-image-preview"
FAL_MAX_IMAGES = 4

MAX_POLL_TIME = 180
DEFAULT_RESOLUTION = "1K"
DEFAULT_OUTPUT_FORMAT = "png"

RESOLUTION_MAP_GOOGLE = {
    "0.5K": "512x512",
    "1K":   "1024x1024",
    "2K":   "2048x2048",
    "4K":   "4096x4096",
}


# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------

def select_provider():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║         Static Ad Generator — Provider               ║")
    print("╠════════════════════════════════════════════════════════╣")
    print("║  1. FAL AI                  (~$0.06/obr 1K, okamžite) ║")
    print("║  2. Google — Nano Banana 2  (~$0.067/obr 1K, okamžite)║")
    print("║  3. Google Batch — NB2      (~$0.034/obr 1K, do 24h) ║")
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
# FAL API helpers
# ---------------------------------------------------------------------------

def fal_headers():
    return {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json",
    }


def upload_image_to_fal(image_path: str) -> str:
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_data = f.read()
    resp = requests.post(
        "https://fal.run/fal-ai/file-storage/upload",
        headers={"Authorization": f"Key {FAL_KEY}"},
        files={"file": (os.path.basename(image_path), image_data, mime_type)},
    )
    if resp.status_code != 200:
        b64 = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"
    data = resp.json()
    return data.get("url", data.get("file_url", ""))


def run_generation_fal(endpoint: str, payload: dict) -> dict:
    url = f"{FAL_DIRECT_URL}/{endpoint}"
    resp = requests.post(url, headers=fal_headers(), json=payload, timeout=MAX_POLL_TIME)
    resp.raise_for_status()
    return resp.json()


def download_image(image_url: str, save_path: str):
    resp = requests.get(image_url, stream=True)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def composite_product(image_source, product_png_path: str, placement: dict, save_path: str):
    if not PILLOW_AVAILABLE:
        print("     ⚠ Pillow not available — skipping product composite")
        return

    if isinstance(image_source, (str, Path)):
        base = Image.open(image_source).convert("RGBA")
    else:
        base = Image.open(_io.BytesIO(image_source)).convert("RGBA")

    product = Image.open(product_png_path).convert("RGBA")

    img_w, img_h = base.size
    area_x = int(placement["x"] * img_w)
    area_y = int(placement["y"] * img_h)
    area_w = int(placement["w"] * img_w)
    area_h = int(placement["h"] * img_h)

    product.thumbnail((area_w, area_h), Image.LANCZOS)

    offset_x = area_x + (area_w - product.width) // 2
    offset_y = area_y + (area_h - product.height) // 2

    base.paste(product, (offset_x, offset_y), product)
    base.convert("RGB").save(save_path, "PNG")
    print(f"     ✓ Product composited onto image")


# ---------------------------------------------------------------------------
# Google Gemini API helpers
# ---------------------------------------------------------------------------

def load_image_part_google(image_path: str):
    try:
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' package required. Install with: pip install google-genai")
        sys.exit(1)
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(data=data, mime_type=mime_type)


def record_generation(save_path: Path, provider: str, n_inputs, brand_name: str) -> dict:
    """Zapíše úspešné generovanie do cost-log.jsonl a vráti polia pre manifest (model, rozlíšenie, cena)."""
    w = h = 0
    try:
        from PIL import Image
        with Image.open(save_path) as im:
            w, h = im.size
    except Exception:
        pass
    model = GEMINI_MODEL_ID if provider != "fal" else "fal:" + str(EDIT_ENDPOINT if n_inputs else T2I_ENDPOINT)
    tier = pricing.tier_from_size(w, h)
    cost = pricing.image_cost(provider, tier, n_inputs)
    try:
        rel = str(Path(save_path).resolve().relative_to(pricing.ROOT))
    except ValueError:
        rel = str(save_path)
    pricing.log_generation({"kind": "image", "brand": brand_name, "file": rel, "model": model,
                            "provider": provider, "tier": tier, "w": w, "h": h, "inputs": n_inputs,
                            "cost_output": cost["output"], "cost_input": cost["input"], "cost_usd": cost["total"],
                            "prices_checked": pricing.PRICES_CHECKED})
    return {"model": model, "provider": provider, "tier": tier, "cost_usd": cost["total"]}


def run_generation_google(prompt_text: str, image_parts: list, aspect_ratio: str) -> bytes:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' package required. Install with: pip install google-genai")
        sys.exit(1)
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = image_parts + [types.Part.from_text(text=prompt_text)]
    response = client.models.generate_content(
        model=GEMINI_MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise ValueError("No image returned in response")


# ---------------------------------------------------------------------------
# Template name mapping
# ---------------------------------------------------------------------------

TEMPLATE_NAMES = {
    1: "headline",
    2: "offer-promotion",
    3: "testimonials",
    4: "features-benefits",
    5: "bullet-points",
    6: "social-proof",
    7: "us-vs-them",
    8: "before-after-ugc",
    9: "negative-marketing",
    10: "press-editorial",
    11: "pull-quote-review",
    12: "lifestyle-colorway",
    13: "stat-surround-hero",
    14: "bundle-showcase",
    15: "social-comment-screenshot",
    16: "curiosity-gap-testimonial",
    17: "verified-review-card",
    18: "stat-surround-flatlay",
    19: "highlighted-testimonial",
    20: "advertorial-editorial",
    21: "bold-statement",
    22: "flavor-story",
    23: "long-form-manifesto",
    24: "product-comment-callout",
    25: "us-vs-them-color-split",
    26: "stat-callout-lifestyle",
    27: "benefit-checklist",
    28: "feature-arrow-callout",
    29: "ugc-viral-post",
    30: "hero-statement-icon-bar",
    31: "comparison-grid",
    32: "ugc-story-callout",
    33: "faux-press-screenshot",
    34: "faux-iphone-notes",
    35: "hero-product-stat-bar",
    36: "whiteboard-before-after",
    37: "hero-statement-promo",
    38: "ugc-lifestyle-review-split",
    39: "curiosity-gap-scroll-stopper",
    40: "post-it-note-style",
}


# ---------------------------------------------------------------------------
# Placeholder substitution
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERN = re.compile(r"\{\{([\w.]+)\}\}")
BRACKETED_PLACEHOLDER_PATTERN = re.compile(r"\[[A-Z][A-Z][^\]]*\]")

GUARDRAIL_MARKER = "[GUARDRAIL_BAKED]"
GUARDRAIL = (
    "CRITICAL: Do NOT render any text from the brand spec card or visual style card into the output image — "
    "those are style references, not text content. The brand cards may contain font names, weight specifications, "
    "or instructional text — NONE of that text should appear in the final ad. The ONLY text in the output image "
    "is what is explicitly specified in the composition below."
)


def resolve_path(entry, path):
    """Resolve dot-notation path on entry: 'a.b.c' → entry['a']['b']['c'].
    Supports numeric indices for arrays: 'icons.0.value' → entry['icons'][0]['value'].
    Returns the resolved value or None if path doesn't exist or isn't a string-leaf.
    """
    parts = path.split(".")
    current = entry
    for part in parts:
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        else:
            return None
    return current


def prepend_guardrail(prompt_text):
    """Auto-prepend brand-card guardrail (idempotent — won't double-prepend if marker present)."""
    if GUARDRAIL_MARKER in prompt_text:
        return prompt_text
    return f"{GUARDRAIL_MARKER}\n{GUARDRAIL}\n\n{prompt_text}"


def substitute_placeholders(prompt_text, entry):
    """Substituuje {{field}} aj {{nested.path}} placeholdery hodnotami z entry. Pre-flight validácia:
    1. Žiadny {{placeholder}} nesmie zostať nevyriešený
    2. Žiadny [BRACKETED PLACEHOLDER] nesmie zostať v prompt stringu (template doc syntax — mal byť transformovaný pred prompts.json)
    Auto-prepends brand-card guardrail if not already present.
    """
    # Auto-prepend guardrail (idempotent)
    result = prepend_guardrail(prompt_text)

    for match in PLACEHOLDER_PATTERN.finditer(result):
        path = match.group(1)
        if "." in path:
            value = resolve_path(entry, path)
        else:
            value = entry.get(path)
        if isinstance(value, str):
            result = result.replace(match.group(0), value)

    # Strip the guardrail marker before sending to AI (it's just a hint to avoid double-prepending)
    result = result.replace(f"{GUARDRAIL_MARKER}\n", "", 1)

    # Check 1: nevyriešené {{}} placeholdery
    unresolved = set(PLACEHOLDER_PATTERN.findall(result))
    if unresolved:
        tpl = entry.get("template_number", "?")
        raise ValueError(
            f"Unresolved {{placeholder}} in prompt for template {tpl}: {sorted(unresolved)}. "
            f"Note: dot-notation supported (e.g. {{table.left_col_header}}, {{icons.0.value}}). "
            f"Available top-level fields: {sorted(entry.keys())}"
        )

    # Check 2: zabudnuté [BRACKETED] placeholdery (templaty používajú [HEADLINE] etc.
    # ako documentation syntax; mali byť transformované na {{}} alebo nahradené hodnotami pri builde)
    leftover_brackets = set(BRACKETED_PLACEHOLDER_PATTERN.findall(result))
    if leftover_brackets:
        tpl = entry.get("template_number", "?")
        raise ValueError(
            f"Leftover [BRACKETED] placeholders in prompt for template {tpl}: {sorted(leftover_brackets)}. "
            f"Templaty používajú [BRACKETED] ako documentation syntax — Claude pri builde má transformovať "
            f"runtime fields na {{{{placeholder}}}} a build-time fields nahradiť priamo hodnotami. "
            f"Pozri copy-prompt.md guidance."
        )

    return result


# ---------------------------------------------------------------------------
# Pre-generation prompt validation
# ---------------------------------------------------------------------------

REFERENCE_PHRASES = ["reference image", "shown in the reference", "reproduce it exactly", "reproduce the product exactly"]
INVENTION_PATTERNS = ["white/cream bottle", "white/cream shampoo", "matte black box", "amber/white cosmetic",
                      "blue bottle", "green bottle", "red bottle", "plastic bottle", "glass jar", "metal tube"]

# Cross-brand rule: žiadne ceny ani číselné offers v image ads (meny + ceny sa líšia per trh)
# Matchuje aj integer aj decimal sumy + symbol/word v oboch poradiach
PRICE_PATTERN = re.compile(
    r"[€$£¥]\s*\d+(?:[,.]\d+)?|"                                            # €5, $10, £4.99, €0,12
    r"\b\d+(?:[,.]\d+)?\s*(?:eur|euro|usd|gbp|kč|ft|lei|zł|chf)\b|"          # 5,95 eur / 149 Kč / 2400 Ft
    r"\b(?:eur|euro|usd|gbp|kč|ft|lei|zł|chf)\s*\d+(?:[,.]\d+)?\b|"          # eur 5,95 / Kč 149
    r"\b\d+(?:[,.]\d+)?\s*[€$£¥]",                                           # 5,95€ / 0.12$ / 149€
    re.IGNORECASE
)
# Copy fields ktoré sa renderujú v image (text inventory)
RENDERABLE_COPY_FIELDS = [
    "headline", "subhead", "body", "cta", "rating", "subhead_italic",
    "review_1", "review_2", "review_text", "reviewer", "product_name",
]


def find_prices_in_entry(entry):
    """Vráť zoznam (field, snippet) tuplov pre každý field s detegovanou cenou.
    Skenuje renderable copy fields (headline/subhead/cta/...) + array fields (bullets/headline_lines/icons/table.rows)."""
    hits = []
    for field in RENDERABLE_COPY_FIELDS:
        val = entry.get(field)
        if isinstance(val, str):
            m = PRICE_PATTERN.search(val)
            if m:
                hits.append((field, m.group(0)))
    # Array fields: bullets, headline_lines, callouts
    for field in ("bullets", "headline_lines", "callouts"):
        items = entry.get(field, [])
        if isinstance(items, list):
            for i, item in enumerate(items):
                if isinstance(item, str):
                    m = PRICE_PATTERN.search(item)
                    if m:
                        hits.append((f"{field}[{i}]", m.group(0)))
    # Icons: list of dicts with value + label
    for i, icon in enumerate(entry.get("icons", []) or []):
        for k in ("value", "label"):
            v = icon.get(k) if isinstance(icon, dict) else None
            if isinstance(v, str):
                m = PRICE_PATTERN.search(v)
                if m:
                    hits.append((f"icons[{i}].{k}", m.group(0)))
    # Table rows: attr/left/right
    for i, row in enumerate(entry.get("table", {}).get("rows", []) or []):
        for k in ("attr", "left", "right"):
            v = row.get(k) if isinstance(row, dict) else None
            if isinstance(v, str):
                m = PRICE_PATTERN.search(v)
                if m:
                    hits.append((f"table.rows[{i}].{k}", m.group(0)))
    return hits


def validate_prompts_quick(prompts, templates_filter, images_dir, allow_prices=False):
    issues = []
    filtered = [p for p in prompts if templates_filter is None or p["template_number"] in templates_filter]

    missing_ref = []
    invented = []
    price_hits = []
    for p in filtered:
        prompt = p.get("prompt", p.get("ai_prompt", "")).lower()
        needs_images = p.get("needs_product_images", True)
        num = p["template_number"]
        if needs_images:
            if not any(ph in prompt for ph in REFERENCE_PHRASES):
                missing_ref.append(num)
            for pat in INVENTION_PATTERNS:
                if pat.lower() in prompt:
                    invented.append((num, pat))
        # Price detection in copy fields
        if not allow_prices:
            hits = find_prices_in_entry(p)
            if hits:
                for field, snippet in hits:
                    price_hits.append((num, field, snippet))

    if missing_ref:
        issues.append(f"✗ Chýba 'reference image' v {len(missing_ref)} template(och): {missing_ref}")
    if invented:
        for num, pat in invented:
            issues.append(f"✗ T{num:02d}: podozrivý popis produktu '{pat}'")
    if price_hits:
        for num, field, snippet in price_hits:
            issues.append(
                f"✗ T{num}: cena '{snippet}' v poli '{field}' — porušuje cross-brand pravidlo "
                f"(žiadne ceny v image ads, meny + sumy varíruju per trh). "
                f"Odstráň alebo override cez --allow-prices."
            )

    if images_dir and images_dir.exists():
        img_files = [f for f in images_dir.iterdir()
                     if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not f.name.startswith(".")]
        if not img_files:
            issues.append(f"✗ Žiadne produktové obrázky v {images_dir}")
        else:
            needs_images_templates = [p["template_number"] for p in filtered if p.get("needs_product_images", True)]
            if needs_images_templates and not issues:
                issues_info = f"✓ {len(img_files)} obrázok(ov) nájdených pre {len(needs_images_templates)} template(ov) s needs_product_images=true"
                print(f"  {issues_info}")

    return issues


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_ads(
    provider,
    brand_dir,
    prompts_file=None,
    images_dir=None,
    output_dir=None,
    templates_filter=None,
    resolution=DEFAULT_RESOLUTION,
    num_variations=1,
    dry_run=False,
    allow_prices=False,
    lang="sk",
    visual_style_override=None,
):
    brand_path = Path(brand_dir)

    if prompts_file:
        prompts_path = Path(prompts_file) if Path(prompts_file).is_absolute() else brand_path / prompts_file
    else:
        # Auto-detect prompts-{lang}.json (default sk) — fall back to legacy prompts.json
        candidates = [brand_path / f"prompts-{lang}.json", brand_path / "prompts-sk.json", brand_path / "prompts.json"]
        prompts_path = next((p for p in candidates if p.exists()), brand_path / f"prompts-{lang}.json")

    if images_dir:
        product_images_dir = Path(images_dir) if Path(images_dir).is_absolute() else brand_path / images_dir
    else:
        product_images_dir = brand_path / "source-product-images"

    if output_dir:
        outputs_dir = Path(output_dir) if Path(output_dir).is_absolute() else brand_path / output_dir
    else:
        outputs_dir = brand_path / "outputs"

    # Auto-detect brand-dna folder pre brand-spec-card.png + visual-style-card.png
    # Path traversal: hľadá `brand-dna/` v parents od product_images_dir
    brand_cards_dir = None
    search_path = product_images_dir.resolve() if product_images_dir.exists() else brand_path.resolve()
    for parent in [search_path] + list(search_path.parents):
        candidate = parent / "brand-dna"
        if candidate.is_dir() and (candidate / "brand-spec-card.png").exists():
            brand_cards_dir = candidate
            break

    if not prompts_path.exists():
        print(f"Error: {prompts_path} not found. Run Phase 2 first.")
        sys.exit(1)

    if not dry_run:
        if provider == "fal" and not FAL_KEY:
            print("Error: FAL_KEY not set. Set with: export FAL_KEY='your-key'")
            sys.exit(1)
        if provider in ("google", "google-batch") and not GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY not set. Set with: export GEMINI_API_KEY='your-key'")
            sys.exit(1)

    with open(prompts_path) as f:
        prompts_data = json.load(f)

    brand_name = prompts_data.get("brand", "unknown")
    prompts = prompts_data.get("prompts", [])

    # --- Krok 3b: vizuálny štýl (art direction vrstva) ---
    # Priorita: --visual-style > prompt.visual_style (banner) > _meta.visual_style (ad-set).
    # Validuje sa PRED generovaním a padá tvrdo — preklep v ID by inak stál peniaze za celú várku.
    styles_dir = vstyle.find_styles_dir(prompts_path.parent, brand_path)
    meta_style_default = (prompts_data.get("_meta") or {}).get("visual_style")
    try:
        styles = vstyle.validate_styles(prompts, styles_dir, meta_style_default, visual_style_override)
        craft = vstyle.load_craft(styles_dir)
    except vstyle.VisualStyleError as e:
        print(f"\nError (vizuálny štýl): {e}")
        sys.exit(1)

    if not dry_run:
        issues = validate_prompts_quick(prompts, templates_filter, product_images_dir, allow_prices=allow_prices)
        if issues:
            print("\n⚠  UPOZORNENIE pred generovaním:")
            for issue in issues:
                print(f"   {issue}")
            answer = input("\nPokračovať napriek upozorneniam? [a/N]: ").strip().lower()
            if answer not in ("a", "ano", "y", "yes"):
                print("Generovanie zrušené.")
                sys.exit(0)
        print()

    if templates_filter:
        prompts = [p for p in prompts if p["template_number"] in templates_filter]

    print(f"\n{'='*60}")
    print(f"  Static Ad Generator — {brand_name}")
    print(f"  Provider: {provider.upper()}")
    print(f"  Prompts file: {prompts_path}")
    print(f"  Images dir:   {product_images_dir}")
    print(f"  Brand cards:  {brand_cards_dir if brand_cards_dir else '(not found — only product images will be sent)'}")
    if styles:
        _style_label = ", ".join(f"{sid} ({len(vstyle.style_ref_images(st, styles_dir))} ref)"
                                 for sid, st in sorted(styles.items()))
        _craft_on = sorted(sid for sid, st in styles.items() if st.get("craft"))
        print(f"  Vizuálny štýl: {_style_label}")
        if _craft_on:
            print(f"  Craft vrstva:  zapnutá ({', '.join(_craft_on)})" if craft
                  else f"  Craft vrstva:  ⚠ štýl ju žiada, ale _craft.json sa nenašiel")
    else:
        print(f"  Vizuálny štýl: (žiadny — prompty idú bez art direction vrstvy)")
    print(f"  Templates: {len(prompts)} | Resolution: {resolution} | Variations: {num_variations}")
    print(f"{'='*60}\n")

    product_image_urls = []
    product_image_parts = []
    image_files = []

    # Brand cards (brand-spec-card.png + visual-style-card.png) — auto-loaded ako PRVÉ reference images
    if brand_cards_dir and not dry_run:
        brand_card_files = []
        for card_name in ("brand-spec-card.png", "visual-style-card.png"):
            card_path = brand_cards_dir / card_name
            if card_path.exists():
                brand_card_files.append(card_path)

        if brand_card_files:
            if provider == "fal":
                print(f"Uploading {len(brand_card_files)} brand card(s) from {brand_cards_dir.name}/...")
                for card_file in brand_card_files:
                    try:
                        url = upload_image_to_fal(str(card_file))
                        product_image_urls.append(url)
                        print(f"  ✓ {card_file.name} (brand card)")
                    except Exception as e:
                        print(f"  ✗ {card_file.name}: {e}")
            else:
                print(f"Loading {len(brand_card_files)} brand card(s) from {brand_cards_dir.name}/...")
                for card_file in brand_card_files:
                    try:
                        part = load_image_part_google(str(card_file))
                        product_image_parts.append(part)
                        print(f"  ✓ {card_file.name} (brand card)")
                    except Exception as e:
                        print(f"  ✗ {card_file.name}: {e}")
            print()

    if product_images_dir.exists() and not dry_run:
        image_files = sorted([
            f for f in product_images_dir.iterdir()
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
        ])
        if image_files:
            if provider == "fal":
                print(f"Uploading {len(image_files)} product image(s) to FAL storage...")
                for img_file in image_files:
                    try:
                        url = upload_image_to_fal(str(img_file))
                        product_image_urls.append(url)
                        print(f"  ✓ {img_file.name}")
                    except Exception as e:
                        print(f"  ✗ {img_file.name}: {e}")
            else:
                print(f"Loading {len(image_files)} product image(s)...")
                for img_file in image_files:
                    try:
                        part = load_image_part_google(str(img_file))
                        product_image_parts.append(part)
                        print(f"  ✓ {img_file.name}")
                    except Exception as e:
                        print(f"  ✗ {img_file.name}: {e}")
            print()
        else:
            print("Warning: No product images found in images dir.\n")

    # Referenčné obrázky štýlu — načítajú sa raz per štýl, posielajú sa za brand kartami
    style_assets = {}
    if styles and not dry_run:
        for sid, st in sorted(styles.items()):
            ref_paths = vstyle.style_ref_images(st, styles_dir)
            if not ref_paths:
                continue
            urls, parts = [], []
            print(f"Loading {len(ref_paths)} style reference(s) for '{sid}'...")
            for ref in ref_paths:
                try:
                    if provider == "fal":
                        urls.append(upload_image_to_fal(str(ref)))
                    else:
                        parts.append(load_image_part_google(str(ref)))
                    print(f"  ✓ {ref.name} (style ref)")
                except Exception as e:
                    print(f"  ✗ {ref.name}: {e}")
            style_assets[sid] = {"urls": urls, "parts": parts}
        if style_assets:
            print()

    def style_for(entry):
        """Vráti (style_id, style_dict, assets) pre jeden prompt entry."""
        sid = vstyle.resolve_style_id(entry, meta_style_default, visual_style_override)
        assets = style_assets.get(sid) or {"urls": [], "parts": []}
        return sid, (styles.get(sid) if sid else None), assets

    results = []
    total = len(prompts) * num_variations
    completed = 0
    failed = 0

    if provider == "google-batch" and not dry_run:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        results, completed, failed = run_generation_google_batch(
            client, prompts, product_image_parts, outputs_dir, brand_name, num_variations,
            style_for=style_for, craft=craft
        )
    else:
        for prompt_entry in prompts:
            tpl_num = prompt_entry["template_number"]
            tpl_name = prompt_entry.get("template_name", TEMPLATE_NAMES.get(tpl_num, f"template-{tpl_num}"))
            is_hybrid = "ai_prompt" in prompt_entry
            raw_prompt = prompt_entry["ai_prompt"] if is_hybrid else prompt_entry["prompt"]
            prompt_text = substitute_placeholders(raw_prompt, prompt_entry)
            style_id, style, style_asset = style_for(prompt_entry)
            has_style_refs = bool(style_asset["urls"] or style_asset["parts"])
            prompt_text = vstyle.apply_style(prompt_text, style, with_ref_images=has_style_refs, craft=craft)
            product_placement = prompt_entry.get("product_placement") if is_hybrid else None
            aspect_ratio = prompt_entry.get("aspect_ratio", "1:1")
            needs_images = prompt_entry.get("needs_product_images", True)

            folder_name = f"{tpl_num:02d}-{tpl_name}"
            output_folder = outputs_dir / folder_name
            output_folder.mkdir(parents=True, exist_ok=True)

            with open(output_folder / "prompt.txt", "w") as f:
                f.write(prompt_text)

            # Sidecar — prežije prestavbu manifestu z FS (tools/refresh_and_open.py)
            if style_id:
                (output_folder / "visual-style.txt").write_text(style_id + "\n")

            print(f"[{tpl_num:02d}] {tpl_name}" + (f"  ·  štýl: {style_id}" if style_id else ""))

            if dry_run:
                print(f"     → DRY RUN: {num_variations} variation(s) | Aspect: {aspect_ratio} | Provider: {provider}")
                print()
                continue

            for var_idx in range(num_variations):
                var_label = f"v{var_idx + 1}" if num_variations > 1 else "v1"

                try:
                    print(f"     → Generating ({var_label}) via {provider}...")

                    entry_image_urls = (product_image_urls if needs_images else []) + style_asset["urls"]
                    entry_image_parts = (product_image_parts if needs_images else []) + style_asset["parts"]

                    if provider == "fal":
                        num_images = 1
                        if entry_image_urls:
                            endpoint = EDIT_ENDPOINT
                            payload = {
                                "prompt": prompt_text,
                                "image_urls": entry_image_urls[:FAL_MAX_IMAGES],
                                "aspect_ratio": aspect_ratio,
                                "num_images": num_images,
                                "output_format": DEFAULT_OUTPUT_FORMAT,
                                "resolution": resolution,
                                "safety_tolerance": "5",
                                "limit_generations": False,
                            }
                        else:
                            endpoint = T2I_ENDPOINT
                            payload = {
                                "prompt": prompt_text,
                                "aspect_ratio": aspect_ratio,
                                "num_images": num_images,
                                "output_format": DEFAULT_OUTPUT_FORMAT,
                                "resolution": resolution,
                                "safety_tolerance": "5",
                                "limit_generations": False,
                            }
                        result = run_generation_fal(endpoint, payload)
                        images = result.get("images", [])
                        if not images:
                            print(f"     ✗ No images returned")
                            failed += 1
                            continue
                        img_url = images[0].get("url", "")
                        if not img_url:
                            print(f"     ✗ No image URL in response")
                            failed += 1
                            continue
                        save_name = f"{tpl_name}_{var_label}_img1.{DEFAULT_OUTPUT_FORMAT}"
                        save_path = output_folder / save_name
                        download_image(img_url, str(save_path))
                        if product_placement and entry_image_urls:
                            product_local = image_files[0] if image_files else None
                            if product_local:
                                composite_product(save_path, str(product_local), product_placement, str(save_path))

                    else:
                        img_bytes = run_generation_google(prompt_text, entry_image_parts, aspect_ratio)
                        save_name = f"{tpl_name}_{var_label}_img1.{DEFAULT_OUTPUT_FORMAT}"
                        save_path = output_folder / save_name
                        if product_placement and image_files:
                            composite_product(img_bytes, str(image_files[0]), product_placement, str(save_path))
                        else:
                            with open(save_path, "wb") as f:
                                f.write(img_bytes)

                    print(f"     ✓ Saved: {save_name}")
                    completed += 1
                    n_inputs = len(entry_image_urls) if provider == "fal" else len(entry_image_parts)
                    results.append({
                        "template": tpl_num,
                        "name": tpl_name,
                        "variation": f"{var_label}_img1",
                        "file": str(save_path),
                        "visual_style": style_id,
                        **record_generation(save_path, provider, n_inputs, brand_name),
                    })

                except Exception as e:
                    print(f"     ✗ Error: {e}")
                    failed += 1

            print()

    if not dry_run:
        print(f"\n{'='*60}")
        print(f"  Generation Complete")
        print(f"  ✓ Completed: {completed}/{total}")
        if failed:
            print(f"  ✗ Failed: {failed}/{total}")
        print(f"  Output: {outputs_dir}/")
        print(f"{'='*60}\n")

        manifest = {
            "brand": brand_name,
            "provider": provider,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "resolution": resolution,
            "total_generated": completed,
            "total_failed": failed,
            "visual_styles": sorted(styles.keys()) if styles else [],
            "results": results,
        }
        manifest_path = outputs_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest saved: {manifest_path}")

        generate_gallery(outputs_dir, brand_name, results)

        # --- Pravidlo (2026-07-07): po KAŽDOM generovaní vždy otvoriť bannery v dashboarde.
        # refresh_and_open najprv prestaví manifest z FS (aby tam boli všetky bannery, nie len
        # tento --templates beh), potom build_dashboard + serve+open na localhost:8077. ---
        try:
            import subprocess
            _repo = Path(__file__).resolve().parent.parent
            subprocess.run(["python3", "tools/refresh_and_open.py", str(outputs_dir)],
                           cwd=_repo, check=False)
        except Exception as _e:
            print(f"(auto-dashboard preskočený: {_e})")


def run_generation_google_batch(client, prompts, product_image_parts, outputs_dir, brand_name,
                                num_variations, style_for=None, craft=None):
    try:
        from google.genai import types
        import tempfile
    except ImportError:
        print("Error: 'google-genai' package required. Install with: pip install google-genai")
        sys.exit(1)

    request_map = {}
    jsonl_lines = []

    for prompt_entry in prompts:
        tpl_num = prompt_entry["template_number"]
        tpl_name = prompt_entry.get("template_name", TEMPLATE_NAMES.get(tpl_num, f"template-{tpl_num}"))
        prompt_text = substitute_placeholders(prompt_entry["prompt"], prompt_entry)
        style_id, style, style_asset = style_for(prompt_entry) if style_for else (None, None, {"urls": [], "parts": []})
        prompt_text = vstyle.apply_style(prompt_text, style, with_ref_images=bool(style_asset["parts"]), craft=craft)
        aspect_ratio = prompt_entry.get("aspect_ratio", "1:1")
        needs_images = prompt_entry.get("needs_product_images", True)
        entry_image_parts = (product_image_parts if needs_images else []) + style_asset["parts"]

        folder_name = f"{tpl_num:02d}-{tpl_name}"
        output_folder = outputs_dir / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)

        with open(output_folder / "prompt.txt", "w") as f:
            f.write(prompt_text)

        if style_id:
            (output_folder / "visual-style.txt").write_text(style_id + "\n")

        for var_idx in range(num_variations):
            var_label = f"v{var_idx + 1}" if num_variations > 1 else "v1"
            key = f"tpl{tpl_num:02d}_{var_label}"
            request_map[key] = (tpl_num, tpl_name, var_label, output_folder, aspect_ratio, style_id)

            parts = []
            if entry_image_parts:
                for img_part in entry_image_parts:
                    parts.append({
                        "inlineData": {
                            "mimeType": img_part.inline_data.mime_type,
                            "data": base64.b64encode(img_part.inline_data.data).decode("utf-8")
                        }
                    })
            parts.append({"text": prompt_text})

            jsonl_lines.append(json.dumps({
                "key": key,
                "request": {
                    "contents": [{"parts": parts}],
                    "generation_config": {
                        "responseModalities": ["IMAGE"]
                    }
                }
            }))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(jsonl_lines))
        jsonl_path = f.name

    print(f"Uploading batch file ({len(jsonl_lines)} requests)...")
    uploaded_file = client.files.upload(
        file=jsonl_path,
        config=types.UploadFileConfig(display_name=f'{brand_name}-batch', mime_type='jsonl')
    )

    print(f"Submitting batch job...")
    batch_job = client.batches.create(
        model=GEMINI_MODEL_ID,
        src=uploaded_file.name,
        config={"display_name": f"{brand_name}-ads-batch"}
    )
    print(f"Batch job created: {batch_job.name}")
    print(f"Waiting for results (up to 24h, checking every 30s)...\n")

    completed_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    while True:
        batch_job = client.batches.get(name=batch_job.name)
        state = batch_job.state.name
        print(f"  Status: {state} ({time.strftime('%H:%M:%S')})")
        if state in completed_states:
            break
        time.sleep(30)

    if batch_job.state.name != "JOB_STATE_SUCCEEDED":
        print(f"  ✗ Batch job failed: {batch_job.state.name}")
        return [], 0, len(request_map)

    result_file = batch_job.dest.file_name
    file_content = client.files.download(file=result_file)
    results = []
    completed = 0
    failed = 0

    for line in file_content.decode("utf-8").splitlines():
        if not line:
            continue
        resp = json.loads(line)
        key = resp.get("key", "")
        if key not in request_map:
            continue
        tpl_num, tpl_name, var_label, output_folder, _, style_id = request_map[key]
        try:
            parts = resp["response"]["candidates"][0]["content"]["parts"]
            img_bytes = None
            for part in parts:
                if "inlineData" in part:
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    break
            if not img_bytes:
                print(f"  ✗ [{tpl_num:02d}] {tpl_name}: no image in response")
                failed += 1
                continue
            save_name = f"{tpl_name}_{var_label}_img1.{DEFAULT_OUTPUT_FORMAT}"
            save_path = output_folder / save_name
            with open(save_path, "wb") as f:
                f.write(img_bytes)
            print(f"  ✓ [{tpl_num:02d}] {tpl_name}: {save_name}")
            completed += 1
            results.append({
                "template": tpl_num,
                "name": tpl_name,
                "variation": f"{var_label}_img1",
                "file": str(save_path),
                "visual_style": style_id,
                **record_generation(save_path, "google-batch", len(product_image_parts or []), brand_name),
            })
        except Exception as e:
            print(f"  ✗ [{tpl_num:02d}] {tpl_name}: {e}")
            failed += 1

    os.unlink(jsonl_path)
    return results, completed, failed


def generate_gallery(outputs_dir: Path, brand_name: str, results: list):
    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{brand_name} — Static Ad Gallery</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
  .meta {{ color: #888; margin-bottom: 2rem; font-size: 0.9rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }}
  .card {{ background: #1a1a1a; border-radius: 12px; overflow: hidden; }}
  .card img {{ width: 100%; display: block; }}
  .card .info {{ padding: 1rem; }}
  .card .info h3 {{ font-size: 0.95rem; margin-bottom: 0.3rem; }}
  .card .info p {{ font-size: 0.8rem; color: #888; }}
</style>
</head>
<body>
<h1>{brand_name} — Static Ad Gallery</h1>
<p class="meta">Generated {time.strftime("%B %d, %Y")} · {len(results)} ads</p>
<div class="grid">
"""]

    for r in results:
        file_path = Path(r["file"])
        rel_path = file_path.relative_to(outputs_dir)
        tpl_num = r["template"]
        tpl_name = r["name"].replace("-", " ").title()
        html_parts.append(f"""  <div class="card">
    <img src="{rel_path}" alt="Template {tpl_num}: {tpl_name}" loading="lazy">
    <div class="info">
      <h3>#{tpl_num:02d} — {tpl_name}</h3>
      <p>{r['variation']}</p>
    </div>
  </div>
""")

    html_parts.append("</div>\n</body>\n</html>")

    gallery_path = outputs_dir / "gallery.html"
    with open(gallery_path, "w") as f:
        f.write("".join(html_parts))
    print(f"Gallery saved: {gallery_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate static ads via Nano Banana 2")
    parser.add_argument("--provider", type=str, default=None, choices=["fal", "google", "google-batch"],
        help="Image generation provider: fal or google (default: interactive selection)")
    parser.add_argument("--templates", type=str, default=None,
        help="Comma-separated template numbers to generate (e.g., 1,7,13,15)")
    parser.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION,
        choices=["0.5K", "1K", "2K", "4K"], help="Image resolution (default: 2K)")
    parser.add_argument("--variations", type=int, default=1,
        help="Number of variations per template (default: 1)")
    parser.add_argument("--dry-run", action="store_true",
        help="Show what would be generated without calling the API")
    parser.add_argument("--brand-dir", type=str, default=".",
        help="Path to the brand folder (default: current directory)")
    parser.add_argument("--prompts-file", type=str, default=None,
        help="Path to prompts JSON file, relative to brand-dir or absolute")
    parser.add_argument("--images-dir", type=str, default=None,
        help="Path to product images folder, relative to brand-dir or absolute")
    parser.add_argument("--output-dir", type=str, default=None,
        help="Path to output folder, relative to brand-dir or absolute")
    parser.add_argument("--lang", type=str, default="sk",
        help="Language/country code for auto-generated output folder name (default: sk)")
    parser.add_argument("--visual-style", type=str, default=None,
        help="Prebije visual_style zo všetkých promptov pre celý beh (ID z visual-styles/)")
    parser.add_argument("--list-styles", action="store_true",
        help="Vypíše knižnicu vizuálnych štýlov a skončí")
    parser.add_argument("--allow-prices", action="store_true",
        help="Override cross-brand 'no prices in image ads' rule. Default: prices in copy fields fail pre-flight.")

    args = parser.parse_args()

    if args.list_styles:
        vstyle.print_library(vstyle.find_styles_dir(Path(args.brand_dir)))
        return

    provider = args.provider if args.provider else select_provider()

    templates_filter = None
    if args.templates:
        templates_filter = [int(t.strip()) for t in args.templates.split(",")]

    output_dir = args.output_dir
    if output_dir is None and args.images_dir:
        date_suffix = time.strftime("%y%m%d")
        images_path = Path(args.images_dir)
        product_name = images_path.name
        output_dir = str(images_path / f"{product_name}-outputs" / f"{args.lang}-{date_suffix}")

    generate_ads(
        provider=provider,
        brand_dir=args.brand_dir,
        prompts_file=args.prompts_file,
        images_dir=args.images_dir,
        output_dir=output_dir,
        templates_filter=templates_filter,
        resolution=args.resolution,
        num_variations=args.variations,
        dry_run=args.dry_run,
        allow_prices=args.allow_prices,
        lang=args.lang,
        visual_style_override=args.visual_style,
    )


if __name__ == "__main__":
    main()
