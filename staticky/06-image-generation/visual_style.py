#!/usr/bin/env python3
"""
Visual Style layer — krok 3b ad-generator pipeline.

Vizuálny štýl = pomenovaná, znovupoužiteľná art direction vrstva medzi brandom
(brand-spec-card + visual-style-card) a copy (prompts-<lang>.json).

Štýl NEMENÍ copy, layout ani identitu produktu — mení len rendering, svetlo,
pozadie, farebné spracovanie a celkový look.

Knižnica: `ad-generator/visual-styles/<id>.json`
Použitie v prompts JSON:

    {
      "_meta": { "visual_style": "memoji-3d" },       # default pre celý ad-set
      "prompts": [
        { "template_number": 1, "visual_style": "typographic-flat" }   # override na banner
      ]
    }

CLI override pre celý beh: `--visual-style <id>`, výpis knižnice: `--list-styles`.
"""

import json
from pathlib import Path

STYLES_DIRNAME = "visual-styles"
CRAFT_FILENAME = "_craft.json"   # zdieľaná vrstva remesla, opt-in cez "craft": true
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
MAX_REF_IMAGES = 2

# Hlavička bloku, ktorý sa vkladá do promptu
STYLE_HEADER = "--- VISUAL STYLE: {name} (art direction layer) ---"
CRAFT_HEADER = "--- CRAFT (typographic and layout discipline) ---"

STYLE_CONTRACT = (
    "This art direction governs rendering, lighting, background, texture and colour treatment "
    "of the entire image. Where it conflicts with generic wording above, follow this art direction. "
    "It does NOT change any copy, wording, layout positions, safe zones or product identity "
    "specified above — those stay exactly as written."
)

STYLE_REF_GUARDRAIL = (
    "The image(s) marked STYLE REFERENCE are supplied for look and feel ONLY. Copy their rendering, "
    "palette, lighting and mood. NEVER copy their text, headlines, logos, layout positions or products — "
    "the only text and products in the output are the ones specified above."
)


class VisualStyleError(Exception):
    """Neznámy štýl, chýbajúci súbor alebo rozbitá schéma — tvrdý fail pred generovaním."""


# ---------------------------------------------------------------------------
# Lokalizácia knižnice
# ---------------------------------------------------------------------------

def find_styles_dir(*start_paths):
    """Nájde `visual-styles/` prechodom nahor od zadaných ciest (aj od tohto skriptu)."""
    candidates = list(start_paths) + [Path(__file__).resolve().parent]
    for start in candidates:
        if not start:
            continue
        p = Path(start).resolve()
        for parent in [p] + list(p.parents):
            candidate = parent / STYLES_DIRNAME
            if candidate.is_dir():
                return candidate
    return None


def available_styles(styles_dir):
    """Zoznam ID štýlov v knižnici (bez súborov začínajúcich podčiarkovníkom)."""
    if not styles_dir or not Path(styles_dir).is_dir():
        return []
    return sorted(
        f.stem for f in Path(styles_dir).glob("*.json")
        if not f.name.startswith("_")
    )


# ---------------------------------------------------------------------------
# Načítanie a validácia
# ---------------------------------------------------------------------------

def load_style(style_id, styles_dir):
    """Načíta definíciu štýlu. Neznáme ID → VisualStyleError so zoznamom dostupných."""
    if not styles_dir:
        raise VisualStyleError(
            f"Prompts žiadajú visual_style '{style_id}', ale priečinok '{STYLES_DIRNAME}/' sa nenašiel."
        )

    path = Path(styles_dir) / f"{style_id}.json"
    if not path.exists():
        raise VisualStyleError(
            f"Neznámy visual_style '{style_id}'. Dostupné: {', '.join(available_styles(styles_dir)) or '(knižnica je prázdna)'}"
        )

    try:
        with open(path) as f:
            style = json.load(f)
    except json.JSONDecodeError as e:
        raise VisualStyleError(f"Rozbitý JSON v {path.name}: {e}")

    if not style.get("prompt_block"):
        raise VisualStyleError(f"Štýl '{style_id}' nemá povinné pole 'prompt_block' ({path.name}).")

    style.setdefault("id", style_id)
    style.setdefault("name", style_id)
    return style


def load_craft(styles_dir):
    """Načíta zdieľanú craft vrstvu. Chýbajúci súbor = craft sa ticho preskočí."""
    if not styles_dir:
        return None
    path = Path(styles_dir) / CRAFT_FILENAME
    if not path.exists():
        return None
    try:
        with open(path) as f:
            craft = json.load(f)
    except json.JSONDecodeError as e:
        raise VisualStyleError(f"Rozbitý JSON v {CRAFT_FILENAME}: {e}")
    if not craft.get("prompt_block"):
        raise VisualStyleError(f"{CRAFT_FILENAME} nemá povinné pole 'prompt_block'.")
    return craft


