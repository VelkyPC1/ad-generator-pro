#!/usr/bin/env python3
"""
Multi-brand Dashboard v2 — zlúčená galéria pre všetky brandy v ad-generatore.

Auto-discoveruje cez:
    brands/*/products/*/product-image-ads/*/outputs*/manifest.json

Novinky v2 (2026-08-19):
- KOLEKCIE: ten istý motív vo viacerých formátoch (1:1 / 4:5 / 9:16 / 1.91:1)
  = jedna karta s prepínaním formátov (formát sa číta z reálnych rozmerov PNG)
- Opravený filter Krajina — whitelist reálnych krajín, zvyšok názvu outputs
  priečinka je "variant" štítok (v3, ugc, paleta...), nie krajina
- Kaskádové filtre Brand → Produkt → Ad-set + filter Formát
- Flagy sa ukladajú cez server API priamo do flagged.json (žiadny localStorage
  export/import tanec) — vyžaduje tools/serve_dashboard.py na :8077
- Poznámka k flagu ("čo opraviť") — uloží sa do flagged.json
- Bannery sa v gride neorezávajú (object-fit: contain)

Output: ad-generator/dashboard.html

Použitie:
    python3 tools/build_dashboard.py
    python3 tools/build_dashboard.py --output custom-dashboard.html
"""

import argparse
import hashlib
import json
import os
import shutil
import re
import struct
import sys
import html as html_lib
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent  # ad-generator/

# Video helpery (ffprobe/ffmpeg) — zdieľané s tools/make_video_poster.py
sys.path.insert(0, str(SCRIPT_DIR))
import pricing
import stats_tab
import footage_tab
from template_sketches import CATEGORIES as TPL_CATEGORIES, CATEGORY_OF as TPL_CATEGORY_OF, \
    CSS as SKETCH_CSS, sketch_html, sketch_ratio
try:
    from make_video_poster import probe as probe_video, make_poster
except Exception:  # ffmpeg helper nie je povinný — dashboard sa postaví aj bez videí
    def probe_video(_path):
        return {}

    def make_poster(*_a, **_kw):
        return False

COUNTRY_TOKENS = {"sk", "cz", "hu", "ro", "pl", "de", "it", "en"}
LANG_LABELS = {"sk": "🇸🇰 SK", "cz": "🇨🇿 CZ", "hu": "🇭🇺 HU", "ro": "🇷🇴 RO",
               "pl": "🇵🇱 PL", "de": "🇩🇪 DE", "it": "🇮🇹 IT", "en": "🇬🇧 EN"}
# Tokeny označujúce formát v názvoch priečinkov/šablón (nie krajinu ani variant)
FORMAT_TOKEN_RE = re.compile(r"^(1x1|4x5|45|9x16|916|portrait|landscape|\d{3,4}x\d{3,4})$", re.I)
FORMAT_ORDER = {"1:1": 0, "4:5": 1, "16:9": 2, "1.91:1": 3, "9:16": 4}


def png_size(path: Path):
    """Prečíta rozmery obrázka (PNG aj JPEG — generátor ukladá JPEG s príponou .png)."""
    try:
        with open(path, "rb") as f:
            head = f.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                return (w, h) if w and h else None
            if head[:2] == b"\xff\xd8":  # JPEG — nájdi SOF marker
                f.seek(2)
                while True:
                    b1 = f.read(1)
                    if not b1:
                        return None
                    if b1 != b"\xff":
                        continue
                    marker = f.read(1)
                    if not marker or marker == b"\xff":
                        continue
                    m = marker[0]
                    if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                        continue
                    seg = f.read(2)
                    if len(seg) < 2:
                        return None
                    seg_len = struct.unpack(">H", seg)[0]
                    if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):  # SOF
                        data = f.read(5)
                        h, w = struct.unpack(">HH", data[1:5])
                        return (w, h) if w and h else None
                    f.seek(seg_len - 2, 1)
        return None
    except Exception:
        return None


HASH_CACHE_PATH = SCRIPT_DIR / ".sha256-cache.json"
_HASH_CACHE = None


def file_sha256(path: Path) -> str:
    """SHA-256 súboru, cache podľa (veľkosť, mtime) — rebuild neprečíta všetko nanovo.

    QA hodnotenie je viazané na tento hash: keď sa banner pregeneruje pod rovnakou
    cestou, hash sa zmení a dashboard ho označí „Prehodnotiť".
    """
    global _HASH_CACHE
    if _HASH_CACHE is None:
        try:
            _HASH_CACHE = json.loads(HASH_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            _HASH_CACHE = {}
    try:
        st = path.stat()
    except OSError:
        return ""
    key = str(path)
    stamp = [st.st_size, st.st_mtime_ns]
    hit = _HASH_CACHE.get(key)
    if hit and hit[:2] == stamp:
        return hit[2]
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    _HASH_CACHE[key] = stamp + [digest.hexdigest()]
    return digest.hexdigest()


def save_hash_cache():
    if _HASH_CACHE is None:
        return
    # súbory, ktoré už neexistujú, z cache vyhoď
    live = {k: v for k, v in _HASH_CACHE.items() if Path(k).exists()}
    tmp = HASH_CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(live), encoding="utf-8")
    tmp.rename(HASH_CACHE_PATH)


def classify_format(w: int, h: int) -> str:
    r = w / h
    for label, target, tol in (("1:1", 1.0, 0.04), ("4:5", 0.8, 0.04),
                               ("9:16", 9 / 16, 0.04), ("1.91:1", 1.91, 0.12),
                               ("16:9", 16 / 9, 0.08)):
        if abs(r - target) <= tol:
            return label
    return f"{w}×{h}"


def format_from_tokens(*names) -> str:
    """Fallback keď PNG nevieme prečítať — uhádni formát z tokenov v názvoch."""
    for name in names:
        for t in str(name).split("-"):
            tl = t.lower()
            if tl in ("9x16", "916"):
                return "9:16"
            if tl in ("4x5", "45"):
                return "4:5"
            m = re.match(r"^(\d{3,4})x(\d{3,4})$", tl)
            if m:
                return classify_format(int(m.group(1)), int(m.group(2)))
    return "1:1"


def parse_outputs_name(odir: str):
    """outputs-cz-9x16 → (lang='cz', variant=''); outputs-v3-9x16 → ('sk', 'v3')."""
    suffix = odir[len("outputs"):].strip("-")
    tokens = [t for t in suffix.split("-") if t]
    lang, variant_tokens, lang_found = "sk", [], False
    for t in tokens:
        tl = t.lower()
        if not lang_found and tl in COUNTRY_TOKENS:
            lang, lang_found = tl, True
            continue
        if FORMAT_TOKEN_RE.match(t):
            continue
        variant_tokens.append(t)
    return lang, "-".join(variant_tokens)


ENUM_TOKEN_RE = re.compile(r"^(k\d+[a-z]?|\d+)$", re.I)


def motif_key(template_name: str, variant: str) -> frozenset:
    """Identita motívu naprieč formátmi.

    Množina tokenov názvu šablóny bez formátových tokenov (1x1/9x16/960x1200/portrait…)
    a bez číslovania na okrajoch, zjednotená s tokenmi variantu priečinka — variant
    (black/uni/v3…) je súčasť identity, inak by sa zlúčili rôzne farebné verzie.
    """
    toks = [t for t in re.split(r"[-_]+", template_name) if t]
    toks = [t for t in toks if not FORMAT_TOKEN_RE.match(t)]
    while toks and ENUM_TOKEN_RE.match(toks[0]):
        toks.pop(0)
    while toks and ENUM_TOKEN_RE.match(toks[-1]):
        toks.pop()
    var_toks = [t for t in re.split(r"[-_]+", variant) if t and not FORMAT_TOKEN_RE.match(t)]
    key = frozenset(t.lower() for t in toks) | frozenset(t.lower() for t in var_toks)
    return key or frozenset(re.split(r"[-_]+", template_name.lower()))


def merge_subset_groups(groups: dict) -> dict:
    """Zlúči skupiny, kde je jeden kľúč podmnožinou druhého (napr. `916-B5-kupon`
    vs `B5-kupon-4x5`, `persona-marta-9x16` vs `persona-marta-hostia`).

    Poistky proti zlepeniu rôznych kreatív: kľúče sa smú líšiť najviac 2 tokenmi,
    formáty oboch skupín musia byť disjunktné a zlúčenie sa odmietne, ak by v
    kolekcii vznikol duplicitný formát (to bráni aj reťazovému zlepovaniu).
    """
    by_scope = {}
    for (brand, product, lang, key), members in groups.items():
        by_scope.setdefault((brand, product, lang), []).append((key, members))

    parent = {k: k for k in groups}
    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    merged_formats = {k: [m["format"] for m in ms] for k, ms in groups.items()}

    candidates = []
    for scope, entries in by_scope.items():
        for i, (ka, msa) in enumerate(entries):
            for kb, msb in entries[i + 1:]:
                if not (ka < kb or kb < ka):
                    continue
                diff = ka ^ kb
                if len(diff) > 2:
                    continue
                fa = {m["format"] for m in msa}
                fb = {m["format"] for m in msb}
                if fa & fb:
                    continue
                same_tpl = 1 if {m["template_num"] for m in msa} & {m["template_num"] for m in msb} else 0
                gap = abs(max(m["mtime"] for m in msa) - max(m["mtime"] for m in msb))
                candidates.append((len(diff), -same_tpl, gap, scope + (ka,), scope + (kb,)))

    for _, _, _, ga, gb in sorted(candidates, key=lambda c: c[:3]):
        ra, rb = find(ga), find(gb)
        if ra == rb:
            continue
        combined = merged_formats[ra] + merged_formats[rb]
        if len(combined) != len(set(combined)):
            continue  # duplicitný formát → nie je to formátová dvojica
        parent[rb] = ra
        merged_formats[ra] = combined

    out = {}
    for k, members in groups.items():
        out.setdefault(find(k), []).extend(members)
    return out


# ---------------------------------------------------------------------------
# Rodokmeň kreatívy — z čoho vznikla (víťaz minulého týždňa + dôvod)
# ---------------------------------------------------------------------------

WINNER_REFS_DIR = ROOT / "winner-refs"
_WINNER_INDEX = None


def winner_index() -> dict:
    """winner-refs/index.json → {"HU/slug": {ad_name, roas, spend, file, ...}}."""
    global _WINNER_INDEX
    if _WINNER_INDEX is None:
        path = WINNER_REFS_DIR / "index.json"
        try:
            _WINNER_INDEX = json.loads(path.read_text(encoding="utf-8")).get("winners", {})
        except Exception:
            _WINNER_INDEX = {}
    return _WINNER_INDEX


def build_lineage(meta: dict) -> dict:
    """`_meta.lineage` z prompts/script JSON → obohatené o metriky a náhľady víťazov."""
    lin = (meta or {}).get("lineage") or {}
    if not lin:
        return {}

    winners = []
    for key in lin.get("winners") or []:
        w = winner_index().get(key)
        if not w:
            continue
        ref = ROOT / w.get("file", "")
        winners.append({
            "key": key,
            "name": w.get("ad_name", key),
            "img": w.get("file", "") if ref.exists() else "",
            "roas": w.get("roas", 0),
            "spend": w.get("spend", 0),
            "purchases": w.get("purchases", 0),
            "thumbstop": w.get("thumbstop", 0),
            "ctr": w.get("ctr", 0),
            "kind": w.get("kind", "image"),
            "state": w.get("spend_state", ""),
        })

    if not winners and not lin.get("why"):
        return {}
    return {
        "type": lin.get("type", "ITERATION"),
        "window": lin.get("window", ""),
        "driver": lin.get("driver", ""),   # čo vyhralo u predlohy (produkt/ponuka/dôvera)
        "offer": lin.get("offer", ""),     # akú ponuku nesie táto kreatíva
        "why": lin.get("why", ""),
        "changed": lin.get("changed", ""),
        "winners": winners,
    }


def load_brand_colors(brand_dir: Path) -> dict:
    brief_path = brand_dir / "brand-dna" / "brand-research-brief.json"
    primary = "#4F52F7"
    if brief_path.exists():
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
            primary = brief.get("visual_system", {}).get("primary_color_hex", primary)
        except Exception:
            pass
    return {"primary": primary}


