"""
Cenník a denník generovaní — spoločný pre generate_ads.py (zápis) a build_dashboard.py (štatistiky).

Ceny overené 2026-10-16 z oficiálnych cenníkov (USD, bez DPH):
  - Gemini API  https://ai.google.dev/gemini-api/docs/pricing
  - ElevenLabs  https://elevenlabs.io/pricing/api
Keď sa cenník zmení, uprav LEN tento súbor — denník si pri každom zázname ukladá cenu platnú v čase generovania.
"""

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # AdGenerator-Pro/staticky
COST_LOG = ROOT / "cost-log.jsonl"
PRICES_CHECKED = "2026-10-16"

IMAGE_MODEL = "gemini-3.1-flash-image-preview"          # Nano Banana 2 (generate_ads.py)

# Cena za 1 vygenerovaný obrázok podľa rozlíšenia — realtime (google) a Batch API (polovica)
IMAGE_PRICE = {
    "realtime": {"0.5K": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151},
    "batch":    {"0.5K": 0.022, "1K": 0.034, "2K": 0.050, "4K": 0.076},
}
# Vstup: text promptu + referenčné obrázky (brand karty, produkt, štýl). 0,50 $ / 1M tokenov,
# obrázok ≈ 1 100 tokenov, prompt ≈ 1 500 tokenov → ~0,0006 $ za obrázok + ~0,0008 $ za prompt.
INPUT_PER_IMAGE = {"realtime": 0.00055, "batch": 0.00028}
INPUT_PER_PROMPT = {"realtime": 0.00075, "batch": 0.00038}
DEFAULT_INPUT_IMAGES = 4                                # typicky 2 brand karty + produkt + štýl

# Video
VOICE_MODEL = "eleven_multilingual_v2"
VOICE_PRICE_PER_1K_CHARS = 0.08                        # ElevenLabs API, Multilingual v2 / v3
VOICE_PRICE_BY_MODEL = {                               # $ / 1 000 znakov (API, Creator/Pro)
    "eleven_multilingual_v2": 0.08, "eleven_v3": 0.08,
    "eleven_turbo_v2_5": 0.04, "eleven_flash_v2_5": 0.04,
}
VOICE_DEFAULT_CHARS = 380                              # ~25 s voiceover, keď script nemá text
VEO_PRICE_PER_SECOND = {                               # AI video klipy (07-video-generation)
    "veo-3.0-fast-generate-001": 0.15,                 # 3.0 už nie je v cenníku — cena z čias použitia
    "veo-3.0-generate-001": 0.40,
    "veo-3.1-fast-generate-preview": 0.12,
    "veo-3.1-generate-preview": 0.40,
    "gemini-omni-1.1-flash": 0.10,
}
VEO_DEFAULT_SECONDS = 8
VEO_DEFAULT_MODEL = "veo-3.0-fast-generate-001"         # default v 07-video-generation/generate_videos.py
OMNI_PRICE_PER_SECOND = 0.10                           # gemini-omni-1.1-flash, 720p (~5 792 tokenov/s × 17,50 $/1M)

# Skutočná útrata z faktúry (Google AI Studio / Cloud Billing, ElevenLabs…) — ak ju doplníš, PREBIJE odhad
# v dashboarde pre danú kategóriu. Kľúče: img_out, img_in, voice, veo, omni. Príklad: {"veo": 42.80}
MANUAL_SPEND = {}


def tier_from_size(w: int, h: int) -> str:
    """Rozlíšenie podľa reálnych pixelov — Google provider parameter --resolution neposiela, výstup je 1K."""
    side = max(w or 0, h or 0)
    if not side:
        return "1K"
    if side <= 700:
        return "0.5K"
    if side <= 1500:
        return "1K"
    if side <= 2800:
        return "2K"
    return "4K"


def mode_of(provider: str) -> str:
    return "batch" if "batch" in (provider or "") else "realtime"


def image_cost(provider: str, tier: str, n_inputs: int = DEFAULT_INPUT_IMAGES) -> dict:
    """Rozpad ceny jedného banneru: výstup (obrázok) + vstup (referencie a prompt)."""
    mode = mode_of(provider)
    out = IMAGE_PRICE[mode].get(tier, IMAGE_PRICE[mode]["1K"])
    inp = INPUT_PER_PROMPT[mode] + INPUT_PER_IMAGE[mode] * (n_inputs if n_inputs is not None else DEFAULT_INPUT_IMAGES)
    return {"output": round(out, 5), "input": round(inp, 5), "total": round(out + inp, 5)}


def voice_cost(chars: int, model: str = None) -> float:
    price = VOICE_PRICE_BY_MODEL.get(model or VOICE_MODEL, VOICE_PRICE_PER_1K_CHARS)
    return round((chars or VOICE_DEFAULT_CHARS) / 1000 * price, 5)


def log_generation(entry: dict):
    """Pripíše záznam do cost-log.jsonl (append-only). Zlyhanie zápisu nikdy nezhodí generovanie."""
    try:
        entry = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), **entry}
        with open(COST_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def read_log() -> list:
    if not COST_LOG.exists():
        return []
    out = []
    for line in COST_LOG.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out