def build_craft_block(craft):
    """Textový blok remeselnej disciplíny — pripája sa za blok štýlu."""
    lines = [CRAFT_HEADER, craft["prompt_block"].strip()]
    never = craft.get("never") or []
    if never:
        lines.append("NEVER: " + "; ".join(n.strip().rstrip(".") for n in never) + ".")
    return "\n".join(lines)


def resolve_style_id(entry, meta_default=None, cli_override=None):
    """Priorita: --visual-style (CLI) > entry.visual_style (banner) > _meta.visual_style (ad-set)."""
    if cli_override:
        return cli_override
    entry_style = (entry or {}).get("visual_style")
    if entry_style:
        return entry_style
    return meta_default


def collect_style_ids(prompts, meta_default=None, cli_override=None):
    """Množina všetkých štýlov použitých v tejto várke — na pre-flight validáciu."""
    ids = set()
    for entry in prompts:
        sid = resolve_style_id(entry, meta_default, cli_override)
        if sid:
            ids.add(sid)
    return ids


def validate_styles(prompts, styles_dir, meta_default=None, cli_override=None):
    """Načíta a overí všetky štýly várky PRED generovaním. Vracia mapu {id: style}.
    Zámerne padá tvrdo — preklep v ID by inak stál peniaze za celú várku."""
    loaded = {}
    for sid in sorted(collect_style_ids(prompts, meta_default, cli_override)):
        loaded[sid] = load_style(sid, styles_dir)
    return loaded


# ---------------------------------------------------------------------------
# Referenčné obrázky štýlu
# ---------------------------------------------------------------------------

def style_ref_images(style, styles_dir, limit=MAX_REF_IMAGES):
    """Cesty k referenčným obrázkom štýlu. `ref_images` môže obsahovať súbor aj priečinok,
    relatívne k `visual-styles/`. Ticho preskočí, čo neexistuje (referencia je voliteľná)."""
    refs = style.get("ref_images") or []
    if not refs or not styles_dir:
        return []

    base = Path(styles_dir)
    found = []
    for ref in refs:
        p = Path(ref)
        if not p.is_absolute():
            p = (base / ref).resolve()
        if p.is_dir():
            found.extend(sorted(f for f in p.iterdir() if f.suffix.lower() in IMAGE_SUFFIXES))
        elif p.exists() and p.suffix.lower() in IMAGE_SUFFIXES:
            found.append(p)

    return found[:limit]


# ---------------------------------------------------------------------------
# Injekcia do promptu
# ---------------------------------------------------------------------------

def build_style_block(style, with_ref_images=False):
    """Zostaví textový blok art direction, ktorý sa pripája na koniec promptu."""
    lines = [STYLE_HEADER.format(name=style.get("name", style["id"]))]
    lines.append(style["prompt_block"].strip())

    never = style.get("never") or []
    if never:
        lines.append("NEVER in this style: " + "; ".join(n.strip().rstrip(".") for n in never) + ".")

    lines.append(STYLE_CONTRACT)
    if with_ref_images:
        lines.append(STYLE_REF_GUARDRAIL)

    return "\n".join(lines)


def apply_style(prompt_text, style, with_ref_images=False, craft=None):
    """Pripojí blok štýlu na koniec promptu, a za neho craft vrstvu, ak ju štýl zapína
    (`"craft": true`). Idempotentné — už vložený blok nepridá druhýkrát."""
    if not style:
        return prompt_text
    header = STYLE_HEADER.format(name=style.get("name", style["id"]))
    if header in prompt_text:
        return prompt_text

    result = f"{prompt_text.rstrip()}\n\n{build_style_block(style, with_ref_images)}\n"

    if style.get("craft") and craft and CRAFT_HEADER not in result:
        result = f"{result.rstrip()}\n\n{build_craft_block(craft)}\n"

    return result


# ---------------------------------------------------------------------------
# Výpis knižnice (CLI --list-styles)
# ---------------------------------------------------------------------------

def print_library(styles_dir):
    ids = available_styles(styles_dir)
    if not ids:
        print(f"Knižnica štýlov je prázdna alebo sa nenašla ({styles_dir}).")
        return
    print(f"\nVizuálne štýly — {styles_dir}\n")
    for sid in ids:
        try:
            style = load_style(sid, styles_dir)
        except VisualStyleError as e:
            print(f"  ✗ {sid}: {e}")
            continue
        refs = style_ref_images(style, styles_dir)
        ar = ", ".join((style.get("works_with") or {}).get("aspect_ratios") or ["—"])
        print(f"  {sid:<22} {style.get('name','')}")
        print(f"  {'':<22} {style.get('summary','').strip()}")
        print(f"  {'':<22} AR: {ar} | ref obrázky: {len(refs)} | craft: {'áno' if style.get('craft') else 'nie'}")
        if style.get("when_to_use"):
            print(f"  {'':<22} Kedy: {style['when_to_use'].strip()}")
        print()