def relpath_from_root(file_str: str) -> str:
    p = Path(file_str)
    if p.is_absolute():
        try:
            return str(p.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")
    return str(p).replace("\\", "/")


def banner_id(brand, product, adset, lang, tpl_num, variation) -> str:
    var_clean = str(variation).replace("_", "-")
    return f"{brand}__{product}__{adset}__{lang}__t{tpl_num}__{var_clean}"


def discover_all_brands() -> list:
    items = []
    brands_dir = ROOT / "brands"
    if not brands_dir.exists():
        return items

    for manifest_path in sorted(brands_dir.glob("*/products/*/product-image-ads/*/outputs*/manifest.json")):
        outputs_dir = manifest_path.parent
        ad_set_dir = outputs_dir.parent
        product_dir = ad_set_dir.parent.parent
        brand_dir = product_dir.parent.parent

        lang, variant = parse_outputs_name(outputs_dir.name)

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        prompts_path = ad_set_dir / f"prompts-{lang}.json"
        if not prompts_path.exists():
            prompts_path = ad_set_dir / "prompts-sk.json"
        prompts_data = {}
        if prompts_path.exists():
            try:
                prompts_data = json.loads(prompts_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        items.append({
            "brand": brand_dir.name,
            "brand_dir": brand_dir,
            "product": product_dir.name,
            "adset": ad_set_dir.name,
            "outputs": outputs_dir.name,
            "lang": lang,
            "variant": variant,
            "ad_set_dir": ad_set_dir,
            "manifest": manifest,
            "prompts": prompts_data,
            "colors": load_brand_colors(brand_dir),
        })

    return items


def build_members(items: list):
    """Manifest results → ploché member dicty + zoskupenie do sekcií a kolekcií."""
    sections = {}  # key → {"meta":..., "collections": {motif: [members]}}
    groups = {}    # (brand, product, lang, motif_key) → [member] — naprieč sekciami
    used_ids = set()
    total_failed = 0

    for ad_set in items:
        total_failed += ad_set["manifest"].get("total_failed", 0)
        prompts_by_name = {p.get("template_name", ""): p for p in ad_set["prompts"].get("prompts", [])}
        lineage = build_lineage(ad_set["prompts"].get("_meta", {}))

        skey = (ad_set["brand"], ad_set["product"], ad_set["adset"], ad_set["lang"], ad_set["variant"])
        if skey not in sections:
            sections[skey] = {
                "brand": ad_set["brand"], "product": ad_set["product"],
                "adset": ad_set["adset"], "lang": ad_set["lang"],
                "variant": ad_set["variant"], "primary": ad_set["colors"]["primary"],
                "outputs_names": [], "mtime": 0, "collections": {},
            }
        section = sections[skey]
        section["outputs_names"].append(ad_set["outputs"])

        for result in ad_set["manifest"].get("results", []):
            tpl_name = result.get("name", "")
            tpl_num = result.get("template", 0)
            variation = result.get("variation", "")
            prompt_def = prompts_by_name.get(tpl_name, {})
            headline = (prompt_def.get("headline") or "").replace("\n", " / ").strip()
            ad_id = prompt_def.get("ad_id") or tpl_name

            rel_str = relpath_from_root(result.get("file", ""))
            abs_path = ROOT / rel_str
            exists = abs_path.exists()
            size_kb = abs_path.stat().st_size / 1024 if exists else 0
            mtime = int(abs_path.stat().st_mtime) if exists else 0

            dims = png_size(abs_path) if exists else None
            if dims:
                fmt = classify_format(*dims)
                w, h = dims
            else:
                fmt = format_from_tokens(tpl_name, ad_set["outputs"])
                w = h = 0

            bid = banner_id(ad_set["brand"], ad_set["product"], ad_set["adset"],
                            ad_set["lang"], tpl_num, variation)
            if bid in used_ids:
                bid = f"{bid}__{fmt.replace(':', 'x')}"
            used_ids.add(bid)

            member = {
                "id": bid,
                "brand": ad_set["brand"],
                "country": ad_set["lang"].upper(),
                "product": ad_set["product"],
                "adset": ad_set["adset"],
                "outputs": ad_set["outputs"],
                "variant_label": ad_set["variant"],
                "ad_id": ad_id,
                "template_name": tpl_name,
                "template_num": tpl_num,
                "variation": variation,
                "file": rel_str,
                "img_url": f"{rel_str}?v={mtime}",
                "headline": headline,
                "format": fmt,
                "w": w, "h": h,
                "size_kb": round(size_kb, 1),
                "mtime": mtime,
                "sha": file_sha256(abs_path) if exists else "",
                "style": result.get("visual_style") or "",
                "provider": result.get("provider") or ad_set["manifest"].get("provider") or "google",
                "tier": result.get("tier") or (pricing.tier_from_size(w, h) if w else "1K"),
                "cost_usd": result.get("cost_usd"),
                "lineage": lineage,
            }
            section["mtime"] = max(section["mtime"], mtime)
            member["_skey"] = skey
            groups.setdefault(
                (ad_set["brand"], ad_set["product"], ad_set["lang"],
                 motif_key(tpl_name, ad_set["variant"])), []
            ).append(member)

    # Fáza 2: zlúč skupiny, kde je jeden kľúč podmnožinou druhého
    groups = merge_subset_groups(groups)

    # Kolekcia patrí do sekcie svojho najnovšieho člena
    for gkey, members in groups.items():
        members.sort(key=lambda m: (FORMAT_ORDER.get(m["format"], 9), -m["mtime"]))
        newest = max(members, key=lambda m: m["mtime"])
        label = "-".join(sorted(gkey[3])) if isinstance(gkey[3], frozenset) else str(gkey[3])
        # rozlíš členov s rovnakým formátom (regenerácie) podľa variantu / ad-setu
        fmt_counts, fmt_sources = {}, {}
        for m in members:
            fmt_counts[m["format"]] = fmt_counts.get(m["format"], 0) + 1
            fmt_sources.setdefault(m["format"], set()).add((m["adset"], m["variant_label"]))
        for m in members:
            if len(fmt_sources[m["format"]]) == 1:
                # rovnaký ad-set aj variant → líšia sa len verziou (v1/v2), nie názvom ad-setu
                # (posledné slovo ad-setu, napr. "gifting", zavádzalo — vyzeralo ako uhol bannera)
                extra = m["variation"].split("_")[0]
            else:
                extra = m["variant_label"] or m["adset"].split("-")[-1]
            m["label"] = f"{m['format']} {extra}"[:16] if fmt_counts[m["format"]] > 1 else m["format"]
        sections[newest["_skey"]]["collections"][label] = members

    for section in sections.values():
        for members in section["collections"].values():
            for m in members:
                m.pop("_skey", None)
    return sections, total_failed


# ---------------------------------------------------------------------------
# Video — AdGenerator-Pro/video (Video Factory)
# ---------------------------------------------------------------------------

# Zdroje videí (symlinky v staticky/, aby ich servoval :8077). Poradie = priorita pri duplicitách:
#   video-out     → ../video/remotion/out  (Remotion render, *_REMOTION / *_FINAL)
#   video-compose → ../video/output        (starší ffmpeg compose)
# Jazykové podpriečinky (CZ/HU/DE/PL/RO) sa prechádzajú tiež.
VIDEO_SOURCES = [
    ("video-out", "v2"),
    ("video-compose", "v2"),
]
POSTER_DIR = ROOT / "video-posters"
LANG_SUFFIX_RE = re.compile(r"^(.+)-(sk|cz|hu|ro|pl|de|it|en)$", re.I)
# Verzia výstupu v názve súboru → label na karte; nižšie číslo = novšia/finálnejšia verzia
VERSION_SUFFIXES = [("_FINAL", "FINAL", 0), ("_REMOTION", "REMOTION", 1)]
SKIP_VIDEO_DIRS = {"frames"}


def split_version(stem: str):
    """`moje-video_FINAL` → (moje-video, FINAL, 0) · bez suffixu → (stem, compose, 2)."""
    for suffix, label, rank in VERSION_SUFFIXES:
        if stem.endswith(suffix):
            return stem[: -len(suffix)], label, rank
    return stem, "compose", 2


def all_videos() -> list:
    """Všetky .mp4 zo všetkých PVF zdrojov (bez .bak) ako dicty, duplicity len raz.

    {path, url, src (v1/v2), lang (z podpriečinka, ak je), cache (PVF cache/ daného zdroja), poster}
    """
    out, seen = [], set()
    for link, src in VIDEO_SOURCES:
        vdir = ROOT / link
        if not vdir.exists():
            continue
        try:
            factory = vdir.resolve().parent
            if factory.name == "remotion":
                factory = factory.parent
        except Exception:
            factory = vdir
        for video in sorted(vdir.rglob("*.mp4")):
            rel = video.relative_to(vdir)
            if ".bak" in video.name or any(part in SKIP_VIDEO_DIRS for part in rel.parts[:-1]):
                continue
            try:
                size = video.stat().st_size
            except OSError:
                continue
            key = (str(rel), size)
            if key in seen:
                continue
            seen.add(key)
            sub = rel.parts[0].lower() if len(rel.parts) > 1 else ""
            out.append({
                "path": video,
                "url": f"{link}/{rel.as_posix()}",
                "src": src,
                "lang": sub if sub in COUNTRY_TOKENS else "",
                "cache": factory / "cache",
                # staré postery (v1) ostávajú pod pôvodným názvom, v2 dostane prefix
                "poster": f"{video.stem}.jpg" if src == "v1" else f"{src}-{video.stem}.jpg",
            })
    return out


def parse_video_name(stem: str, known_brands: set, prefix_counts: dict):
    """`znacka-akcia-1` → (znacka, sk, akcia) · `kampan-a` + `kampan-b` → (video, sk, kampan)."""
    base, lang = stem, "sk"
    m = LANG_SUFFIX_RE.match(stem)
    if m:
        base, lang = m.group(1), m.group(2).lower()

    tokens = base.split("-")
    prefix = tokens[0].lower()
    brand = prefix if prefix in known_brands else "video"

    if prefix == brand and len(tokens) > 1:
        series = tokens[1]                      # znacka-akcia-1 → akcia
    elif prefix_counts.get(prefix, 0) >= 2 and len(tokens) > 1:
        series = prefix                         # kampan-a + kampan-b → kampan
    else:
        series = "ostatné"
    return brand, lang, series, base


def load_video_script(stem: str, cache_dir: Path) -> dict:
    """Metadáta z PVF `cache/script_<id>.json` — title, hook, transkript. {} ak chýba."""
    path = cache_dir / f"script_{stem}.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    hook = (data.get("hook") or data.get("hook_clip_line") or "").strip()
    segments = [s.get("text", "") for s in data.get("segments", []) if isinstance(s, dict)]
    transcript = " ".join(filter(None, [hook] + segments + [(data.get("cta") or "").strip()]))
    return {
        "title": (data.get("title") or "").strip(),
        "hook": hook,
        "transcript": transcript.strip(),
        "n_segments": len(segments),
        "lineage": build_lineage(data),
    }


def discover_videos() -> dict:
    """PVF .mp4 → sekcie v rovnakom tvare ako image sekcie (skey → section).

    Verzie toho istého videa (`*_FINAL`, `*_REMOTION`, starý compose, v1 / v2) sa zlúčia do JEDNEJ
    karty s prepínaním — rovnako ako formáty u bannerov. FINAL z v2 je default.
    """
    videos = all_videos()
    if not videos:
        return {}

    known_brands = {d.name for d in (ROOT / "brands").iterdir() if d.is_dir()} \
        if (ROOT / "brands").exists() else set()

    prefix_counts = {}
    for v in videos:
        base_stem, _, _ = split_version(v["path"].stem)
        m = LANG_SUFFIX_RE.match(base_stem)
        base_stem = m.group(1) if m else base_stem
        key = base_stem.split("-")[0].lower()
        prefix_counts[key] = prefix_counts.get(key, 0) + 1

    sections = {}
    used_ids = set()
    SRC_RANK = {"v2": 0, "v1": 1}

    for v in videos:
        video = v["path"]
        base_stem, ver_label, ver_rank = split_version(video.stem)
        brand, lang, series, base = parse_video_name(base_stem, known_brands, prefix_counts)
        if v["lang"] and lang == "sk":
            lang = v["lang"]   # out/DE/de-gifting-a → jazyk z podpriečinka
        try:
            stat = video.stat()
        except OSError:
            continue
        mtime = int(stat.st_mtime)
        meta = probe_video(video)
        script = load_video_script(base_stem, v["cache"]) or load_video_script(video.stem, v["cache"])

        poster = POSTER_DIR / v["poster"]
        poster_rel = f"video-posters/{v['poster']}" if poster.exists() else ""

        w, h = meta.get("w", 0), meta.get("h", 0)
        fmt = classify_format(w, h) if w and h else "9:16"

        skey = (brand, "pvf-video", series, lang, "")
        if skey not in sections:
            brand_dir = ROOT / "brands" / brand
            sections[skey] = {
                "brand": brand, "product": "pvf-video", "adset": series,
                "lang": lang, "variant": "",
                "primary": load_brand_colors(brand_dir)["primary"] if brand_dir.exists() else "#7A5CFF",
                "outputs_names": [], "mtime": 0, "collections": {},
            }
        section = sections[skey]
        src_dir = v["url"].split("/")[0]
        if src_dir not in section["outputs_names"]:
            section["outputs_names"].append(src_dir)

        vid = f"{brand}__pvf-video__{lang}__{video.stem}"
        if vid in used_ids:
            vid = f"{vid}__{v['src']}"
        used_ids.add(vid)

        member = {
            "id": vid,
            "kind": "video",
            "brand": brand,
            "country": lang.upper(),
            "product": "pvf-video",
            "adset": series,
            "outputs": "Video Factory",
            "variant_label": ver_label,
            "ad_id": base_stem,
            "template_name": video.stem,
            "template_num": 0,
            "variation": "video",
            "file": v["url"],
            "video_url": f"{v['url']}?v={mtime}",
            "img_url": f"{poster_rel}?v={mtime}" if poster_rel else "",
            "headline": script.get("title") or script.get("hook") or "",
            "transcript": script.get("transcript", ""),
            "vo_chars": len(script.get("transcript", "")),
            "duration": meta.get("duration", 0),
            "format": fmt,
            "w": w, "h": h,
            "size_kb": round(stat.st_size / 1024, 1),
            "mtime": mtime,
            "sha": file_sha256(video),
            "label": ver_label,
            "src": v["src"],
            "lineage": script.get("lineage") or {},
            "_rank": (ver_rank, SRC_RANK.get(v["src"], 9)),
        }

        section["collections"].setdefault(f"video:{base_stem}", []).append(member)
        section["mtime"] = max(section["mtime"], mtime)

    # FINAL ako prvý (= default na karte), potom REMOTION, potom compose; v2 pred v1
    for section in sections.values():
        for members in section["collections"].values():
            members.sort(key=lambda m: (m["_rank"], -m["mtime"]))
            for m in members:
                m.pop("_rank", None)

    return sections


# ---------------------------------------------------------------------------
# Tab „Templaty a štýly" + tab „Pod kapotou" (statické panely, číta sa pri builde)
# ---------------------------------------------------------------------------

STYLES_DIR = ROOT / "visual-styles"
TEMPLATES_DIR = ROOT / "04-brief-template-copy-prompts" / "01-templates-by-motion"
# AI ukážky templatov (voliteľné, platené — generujú sa len na pokyn): template-previews/<NN>.png|jpg
TEMPLATE_PREVIEWS_DIR = ROOT / "template-previews"
PVF_ROOT = ROOT.parent / "video"   # AdGenerator-Pro/video


def load_visual_styles() -> list:
    styles = []
    for f in sorted(STYLES_DIR.glob("*.json")):
        if f.name.startswith("_"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        refs = []
        for r in d.get("ref_images") or []:
            path = (STYLES_DIR / r).resolve()
            try:
                refs.append(str(path.relative_to(ROOT.resolve())))
            except ValueError:
                pass
        d["_refs"] = [r for r in refs if (ROOT / r).exists()]
        styles.append(d)
    return styles


def load_templates() -> list:
    """40 Motion templatov — názov, jednoriadkový popis, metadáta a „What this format is"."""
    out = []
    for f in sorted(TEMPLATES_DIR.glob("[0-9][0-9]-*.md")):
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else f.stem
        tagline = next((l.replace("🏷️", "").strip() for l in lines if l.startswith("🏷")), "")
        def meta(key):
            m = re.search(r"\*\*" + key + r":\*\*\s*(.+)", text)
            return m.group(1).strip() if m else ""
        what = ""
        m = re.search(r"## What this format is\s*\n+(.+?)(?:\n\s*\n|\n#)", text, re.S)
        if m:
            what = " ".join(m.group(1).split())
        styles = re.findall(r"^### Style ([A-Z]):\s*(.+)$", text, re.M)
        num, _, name = title.partition("—")
        if not name:  # „# Headline" bez čísla → číslo z názvu súboru
            num, name = f.name[:2], title
        out.append({
            "num": num.strip(), "name": name.strip() or title, "tagline": tagline,
            "aspect": meta("aspect_ratio"), "needs_product": meta("needs_product_images"),
            "what": what, "styles": styles, "file": str(f.relative_to(ROOT)),
        })
    return out


def build_styles_tab(style_samples: dict) -> str:
    styles = load_visual_styles()
    templates = load_templates()

    cards = []
    for st in styles:
        sid = st.get("id", "")
        samples = style_samples.get(sid, [])[:4]
        refs = st["_refs"][:3]
        gallery = "".join(f'<img src="{esc(r)}" alt="" loading="lazy" title="Predloha štýlu">' for r in refs)
        gallery += "".join(f'<img src="{esc(m["img_url"])}" alt="" loading="lazy" title="Vygenerované: {esc(m["ad_id"])}" class="sample">' for m in samples)
        if not gallery:
            gallery = '<div class="st-noimg">Bez predlohy — štýl je definovaný len textom</div>'
        variants = st.get("variants") or {}
        var_html = "".join(f"<li><b>{esc(k)}</b> — {esc(v)}</li>" for k, v in variants.items())
        never = "".join(f"<li>{esc(n)}</li>" for n in (st.get("never") or []))
        ww = st.get("works_with") or {}
        chips = "".join(f'<span class="chip">{esc(a)}</span>' for a in ww.get("aspect_ratios") or [])
        chips += "".join(f'<span class="chip ok">✓ {esc(b)}</span>' for b in st.get("brands_validated") or [])
        if st.get("craft"):
            chips += '<span class="chip accent">+ craft vrstva</span>'
        n_used = len(style_samples.get(sid, []))
        used = f'<span class="st-used">{n_used} bannerov</span>' if n_used else '<span class="st-used none">zatiaľ nepoužitý</span>'
        cards.append(f"""
      <article class="st-card">
        <div class="st-gallery">{gallery}</div>
        <div class="st-body">
          <div class="st-head"><h3>{esc(st.get('name', sid))}</h3><code>{esc(sid)}</code>{used}</div>
          <p class="st-summary">{esc(st.get('summary', ''))}</p>
          {f'<p class="st-when"><b>Kedy použiť:</b> {esc(st.get("when_to_use", ""))}</p>' if st.get('when_to_use') else ''}
          <div class="chips">{chips}</div>
          {f'<details><summary>Varianty ({len(variants)})</summary><ul>{var_html}</ul></details>' if variants else ''}
          {f'<details><summary>Čo štýl nikdy nerobí</summary><ul>{never}</ul></details>' if never else ''}
          <details><summary>Prompt blok</summary><pre>{esc(st.get('prompt_block', ''))}</pre></details>
        </div>
      </article>""")

    tcards = []
    cat_counts = {}
    for t in templates:
        try:
            num = int(t["num"])
        except ValueError:
            num = 0
        cat = TPL_CATEGORY_OF.get(num, "new")
        ratio_hint = (re.match(r"\s*(\d+:\d+)", t["aspect"] or "") or [None, "4:5"])[1]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        cat_label = dict(TPL_CATEGORIES).get(cat, "")
        ai = next((TEMPLATE_PREVIEWS_DIR / f"{num:02d}{ext}" for ext in (".png", ".jpg", ".webp")
                   if (TEMPLATE_PREVIEWS_DIR / f"{num:02d}{ext}").exists()), None)
        sketch = sketch_html(num, ratio_hint)
        if ai:
            rel = ai.relative_to(ROOT)
            stage = (f'<img class="tp-ai" src="{esc(rel)}?v={int(ai.stat().st_mtime)}" alt="">'
                     f'<div class="tp-sketch-alt">{sketch}</div><span class="tp-kind ai">AI ukážka</span>')
        else:
            stage = f'{sketch}<span class="tp-kind">náčrt</span>'
        st_list = ", ".join(f"{k}: {v}" for k, v in t["styles"])
        tcards.append(f"""
      <article class="tp-card" data-cat="{cat}" data-search="{esc((t['num'] + ' ' + t['name'] + ' ' + t['tagline'] + ' ' + t['what'] + ' ' + cat_label).lower())}">
        <div class="tp-stage">{stage}</div>
        <div class="tp-body">
          <div class="tp-title"><span class="tp-num">{esc(t['num'])}</span><h3>{esc(t['name'])}</h3></div>
          <p class="tp-tag">{esc(t['tagline'])}</p>
          <div class="chips"><span class="chip accent">{esc(cat_label)}</span><span class="chip">{esc(sketch_ratio(num, ratio_hint))}</span>{'<span class="chip">fotka produktu</span>' if t['needs_product'].lower().startswith('true') else ''}{f'<span class="chip">{len(t["styles"])} štýly</span>' if t['styles'] else ''}</div>
          <details><summary>Ako formát funguje</summary><p class="tp-what">{esc(t['what'])}</p>{f'<p class="tp-styles">Štýly: {esc(st_list)}</p>' if st_list else ''}<p class="tp-styles"><code>{esc(t['file'])}</code></p></details>
        </div>
      </article>""")

    seg = '<button data-cat="" aria-pressed="true">Všetky <span>' + str(len(templates)) + '</span></button>' + "".join(
        f'<button data-cat="{k}" aria-pressed="false">{esc(v)} <span>{cat_counts.get(k, 0)}</span></button>'
        for k, v in TPL_CATEGORIES if cat_counts.get(k, 0) or k != "new")

    return f"""
  <section class="panel-section">
    <div class="panel-head"><h2>Vizuálne štýly <span class="count">{len(styles)}</span></h2>
      <p>Art direction vrstva — prompt hovorí <b>čo</b> je na banneri, štýl <b>ako</b> to vyzerá. Zapisuje sa do <code>_meta.visual_style</code> v prompts JSON. Prvé obrázky sú predlohy štýlu, ďalšie sú tvoje vygenerované bannery v tom štýle.</p></div>
    <div class="st-grid">{"".join(cards)}</div>
  </section>
  <section class="panel-section">
    <div class="panel-head"><h2>Templaty <span class="count">{len(templates)}</span></h2>
      <p>Formáty z analytiky kreatív knižnice — kostra kompozície a copy slotov, z ktorej sa píšu prompty. Náčrt ukazuje rozloženie: kde je produkt, nadpis, recenzia, cena a CTA.</p></div>
    <div class="tp-toolbar"><div class="tp-seg" id="tp-seg">{seg}</div>
      <input type="search" id="tp-search" class="panel-search" placeholder="Hľadať… (recenzia, zľava, ugc, porovnanie)"></div>
    <div class="tp-grid">{"".join(tcards)}</div>
  </section>"""


def _env_keys(path: Path) -> dict:
    """Názov kľúča → hash hodnoty (prvých 8 znakov SHA-256) alebo '' ak je prázdny. Hodnota sa nikam nedostane."""
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.*)$", line.strip())
        if m:
            val = m.group(2).strip().strip("'\"")
            out[m.group(1)] = hashlib.sha256(val.encode()).hexdigest()[:8] if val else ""
    return out


def api_rows() -> list:
    """Prehľad napojených služieb — iba názvy a stav (nastavený / prázdny), nikdy hodnoty."""
    rows = []
    envs = {"ad-generator (root)": _env_keys(ROOT / ".env")}
    for f in sorted((ROOT / "brands").glob("*/.env")):
        envs[f.parent.name] = _env_keys(f)

    groups = {}
    for owner, keys in envs.items():
        h = keys.get("GEMINI_API_KEY")
        if h:
            groups.setdefault(h, []).append(owner)
    letters = "ABCDEFGH"
    gem_detail = " · ".join(f"<b>kľúč {letters[i]}</b>: {esc(', '.join(o))}" for i, o in enumerate(groups.values()))
    rows.append(("Google Gemini", "GEMINI_API_KEY", f"<code>.env</code> v ad-generator/ a v každom <code>brands/&lt;brand&gt;/.env</code>",
                 "Generovanie bannerov (Nano Banana, <code>generate_ads.py</code>), Veo3 a Omni video klipy (<code>07-video-generation</code>). Pred generovaním sa vždy volí token.",
                 f"✓ {len(groups)} rôzne kľúče" if groups else "✕ chýba", "ok" if groups else "bad", gem_detail))

    fal = sum(1 for k in envs.values() if k.get("FAL_KEY"))
    rows.append(("FAL AI", "FAL_KEY", "<code>.env</code> (rovnaké miesta ako Gemini)",
                 "Alternatívny provider obrázkov (<code>--provider fal</code>) — nepoužíva sa, default je Google.",
                 f"✓ {fal}×" if fal else "— prázdny", "ok" if fal else "off", ""))

    pvf_cfg = {}
    try:
        pvf_cfg = json.loads((PVF_ROOT / "config.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    n_cfg = len(list(PVF_ROOT.glob("config*.json")))
    def st(key):
        return ("✓ nastavený", "ok") if pvf_cfg.get(key) else ("— prázdny", "off")
    s_el = st("elevenlabs_api_key")
    rows.append(("ElevenLabs", "elevenlabs_api_key", f"<code>video/config.json</code> (+ trhové configy, spolu {n_cfg})",
                 "Voiceover s presným časovaním slov pre karaoke titulky (<code>step2_voice.py</code>). Bez kľúča fallback na edge-tts zadarmo.",
                 s_el[0], s_el[1], ""))
    rows.append(("Claude (Anthropic)", "prihlásenie Claude Code", "<code>claude -p</code> / voliteľne env <code>ANTHROPIC_API_KEY</code>",
                 "Písanie video scriptov (<code>step1_script.py</code>) a reportov — beží cez tvoje Claude Code prihlásenie.",
                 "✓ cez Claude Code", "ok", ""))
    return rows


def build_system_tab() -> str:
    ad_items = [
        ("01-brand-research-prompt/", "Prompt na brand research — z neho vzniká brand DNA nového klienta."),
        ("02-brand-cards/", "Prompty na brand karty (brand-spec + visual-style card). Karty idú do každého generovania ako referenčný obrázok — fonty, farby, logo."),
        ("03-product-research/", "Metodika produktového researchu: avatar sheet, offer brief, deep research, sťahovanie fotiek produktu."),
        ("04-brief-template-copy-prompts/", "40 Motion templatov, copy prompty a ad swipe — kostra, z ktorej sa píšu prompty."),
        ("05-scoring-agents/", "8 hodnotiacich agentov copy (persona, angle, emócia, brand, copy, formát, fakty, gramatika)."),
        ("06-image-generation/", "<b>generate_ads.py</b> — hlavný generátor bannerov (Gemini realtime / batch, FAL), validácia promptov, vizuálne štýly, preklady."),
        ("07-video-generation/", "AI video klipy: Veo3 (<code>generate_videos.py</code>) a Gemini Omni (<code>generate_omni.py</code>) → footage pre PVF."),
        ("brands/&lt;klient&gt;/", "Všetko o klientovi (lokálne, vzor <code>brands/_priklad/</code>): <code>brand-dna/</code> (logá, karty), <code>products/&lt;produkt&gt;/product-image-ads/&lt;ad-set&gt;/</code> s <code>prompts-&lt;jazyk&gt;.json</code> a <code>outputs*/</code>, vlastný <code>.env</code>."),
        ("visual-styles/", "Knižnica vizuálnych štýlov (<code>&lt;id&gt;.json</code>) + zdieľaná craft vrstva <code>_craft.json</code>."),
        ("tools/", "Dashboard (<code>build_dashboard.py</code>, <code>serve_dashboard.py</code> :8077), logo/CTA overlay skripty, <code>refresh_and_open.py</code> (prestavba manifestu po generovaní)."),
        ("flagged.json · approved.json", "QA hodnotenia z dashboardu: na opravu (FAIL / drobná oprava) a schválené PASS."),
        ("BONUS/", "Multiply, animácie, prekladače obrázkov a copy."),
        ("video-out · video-compose", "Symlinky na výstupy <code>../video/</code> — odtiaľ berie dashboard videá."),
    ]
    pvf_items = [
        ("scripts/step1_script.py", "Script videa (hook, segmenty, CTA) cez <code>claude -p</code> podľa copy playbooku značky (config → copy_playbook)."),
        ("scripts/step2_voice.py", "Voiceover cez ElevenLabs (<code>eleven_multilingual_v2</code>) s časovaním slov pre titulky."),
        ("scripts/build_silent_seq.py · step3_*", "Zostavenie klipov: vlastné zábery (<code>step3_local</code>), voliteľne stock / ilustrácie / animácie."),
        ("remotion/src/Ad.tsx", "<b>v2 jadro</b> — celé video v Remotion: footage + 19 prechodov + Ken Burns + titulky + audio v jednom renderi."),
        ("remotion/src/Captions.tsx", "Karaoke titulky so zvýraznením slova vo farbe značky."),
        ("remotion/src/Scenes.tsx · Punch.tsx · FlashPhoto.tsx", "Animované scény, rytmické „punch“ momenty a flash fotky."),
        ("remotion/make_ad_props.py", "Generuje props pre render: delenie času, kompenzácia 24→30 fps."),
        ("remotion/out/ (+ CZ, HU, DE, PL, RO)", "Hotové videá <code>*_REMOTION.mp4</code> / <code>*_FINAL.mp4</code> — tie vidíš v tabe Video."),
        ("scripts/build_hookvideo.sh", "Hook video: predradí UGC hook klip (vlastné audio) pred produktovú sekciu → <code>_FINAL.mp4</code>."),
        ("locales/ · scripts/make_locale.py", "Preklady scriptov — klipy a poradie ostávajú, mení sa len text."),
        ("assets/footage/ · assets/music/", "Tvoje klipy (<code>seq_*</code>, <code>product_*</code>, <code>hook_*</code>) a hudobné podmazy."),
        ("cache/", "Scripty (<code>script_&lt;id&gt;.json</code>) a voiceover — dashboard z nich berie názov a transkript videa."),
        ("config*.json", "Nastavenia per trh (hlas, dĺžka, brief) a kľúč ElevenLabs."),
        ("security/render-sandbox.sb", "Render beží v sandboxe — Node/Chromium nevidí ~/.claude, ~/.api-keys ani Keychain."),
        ("RULES.md · REMOTION-V2.md · README.md", "Pravidlá skladania videí, technická dokumentácia a návod."),
    ]
    def col(items):
        return "".join(f'<li><code class="path">{p}</code><span>{d}</span></li>' for p, d in items)

    rows = api_rows()
    trs = "".join(
        f'<tr><td><b>{esc(n)}</b><div class="api-key">{k}</div></td><td>{where}</td><td>{use}{f"<div class=api-detail>{det}</div>" if det else ""}</td>'
        f'<td><span class="api-st {cls}">{stt}</span></td></tr>'
        for n, k, where, use, stt, cls, det in rows)

    pipeline = " → ".join(f"<span>{x}</span>" for x in ("script", "voiceover", "klipy", "Remotion render", "lokalizácia"))
    tree = """<div class="tree"><div class="tree-head"><span class="split-icon brand-icon"><img class="logo-mark on-light" src="assets/brand/mark-light.png" alt=""><img class="logo-mark on-dark" src="assets/brand/mark-dark.png" alt=""></span><div><h2>AdGenerator Pro</h2><p class="tagline">Create more. Design less.</p><p><code>AdGenerator-Pro/</code> · všetky nástroje na tvorbu reklám na jednom mieste</p></div></div>
      <div class="tree-grid">
        <div><code class="path">staticky/</code><span>Generátor statických bannerov + dashboard (:8077)</span></div>
        <div><code class="path">video/</code><span>Video Factory — Reels z vlastných klipov</span></div>
        <div><code class="path">vystupy/</code><span>Hotové súbory: <code>statiky/&lt;klient&gt;/&lt;produkt&gt;/&lt;kampaň&gt;/</code> a <code>videa/&lt;klient&gt;/&lt;jazyk&gt;/</code> — zrkadlo, obnovuje sa pri každom builde dashboardu</span></div>
      </div>
      <p class="tree-note">Klientske dáta (brands/), výstupy a footage sú lokálne — nie sú súčasťou distribúcie.</p></div>"""
    return f"""
  {tree}
  <div class="split">
    <section class="split-col">
      <div class="split-head"><span class="split-icon">🖼</span><div><h2>Statiky</h2><p><code>AdGenerator-Pro/staticky/</code> · statické bannery cez Gemini + tento dashboard</p></div></div>
      <div class="flow">brand DNA → research → template + štýl → prompty → generovanie → overlay → dashboard</div>
      <ul class="files">{col(ad_items)}</ul>
    </section>
    <section class="split-col">
      <div class="split-head"><span class="split-icon">🎬</span><div><h2>Video Factory</h2><p><code>AdGenerator-Pro/video/</code> · Reels 9:16 z vlastných klipov, celé video v Remotion</p></div></div>
      <div class="flow">{pipeline}</div>
      <ul class="files">{col(pvf_items)}</ul>
    </section>
  </div>
  <section class="panel-section api">
    <div class="panel-head"><h2>Napojené API a služby</h2>
      <p>Stav sa číta pri každom builde dashboardu. Hodnoty kľúčov sa nikde nezobrazujú ani neukladajú — len názov a či je vyplnený. Rovnaké kľúče sa spárujú porovnaním odtlačku.</p></div>
    <div class="api-wrap"><table class="api-table"><thead><tr><th>Služba</th><th>Kde je kľúč</th><th>Na čo sa používa</th><th>Stav</th></tr></thead><tbody>{trs}</tbody></table></div>
  </section>"""


# ---------------------------------------------------------------------------
# Zrkadlo hotových súborov → AdGenerator-Pro/vystupy/{statiky,videa}
# ---------------------------------------------------------------------------

VYSTUPY_DIR = ROOT.parent / "vystupy"
VYSTUPY_STATE = VYSTUPY_DIR / ".zrkadlo.json"


def sync_vystupy(sections: dict) -> dict:
    """Hotové bannery a videá ako hardlinky (0 MB navyše), usporiadané pre človeka:

        vystupy/statiky/<klient>/<produkt>/<kampaň>/<jazyk-variant>/<súbor>
        vystupy/videa/<klient>/<JAZYK>/<súbor>

    Spravuje len súbory, ktoré sám vytvoril (zoznam v .zrkadlo.json) — čo tam pridáš ručne,
    nezmaže. Pregenerovaný súbor (nový inode) sa pri ďalšom builde nahradí.
    """
    targets = {}
    for section in sections.values():
        for members in section["collections"].values():
            for m in members:
                src = (ROOT / m["file"]).resolve()
                if not src.is_file() or "_clean" in src.name:
                    continue
                if m.get("kind") == "video":
                    if not m["file"].startswith("video-out/"):
                        continue  # starý ffmpeg compose do výstupov nepatrí
                    rel = Path("videa") / m["brand"] / (m["country"] or "SK") / src.name
                else:
                    sub = m["outputs"][len("outputs"):].strip("-") or "sk"
                    rel = Path("statiky") / m["brand"] / m["product"] / m["adset"] / sub / src.name
                targets[str(rel)] = src

    try:
        previous = set(json.loads(VYSTUPY_STATE.read_text(encoding="utf-8")))
    except Exception:
        previous = set()

    linked = kept = 0
    for rel, src in targets.items():
        dst = VYSTUPY_DIR / rel
        try:
            if dst.exists() and dst.samefile(src):
                kept += 1
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() or dst.is_symlink():
                dst.unlink()
            try:
                os.link(src, dst)
            except OSError:
                shutil.copy2(src, dst)
            linked += 1
        except OSError:
            continue

    removed = 0
    for rel in previous - set(targets):
        dst = VYSTUPY_DIR / rel
        try:
            if dst.is_file():
                dst.unlink()
                removed += 1
            parent = dst.parent
            while parent != VYSTUPY_DIR and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        except OSError:
            pass

    VYSTUPY_DIR.mkdir(parents=True, exist_ok=True)
    VYSTUPY_STATE.write_text(json.dumps(sorted(targets), ensure_ascii=False), encoding="utf-8")
    return {"spolu": len(targets), "nové": linked, "bez zmeny": kept, "odstránené": removed}


# Farba klienta pre pruh s názvom setu (brief má často čiernu / nič) — pevne, nech sa nemení medzi buildmi
BRAND_ACCENT = {
    # "moja-znacka": "#4F52F7",   ← farba pruhu setu pre klienta (inak sa priradí automaticky)
}
FALLBACK_ACCENTS = ["#0A84FF", "#FF9F0A", "#30B0C7", "#AF52DE", "#FF375F", "#34C759", "#5856D6", "#A2845E"]


def brand_accent(brand: str) -> str:
    if brand in BRAND_ACCENT:
        return BRAND_ACCENT[brand]
    return FALLBACK_ACCENTS[sum(map(ord, brand)) % len(FALLBACK_ACCENTS)]


def esc(s) -> str:
    return html_lib.escape(str(s))


def build_collection_card(motif: str, members: list, section: dict) -> str:
    m0 = members[0]
    primary = section["primary"]
    members_json = json.dumps(members, ensure_ascii=False).replace("</", "<\\/")
    search_blob = " ".join(
        f"{m['ad_id']} {m['template_name']} {m['headline']} {m['variation']} {m.get('transcript', '')}"
        for m in members
    ).lower()
    formats = sorted({m["format"] for m in members}, key=lambda f: FORMAT_ORDER.get(f, 9))

    thumbs = ""
    if len(members) > 1:
        tb = []
        for i, m in enumerate(members):
            tip = f"{m['format']} · {m['template_name']} · {m['outputs']}"
            tb.append(
                f'<button class="thumb{" active" if i == 0 else ""}" data-idx="{i}" data-mid="{esc(m["id"])}" title="{esc(tip)}">'
                f'<img src="{esc(m["img_url"])}" alt="" loading="lazy"><span>{esc(m.get("label", m["format"]))}</span></button>'
            )
        thumbs = f'<div class="thumbs">{"".join(tb)}</div>'

    sources = sorted({m["outputs"] for m in members})
    merged_tag = (f'<span class="merged-tag" title="{esc(", ".join(sources))}">⛓ {len(sources)} zdroje</span>'
                  if len(sources) > 1 else "")

    is_video = m0.get("kind") == "video"
    kind = "video" if is_video else "image"

    # Rodokmeň — z ktorého víťaza kreatíva vychádza
    lin = m0.get("lineage") or {}
    lin_badge = lin_row = ""
    if lin:
        ltype = lin.get("type", "ITERATION")
        icon = {"ITERATION": "🔁", "EXPERIMENT": "🧪", "RE-TEST": "♻️"}.get(ltype, "🔁")
        lin_badge = f'<span class="lin-tag" title="{esc(lin.get("why", ""))}">{icon} {esc(ltype.lower())}</span>'
        top = (lin.get("winners") or [None])[0]
        if top:
            lin_row = (f'<p class="lin-row" title="{esc(lin.get("why", ""))}">◀ z víťaza '
                       f'<b>{esc(top["name"][:26])}</b> · ROAS {top["roas"]}</p>')
        else:
            lin_row = f'<p class="lin-row">◀ {esc(ltype.lower())}</p>'
    play_overlay = ""
    if is_video:
        dur = m0.get("duration") or 0
        dur_label = f"{dur:.0f}s" if dur else "video"
        play_overlay = f'<span class="play-overlay">▶</span><span class="dur-tag">{esc(dur_label)}</span>'

    return f"""
        <div class="ccard{' is-video' if is_video else ''}" data-kind="{kind}" data-motif="{esc(motif)}" data-brand="{esc(m0['brand'])}" data-country="{esc(m0['country'])}" data-product="{esc(m0['product'])}" data-adset="{esc(m0['adset'])}" data-formats="{esc('|'.join(formats))}" data-styles="{esc('|'.join(sorted({m.get('style') or '-' for m in members})))}" data-search="{esc(search_blob)}">
          <script type="application/json" class="members-data">{members_json}</script>
          <div class="stage">
            <div class="qa-bar" title="Shift + klik = všetky formáty motívu">
              <button class="qa-btn qa-pass" data-qa="pass" title="PASS — schválené (Shift = všetky formáty)">✓</button>
              <button class="qa-btn qa-fix" data-qa="fix" title="Drobná oprava (Shift = všetky formáty)">✎</button>
              <button class="qa-btn qa-fail" data-qa="fail" title="FAIL — prerobiť (Shift = všetky formáty)">✕</button>
            </div>
            <span class="qa-badge"></span>
            <span class="brand-tag" style="background:{primary}">{esc(m0['brand'])}</span>
            <span class="country-tag">{esc(m0['country'])}</span>
            <span class="fmt-tag">{esc(m0['format'])}</span>
            {lin_badge}
            {merged_tag}
            <img class="stage-img" src="{esc(m0['img_url'])}" alt="{esc(m0['ad_id'])}" loading="lazy">
            {play_overlay}
          </div>
          {thumbs}
          <div class="card-info">
            <h4>{'<span class="vid-badge">🎬 PVF</span>' if is_video else f'<span class="tnum">T{m0["template_num"]:02d}</span>'} · <span class="adid">{esc(m0['ad_id'])}</span> <span class="var-badge" style="background:{primary}">{esc((m0['variation'] or 'v?').split('_')[0])}</span></h4>
            <p class="hl">{esc(m0['headline']) if m0['headline'] else '<em>(bez headline)</em>'}</p>
            <p class="meta"><span class="m-fmt">{esc(m0['format'])}</span> · <span class="m-dim">{f"{m0['w']}×{m0['h']}" if m0['w'] else '—'}</span> · <span class="m-kb">{m0['size_kb']} KB</span><button class="reveal-btn" title="Ukázať vo Finderi">📂</button><button class="sel-btn" title="Pridať do výberu na porovnanie / PDF">☐</button></p>
            {lin_row}
            <div class="note-row" hidden>
              <textarea class="note-input" rows="2" placeholder="Čo opraviť? Píš rovno sem…"></textarea>
              <span class="note-hint">Enter = uložiť · Shift+Enter = nový riadok</span>
            </div>
          </div>
        </div>"""


CSS = """
  /* ================= Dizajn tokeny — Apple systémové farby, svetlý / tmavý režim ================= */
  :root, :root[data-theme="dark"] {
    color-scheme: dark;
    --bg: #000000; --bg-elev: #1c1c1e; --bg-elev2: #2c2c2e; --stage: #111113;
    --fill: rgba(120,120,128,0.24); --fill-2: rgba(120,120,128,0.36);
    --label: #ffffff; --label-2: rgba(235,235,245,0.62); --label-3: rgba(235,235,245,0.32);
    --sep: rgba(84,84,88,0.55);
    --accent: #0A84FF; --accent-tint: rgba(10,132,255,0.18);
    --material: rgba(28,28,30,0.72); --material-strong: rgba(44,44,46,0.94); --material-edge: rgba(255,255,255,0.08);
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.5);
    --shadow: 0 1px 2px rgba(0,0,0,0.45), 0 10px 30px rgba(0,0,0,0.35);
    --shadow-lg: 0 24px 60px rgba(0,0,0,0.55);
    --scrim: rgba(0,0,0,0.78);
    --glass: rgba(255,255,255,0.13); --glass-h: rgba(255,255,255,0.22); --on-glass: #ffffff;
    --q-fail: #FF453A; --q-fix: #FF9F0A; --q-stale: #BF5AF2; --q-pass: #30D158;
    --teal: #40C8E0; --mint: #63E6BE;
  }
  :root[data-theme="light"] {
    color-scheme: light;
    --bg: #f2f2f7; --bg-elev: #ffffff; --bg-elev2: #f2f2f7; --stage: #f5f5f7;
    --fill: rgba(120,120,128,0.12); --fill-2: rgba(120,120,128,0.2);
    --label: #000000; --label-2: rgba(60,60,67,0.62); --label-3: rgba(60,60,67,0.32);
    --sep: rgba(60,60,67,0.16);
    --accent: #007AFF; --accent-tint: rgba(0,122,255,0.12);
    --material: rgba(255,255,255,0.72); --material-strong: rgba(255,255,255,0.95); --material-edge: rgba(0,0,0,0.06);
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.06);
    --shadow: 0 1px 2px rgba(0,0,0,0.05), 0 8px 24px rgba(0,0,0,0.07);
    --shadow-lg: 0 24px 60px rgba(0,0,0,0.18);
    --scrim: rgba(242,242,247,0.86);
    --glass: rgba(0,0,0,0.06); --glass-h: rgba(0,0,0,0.11); --on-glass: #1d1d1f;
    --q-fail: #FF3B30; --q-fix: #FF9500; --q-stale: #AF52DE; --q-pass: #34C759;
    --teal: #0A9DB8; --mint: #0E9F7A;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { -webkit-font-smoothing: antialiased; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', system-ui, sans-serif; font-size: 15px; line-height: 1.4; letter-spacing: -0.01em; background: var(--bg); color: var(--label); padding: 0 24px 24px; transition: background-color 0.35s ease, color 0.35s ease; }
  button, select, input, textarea { font-family: inherit; color: inherit; }
  button { -webkit-tap-highlight-color: transparent; }
  :focus-visible { outline: 3px solid var(--accent-tint); outline-offset: 2px; }

  /* ---------- Hlavička = translucentný materiál, obsah roluje pod ňou ---------- */
  header { position: sticky; top: 0; z-index: 10; margin: 0 -24px 22px; padding: 14px 24px 12px; background: var(--material); backdrop-filter: blur(24px) saturate(180%); -webkit-backdrop-filter: blur(24px) saturate(180%); box-shadow: 0 1px 0 var(--sep); }
  .headrow { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-bottom: 12px; }
  h1 { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.025em; line-height: 1.1; white-space: nowrap; }
  h1.brand { display: inline-flex; align-items: center; gap: 10px; }
  .logo-mark { height: 32px; width: auto; display: block; }
  .logo-mark.on-dark, :root[data-theme="dark"] .logo-mark.on-light { display: none; }
  :root[data-theme="dark"] .logo-mark.on-dark { display: block; }
  .wm { font-weight: 700; letter-spacing: -0.035em; }
  /* Paleta identity AdGenerator (2026-10-16): #4F52F7 · #458EF8 · #2DC7D9 · #4ED4AC · #EFF1F4 · #13161D */
  .wm .gen { background: linear-gradient(90deg, #4F52F7 0%, #458EF8 40%, #2DC7D9 75%, #4ED4AC 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
  :root[data-theme="dark"] .wm .gen { background-image: linear-gradient(90deg, #6D70FF 0%, #5A9CFF 40%, #3FD3E3 75%, #5EE0B8 100%); }
  .pro-chip { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.02em; color: #fff; background: linear-gradient(135deg, #4F52F7, #458EF8 55%, #2DC7D9); padding: 3px 8px; border-radius: 999px; }
  h1 .pro { background: linear-gradient(135deg, var(--accent), #BF5AF2); -webkit-background-clip: text; background-clip: text; color: transparent; }
  h1 .ver { font-size: 0.7rem; font-weight: 600; letter-spacing: 0; background: var(--accent-tint); color: var(--accent); padding: 3px 8px; border-radius: 999px; vertical-align: 4px; margin-left: 2px; }
  .stats { color: var(--label-2); font-size: 0.8rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
  .stats b { color: var(--label); font-weight: 600; }
  .srv-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--label-3); margin-right: 5px; vertical-align: 1px; }
  .srv-dot.on { background: var(--q-pass); box-shadow: 0 0 0 3px color-mix(in srgb, var(--q-pass) 22%, transparent); }

  .qa-counts { margin-left: auto; display: flex; gap: 2px; padding: 2px; background: var(--fill); border-radius: 999px; white-space: nowrap; }
  .qc { font-size: 0.78rem; font-weight: 600; padding: 4px 10px; border-radius: 999px; font-variant-numeric: tabular-nums; }
  .qc b { font-size: 0.86rem; font-weight: 700; }
  .qc.q-fail { color: var(--q-fail); } .qc.q-fix { color: var(--q-fix); }
  .qc.q-stale { color: var(--q-stale); } .qc.q-pass { color: var(--q-pass); }

  /* Tlačidlá = kapsule, odozva hneď pri stlačení */
  .flag-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .flag-actions button, .theme-toggle, .sel-bar button { background: var(--fill); border: none; color: var(--label); padding: 7px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 500; cursor: pointer; transition: background-color 0.15s ease, transform 0.1s ease-out; }
  .flag-actions button:hover, .sel-bar button:hover { background: var(--fill-2); }
  .flag-actions button:active, .sel-bar button:active, .theme-toggle:active { transform: scale(0.97); }
  .flag-actions button.primary { background: var(--accent); color: #fff; }
  .flag-actions button.primary:hover { background: color-mix(in srgb, var(--accent) 88%, #000); }
  .flag-actions button.danger, .sel-bar button.danger { background: transparent; color: var(--label-2); }
  .flag-actions button.danger:hover, .sel-bar button.danger:hover { color: var(--q-fail); background: transparent; }
  .theme-toggle { width: 34px; height: 34px; padding: 0; display: inline-flex; align-items: center; justify-content: center; font-size: 1rem; }

  .dl-wrap { position: relative; }
  .dl-menu { display: flex; visibility: hidden; opacity: 0; transform: scale(0.94); transform-origin: top left; transition: opacity 0.16s ease, transform 0.22s cubic-bezier(0.2,0.9,0.3,1), visibility 0s linear 0.22s; position: absolute; top: calc(100% + 8px); left: 0; z-index: 60; background: var(--material-strong); backdrop-filter: blur(30px) saturate(180%); -webkit-backdrop-filter: blur(30px) saturate(180%); border: 1px solid var(--material-edge); border-radius: 14px; padding: 6px; min-width: 260px; box-shadow: var(--shadow-lg); flex-direction: column; gap: 2px; }
  .dl-menu.open { visibility: visible; opacity: 1; transform: scale(1); transition-delay: 0s; }
  .flag-actions .dl-menu button { background: transparent; color: var(--label); text-align: left; display: flex; justify-content: space-between; gap: 12px; padding: 9px 12px; border-radius: 9px; }
  .flag-actions .dl-menu button:hover { background: var(--accent); color: #fff; }
  .flag-actions .dl-menu button:hover b { color: rgba(255,255,255,0.85); }
  .dl-menu button b { color: var(--label-2); font-weight: 500; font-variant-numeric: tabular-nums; }
  .dl-hint { font-size: 0.7rem; color: var(--label-3); padding: 6px 12px 3px; }

  /* ---------- Filtre ---------- */
  .filters { display: flex; gap: 8px 14px; flex-wrap: wrap; align-items: center; }
  .filters label { font-size: 0.78rem; color: var(--label-2); display: flex; align-items: center; gap: 6px; }
  .filters select, .filters input { background: var(--fill); border: none; color: var(--label); padding: 6px 10px; border-radius: 9px; font-size: 0.82rem; max-width: 210px; transition: background-color 0.15s, box-shadow 0.15s; }
  .filters select:hover, .filters input:hover { background: var(--fill-2); }
  .filters select:focus, .filters input:focus { outline: none; box-shadow: 0 0 0 3px var(--accent-tint); }
  .filters input::placeholder { color: var(--label-3); }
  .filters label.active { color: var(--accent); font-weight: 600; }
  .filters label[hidden] { display: none; }
  body[data-tab="video"] .filters .banners-only { display: none; }
  .filters label.active select { background: var(--accent-tint); color: var(--accent); }
  .btn-reset { background: none; border: none; color: var(--accent); font-size: 0.82rem; cursor: pointer; }
  .btn-reset:hover { text-decoration: underline; }

  /* ---------- Sekcie ---------- */
  .adset-section { margin-bottom: 44px; }
  /* Pruh s názvom setu — liquid glass cez celú šírku, tónovaný farbou klienta, prilepený pod hlavičkou */
  .section-header { position: sticky; top: calc(var(--hdr-h, 150px) + 8px); z-index: 8; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    margin: 0 -8px 16px; padding: 12px 18px 12px 22px; border-radius: 16px; overflow: hidden;
    background: linear-gradient(100deg, color-mix(in srgb, var(--brand) 22%, transparent) 0%, color-mix(in srgb, var(--brand) 8%, transparent) 45%, transparent 75%), var(--material);
    backdrop-filter: blur(22px) saturate(180%); -webkit-backdrop-filter: blur(22px) saturate(180%);
    border: 1px solid var(--material-edge); box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), var(--shadow-sm); }
  .section-header::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background: var(--brand); }
  .section-title { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.12rem; font-weight: 700; letter-spacing: -0.02em; color: var(--label); }
  .section-title::before { content: ''; display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: var(--brand); margin-right: 9px; vertical-align: 2px; box-shadow: 0 0 0 3px color-mix(in srgb, var(--brand) 25%, transparent); }
  .section-badge { font-size: 0.72rem; padding: 2px 9px; border-radius: 999px; background: var(--fill); color: var(--label-2); font-weight: 600; }
  .section-badge.lang { background: var(--fill); color: var(--label); }
  .section-meta { font-size: 0.75rem; color: var(--label-3); font-variant-numeric: tabular-nums; }
  .section-added { font-size: 0.75rem; color: var(--label-2); margin-left: auto; font-variant-numeric: tabular-nums; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(272px, 1fr)); gap: 20px; }

  /* ---------- Karty ---------- */
  .ccard { background: var(--bg-elev); border-radius: 18px; overflow: hidden; position: relative; display: flex; flex-direction: column; box-shadow: var(--shadow); transition: transform 0.35s cubic-bezier(0.2,0.9,0.3,1), box-shadow 0.35s ease; }
  .ccard:hover { transform: translateY(-3px); box-shadow: var(--shadow-sm), var(--shadow-lg); }
  .ccard::after { content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; box-shadow: inset 0 0 0 0 transparent; transition: box-shadow 0.25s ease; z-index: 6; }
  .ccard[data-qa="fail"]::after { box-shadow: inset 0 0 0 3px var(--q-fail); }
  .ccard[data-qa="fix"]::after { box-shadow: inset 0 0 0 3px var(--q-fix); }
  .ccard[data-qa="stale"]::after { box-shadow: inset 0 0 0 3px color-mix(in srgb, var(--q-stale) 80%, transparent); }
  .ccard[data-qa="pass"]::after { box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--q-pass) 70%, transparent); }
  .stage { position: relative; height: 300px; background: var(--stage); cursor: zoom-in; }
  .stage-img { width: 100%; height: 100%; object-fit: contain; display: block; }

  /* Štítky nad obrázkom = tmavé sklo (čitateľné nad akýmkoľvek banerom, v oboch režimoch) */
  .brand-tag, .country-tag, .fmt-tag, .merged-tag, .lin-tag, .stage .dur-tag { position: absolute; z-index: 4; color: #fff; font-size: 0.66rem; font-weight: 600; letter-spacing: 0.01em; padding: 3px 8px; border-radius: 999px; backdrop-filter: blur(12px) saturate(160%); -webkit-backdrop-filter: blur(12px) saturate(160%); }
  .brand-tag { top: 10px; left: 10px; text-transform: uppercase; letter-spacing: 0.04em; }
  .country-tag { top: 36px; left: 10px; background: rgba(0,0,0,0.45); }
  .lin-tag { top: 62px; left: 10px; background: color-mix(in srgb, var(--teal) 75%, rgba(0,0,0,0.5)); text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.6rem; }
  .fmt-tag { bottom: 10px; left: 10px; background: rgba(0,0,0,0.45); font-variant-numeric: tabular-nums; }
  .merged-tag { bottom: 10px; right: 10px; background: rgba(0,0,0,0.45); }

  /* QA tlačidlá: ✓ PASS · ✎ drobná oprava · ✕ FAIL */
  .qa-bar { position: absolute; top: 10px; right: 10px; z-index: 7; display: flex; gap: 5px; padding: 3px; border-radius: 999px; background: rgba(0,0,0,0.35); backdrop-filter: blur(14px) saturate(160%); -webkit-backdrop-filter: blur(14px) saturate(160%); opacity: 0; transform: translateY(-3px); transition: opacity 0.18s ease, transform 0.25s cubic-bezier(0.2,0.9,0.3,1); }
  .ccard:hover .qa-bar, .ccard .qa-bar:has(.on), .ccard .qa-bar:focus-within { opacity: 1; transform: none; }
  .qa-btn { background: transparent; border: none; color: #fff; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; font-size: 0.88rem; font-weight: 700; line-height: 1; display: flex; align-items: center; justify-content: center; transition: background-color 0.15s ease, transform 0.1s ease-out; }
  .qa-btn:hover { background: rgba(255,255,255,0.18); }
  .qa-btn:active { transform: scale(0.9); }
  .qa-btn.qa-pass.on { background: var(--q-pass); }
  .qa-btn.qa-fix.on { background: var(--q-fix); }
  .qa-btn.qa-fail.on { background: var(--q-fail); }
  .qa-badge { font-size: 0.66rem; font-weight: 600; padding: 3px 8px; border-radius: 999px; color: #fff; white-space: nowrap; }
  .qa-badge:empty { display: none; }
  .stage .qa-badge { position: absolute; top: 50px; right: 10px; z-index: 5; box-shadow: var(--shadow-sm); }
  .qa-badge.q-pass { background: var(--q-pass); } .qa-badge.q-fix { background: var(--q-fix); }
  .qa-badge.q-fail { background: var(--q-fail); } .qa-badge.q-stale { background: var(--q-stale); }

  /* Prepínač formátov */
  .thumbs { display: flex; gap: 6px; padding: 10px 12px 0; flex-wrap: wrap; }
  .thumb { position: relative; background: var(--stage); border: none; box-shadow: inset 0 0 0 1.5px var(--sep); border-radius: 10px; padding: 3px; cursor: pointer; width: 54px; display: flex; flex-direction: column; align-items: center; gap: 2px; transition: box-shadow 0.15s, transform 0.1s; }
  .thumb:active { transform: scale(0.95); }
  .thumb img { width: 100%; height: 40px; object-fit: contain; display: block; border-radius: 6px; }
  .thumb span { font-size: 0.6rem; color: var(--label-2); font-weight: 600; font-variant-numeric: tabular-nums; }
  .thumb.active { box-shadow: inset 0 0 0 2px var(--accent); }
  .thumb.active span { color: var(--accent); }
  .thumb[data-qa]:not([data-qa="none"])::after { content: ''; position: absolute; top: 3px; right: 3px; width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 0 2px var(--bg-elev); }
  .thumb[data-qa="fail"]::after, .lb-formats button[data-qa="fail"]::after { background: var(--q-fail); }
  .thumb[data-qa="fix"]::after, .lb-formats button[data-qa="fix"]::after { background: var(--q-fix); }
  .thumb[data-qa="stale"]::after, .lb-formats button[data-qa="stale"]::after { background: var(--q-stale); }
  .thumb[data-qa="pass"]::after, .lb-formats button[data-qa="pass"]::after { background: var(--q-pass); }

  .card-info { padding: 12px 14px 14px; }
  .card-info h4 { font-size: 0.86rem; font-weight: 600; letter-spacing: -0.01em; margin-bottom: 4px; color: var(--label); line-height: 1.3; }
  .tnum { color: var(--label-2); font-weight: 500; font-variant-numeric: tabular-nums; }
  .var-badge { color: #fff; padding: 1px 7px; border-radius: 999px; font-size: 0.66rem; font-weight: 600; vertical-align: 1px; }
  .card-info .hl { font-size: 0.78rem; color: var(--label-2); margin-bottom: 6px; line-height: 1.4; }
  .card-info .meta { font-size: 0.72rem; color: var(--label-3); display: flex; align-items: center; gap: 4px; font-variant-numeric: tabular-nums; }
  .reveal-btn, .sel-btn { background: none; border: none; cursor: pointer; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.85rem; color: var(--label-2); transition: background-color 0.15s, color 0.15s, transform 0.1s; }
  .reveal-btn { margin-left: auto; }
  .reveal-btn:hover, .sel-btn:hover { background: var(--fill); }
  .reveal-btn:active, .sel-btn:active { transform: scale(0.9); }
  .sel-btn.on { color: var(--accent); background: var(--accent-tint); }

  /* Poznámka „čo opraviť" — píše sa priamo do karty / náhľadu, ukladá sa počas písania */
  .note-row { margin-top: 8px; }
  .note-input { width: 100%; resize: vertical; min-height: 46px; font: inherit; font-size: 0.8rem; line-height: 1.4; color: var(--label); background: color-mix(in srgb, var(--q-fix) 10%, var(--bg-elev)); border: none; box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--q-fix) 35%, transparent); border-radius: 12px; padding: 9px 11px; outline: none; transition: box-shadow 0.15s ease, background-color 0.15s ease; }
  .note-input::placeholder { color: var(--label-3); }
  .note-input:focus { box-shadow: inset 0 0 0 1.5px var(--q-fix), 0 0 0 4px color-mix(in srgb, var(--q-fix) 18%, transparent); }
  .ccard[data-qa="fail"] .note-input { background: color-mix(in srgb, var(--q-fail) 9%, var(--bg-elev)); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--q-fail) 35%, transparent); }
  .ccard[data-qa="fail"] .note-input:focus { box-shadow: inset 0 0 0 1.5px var(--q-fail), 0 0 0 4px color-mix(in srgb, var(--q-fail) 18%, transparent); }
  .note-hint { display: none; font-size: 0.68rem; color: var(--label-3); margin-top: 4px; }
  .note-row:focus-within .note-hint { display: block; }
  .lightbox .lb-note-input { width: min(520px, 44vw); margin-top: 8px; display: block; font-size: 0.86rem; background: color-mix(in srgb, var(--q-fix) 10%, var(--bg-elev)); }

  .empty-state { text-align: center; padding: 80px 20px; color: var(--label-2); }

  .toast { position: fixed; bottom: 28px; left: 50%; transform: translate(-50%, 12px) scale(0.96); background: var(--material); color: var(--label); backdrop-filter: blur(30px) saturate(180%); -webkit-backdrop-filter: blur(30px) saturate(180%); border: 1px solid var(--material-edge); padding: 11px 20px; border-radius: 999px; font-size: 0.86rem; font-weight: 600; box-shadow: var(--shadow-lg); opacity: 0; transition: opacity 0.2s ease, transform 0.3s cubic-bezier(0.2,0.9,0.3,1); pointer-events: none; z-index: 300; }
  .toast.show { opacity: 1; transform: translate(-50%, 0) scale(1); }
  .toast.err { color: var(--q-fail); }

  /* ---------- Lightbox = rozmazaná vrstva nad obsahom ---------- */
  .lightbox { position: fixed; inset: 0; background: var(--scrim); backdrop-filter: blur(28px) saturate(140%); -webkit-backdrop-filter: blur(28px) saturate(140%); z-index: 200; display: none; align-items: center; justify-content: center; }
  .lightbox.open { display: flex; animation: lb-in 0.22s ease; }
  @keyframes lb-in { from { opacity: 0; } to { opacity: 1; } }
  .lightbox .lb-img { max-width: 86vw; max-height: 72vh; object-fit: contain; border-radius: 14px; box-shadow: var(--shadow-lg); background: var(--stage); animation: lb-img-in 0.3s cubic-bezier(0.2,0.9,0.3,1); }
  @keyframes lb-img-in { from { transform: scale(0.97); opacity: 0.6; } to { transform: none; opacity: 1; } }
  .lightbox .lb-close, .lightbox .lb-note, .lightbox .lb-compare-btn, .lightbox .lb-lineage-btn, .lightbox .lb-select, .lightbox .lb-qa .qa-btn, .compare-head button { background: var(--glass); border: none; color: var(--on-glass); width: 44px; height: 44px; border-radius: 50%; font-size: 1.05rem; cursor: pointer; line-height: 1; display: inline-flex; align-items: center; justify-content: center; transition: background-color 0.15s ease, transform 0.1s ease-out; }
  .lightbox .lb-close:hover, .lightbox .lb-note:hover, .lightbox .lb-compare-btn:hover, .lightbox .lb-lineage-btn:hover, .lightbox .lb-select:hover, .lightbox .lb-qa .qa-btn:hover, .compare-head button:hover { background: var(--glass-h); }
  .lightbox button:active, .compare-head button:active { transform: scale(0.92); }
  .lightbox .lb-close { position: fixed; top: 18px; right: 24px; z-index: 201; }
  .lightbox .lb-note { position: fixed; top: 18px; right: 78px; z-index: 201; }
  .lightbox .lb-compare-btn { position: fixed; top: 18px; right: 132px; z-index: 201; }
  .lightbox .lb-lineage-btn { position: fixed; top: 18px; right: 186px; z-index: 203; display: none; }
  .lightbox .lb-lineage-btn.avail { display: inline-flex; }
  .lightbox.compare .lb-compare-btn, .lightbox.lineage-open .lb-lineage-btn { background: var(--accent); color: #fff; }
  .lightbox .lb-qa { position: fixed; top: 18px; left: 24px; z-index: 203; display: grid; grid-template-columns: repeat(4, 44px); gap: 8px; }
  .lightbox .lb-qa .qa-btn.qa-pass.on { background: var(--q-pass); color: #fff; }
  .lightbox .lb-qa .qa-btn.qa-fix.on { background: var(--q-fix); color: #fff; }
  .lightbox .lb-qa .qa-btn.qa-fail.on { background: var(--q-fail); color: #fff; }
  .lightbox .lb-select.on { background: var(--accent); color: #fff; }
  .lightbox .lb-qa-info { grid-column: 1 / -1; justify-self: start; width: max-content; max-width: 46vw; font-size: 0.78rem; color: var(--label); line-height: 1.5; background: var(--material); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid var(--material-edge); border-radius: 14px; padding: 8px 12px; box-shadow: var(--shadow); }
  .lightbox .lb-qa-info:empty { display: none; }
  .lightbox .lb-qa-info .muted { color: var(--label-2); }
  .lightbox .lb-qa-note { color: var(--q-fix); }
  .lightbox .lb-brief { margin: 8px 8px 0 0; background: var(--fill); border: none; color: var(--label); font-size: 0.78rem; font-weight: 600; padding: 6px 12px; border-radius: 999px; cursor: pointer; }
  .lightbox .lb-brief:hover { background: var(--fill-2); }
  .lightbox .lb-prev, .lightbox .lb-next { position: fixed; top: 50%; transform: translateY(-50%); background: var(--glass); border: none; color: var(--on-glass); width: 48px; height: 48px; border-radius: 50%; font-size: 1.6rem; cursor: pointer; line-height: 1; z-index: 201; transition: background-color 0.15s ease; }
  .lightbox .lb-prev { left: 22px; } .lightbox .lb-next { right: 22px; }
  .lightbox .lb-prev:hover, .lightbox .lb-next:hover { background: var(--glass-h); }
  .lightbox .lb-prev:active, .lightbox .lb-next:active { transform: translateY(-50%) scale(0.92); }
  /* Pásik s ostatnými rozmermi toho istého motívu */
  .lightbox .lb-formats { position: fixed; bottom: 62px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 201; background: var(--material); backdrop-filter: blur(24px) saturate(180%); -webkit-backdrop-filter: blur(24px) saturate(180%); padding: 7px; border-radius: 16px; border: 1px solid var(--material-edge); box-shadow: var(--shadow); max-width: 92vw; overflow-x: auto; }
  .lightbox .lb-formats button { position: relative; background: var(--stage); border: none; box-shadow: inset 0 0 0 1.5px var(--sep); border-radius: 10px; padding: 3px; cursor: pointer; width: 62px; flex: 0 0 auto; display: flex; flex-direction: column; align-items: center; gap: 2px; }
  .lightbox .lb-formats button img { width: 100%; height: 54px; object-fit: contain; display: block; border-radius: 7px; }
  .lightbox .lb-formats button span { font-size: 0.62rem; color: var(--label-2); font-weight: 600; }
  .lightbox .lb-formats button.active { box-shadow: inset 0 0 0 2px var(--accent); }
  .lightbox .lb-formats button.active span { color: var(--accent); }
  .lightbox .lb-formats button[data-qa]:not([data-qa="none"])::after { content: ''; position: absolute; top: 4px; right: 4px; width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 0 2px var(--bg-elev); }

  /* Režim: všetky rozmery vedľa seba */
  .lightbox .lb-compare { display: none; gap: 18px; align-items: center; justify-content: center; width: 92vw; }
  .lightbox.compare .lb-compare { display: flex; }
  .lightbox.compare .lb-img, .lightbox.compare .lb-formats,
  .lightbox.compare .lb-prev, .lightbox.compare .lb-next { display: none; }
  .lb-compare figure { display: flex; flex-direction: column; align-items: center; gap: 8px; cursor: pointer; flex: 1 1 0; min-width: 0; }
  .lb-compare img { max-height: 72vh; max-width: 100%; object-fit: contain; border-radius: 12px; background: var(--stage); box-shadow: var(--shadow); outline: 3px solid transparent; outline-offset: 3px; transition: outline-color 0.15s; }
  .lb-compare figure.active img { outline-color: var(--accent); }
  .lb-compare figcaption { color: var(--label-2); font-size: 0.8rem; font-weight: 600; }
  .lb-compare figure[data-qa="fail"] figcaption::after { content: ' ✕'; color: var(--q-fail); }
  .lb-compare figure[data-qa="fix"] figcaption::after { content: ' ✎'; color: var(--q-fix); }
  .lb-compare figure[data-qa="stale"] figcaption::after { content: ' ↻'; color: var(--q-stale); }
  .lb-compare figure[data-qa="pass"] figcaption::after { content: ' ✓'; color: var(--q-pass); }
  .lightbox .lb-caption { position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); color: var(--label); font-size: 0.82rem; font-weight: 500; background: var(--material); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid var(--material-edge); padding: 7px 16px; border-radius: 999px; text-align: center; max-width: 84vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; box-shadow: var(--shadow-sm); }

  /* ---------- Video karty (PVF) ---------- */
  .ccard.is-video .stage { cursor: pointer; }
  .stage .play-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 54px; height: 54px; border-radius: 50%; background: rgba(0,0,0,0.35); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); color: #fff; font-size: 1.15rem; display: flex; align-items: center; justify-content: center; pointer-events: none; z-index: 3; padding-left: 3px; transition: transform 0.25s cubic-bezier(0.2,0.9,0.3,1), background-color 0.2s; }
  .ccard.is-video:hover .play-overlay { transform: translate(-50%,-50%) scale(1.08); background: rgba(0,0,0,0.5); }
  .stage .dur-tag { bottom: 10px; right: 10px; background: rgba(0,0,0,0.45); font-variant-numeric: tabular-nums; }
  .vid-badge { display: inline-block; background: var(--q-stale); color: #fff; font-size: 0.62rem; font-weight: 600; padding: 1px 7px; border-radius: 999px; margin-left: 2px; vertical-align: 1px; }

  .lightbox .lb-video { max-width: 86vw; max-height: 78vh; border-radius: 14px; box-shadow: var(--shadow-lg); background: #000; display: none; }
  .lightbox.video-mode .lb-video { display: block; }
  .lightbox.video-mode .lb-img, .lightbox.video-mode .lb-formats,
  .lightbox.video-mode .lb-compare-btn { display: none; }
  .lightbox .lb-transcript { position: fixed; bottom: 64px; left: 50%; transform: translateX(-50%); color: var(--label); font-size: 0.8rem; background: var(--material); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); padding: 8px 16px; border-radius: 14px; text-align: center; max-width: 72vw; line-height: 1.45; display: none; }
  .lightbox.video-mode .lb-transcript.has-text { display: block; }

  /* ---------- Rodokmeň kreatívy (z čoho vznikla) ---------- */
  .lin-row { font-size: 0.74rem; color: var(--teal); margin-top: 6px; line-height: 1.3; cursor: help; }
  .lin-row b { color: var(--teal); font-weight: 600; }
  .lightbox .lb-lineage { position: fixed; top: 0; right: 0; width: 340px; height: 100%; background: var(--material); backdrop-filter: blur(30px) saturate(180%); -webkit-backdrop-filter: blur(30px) saturate(180%); border-left: 1px solid var(--material-edge); padding: 76px 20px 20px; overflow-y: auto; z-index: 202; display: none; box-shadow: var(--shadow-lg); }
  .lightbox.lineage-open .lb-lineage { display: block; animation: sheet-in 0.32s cubic-bezier(0.2,0.9,0.3,1); }
  @keyframes sheet-in { from { transform: translateX(24px); opacity: 0; } to { transform: none; opacity: 1; } }
  .lightbox.lineage-open .lb-img, .lightbox.lineage-open .lb-video { max-width: calc(86vw - 340px); }
  .lb-lineage h3 { font-size: 1.05rem; font-weight: 700; letter-spacing: -0.02em; color: var(--label); margin-bottom: 2px; }
  .lb-lineage .lin-window { font-size: 0.72rem; color: var(--label-2); margin-bottom: 14px; }
  .lb-lineage h4 { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--label-2); margin: 18px 0 8px; }
  .lb-lineage p { font-size: 0.82rem; color: var(--label); line-height: 1.5; }
  .lb-lineage p.lin-driver { background: color-mix(in srgb, var(--teal) 14%, transparent); padding: 9px 12px; border-radius: 12px; }
  .lb-lineage p.lin-offer { background: color-mix(in srgb, var(--q-fix) 14%, transparent); padding: 9px 12px; border-radius: 12px; }
  .lb-win { display: flex; gap: 11px; background: var(--bg-elev); border-radius: 14px; padding: 9px; margin-bottom: 9px; box-shadow: var(--shadow-sm); }
  .lb-win img { width: 62px; height: 78px; object-fit: cover; border-radius: 9px; background: #000; flex: 0 0 auto; }
  .lb-win .w-body { min-width: 0; }
  .lb-win .w-name { font-size: 0.76rem; color: var(--label); font-weight: 600; line-height: 1.3; margin-bottom: 4px; word-break: break-word; }
  .lb-win .w-metrics { font-size: 0.72rem; color: var(--label-2); line-height: 1.55; font-variant-numeric: tabular-nums; }
  .lb-win .w-metrics b { color: var(--q-pass); }
  .lb-win .w-state { display: inline-block; font-size: 0.6rem; padding: 2px 7px; border-radius: 999px; background: var(--fill); color: var(--label-2); margin-top: 3px; text-transform: uppercase; font-weight: 600; }
  .lb-win .w-state.declining { background: color-mix(in srgb, var(--q-fail) 18%, transparent); color: var(--q-fail); }

  /* ---------- Výber + porovnanie vedľa seba + PDF ---------- */
  .sel-bar { position: fixed; bottom: 22px; left: 50%; transform: translate(-50%, 160%); background: var(--material); backdrop-filter: blur(30px) saturate(180%); -webkit-backdrop-filter: blur(30px) saturate(180%); border: 1px solid var(--material-edge); border-radius: 999px; padding: 7px 8px 7px 18px; display: flex; gap: 6px; align-items: center; z-index: 150; box-shadow: var(--shadow-lg); transition: transform 0.4s cubic-bezier(0.2,0.9,0.3,1); font-size: 0.84rem; }
  .sel-bar { visibility: hidden; }
  .sel-bar.show { transform: translate(-50%, 0); visibility: visible; }
  .sel-bar > span { margin-right: 6px; color: var(--label-2); }
  .sel-bar b { color: var(--accent); }
  .compare-view { position: fixed; inset: 0; background: var(--bg); z-index: 250; display: none; flex-direction: column; overflow-y: auto; padding: 20px 26px 48px; }
  .compare-view.open { display: flex; animation: lb-in 0.22s ease; }
  .compare-head { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
  .compare-head h2 { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.025em; color: var(--label); }
  .compare-head .print-meta { display: none; }
  .compare-head button { margin-left: auto; }
  .compare-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 20px; align-items: start; }
  .cmp-item { background: var(--bg-elev); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow); position: relative; }
  .cmp-item::after { content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; }
  .cmp-item[data-qa="fail"]::after { box-shadow: inset 0 0 0 3px var(--q-fail); } .cmp-item[data-qa="fix"]::after { box-shadow: inset 0 0 0 3px var(--q-fix); }
  .cmp-item[data-qa="stale"]::after { box-shadow: inset 0 0 0 3px var(--q-stale); } .cmp-item[data-qa="pass"]::after { box-shadow: inset 0 0 0 2px var(--q-pass); }
  .cmp-item img, .cmp-item video { width: 100%; max-height: 70vh; object-fit: contain; display: block; background: var(--stage); }
  .cmp-item figcaption { padding: 11px 13px 13px; font-size: 0.8rem; color: var(--label); line-height: 1.45; }
  .cmp-item .cmp-hl { color: var(--label-2); } .cmp-item .cmp-note { color: var(--q-fix); }
  .cmp-qa { display: flex; gap: 5px; align-items: center; margin-top: 9px; position: relative; z-index: 1; }
  .cmp-qa .qa-badge { margin-right: auto; }
  .cmp-qa .qa-btn { width: 30px; height: 30px; font-size: 0.82rem; background: var(--fill); color: var(--label); }
  .cmp-qa .qa-btn:hover { background: var(--fill-2); }
  .cmp-qa .qa-btn.on { color: #fff; }
  .cmp-remove { background: var(--fill); border: none; color: var(--label-2); width: 30px; height: 30px; border-radius: 50%; cursor: pointer; }

  .refresh-btn { background: var(--fill); border: none; color: var(--label); padding: 7px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background-color 0.15s ease, transform 0.1s ease-out; }
  .refresh-btn:hover { background: var(--fill-2); }
  .refresh-btn:active { transform: scale(0.97); }
  .refresh-btn.busy { color: var(--accent); cursor: progress; }
  .headrow > .refresh-btn { margin-left: auto; }
  .headrow > .refresh-btn + .theme-toggle { margin-left: 0; }

  /* ---------- Taby (segmented control) ---------- */
  .tabs { display: flex; gap: 2px; padding: 3px; background: var(--fill); border-radius: 12px; margin-left: 10px; }
  .tabs button { background: transparent; border: none; color: var(--label-2); font-size: 0.86rem; font-weight: 600; padding: 7px 14px; border-radius: 9px; cursor: pointer; white-space: nowrap; transition: background-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease, transform 0.1s ease-out; }
  .tabs button span { font-weight: 500; color: var(--label-3); margin-left: 3px; font-variant-numeric: tabular-nums; }
  .tabs button:hover { color: var(--label); }
  .tabs button:active { transform: scale(0.97); }
  .tabs button[aria-selected="true"] { background: var(--bg-elev); color: var(--label); box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 0 0 0.5px var(--material-edge); }
  :root[data-theme="dark"] .tabs button[aria-selected="true"] { background: #636366; }
  .tabs button[aria-selected="true"] span { color: var(--label-2); }
  .headrow > .theme-toggle { margin-left: auto; }
  .tab-panel { display: none; }
  body[data-tab="banners"] #sections, body[data-tab="video"] #sections { display: block; }
  body[data-tab="styles"] #panel-styles, body[data-tab="system"] #panel-system, body[data-tab="stats"] #panel-stats { display: block; animation: lb-in 0.2s ease; }
  body[data-tab="styles"] .grid-only, body[data-tab="system"] .grid-only, body[data-tab="stats"] .grid-only { display: none !important; }
  body[data-tab="styles"] header .headrow, body[data-tab="system"] header .headrow, body[data-tab="stats"] header .headrow { margin-bottom: 0; }

  /* ---------- Panely: spoločné ---------- */
  .panel-section { margin-bottom: 44px; }
  .panel-head { margin-bottom: 16px; max-width: 900px; }
  .panel-head h2 { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.025em; margin-bottom: 6px; }
  .panel-head h2 .count { font-size: 0.95rem; font-weight: 600; color: var(--label-3); margin-left: 4px; }
  .panel-head p { color: var(--label-2); font-size: 0.9rem; line-height: 1.5; }
  .panel-search { margin-top: 12px; width: min(420px, 100%); background: var(--fill); border: none; color: var(--label); padding: 9px 14px; border-radius: 10px; font-size: 0.88rem; }
  .panel-search:focus { outline: none; box-shadow: 0 0 0 3px var(--accent-tint); }
  code { font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 0.86em; background: var(--fill); padding: 1px 6px; border-radius: 6px; }
  .chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
  .chip { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; background: var(--fill); color: var(--label-2); }
  .chip.ok { background: color-mix(in srgb, var(--q-pass) 16%, transparent); color: var(--q-pass); }
  .chip.accent { background: var(--accent-tint); color: var(--accent); }
  details { margin-top: 10px; }
  details summary { cursor: pointer; font-size: 0.8rem; font-weight: 600; color: var(--accent); list-style: none; }
  details summary::-webkit-details-marker { display: none; }
  details summary::before { content: '›'; display: inline-block; margin-right: 6px; transition: transform 0.2s ease; }
  details[open] summary::before { transform: rotate(90deg); }
  details ul { margin: 8px 0 0 18px; font-size: 0.8rem; color: var(--label-2); line-height: 1.5; }
  details pre { margin-top: 8px; white-space: pre-wrap; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 0.72rem; line-height: 1.5; color: var(--label-2); background: var(--bg-elev2); padding: 10px 12px; border-radius: 10px; max-height: 260px; overflow: auto; }

  /* Vizuálne štýly */
  .st-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
  .st-card { background: var(--bg-elev); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow); display: flex; flex-direction: column; }
  .st-gallery { display: flex; gap: 2px; height: 170px; background: var(--stage); overflow-x: auto; scrollbar-width: none; }
  .st-gallery img { height: 100%; width: auto; flex: 0 0 auto; object-fit: cover; }
  .st-gallery img.sample { outline: 2px solid var(--accent); outline-offset: -2px; }
  .st-noimg { margin: auto; color: var(--label-3); font-size: 0.8rem; }
  .st-body { padding: 14px 16px 16px; }
  .st-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
  .st-head h3 { font-size: 1.05rem; font-weight: 700; letter-spacing: -0.015em; }
  .st-used { margin-left: auto; font-size: 0.72rem; font-weight: 600; color: var(--accent); }
  .st-used.none { color: var(--label-3); }
  .st-summary { margin-top: 6px; font-size: 0.84rem; line-height: 1.5; color: var(--label); }
  .st-when { margin-top: 6px; font-size: 0.8rem; line-height: 1.5; color: var(--label-2); }

  /* Templaty */
  .tp-toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 18px; }
  .tp-toolbar .panel-search { margin-top: 0; width: 280px; }
  .tp-seg { display: flex; flex-wrap: wrap; gap: 2px; padding: 3px; background: var(--fill); border-radius: 12px; }
  .tp-seg button { background: transparent; border: none; color: var(--label-2); font-size: 0.82rem; font-weight: 600; padding: 6px 12px; border-radius: 9px; cursor: pointer; transition: background-color 0.2s, color 0.2s, transform 0.1s; }
  .tp-seg button span { color: var(--label-3); font-weight: 500; margin-left: 2px; }
  .tp-seg button:hover { color: var(--label); }
  .tp-seg button:active { transform: scale(0.97); }
  .tp-seg button[aria-pressed="true"] { background: var(--bg-elev); color: var(--label); box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
  :root[data-theme="dark"] .tp-seg button[aria-pressed="true"] { background: #636366; }
  .tp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
  .tp-card { background: var(--bg-elev); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow); display: flex; flex-direction: column; transition: transform 0.35s cubic-bezier(0.2,0.9,0.3,1), box-shadow 0.35s ease; }
  .tp-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-sm), var(--shadow-lg); }
  .tp-stage { position: relative; height: 270px; padding: 18px; background: var(--stage); display: flex; justify-content: center; align-items: center; }
  .tp-stage > .mk { height: 100%; }
  .tp-ai { height: 100%; width: auto; max-width: 100%; object-fit: contain; border-radius: 10px; box-shadow: var(--shadow); }
  .tp-sketch-alt { display: none; height: 100%; }
  .tp-kind { position: absolute; top: 10px; right: 10px; font-size: 0.64rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; background: var(--material); color: var(--label-2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }
  .tp-kind.ai { color: var(--accent); }
  .tp-body { padding: 13px 15px 15px; }
  .tp-title { display: flex; gap: 8px; align-items: baseline; }
  .tp-num { font-size: 0.78rem; font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; }
  .tp-body h3 { font-size: 0.95rem; font-weight: 700; letter-spacing: -0.01em; line-height: 1.25; }
  .tp-tag { font-size: 0.8rem; color: var(--label-2); margin-top: 4px; line-height: 1.4; }
  .tp-what { font-size: 0.78rem; color: var(--label-2); margin-top: 8px; line-height: 1.5; }
  .tp-styles { font-size: 0.72rem; color: var(--label-3); margin-top: 6px; }

  /* Pod kapotou: split screen */
  .split { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 36px; align-items: start; }
  .split-col { background: var(--bg-elev); border-radius: 20px; box-shadow: var(--shadow); padding: 20px 22px 12px; }
  .split-head { display: flex; gap: 14px; align-items: center; margin-bottom: 12px; }
  .split-icon { width: 46px; height: 46px; border-radius: 13px; background: var(--fill); display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex: 0 0 auto; }
  .split-head h2 { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; }
  .split-head p { font-size: 0.8rem; color: var(--label-2); margin-top: 2px; }
  .ver-chip { font-size: 0.7rem; font-weight: 600; background: var(--accent-tint); color: var(--accent); padding: 2px 8px; border-radius: 999px; vertical-align: 3px; }
  .flow { font-size: 0.78rem; color: var(--label-2); background: var(--bg-elev2); border-radius: 12px; padding: 9px 12px; margin-bottom: 8px; line-height: 1.6; }
  .flow span { color: var(--label); font-weight: 600; }
  .files { list-style: none; }
  .files li { display: grid; grid-template-columns: minmax(150px, 38%) 1fr; gap: 14px; padding: 11px 0; border-top: 1px solid var(--sep); font-size: 0.82rem; line-height: 1.45; }
  .files li:first-child { border-top: none; }
  .files code.path { background: none; padding: 0; color: var(--accent); font-weight: 600; word-break: break-word; }
  .files span { color: var(--label-2); }
  .files span code { font-size: 0.8em; }
  .api-wrap { background: var(--bg-elev); border-radius: 18px; box-shadow: var(--shadow); overflow-x: auto; }
  .api-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
  .api-table th { text-align: left; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--label-3); padding: 12px 16px 8px; }
  .api-table td { padding: 12px 16px; border-top: 1px solid var(--sep); vertical-align: top; line-height: 1.45; color: var(--label-2); }
  .api-table td:first-child { color: var(--label); white-space: nowrap; }
  .api-key { font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 0.7rem; color: var(--label-3); margin-top: 2px; }
  .api-detail { margin-top: 5px; font-size: 0.76rem; color: var(--label-3); }
  .api-detail b { color: var(--label-2); }
  .api-st { display: inline-block; font-size: 0.74rem; font-weight: 600; padding: 3px 10px; border-radius: 999px; white-space: nowrap; }
  .api-st.ok { background: color-mix(in srgb, var(--q-pass) 16%, transparent); color: var(--q-pass); }
  .api-st.off { background: var(--fill); color: var(--label-3); }
  .api-st.bad { background: color-mix(in srgb, var(--q-fail) 16%, transparent); color: var(--q-fail); }
  .tree { background: var(--bg-elev); border-radius: 20px; box-shadow: var(--shadow); padding: 20px 22px; margin-bottom: 20px; }
  .tree-head { display: flex; gap: 14px; align-items: center; margin-bottom: 14px; }
  .split-icon.brand-icon .logo-mark { height: 28px; }
  .tree-head .tagline { font-size: 0.92rem; font-weight: 600; color: var(--label-2); letter-spacing: -0.01em; margin-top: 0; }
  .tree-head h2 { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.025em; }
  .tree-head p { font-size: 0.8rem; color: var(--label-2); margin-top: 2px; }
  .tree-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .tree-grid > div { background: var(--bg-elev2); border-radius: 14px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; line-height: 1.45; }
  .tree-grid code.path { background: none; padding: 0; color: var(--accent); font-weight: 700; font-size: 0.9rem; }
  .tree-grid span { color: var(--label-2); }
  .tree-note { margin-top: 12px; font-size: 0.76rem; color: var(--label-3); }
  @media (max-width: 1100px) { .split { grid-template-columns: 1fr; } .tree-grid { grid-template-columns: 1fr 1fr; } }

  /* ---------- Prístupnosť ---------- */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
    .ccard:hover { transform: none; }
  }
  @media (prefers-reduced-transparency: reduce) {
    header, .dl-menu, .toast, .sel-bar, .lightbox .lb-formats, .lightbox .lb-caption, .lightbox .lb-lineage, .lightbox .lb-qa-info { background: var(--bg-elev); backdrop-filter: none; -webkit-backdrop-filter: none; }
    .lightbox { background: var(--bg); backdrop-filter: none; -webkit-backdrop-filter: none; }
  }

  @media print {
    body.printing > *:not(.compare-view) { display: none !important; }
    body.printing { background: #fff; padding: 0; color: #000; }
    body.printing .compare-view { position: static; display: block; background: #fff; overflow: visible; padding: 0; }
    body.printing .compare-head h2 { color: #111; }
    body.printing .compare-head .print-meta { display: inline; color: #666; font-size: 0.75rem; }
    body.printing .compare-head button, body.printing .cmp-qa .qa-btn, body.printing .cmp-remove { display: none; }
    body.printing .compare-grid { grid-template-columns: repeat(2, 1fr); }
    body.printing .cmp-item { break-inside: avoid; background: #fff; box-shadow: none; border: 1px solid #ddd; }
    body.printing .cmp-item img { background: #fff; max-height: 115mm; }
    body.printing .cmp-item figcaption { color: #222; }
    body.printing .cmp-item .cmp-hl { color: #555; }
  }
"""

JS = """
  // ---------- QA store (v3): flagged.json = na opravu (FAIL / oprava), approved.json = PASS ----------
  // Každé hodnotenie nesie SHA-256 súboru, ku ktorému patrí. Keď sa banner pregeneruje,
  // hash nesedí → stav „Prehodnotiť" (pôvodný verdikt ostane v histórii).
  const STORAGE_KEY = 'ad-gen-flagged';
  const APPROVED_KEY = 'ad-gen-approved';
  const SELECTION_KEY = 'ad-gen-selection';
  let FLAGS = {};
  let APPROVED = {};
  let SERVER_MODE = false;
  const QA_LABEL = { pass: 'PASS', fix: 'Drobná oprava', fail: 'FAIL', stale: 'Prehodnotiť', none: 'Nehodnotené' };
  const QA_ICON = { pass: '✓', fix: '✎', fail: '✕', stale: '↻', none: '' };

  function readLocal(key) {
    try { return JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) { return {}; }
  }

  async function loadFlags() {
    try {
      const [rf, ra] = await Promise.all([
        fetch('/api/flags', { cache: 'no-store' }),
        fetch('/api/approved', { cache: 'no-store' }),
      ]);
      if (!rf.ok || !ra.ok) throw new Error(rf.status + '/' + ra.status);
      FLAGS = await rf.json();
      APPROVED = await ra.json();
      SERVER_MODE = true;
    } catch (e) {
      FLAGS = readLocal(STORAGE_KEY);
      APPROVED = readLocal(APPROVED_KEY);
      SERVER_MODE = false;
    }
    const dot = document.getElementById('srv-dot');
    dot.classList.toggle('on', SERVER_MODE);
    dot.title = SERVER_MODE ? 'Hodnotenia sa ukladajú do flagged.json / approved.json (server beží)' : 'Server nebeží — hodnotenia len v prehliadači (localStorage)';
  }

  // Staré v2 flagy nemajú stav ani hash: stav = drobná oprava; hash = aktuálny súbor,
  // pokiaľ súbor nebol pregenerovaný až po flagnutí (vtedy rovno Prehodnotiť).
  function migrateReviews() {
    let changed = false;
    for (const store of [FLAGS, APPROVED]) {
      for (const [id, r] of Object.entries(store)) {
        if (!r.status) { r.status = store === APPROVED ? 'pass' : 'fix'; changed = true; }
        if (r.sha256) continue;
        const hit = MEMBER_INDEX[id];
        if (!hit) continue;
        const at = Date.parse(r.reviewed_at || r.flagged_at || '') || 0;
        r.sha256 = (at && hit.member.mtime * 1000 > at + 60000) ? 'pred-v3' : hit.member.sha;
        changed = true;
      }
    }
    if (changed) persistFlags();
  }

  let persistTimer = null;
  function persistFlags() {
    if (SERVER_MODE) {
      clearTimeout(persistTimer);
      persistTimer = setTimeout(async () => {
        try {
          const [rf, ra] = await Promise.all([
            fetch('/api/flags', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(FLAGS) }),
            fetch('/api/approved', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(APPROVED) }),
          ]);
          if (!rf.ok || !ra.ok) throw new Error(rf.status + '/' + ra.status);
        } catch (e) { showToast('Zápis flagged.json / approved.json zlyhal', true); }
      }, 250);
    } else {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(FLAGS));
      localStorage.setItem(APPROVED_KEY, JSON.stringify(APPROVED));
    }
    updateCounter();
  }

  function reviewOf(id) { return FLAGS[id] || APPROVED[id] || null; }

  function qaState(m) {
    const r = reviewOf(m.id);
    if (!r) return 'none';
    if (!m.sha || r.sha256 !== m.sha) return 'stale';
    return r.status || 'fix';
  }

  // Najhorší stav kolekcie → farba rámu karty
  const QA_RANK = { fail: 0, stale: 1, fix: 2, pass: 3, none: 4 };
  function worstState(members) {
    return members.map(qaState).sort((a, b) => QA_RANK[a] - QA_RANK[b])[0] || 'none';
  }

  function updateCounter() {
    const counts = { fail: 0, fix: 0, stale: 0, pass: 0 };
    Object.values(MEMBER_INDEX).forEach(({ member }) => {
      const s = qaState(member);
      if (s in counts) counts[s]++;
    });
    for (const k in counts) document.getElementById('qa-n-' + k).textContent = counts[k];
  }

  function showToast(msg, isErr) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.toggle('err', !!isErr);
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2400);
  }

  // ---------- Karty / kolekcie ----------
  const CARDS = [];           // { el, members, active }
  const MEMBER_INDEX = {};    // id → { member, card }

  function initCards() {
    document.querySelectorAll('.ccard').forEach(el => {
      let members = [];
      try { members = JSON.parse(el.querySelector('.members-data').textContent); } catch (e) {}
      const card = { el, members, active: 0 };
      el._card = card;
      CARDS.push(card);
      members.forEach(m => { MEMBER_INDEX[m.id] = { member: m, card }; });

      el.querySelectorAll('.thumb').forEach(tb => {
        tb.addEventListener('click', e => { e.stopPropagation(); setActive(card, parseInt(tb.dataset.idx)); });
      });
      el.querySelectorAll('.qa-btn').forEach(b => {
        b.addEventListener('click', e => {
          e.stopPropagation();
          if (e.shiftKey) { setStatusAll(card, b.dataset.qa); } else { setStatus(activeMember(card), b.dataset.qa); }
        });
      });
      el.querySelector('.stage').addEventListener('click', e => {
        if (e.target.closest('.qa-bar')) return;
        openLightbox(card);
      });
      const rv = el.querySelector('.reveal-btn');
      if (rv) rv.addEventListener('click', e => { e.stopPropagation(); revealMember(card.members[card.active]); });
      const sb = el.querySelector('.sel-btn');
      if (sb) sb.addEventListener('click', e => { e.stopPropagation(); toggleSelect(activeMember(card)); });
    });
  }

  function activeMember(card) { return card.members[card.active]; }

  function setActive(card, idx) {
    if (idx < 0 || idx >= card.members.length) return;
    card.active = idx;
    const m = card.members[idx];
    const el = card.el;
    el.querySelector('.stage-img').src = m.img_url;
    el.querySelector('.fmt-tag').textContent = m.format;
    el.querySelector('.tnum').textContent = 'T' + String(m.template_num).padStart(2, '0');
    el.querySelector('.adid').textContent = m.ad_id;
    el.querySelector('.var-badge').textContent = (m.variation || 'v?').split('_')[0];
    const hl = el.querySelector('.hl');
    if (m.headline) { hl.textContent = m.headline; } else { hl.innerHTML = '<em>(bez headline)</em>'; }
    el.querySelector('.m-fmt').textContent = m.format;
    el.querySelector('.m-dim').textContent = m.w ? (m.w + '×' + m.h) : '—';
    el.querySelector('.m-kb').textContent = m.size_kb + ' KB';
    el.querySelectorAll('.thumb').forEach(tb => tb.classList.toggle('active', parseInt(tb.dataset.idx) === idx));
    renderCardFlags(card);
  }

  function renderCardFlags(card) {
    const el = card.el;
    const act = activeMember(card);
    const st = qaState(act);
    const rev = reviewOf(act.id);
    el.dataset.qa = worstState(card.members);
    el.querySelectorAll('.qa-btn').forEach(b => b.classList.toggle('on', st === b.dataset.qa));
    const badge = el.querySelector('.qa-badge');
    badge.className = 'qa-badge q-' + st;
    badge.textContent = st === 'none' ? '' : QA_ICON[st] + ' ' + QA_LABEL[st];
    el.querySelectorAll('.thumb').forEach(tb => {
      const s = qaState(MEMBER_INDEX[tb.dataset.mid].member);
      tb.dataset.qa = s;
    });
    const sb = el.querySelector('.sel-btn');
    if (sb) { const on = SELECTION.has(act.id); sb.classList.toggle('on', on); sb.textContent = on ? '☑' : '☐'; }
    const noteRow = el.querySelector('.note-row');
    const input = el.querySelector('.note-input');
    if (st === 'fix' || st === 'fail' || (rev && rev.note && st !== 'stale')) {
      noteRow.hidden = false;
      if (document.activeElement !== input) input.value = (rev && st !== 'stale' && rev.note) || '';
      input.placeholder = st === 'fail' ? 'Prečo FAIL? Čo prerobiť…' : 'Čo opraviť? Píš rovno sem…';
      bindNoteInput(input, () => activeMember(card));
    } else {
      noteRow.hidden = true;
    }
  }

  function renderAllFlags() {
    CARDS.forEach(renderCardFlags);
    updateCounter();
  }

  function flagPayload(m) {
    const p = {
      kind: m.kind || 'image',
      brand: m.brand, country: m.country, product: m.product, adset: m.adset,
      ad_id: m.ad_id, template_name: m.template_name, template_num: m.template_num,
      variation: m.variation, format: m.format, file: m.file, headline: m.headline,
      outputs: m.outputs,
    };
    if (m.kind === 'video') { p.duration = m.duration; p.transcript = m.transcript || ''; }
    return p;
  }

  // Zapíše verdikt; klik na už aktívny (a platný) stav ho zruší. Starý verdikt ide do histórie.
  function writeStatus(m, status, { toggle = true } = {}) {
    const prev = reviewOf(m.id);
    const prevState = qaState(m);
    delete FLAGS[m.id];
    delete APPROVED[m.id];
    if (toggle && prev && prevState === status) return 'cleared';

    const history = (prev && prev.history) ? prev.history.slice() : [];
    if (prev) history.push({ status: prev.status, sha256: prev.sha256, at: prev.reviewed_at || prev.flagged_at, note: prev.note || undefined });
    const now = new Date().toISOString();
    const entry = { ...flagPayload(m), status, sha256: m.sha, reviewed_at: now };
    // poznámka sa vzťahuje na konkrétnu verziu súboru — po regenerácii ostane len v histórii
    if (prev && prev.note && prevState !== 'stale') entry.note = prev.note;
    if (history.length) entry.history = history.slice(-5);
    if (status === 'pass') { APPROVED[m.id] = entry; }
    else { entry.flagged_at = now; FLAGS[m.id] = entry; }
    return 'set';
  }

  function afterStatusChange(card) {
    persistFlags();
    renderCardFlags(card);
    if (document.getElementById('filter-qa').value) applyFilters();
    if (document.getElementById('lightbox').classList.contains('open')) showLightbox();
    if (document.getElementById('compare-view').classList.contains('open')) renderCompare();
  }

  function setStatus(m, status) {
    const res = writeStatus(m, status);
    afterStatusChange(MEMBER_INDEX[m.id].card);
    showToast(res === 'cleared' ? 'Hodnotenie zrušené' : QA_ICON[status] + ' ' + QA_LABEL[status]);
    if (res === 'set' && (status === 'fix' || status === 'fail')) focusNote(m);
  }

  function setStatusAll(card, status) {
    const allOn = card.members.every(m => qaState(m) === status);
    card.members.forEach(m => {
      if (allOn) { delete FLAGS[m.id]; delete APPROVED[m.id]; }
      else if (qaState(m) !== status) { writeStatus(m, status, { toggle: false }); }
    });
    afterStatusChange(card);
    showToast(allOn ? 'Hodnotenie zrušené na všetkých formátoch' : QA_LABEL[status] + ' — všetky formáty motívu');
  }

  // Poznámka sa píše priamo do textového poľa a ukladá počas písania (debounce v persistFlags).
  function saveNote(m, text) {
    // poznámka bez hodnotenia (alebo k neplatnému) = drobná oprava
    if (!reviewOf(m.id) || qaState(m) === 'stale' || qaState(m) === 'pass') writeStatus(m, 'fix', { toggle: false });
    const r = reviewOf(m.id);
    const t = text.trim();
    if (t) { r.note = t; } else { delete r.note; }
    persistFlags();
  }

  function bindNoteInput(input, getMember) {
    if (input._bound) return;
    input._bound = true;
    input.addEventListener('click', e => e.stopPropagation());
    input.addEventListener('input', () => {
      const m = getMember();
      const wasFlag = !!FLAGS[m.id];
      saveNote(m, input.value);
      // prvé písmeno k neohodnotenému banneru → karta dostane stav oprava (bez straty fokusu)
      if (!wasFlag) { const c = MEMBER_INDEX[m.id].card; c.el.dataset.qa = worstState(c.members); updateCounter(); }
    });
    input.addEventListener('keydown', e => {
      e.stopPropagation();  // P/F/X/N/šípky v lightboxe nesmú reagovať počas písania
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); input.blur(); }
      else if (e.key === 'Escape') { input.blur(); }
    });
    input.addEventListener('blur', () => {
      const m = getMember();
      const card = MEMBER_INDEX[m.id].card;
      renderCardFlags(card);
      if (input.value.trim()) showToast('📝 Poznámka uložená');
    });
  }

  // Po kliknutí na ✎ / ✕ (alebo N) skočí kurzor rovno do poľa na poznámku
  function focusNote(m) {
    const lbOpen = document.getElementById('lightbox').classList.contains('open');
    const input = lbOpen ? document.getElementById('lb-note-input')
                         : MEMBER_INDEX[m.id].card.el.querySelector('.note-input');
    if (!input) return;
    const row = input.closest('.note-row');
    if (row) row.hidden = false;
    setTimeout(() => { input.focus(); input.setSelectionRange(input.value.length, input.value.length); }, 30);
  }

  function editNote(m) {
    if (!reviewOf(m.id) || qaState(m) === 'stale') {
      writeStatus(m, 'fix', { toggle: false });
      afterStatusChange(MEMBER_INDEX[m.id].card);
    }
    focusNote(m);
  }

  async function revealMember(m) {
    if (!SERVER_MODE) { showToast('Server nebeží — Finder sa nedá otvoriť', true); return; }
    try {
      await fetch('/api/reveal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ file: m.file }) });
    } catch (e) { showToast('Otvorenie Findera zlyhalo', true); }
  }

  // ---------- Svetlý / tmavý režim (voľba v prehliadači, inak podľa systému) ----------
  function renderThemeToggle() {
    const dark = document.documentElement.dataset.theme !== 'light';
    const btn = document.getElementById('theme-toggle');
    btn.textContent = dark ? '☀︎' : '☾';
    btn.title = dark ? 'Prepnúť na svetlý režim' : 'Prepnúť na tmavý režim';
  }
  function toggleTheme() {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('ad-gen-theme', next); } catch (e) {}
    renderThemeToggle();
  }

  // ---------- Výber (len v prehliadači) + porovnanie + PDF ----------
  let SELECTION = new Set();
  function loadSelection() {
    try { SELECTION = new Set(JSON.parse(localStorage.getItem(SELECTION_KEY) || '[]').filter(id => MEMBER_INDEX[id])); }
    catch (e) { SELECTION = new Set(); }
  }
  function saveSelection() {
    try { localStorage.setItem(SELECTION_KEY, JSON.stringify([...SELECTION])); } catch (e) {}
    renderSelectionBar();
  }
  function toggleSelect(m) {
    if (SELECTION.has(m.id)) SELECTION.delete(m.id); else SELECTION.add(m.id);
    saveSelection();
    renderCardFlags(MEMBER_INDEX[m.id].card);
    if (document.getElementById('lightbox').classList.contains('open')) showLightbox();
  }
  function selectedMembers() {
    return [...SELECTION].map(id => MEMBER_INDEX[id]).filter(Boolean).map(x => x.member);
  }
  function clearSelection() {
    SELECTION.clear();
    saveSelection();
    CARDS.forEach(renderCardFlags);
    closeCompare();
  }
  function renderSelectionBar() {
    const bar = document.getElementById('sel-bar');
    document.getElementById('sel-count').textContent = SELECTION.size;
    bar.classList.toggle('show', SELECTION.size > 0);
  }

  function renderCompare() {
    const list = selectedMembers();
    const wrap = document.getElementById('compare-grid');
    wrap.innerHTML = list.map(m => {
      const st = qaState(m);
      const r = reviewOf(m.id);
      const media = m.kind === 'video'
        ? '<video src="' + esc(m.video_url) + '" controls playsinline preload="metadata"></video>'
        : '<img src="' + esc(m.img_url) + '" alt="">';
      return '<figure class="cmp-item" data-qa="' + st + '" data-mid="' + esc(m.id) + '">' + media +
        '<figcaption><b>' + esc(m.country + ' · ' + m.ad_id) + '</b> · ' + esc(m.format) +
        (m.headline ? '<br><span class="cmp-hl">' + esc(m.headline) + '</span>' : '') +
        (r && r.note ? '<br><span class="cmp-note">📝 ' + esc(r.note) + '</span>' : '') +
        '<span class="cmp-qa"><span class="qa-badge q-' + st + '">' + (st === 'none' ? '' : QA_ICON[st] + ' ' + QA_LABEL[st]) + '</span>' +
        ['pass', 'fix', 'fail'].map(s => '<button class="qa-btn qa-' + s + (st === s ? ' on' : '') + '" data-qa="' + s + '" title="' + QA_LABEL[s] + '">' + QA_ICON[s] + '</button>').join('') +
        '<button class="cmp-remove" title="Odobrať z výberu">−</button></span></figcaption></figure>';
    }).join('');
    wrap.querySelectorAll('.cmp-item').forEach(fig => {
      const m = MEMBER_INDEX[fig.dataset.mid].member;
      fig.querySelectorAll('.qa-btn').forEach(b => b.addEventListener('click', () => setStatus(m, b.dataset.qa)));
      fig.querySelector('.cmp-remove').addEventListener('click', () => { toggleSelect(m); renderCompare(); if (!SELECTION.size) closeCompare(); });
    });
    document.getElementById('compare-title').textContent = list.length + ' vybraných kreatív';
  }
  function openCompare() {
    if (!SELECTION.size) { showToast('Najprv vyber kreatívy (☐ na karte alebo kláves S)'); return; }
    closeLightbox();
    renderCompare();
    document.getElementById('compare-view').classList.add('open');
  }
  function closeCompare() {
    const cv = document.getElementById('compare-view');
    cv.classList.remove('open');
    cv.querySelectorAll('video').forEach(v => v.pause());
  }
  function printSelected() {
    if (!SELECTION.size) { showToast('Najprv vyber kreatívy'); return; }
    renderCompare();
    document.getElementById('compare-view').classList.add('open');
    document.body.classList.add('printing');
    // obrázky musia byť načítané, inak sú v PDF prázdne rámčeky
    const imgs = [...document.querySelectorAll('#compare-grid img')];
    Promise.all(imgs.map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; }))).then(() => {
      window.print();
      document.body.classList.remove('printing');
    });
  }

  // ---------- Export / download ----------
  function flagsAsItems() {
    return Object.entries(FLAGS).map(([id, v]) => ({ id, ...v }));
  }

  // Čitateľné zadanie na opravu — vloží sa do chatu s Claude (platené pregenerovanie potvrdzuješ tam)
  function briefFor(items) {
    const byKey = {};
    items.forEach(it => {
      const k = [it.brand, it.product, it.adset, it.country].join(' · ');
      (byKey[k] = byKey[k] || []).push(it);
    });
    const fail = items.filter(i => i.status === 'fail').length;
    let out = 'Oprav bannery z dashboardu AdGenerator Pro (' + items.length + ': ' + fail + '× FAIL = prerobiť koncept, '
      + (items.length - fail) + '× drobná oprava = len to, čo je v poznámke).\\n'
      + 'Pregeneruj IBA tieto, pred generovaním mi daj súhrn na potvrdenie.\\n';
    Object.entries(byKey).forEach(([k, list]) => {
      out += '\\n■ ' + k + '\\n';
      list.forEach(it => {
        out += '  • ' + (it.status === 'fail' ? '✕ FAIL' : '✎ oprava') + ' — ' + (it.template_name || it.ad_id) + ' (' + it.format + ')\\n'
          + '    poznámka: ' + (it.note ? it.note.replace(/\\n/g, ' / ') : '— (bez poznámky, doplň čo zmeniť)') + '\\n'
          + '    súbor: ' + it.file + '\\n';
      });
    });
    return out;
  }

  async function copyBrief(items, label) {
    if (!items.length) { showToast('Nič na opravu — označ bannery ✎ alebo ✕'); return; }
    try {
      await navigator.clipboard.writeText(briefFor(items));
      showToast('📋 ' + label + ' skopírované — vlož do chatu');
    } catch (e) { showToast('Clipboard zlyhal', true); }
  }

  function copyFlagged() {
    // len platné hodnotenia (pregenerované ↻ čakajú na nové posúdenie)
    const items = Object.entries(FLAGS)
      .filter(([id]) => MEMBER_INDEX[id] && ['fix', 'fail'].includes(qaState(MEMBER_INDEX[id].member)))
      .map(([id, v]) => ({ id, ...v }));
    copyBrief(items, 'Zadanie na opravu (' + items.length + ')');
  }

  function safeName(m) {
    const ext = m.kind === 'video' ? '.mp4' : '.png';
    const base = m.kind === 'video'
      ? (m.country + '_' + m.brand + '_' + (m.ad_id || 'video') + ext)
      : (m.country + '_' + m.brand + '_t' + m.template_num + '_' + (m.ad_id || 'banner') + '_' + m.format + ext);
    return base.replace(/[:]/g, 'x').replace(/[^\\w.\\-]+/g, '-');
  }

  async function downloadList(list) {
    if (!list.length) { showToast('Nič na stiahnutie'); return; }
    // Safari nevie showDirectoryPicker → priečinok vyberie macOS dialóg cez server
    if (!window.showDirectoryPicker && SERVER_MODE) {
      showToast('Vyber priečinok v okne macOS…');
      try {
        const r = await fetch('/api/save-to-folder', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: list.map(m => ({ file: m.file, name: safeName(m) })) }) });
        const res = await r.json();
        if (res.cancelled) return;
        showToast('Uložené ' + res.copied + ' súborov' + (res.failed ? ' · ' + res.failed + ' zlyhalo' : '') + ' → ' + res.dir.split('/').filter(Boolean).pop());
      } catch (e) { showToast('Uloženie zlyhalo', true); }
      return;
    }
    if (window.showDirectoryPicker) {
      let dir;
      try { dir = await window.showDirectoryPicker(); } catch (e) { return; }
      let ok = 0, fail = 0;
      for (const m of list) {
        try {
          const resp = await fetch(m.file);
          const blob = await resp.blob();
          const fh = await dir.getFileHandle(safeName(m), { create: true });
          const w = await fh.createWritable();
          await w.write(blob); await w.close();
          ok++;
        } catch (e) { fail++; }
      }
      showToast('Uložené ' + ok + ' súborov' + (fail ? ' · ' + fail + ' zlyhalo' : ''));
    } else {
      let ok = 0, fail = 0;
      for (const m of list) {
        try {
          const resp = await fetch(m.file);
          const blob = await resp.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url; a.download = safeName(m); a.click();
          URL.revokeObjectURL(url); ok++;
          await new Promise(r => setTimeout(r, 150));
        } catch (e) { fail++; }
      }
      showToast('Stiahnuté ' + ok + (fail ? ' · ' + fail + ' zlyhalo' : ''));
    }
  }

  // Čo stiahnuť: pass = schválené (na nahratie do reklám), todo = na opravu, all = všetko označené.
  // Len platné hodnotenia — banner pregenerovaný po hodnotení (↻) sa nesťahuje.
  function downloadByQa(which) {
    document.getElementById('dl-menu').classList.remove('open');
    const want = { pass: ['pass'], todo: ['fix', 'fail'], all: ['pass', 'fix', 'fail'] }[which];
    const list = Object.values(MEMBER_INDEX).map(x => x.member).filter(m => want.includes(qaState(m)));
    downloadList(list);
  }

  function renderDlMenu() {
    const n = s => Object.values(MEMBER_INDEX).filter(x => s.includes(qaState(x.member))).length;
    document.getElementById('dl-n-pass').textContent = n(['pass']);
    document.getElementById('dl-n-todo').textContent = n(['fix', 'fail']);
    document.getElementById('dl-n-all').textContent = n(['pass', 'fix', 'fail']);
  }

  function clearFlags() {
    if (!confirm('Naozaj zrušiť všetky označenia na opravu (FAIL / drobná oprava)? Schválené PASS ostanú.')) return;
    FLAGS = {};
    localStorage.removeItem(STORAGE_KEY);
    persistFlags();
    renderAllFlags();
    applyFilters();
    showToast('Označenia na opravu zrušené');
  }

  // ---------- Lightbox ----------
  let lbCards = [];
  let lbIndex = 0;
  let lbWheelLock = false;

  function lbCard() { return lbCards[lbIndex]; }

  function showLightbox() {
    const card = lbCard();
    if (!card) return;
    const m = activeMember(card);
    const lb = document.getElementById('lightbox');
    const vid = document.getElementById('lb-video');
    const isVideo = m.kind === 'video';

    lb.classList.toggle('video-mode', isVideo);
    if (isVideo) {
      lb.classList.remove('compare');
      if (vid.dataset.src !== m.video_url) {
        vid.src = m.video_url;
        vid.dataset.src = m.video_url;
      }
      vid.currentTime = 0;
      vid.play().catch(() => {});
    } else {
      vid.pause();
      document.getElementById('lb-img').src = m.img_url;
    }

    const tr = document.getElementById('lb-transcript');
    tr.textContent = isVideo ? (m.transcript || '') : '';
    tr.classList.toggle('has-text', isVideo && !!m.transcript);

    renderLineage(m);

    document.getElementById('lb-caption').textContent =
      m.country + ' · ' + m.ad_id + ' · ' + m.format +
      (isVideo && m.duration ? ' · ' + m.duration + 's' : '') +
      (m.headline ? ' · ' + m.headline : '') + '  (' + (lbIndex + 1) + '/' + lbCards.length + ')';
    // Pásik s ostatnými rozmermi toho istého motívu
    const fwrap = document.getElementById('lb-formats');
    const cbtn = document.getElementById('lb-compare-btn');
    if (card.members.length > 1) {
      fwrap.innerHTML = card.members.map((mm, i) =>
        '<button data-idx="' + i + '" title="' + (mm.template_name || '') + ' · ' + mm.outputs + '" class="' +
        (i === card.active ? 'active ' : '') + '" data-qa="' + qaState(mm) + '">' +
        '<img src="' + mm.img_url + '" alt=""><span>' + (mm.label || mm.format) + '</span></button>'
      ).join('');
      fwrap.querySelectorAll('button').forEach(b =>
        b.addEventListener('click', () => { setActive(card, parseInt(b.dataset.idx)); showLightbox(); }));
      fwrap.style.display = '';
      cbtn.style.display = '';
    } else {
      fwrap.style.display = 'none';
      cbtn.style.display = 'none';
      document.getElementById('lightbox').classList.remove('compare');
    }

    // Režim všetky rozmery vedľa seba
    const cwrap = document.getElementById('lb-compare');
    cwrap.innerHTML = card.members.map((mm, i) =>
      '<figure data-idx="' + i + '" class="' + (i === card.active ? 'active' : '') + '" data-qa="' + qaState(mm) + '">' +
      '<img src="' + mm.img_url + '" alt=""><figcaption>' + (mm.label || mm.format) + '</figcaption></figure>'
    ).join('');
    cwrap.querySelectorAll('figure').forEach(f =>
      f.addEventListener('click', () => { setActive(card, parseInt(f.dataset.idx)); showLightbox(); }));

    updateLbFlag();
  }

  // ---------- Rodokmeň: z čoho kreatíva vznikla ----------
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  function renderLineage(m) {
    const lb = document.getElementById('lightbox');
    const box = document.getElementById('lb-lineage');
    const btn = document.getElementById('lb-lineage-btn');
    const lin = m.lineage;

    if (!lin || (!lin.why && !(lin.winners || []).length)) {
      btn.classList.remove('avail');
      lb.classList.remove('lineage-open');
      box.innerHTML = '';
      return;
    }
    btn.classList.add('avail');

    const icon = { ITERATION: '🔁', EXPERIMENT: '🧪', 'RE-TEST': '♻️' }[lin.type] || '🔁';
    let html = '<h3>' + icon + ' ' + esc(lin.type || 'ITERATION') + '</h3>';
    if (lin.window) html += '<div class="lin-window">dáta ' + esc(lin.window) + '</div>';

    if ((lin.winners || []).length) {
      html += '<h4>Víťaz, z ktorého vychádza</h4>';
      for (const w of lin.winners) {
        const st = w.state ? '<span class="w-state ' + esc(w.state) + '">' + esc(w.state) + '</span>' : '';
        const extra = w.kind === 'video' && w.thumbstop
          ? ' · thumbstop <b>' + w.thumbstop + '%</b>' : '';
        html += '<div class="lb-win">' +
          (w.img ? '<img src="' + esc(w.img) + '" alt="" loading="lazy">' : '') +
          '<div class="w-body"><div class="w-name">' + esc(w.name) + '</div>' +
          '<div class="w-metrics">ROAS <b>' + w.roas + '</b> · ' +
          (w.spend || 0).toLocaleString('sk-SK') + ' spend<br>' +
          (w.purchases || 0) + ' nákupov' + extra + '<br>' + st + '</div></div></div>';
      }
    }
    if (lin.driver) html += '<h4>Čo víťaza vyhralo (driver)</h4><p class="lin-driver">' + esc(lin.driver) + '</p>';
    if (lin.offer) html += '<h4>Ponuka tejto kreatívy</h4><p class="lin-offer">' + esc(lin.offer) + '</p>';
    if (lin.why) html += '<h4>Prečo táto kreatíva</h4><p>' + esc(lin.why) + '</p>';
    if (lin.changed) html += '<h4>Čo sa zmenilo</h4><p>' + esc(lin.changed) + '</p>';

    box.innerHTML = html;
  }

  function toggleLineage() {
    const btn = document.getElementById('lb-lineage-btn');
    if (!btn.classList.contains('avail')) return;
    document.getElementById('lightbox').classList.toggle('lineage-open');
  }

  function toggleCompare() {
    const card = lbCard();
    if (!card || card.members.length < 2) return;
    document.getElementById('lightbox').classList.toggle('compare');
  }

  function updateLbFlag() {
    const card = lbCard();
    if (!card) return;
    const m = activeMember(card);
    const st = qaState(m);
    const r = reviewOf(m.id);
    document.querySelectorAll('#lb-qa .qa-btn').forEach(b => b.classList.toggle('on', st === b.dataset.qa));
    const sel = document.getElementById('lb-select');
    sel.classList.toggle('on', SELECTION.has(m.id));
    sel.textContent = SELECTION.has(m.id) ? '☑' : '☐';
    // stav + história verdiktov k tomuto banneru
    const info = document.getElementById('lb-qa-info');
    let html = st === 'none' ? '<span class="muted">Nehodnotené</span>'
      : '<span class="qa-badge q-' + st + '">' + QA_ICON[st] + ' ' + QA_LABEL[st] + '</span>';
    if (st === 'stale') html += '<div class="muted">Súbor sa zmenil po hodnotení (' + esc(QA_LABEL[r.status] || r.status) + ') — posúď znova.</div>';
    const canNote = st === 'fix' || st === 'fail' || (r && r.note && st !== 'stale');
    if (st === 'fix' || st === 'fail') {
      html += '<button class="lb-brief" id="lb-brief" type="button">📋 Skopírovať zadanie na opravu</button>';
    }
    if (canNote) {
      html += '<textarea id="lb-note-input" class="note-input lb-note-input" rows="2" placeholder="' +
        (st === 'fail' ? 'Prečo FAIL? Čo prerobiť…' : 'Čo opraviť? Píš rovno sem…') + '"></textarea>' +
        '<div class="muted" style="font-size:0.62rem">Enter = uložiť · Shift+Enter = nový riadok · N = písať</div>';
    } else if (st === 'stale' && r && r.note) {
      html += '<div class="muted">Pôvodná poznámka: ' + esc(r.note) + '</div>';
    }
    const hist = (r && r.history) || [];
    if (hist.length) {
      html += '<div class="muted">História: ' + hist.slice().reverse().map(h =>
        esc(QA_LABEL[h.status] || h.status) + (h.at ? ' ' + esc(new Date(h.at).toLocaleDateString('sk-SK')) : '')).join(' · ') + '</div>';
    }
    info.innerHTML = html;
    const lbBrief = document.getElementById('lb-brief');
    if (lbBrief) lbBrief.onclick = () => copyBrief([{ id: m.id, ...reviewOf(m.id) }], 'Zadanie pre tento banner');
    const lbInput = document.getElementById('lb-note-input');
    if (lbInput) {
      lbInput.value = (r && r.note) || '';
      if (st === 'fail') lbInput.style.borderColor = 'rgba(255,90,95,0.5)';
      const mid = m.id;
      bindNoteInput(lbInput, () => MEMBER_INDEX[mid].member);
      lbInput.addEventListener('blur', () => updateLbFlag());
    }
  }

  function openLightbox(card) {
    lbCards = CARDS.filter(c => c.el.style.display !== 'none' && c.el.closest('.adset-section').style.display !== 'none');
    lbIndex = lbCards.indexOf(card);
    if (lbIndex < 0) { lbCards = [card]; lbIndex = 0; }
    showLightbox();
    document.getElementById('lightbox').classList.add('open');
  }

  function lbMove(d) {
    if (!lbCards.length) return;
    lbIndex = (lbIndex + d + lbCards.length) % lbCards.length;
    showLightbox();
  }

  function lbSwitchFormat(d) {
    const card = lbCard();
    if (!card || card.members.length < 2) return;
    setActive(card, (card.active + d + card.members.length) % card.members.length);
    showLightbox();
  }

  function closeLightbox() {
    const lb = document.getElementById('lightbox');
    lb.classList.remove('open');
    lb.classList.remove('compare');
    lb.classList.remove('video-mode');
    const vid = document.getElementById('lb-video');
    if (vid) vid.pause();
  }

  // ---------- Filtre ----------
  const BOOT = __BOOT_JSON__;
  const filterCountry = document.getElementById('filter-country');
  const filterBrand = document.getElementById('filter-brand');
  const filterProduct = document.getElementById('filter-product');
  const filterAdset = document.getElementById('filter-adset');
  const filterFormat = document.getElementById('filter-format');
  const filterKind = document.getElementById('filter-kind');
  const filterSearch = document.getElementById('filter-search');
  const filterSort = document.getElementById('filter-sort');
  const filterQa = document.getElementById('filter-qa');
  const filterStyle = document.getElementById('filter-style');

  function fillSelect(sel, values, keepValue) {
    const prev = keepValue ? sel.value : '';
    sel.innerHTML = '<option value="">všetky</option>' + values.map(v => '<option value="' + v.replace(/"/g, '&quot;') + '">' + v + '</option>').join('');
    if (prev && values.includes(prev)) sel.value = prev;
  }

  function cascade() {
    const b = filterBrand.value;
    const products = b ? (BOOT.productsByBrand[b] || []) : BOOT.allProducts;
    fillSelect(filterProduct, products, true);
    const p = filterProduct.value;
    let adsets;
    if (b && p) { adsets = BOOT.adsetsByBrandProduct[b + '|' + p] || []; }
    else if (b) { adsets = [...new Set(products.flatMap(pp => BOOT.adsetsByBrandProduct[b + '|' + pp] || []))].sort(); }
    else { adsets = BOOT.allAdsets; }
    fillSelect(filterAdset, adsets, true);
  }

  function applySort() {
    const mode = filterSort.value;
    const grid = document.getElementById('sections');
    const sections = [...grid.querySelectorAll('.adset-section')];
    sections.sort((a, b) => {
      if (mode === 'name') {
        return (a.dataset.brand + a.dataset.adset).toLowerCase().localeCompare((b.dataset.brand + b.dataset.adset).toLowerCase());
      }
      const am = parseInt(a.dataset.mtime) || 0;
      const bm = parseInt(b.dataset.mtime) || 0;
      return mode === 'oldest' ? am - bm : bm - am;
    });
    sections.forEach(s => grid.appendChild(s));
  }

  function applyFilters() {
    const co = filterCountry.value.toUpperCase();
    const b = filterBrand.value.toLowerCase();
    const p = filterProduct.value.toLowerCase();
    const ads = filterAdset.value.toLowerCase();
    const fmt = filterFormat.value;
    const sty = filterStyle ? filterStyle.value : '';
    const kind = filterKind ? filterKind.value : '';
    const s = filterSearch.value.toLowerCase().trim();
    const qa = filterQa.value;
    // 'todo' = všetko, čo treba riešiť (FAIL + oprava + prehodnotiť)
    const qaMatch = m => { const st = qaState(m); return qa === 'todo' ? (st === 'fail' || st === 'fix' || st === 'stale') : st === qa; };

    filterQa.parentElement.classList.toggle('active', !!qa);

    let visible = 0;
    CARDS.forEach(card => {
      const el = card.el;
      let show = true;
      if (co && el.dataset.country !== co) show = false;
      if (b && el.dataset.brand.toLowerCase() !== b) show = false;
      if (p && el.dataset.product.toLowerCase() !== p) show = false;
      if (ads && el.dataset.adset.toLowerCase() !== ads) show = false;
      if (kind && (el.dataset.kind || 'image') !== kind) show = false;
      if (fmt && !el.dataset.formats.split('|').includes(fmt)) show = false;
      if (sty && !(el.dataset.styles || '-').split('|').includes(sty)) show = false;
      if (s && !el.dataset.search.includes(s)) show = false;
      if (qa && !card.members.some(qaMatch)) show = false;
      el.style.display = show ? '' : 'none';
      if (show) {
        visible++;
        // Pri aktívnom formát filtri prepni kartu na zodpovedajúci formát
        if (fmt && activeMember(card).format !== fmt) {
          const idx = card.members.findIndex(m => m.format === fmt);
          if (idx >= 0) setActive(card, idx);
        }
        // Pri QA filtri prepni na formát v hľadanom stave
        if (qa && !qaMatch(activeMember(card))) {
          const idx = card.members.findIndex(qaMatch);
          if (idx >= 0) setActive(card, idx);
        }
      }
    });

    document.querySelectorAll('.adset-section').forEach(section => {
      const hasVisible = [...section.querySelectorAll('.ccard')].some(c => c.style.display !== 'none');
      section.style.display = hasVisible ? '' : 'none';
    });

    document.getElementById('visible-count').textContent = visible;
    syncUrl();
  }

  // Aktuálne filtre do URL → pohľad sa dá uložiť ako záložka alebo poslať ako link
  // ---------- Tlačidlo „↻ Obnoviť": načíta nové bannery / videá / štýly / templaty (nič nebeží na pozadí) ----------
  async function refreshDashboard() {
    const btn = document.getElementById('btn-refresh');
    if (btn.classList.contains('busy')) return;
    btn.classList.add('busy');
    btn.textContent = '⟳ Načítavam celý dashboard…';
    try {
      const r = await fetch('/api/rebuild', { method: 'POST' });
      if (!r.ok) throw new Error(r.status);
      location.reload();
    } catch (e) {
      btn.classList.remove('busy');
      btn.textContent = '⟳ Úplná obnova';
      showToast(SERVER_MODE ? 'Obnova zlyhala' : 'Server nebeží — spusti tools/serve_dashboard.sh', true);
    }
  }

  // ---------- Taby: Bannery · Video · Templaty a štýly · Pod kapotou ----------
  const TABS = ['banners', 'video', 'styles', 'stats', 'system'];
  let TAB = 'banners';
  function switchTab(tab, { silent = false } = {}) {
    TAB = tab;
    document.body.dataset.tab = tab;
    document.querySelectorAll('#tabs button').forEach(b => b.setAttribute('aria-selected', String(b.dataset.tab === tab)));
    try { localStorage.setItem('ad-gen-tab', tab); } catch (e) {}
    if (tab === 'banners' || tab === 'video') {
      filterKind.value = tab === 'video' ? 'video' : 'image';
      if (!silent) applyFilters();
    } else {
      syncUrl();
    }
    if (!silent) window.scrollTo({ top: 0 });
  }

  let TP_CAT = '';
  function filterTemplates() {
    const q = document.getElementById('tp-search').value.toLowerCase().trim();
    document.querySelectorAll('.tp-card').forEach(c => {
      const ok = (!TP_CAT || c.dataset.cat === TP_CAT) && (!q || c.dataset.search.includes(q));
      c.style.display = ok ? '' : 'none';
    });
  }

  function syncUrl() {
    const qp = new URLSearchParams();
    const put = (k, v) => { if (v) qp.set(k, v); };
    put('brand', filterBrand.value); put('product', filterProduct.value); put('adset', filterAdset.value);
    put('country', filterCountry.value); put('format', filterFormat.value);
    if (TAB !== 'banners') qp.set('tab', TAB);
    put('search', filterSearch.value.trim()); put('qa', filterQa.value);
    if (filterStyle) put('style', filterStyle.value);
    if (filterSort.value !== 'newest') put('sort', filterSort.value);
    const qs = qp.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }

  function resetFilters() {
    filterCountry.value = ''; filterBrand.value = ''; filterFormat.value = '';
    if (filterKind) filterKind.value = TAB === 'video' ? 'video' : 'image';
    filterSearch.value = ''; filterQa.value = '';
    if (filterStyle) filterStyle.value = '';
    cascade();
    filterProduct.value = ''; filterAdset.value = '';
    applyFilters();
  }

  // ---------- Wire up ----------
  document.addEventListener('DOMContentLoaded', async () => {
    renderThemeToggle();
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    const setHdr = () => document.documentElement.style.setProperty('--hdr-h', document.querySelector('header').offsetHeight + 'px');
    setHdr();
    window.addEventListener('resize', setHdr);
    new ResizeObserver(setHdr).observe(document.querySelector('header'));
    document.getElementById('btn-refresh').addEventListener('click', refreshDashboard);
    document.querySelectorAll('#tabs button').forEach(b => b.addEventListener('click', () => switchTab(b.dataset.tab)));
    const tps = document.getElementById('tp-search');
    if (tps) tps.addEventListener('input', filterTemplates);
    document.querySelectorAll('#tp-seg button').forEach(btn => btn.addEventListener('click', () => {
      TP_CAT = btn.dataset.cat;
      document.querySelectorAll('#tp-seg button').forEach(x => x.setAttribute('aria-pressed', String(x === btn)));
      filterTemplates();
    }));
    matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
      let saved = null;
      try { saved = localStorage.getItem('ad-gen-theme'); } catch (err) {}
      if (saved) return;  // ručná voľba má prednosť pred systémom
      document.documentElement.dataset.theme = e.matches ? 'light' : 'dark';
      renderThemeToggle();
    });
    initCards();
    loadSelection();
    await loadFlags();
    migrateReviews();
    renderAllFlags();
    renderSelectionBar();
    cascade();

    document.getElementById('lb-close').addEventListener('click', closeLightbox);
    document.querySelectorAll('#lb-qa .qa-btn').forEach(b =>
      b.addEventListener('click', () => setStatus(activeMember(lbCard()), b.dataset.qa)));
    document.getElementById('lb-select').addEventListener('click', () => toggleSelect(activeMember(lbCard())));
    document.getElementById('btn-compare').addEventListener('click', openCompare);
    document.getElementById('btn-print').addEventListener('click', printSelected);
    document.getElementById('btn-sel-download').addEventListener('click', () => downloadList(selectedMembers()));
    document.getElementById('btn-sel-clear').addEventListener('click', clearSelection);
    document.getElementById('compare-close').addEventListener('click', closeCompare);
    document.getElementById('lb-note').addEventListener('click', () => editNote(activeMember(lbCard())));
    document.getElementById('lb-compare-btn').addEventListener('click', toggleCompare);
    document.getElementById('lb-lineage-btn').addEventListener('click', toggleLineage);
    document.getElementById('lb-prev').addEventListener('click', () => lbMove(-1));
    document.getElementById('lb-next').addEventListener('click', () => lbMove(1));
    document.getElementById('lightbox').addEventListener('click', e => { if (e.target.id === 'lightbox') closeLightbox(); });
    document.getElementById('lightbox').addEventListener('wheel', e => {
      e.preventDefault();
      if (lbWheelLock) return;
      lbWheelLock = true;
      lbMove(e.deltaY > 0 ? 1 : -1);
      setTimeout(() => { lbWheelLock = false; }, 220);
    }, { passive: false });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && document.getElementById('compare-view').classList.contains('open')) { closeCompare(); return; }
      if (!document.getElementById('lightbox').classList.contains('open')) return;
      if (e.key === 'Escape') {
        const lb = document.getElementById('lightbox');
        if (lb.classList.contains('lineage-open')) lb.classList.remove('lineage-open');
        else if (lb.classList.contains('compare')) lb.classList.remove('compare');
        else closeLightbox();
      }
      else if (e.key === 'a' || e.key === 'A') { e.preventDefault(); toggleCompare(); }
      else if (e.key === 'w' || e.key === 'W') { e.preventDefault(); toggleLineage(); }
      else if (e.key === 'ArrowRight') lbMove(1);
      else if (e.key === 'ArrowLeft') lbMove(-1);
      else if (e.key === 'ArrowUp') { e.preventDefault(); lbSwitchFormat(-1); }
      else if (e.key === 'ArrowDown') { e.preventDefault(); lbSwitchFormat(1); }
      else if (e.key === 'p' || e.key === 'P') setStatus(activeMember(lbCard()), 'pass');
      else if (e.key === 'f' || e.key === 'F') setStatus(activeMember(lbCard()), 'fix');
      else if (e.key === 'x' || e.key === 'X') setStatus(activeMember(lbCard()), 'fail');
      else if (e.key === 's' || e.key === 'S') toggleSelect(activeMember(lbCard()));
      else if (e.key === 'n' || e.key === 'N') { e.preventDefault(); editNote(activeMember(lbCard())); }
    });

    document.getElementById('btn-download').addEventListener('click', e => {
      e.stopPropagation();
      renderDlMenu();
      document.getElementById('dl-menu').classList.toggle('open');
    });
    document.querySelectorAll('#dl-menu button').forEach(b =>
      b.addEventListener('click', e => { e.stopPropagation(); downloadByQa(b.dataset.dl); }));
    document.addEventListener('click', () => document.getElementById('dl-menu').classList.remove('open'));
    document.getElementById('btn-copy').addEventListener('click', copyFlagged);
    document.getElementById('btn-clear').addEventListener('click', clearFlags);
    document.getElementById('btn-reset-filters').addEventListener('click', resetFilters);

    filterCountry.addEventListener('change', applyFilters);
    filterBrand.addEventListener('change', () => { cascade(); applyFilters(); });
    filterProduct.addEventListener('change', () => { cascade(); applyFilters(); });
    filterAdset.addEventListener('change', applyFilters);
    filterFormat.addEventListener('change', applyFilters);
    if (filterKind) filterKind.addEventListener('change', applyFilters);
    filterSearch.addEventListener('input', applyFilters);
    filterSort.addEventListener('change', () => { applySort(); syncUrl(); });
    filterQa.addEventListener('change', applyFilters);
    if (filterStyle) filterStyle.addEventListener('change', applyFilters);

    // Predfilter z URL (?brand=...&product=...&country=...&format=...&search=...)
    const qp = new URLSearchParams(window.location.search);
    const setSel = (el, val) => {
      if (!val) return;
      const opt = [...el.options].find(o => o.value.toLowerCase() === val.toLowerCase());
      if (opt) el.value = opt.value;
    };
    setSel(filterBrand, qp.get('brand'));
    cascade();
    setSel(filterProduct, qp.get('product'));
    cascade();
    setSel(filterAdset, qp.get('adset'));
    setSel(filterCountry, qp.get('country'));
    setSel(filterFormat, qp.get('format'));
    // tab z URL (?tab=video), inak posledný použitý; staré ?kind=video otvorí tab Video
    let startTab = qp.get('tab') || (qp.get('kind') === 'video' ? 'video' : null);
    if (!TABS.includes(startTab)) { try { startTab = localStorage.getItem('ad-gen-tab'); } catch (e) {} }
    switchTab(TABS.includes(startTab) ? startTab : 'banners', { silent: true });
    if (qp.get('search')) filterSearch.value = qp.get('search');
    setSel(filterQa, qp.get('qa'));
    if (filterStyle) setSel(filterStyle, qp.get('style'));
    if (qp.get('sort')) { setSel(filterSort, qp.get('sort')); applySort(); }
    applyFilters();
  });
"""


def build_html(sections: dict, total_failed: int) -> str:
    section_htmls = []
    countries, brands, formats = set(), set(), set()
    products_by_brand, adsets_by_bp = {}, {}
    total_banners = 0
    total_motifs = 0
    n_img_motifs = n_img = n_vid_motifs = n_vid = 0
    style_samples = {}

    for skey in sections:
        section = sections[skey]
        brand, product, adset, lang, variant = skey
        brands.add(brand)
        countries.add(lang.upper())
        products_by_brand.setdefault(brand, set()).add(product)
        adsets_by_bp.setdefault(f"{brand}|{product}", set()).add(adset)

        cards = []
        n_banners = 0
        fmt_counts = {}
        for motif, members in section["collections"].items():
            cards.append(build_collection_card(motif, members, section))
            n_banners += len(members)
            for m in members:
                formats.add(m["format"])
                fmt_counts[m["format"]] = fmt_counts.get(m["format"], 0) + 1
        if not cards:
            continue
        total_banners += n_banners
        total_motifs += len(section["collections"])
        is_video = product == "pvf-video"
        if is_video:
            n_vid_motifs += len(section["collections"]); n_vid += n_banners
        else:
            n_img_motifs += len(section["collections"]); n_img += n_banners
            for members in section["collections"].values():
                for m in members:
                    if m.get("style"):
                        style_samples.setdefault(m["style"], []).append(m)

        added_label = datetime.fromtimestamp(section["mtime"]).strftime("%d.%m. %H:%M") if section["mtime"] else "—"
        variant_badge = f'<span class="section-badge">{esc(variant)}</span>' if variant else ""
        fmt_summary = " · ".join(f"{f} ×{c}" for f, c in sorted(fmt_counts.items(), key=lambda x: FORMAT_ORDER.get(x[0], 9)))
        outputs_list = ", ".join(sorted(set(section["outputs_names"])))

        section_htmls.append((section["mtime"], f"""
  <section class="adset-section" style="--brand:{brand_accent(brand)}" data-kind="{'video' if product == 'pvf-video' else 'image'}" data-brand="{esc(brand)}" data-adset="{esc(adset)}" data-product="{esc(product)}" data-mtime="{section['mtime']}">
    <div class="section-header">
      <span class="section-title">{esc(brand)} · {esc(product)} · {esc(adset)}</span>
      <span class="section-badge lang">{esc(LANG_LABELS.get(lang, lang.upper()))}</span>
      {variant_badge}
      <span class="section-meta">{esc(fmt_summary)} · {len(section['collections'])} motívov / {n_banners} bannerov</span>
      <span class="section-added" title="{esc(outputs_list)}">🕒 {added_label}</span>
    </div>
    <div class="grid">
{"".join(cards)}
    </div>
  </section>"""))

    section_htmls.sort(key=lambda t: t[0], reverse=True)
    sections_content = "\n".join(s[1] for s in section_htmls) if section_htmls else '<div class="empty-state">Zatiaľ tu nie sú žiadne kreatívy.<br><br>Prvé bannery a videá vytvoríš podľa <b>README.md</b> → „3. Prvé spustenie" (vzor klienta: <code>staticky/brands/_priklad/</code>).<br>Potom klikni na „⟳ Úplná obnova".</div>'

    boot = {
        "allProducts": sorted({p for ps in products_by_brand.values() for p in ps}),
        "allAdsets": sorted({a for ads in adsets_by_bp.values() for a in ads}),
        "productsByBrand": {b: sorted(ps) for b, ps in products_by_brand.items()},
        "adsetsByBrandProduct": {k: sorted(v) for k, v in adsets_by_bp.items()},
    }
    js = JS.replace("__BOOT_JSON__", json.dumps(boot, ensure_ascii=False).replace("</", "<\\/"))

    country_options = "".join(f'<option value="{c}">{LANG_LABELS.get(c.lower(), c)}</option>' for c in sorted(countries))
    brand_options = "".join(f'<option value="{esc(b)}">{esc(b)}</option>' for b in sorted(brands))
    style_names = {st.get("id"): st.get("name", st.get("id")) for st in load_visual_styles()}
    style_counts = {}
    for sec in sections.values():
        for members in sec["collections"].values():
            for m in members:
                if m.get("kind") != "video":
                    k = m.get("style") or "-"
                    style_counts[k] = style_counts.get(k, 0) + 1
    style_options = "".join(f'<option value="{esc(k)}">{esc(style_names.get(k, k))} ({v})</option>'
                            for k, v in sorted(style_counts.items(), key=lambda kv: -kv[1]) if k != "-")
    if "-" in style_counts:
        style_options += f'<option value="-">bez štýlu ({style_counts["-"]})</option>'
    format_options = "".join(f'<option value="{esc(f)}">{esc(f)}</option>' for f in sorted(formats, key=lambda x: FORMAT_ORDER.get(x, 9)))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for lst in style_samples.values():
        lst.sort(key=lambda m: -m["mtime"])
    styles_html = build_styles_tab(style_samples)
    system_html = build_system_tab()
    stats_html = stats_tab.build(sections, ROOT.parent / "video")
    footage = footage_tab.build(ROOT, ROOT.parent / "video", make_poster)
    n_styles = len(load_visual_styles())
    n_templates = len(load_templates())

    return f"""<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AdGenerator Pro</title>
<meta name="description" content="AdGenerator Pro — bannery, videá, štýly a štatistiky na jednom mieste">
<link rel="icon" type="image/png" href="assets/brand/icon-light-64.png" media="(prefers-color-scheme: light)">
<link rel="icon" type="image/png" href="assets/brand/icon-dark-64.png" media="(prefers-color-scheme: dark)">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<meta property="og:title" content="AdGenerator Pro">
<meta property="og:image" content="assets/brand/og-adgenerator.jpg">
<script>
  (function () {{
    var t = null;
    try {{ t = localStorage.getItem('ad-gen-theme'); }} catch (e) {{}}
    if (t !== 'light' && t !== 'dark') t = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    document.documentElement.dataset.theme = t;
  }})();
</script>
<style>{CSS}{SKETCH_CSS}{stats_tab.CSS}{footage_tab.CSS}</style>
</head>
<body>

<header>
  <div class="headrow">
    <h1 class="brand"><img class="logo-mark on-light" src="assets/brand/mark-light.png" alt=""><img class="logo-mark on-dark" src="assets/brand/mark-dark.png" alt=""><span class="wm">Ad<span class="gen">Generator</span></span><span class="pro-chip">Pro</span></h1>
    <nav class="tabs" id="tabs" role="tablist">
      <button role="tab" data-tab="banners">🖼 Bannery <span>{n_img_motifs}</span></button>
      <button role="tab" data-tab="video">🎬 Video <span>{n_vid_motifs}</span></button>
      <button role="tab" data-tab="styles">🎨 Templaty a štýly <span>{n_styles + n_templates}</span></button>
      <button role="tab" data-tab="stats">📊 Štatistiky</button>
      <button role="tab" data-tab="system">⚙️ Pod kapotou</button>
    </nav>
    <button class="refresh-btn" id="btn-refresh" type="button" title="Znova načíta celý dashboard od nuly: všetky bannery, videá, štýly, templaty, štatistiky a priečinok vystupy/ (~10 s)">⟳ Úplná obnova</button>
    <button class="theme-toggle" id="theme-toggle" title="Svetlý / tmavý režim"></button>
  </div>
  <div class="headrow grid-only">
    <div class="vmode" role="group"><button type="button" data-vmode="videos" aria-pressed="true">🎬 Hotové videá</button><button type="button" data-vmode="footage" aria-pressed="false">🎞 Footage knižnica <span>{footage["count"]}</span></button></div>
    <span class="stats"><span class="srv-dot" id="srv-dot"></span><b>{n_img_motifs}</b> motívov / <b>{n_img}</b> bannerov · <b>{n_vid_motifs}</b> videí ({n_vid} verzií) · {total_failed} fail · <span id="visible-count">{total_motifs}</span> zobrazených · {timestamp}</span>
    <span class="qa-counts">
      <span class="qc q-fail" title="FAIL">✕ <b id="qa-n-fail">0</b></span>
      <span class="qc q-fix" title="Drobná oprava">✎ <b id="qa-n-fix">0</b></span>
      <span class="qc q-stale" title="Prehodnotiť — súbor sa zmenil po hodnotení">↻ <b id="qa-n-stale">0</b></span>
      <span class="qc q-pass" title="PASS">✓ <b id="qa-n-pass">0</b></span>
    </span>
    <div class="flag-actions">
      <div class="dl-wrap">
        <button id="btn-download" class="primary">⬇ Stiahnuť označené ▾</button>
        <div class="dl-menu" id="dl-menu">
          <button data-dl="pass">✓ PASS — schválené <b id="dl-n-pass">0</b></button>
          <button data-dl="todo">✎ ✕ Na opravu <b id="dl-n-todo">0</b></button>
          <button data-dl="all">Všetky označené <b id="dl-n-all">0</b></button>
          <span class="dl-hint">Po kliknutí si vyberieš priečinok</span>
        </div>
      </div>
      <button id="btn-copy" title="Skopíruje čitateľný zoznam bannerov na opravu s poznámkami — vlož ho do chatu">📋 Zadanie na opravu</button>
      <button id="btn-clear" class="danger" title="Zruší FAIL / opravy, PASS ostanú">✕ Zrušiť opravy</button>
    </div>
  </div>

  <div class="filters grid-only">
    <label>Krajina <select id="filter-country"><option value="">všetky</option>{country_options}</select></label>
    <label>Brand <select id="filter-brand"><option value="">všetky</option>{brand_options}</select></label>
    <label>Produkt <select id="filter-product"><option value="">všetky</option></select></label>
    <label>Ad-set <select id="filter-adset"><option value="">všetky</option></select></label>
    <label>Formát <select id="filter-format"><option value="">všetky</option>{format_options}</select></label>
    <label hidden>Typ <select id="filter-kind"><option value="">všetko</option><option value="image">🖼 bannery</option><option value="video">🎬 videá</option></select></label>
    <label>Hľadať <input type="search" id="filter-search" placeholder="V1, BD01, hero, leto, text z videa..." /></label>
    <label>Zoradiť <select id="filter-sort"><option value="newest">🕒 Najnovšie</option><option value="oldest">Najstaršie</option><option value="name">Názov A–Z</option></select></label>
    <label class="banners-only">Štýl <select id="filter-style"><option value="">všetky</option>{style_options}</select></label>
    <label>QA <select id="filter-qa">
      <option value="">všetky</option>
      <option value="todo">⚑ na riešenie</option>
      <option value="fail">✕ FAIL</option>
      <option value="fix">✎ drobná oprava</option>
      <option value="stale">↻ prehodnotiť</option>
      <option value="pass">✓ PASS</option>
      <option value="none">nehodnotené</option>
    </select></label>
    <button class="btn-reset" id="btn-reset-filters">reset</button>
  </div>
</header>

<div id="sections" class="tab-panel grid-only">
{sections_content}
</div>

<main id="panel-styles" class="tab-panel" data-panel="styles">
{styles_html}
</main>

<main id="panel-footage">
{footage["html"]}
</main>

<main id="panel-stats" class="tab-panel stats-root" data-panel="stats">
{stats_html}
</main>

<main id="panel-system" class="tab-panel" data-panel="system">
{system_html}
</main>

<div class="lightbox" id="lightbox">
  <button class="lb-lineage-btn" id="lb-lineage-btn" title="Z čoho kreatíva vznikla — víťaz a dôvod (W)">🏆</button>
  <button class="lb-compare-btn" id="lb-compare-btn" title="Všetky rozmery vedľa seba (A)">⊞</button>
  <button class="lb-note" id="lb-note" title="Poznámka čo opraviť (N)">📝</button>
  <div class="lb-qa" id="lb-qa">
    <button class="qa-btn qa-pass" data-qa="pass" title="PASS (P)">✓</button>
    <button class="qa-btn qa-fix" data-qa="fix" title="Drobná oprava (F)">✎</button>
    <button class="qa-btn qa-fail" data-qa="fail" title="FAIL (X)">✕</button>
    <button class="lb-select" id="lb-select" title="Do výberu na porovnanie / PDF (S)">☐</button>
    <div class="lb-qa-info" id="lb-qa-info"></div>
  </div>
  <button class="lb-close" id="lb-close" title="Zavrieť (Esc)">✕</button>
  <button class="lb-prev" id="lb-prev" title="Predošlý motív (←)">‹</button>
  <img class="lb-img" id="lb-img" src="" alt="">
  <video class="lb-video" id="lb-video" controls playsinline preload="metadata"></video>
  <div class="lb-compare" id="lb-compare"></div>
  <button class="lb-next" id="lb-next" title="Ďalší motív (→)">›</button>
  <div class="lb-formats" id="lb-formats"></div>
  <div class="lb-transcript" id="lb-transcript"></div>
  <aside class="lb-lineage" id="lb-lineage"></aside>
  <div class="lb-caption" id="lb-caption"></div>
</div>

<div class="sel-bar" id="sel-bar">
  <span><b id="sel-count">0</b> vybraných</span>
  <button id="btn-compare">⊞ Porovnať vedľa seba</button>
  <button id="btn-print">🖨 PDF</button>
  <button id="btn-sel-download">⬇ Stiahnuť</button>
  <button id="btn-sel-clear" class="danger">✕ Zrušiť výber</button>
</div>

<div class="compare-view" id="compare-view">
  <div class="compare-head">
    <h2 id="compare-title"></h2>
    <span class="print-meta">Ad Generator · {timestamp}</span>
    <button id="compare-close" title="Zavrieť (Esc)">✕</button>
  </div>
  <div class="compare-grid" id="compare-grid"></div>
</div>

<div class="toast" id="toast"></div>

<script>{js}{stats_tab.JS}{footage_tab.JS}</script>

</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Build multi-brand dashboard for ad-generator")
    ap.add_argument("--output", "-o", default=str(ROOT / "dashboard.html"),
                    help="Output HTML path (default: ad-generator/dashboard.html)")
    ap.add_argument("--no-videos", action="store_true",
                    help="Preskočiť PVF videá (len statické bannery)")
    args = ap.parse_args()

    items = discover_all_brands()
    sections, total_failed = build_members(items)

    # Videá (PVF) — postery najprv, potom sekcie; bez ffmpeg sa len preskočia
    n_videos = 0
    if not args.no_videos:
        for v in all_videos():
            make_poster(v["path"], POSTER_DIR / v["poster"])
        video_sections = discover_videos()
        n_videos = sum(len(ms) for s in video_sections.values() for ms in s["collections"].values())
        sections.update(video_sections)

    save_hash_cache()
    try:
        vs = sync_vystupy(sections)
        print(f"  Výstupy: {vs['spolu']} súborov v {VYSTUPY_DIR} (nové {vs['nové']}, odstránené {vs['odstránené']})")
    except Exception as e:  # zrkadlo nesmie zhodiť dashboard
        print(f"  ⚠ Výstupy sa nepodarilo zrkadliť: {e}")
    html_content = build_html(sections, total_failed)
    output_path = Path(args.output)
    output_path.write_text(html_content, encoding="utf-8")

    brands = sorted({s["brand"] for s in sections.values()})
    total_banners = sum(len(ms) for s in sections.values() for ms in s["collections"].values())
    total_motifs = sum(len(s["collections"]) for s in sections.values())
    multi = sum(1 for s in sections.values() for ms in s["collections"].values() if len(ms) > 1)
    print(f"✓ Dashboard saved: {output_path}")
    print(f"  Brandy: {len(brands)} ({', '.join(brands)})")
    print(f"  Sekcie: {len(sections)} · Motívy: {total_motifs} (z toho {multi} viacformátových)"
          f" · Kreatívy: {total_banners} (z toho 🎬 {n_videos} videí)")


if __name__ == "__main__":
    main()
