#!/usr/bin/env python3
"""Modul 2 — z textu skriptu vyrobí voiceover (mp3) + presné časovanie slov.

Vstup:  cache/script_<id>.json
Výstup: cache/voice_<id>.mp3
        cache/words_<id>.json  -> [{"word": "...", "start": s, "end": s}, ...]
        (start/end v sekundách)

edge-tts vracia WordBoundary eventy s časom v 100ns jednotkách.
"""
import asyncio
import base64
import json
import os
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"



# Denník nákladov AdGenerator Pro (staticky/tools/pricing.py) — zlyhanie nikdy nezastaví výrobu
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "staticky" / "tools"))
    import pricing as _pricing
except Exception:
    _pricing = None


def load_config():
    return json.loads((ROOT / os.environ.get("FF_CONFIG", "config.json")).read_text())


def full_text(script: dict) -> str:
    # voice_hook / voice / voice_cta = text pre TTS (celé slová, URL slovom)
    # hook / text / cta = display text pre titulky (skratky, symboly)
    parts = [script.get("voice_hook", script["hook"]).strip()]
    for seg in script["segments"]:
        parts.append(seg.get("voice", seg["text"]).strip())
    parts.append(script.get("voice_cta", script["cta"]).strip())
    # spojíme medzerou; bodky v texte zabezpečia prirodzené pauzy
    return "  ".join(parts)


def split_sentence(text, start, dur):
    """Rozdeľ vetu na slová a každému prirad čas proporčne podľa dĺžky slova."""
    toks = text.split()
    if not toks:
        return []
    weights = [len(t) + 1 for t in toks]
    tot = sum(weights)
    out, t = [], start
    for tok, wt in zip(toks, weights):
        d = dur * wt / tot
        out.append({"word": tok, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


async def synth(text, voice, rate, mp3_path, words_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    words = []          # ak by hlas dával WordBoundary
    sentences = []      # SentenceBoundary (default v edge-tts 7.x)
    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            t = chunk["type"]
            if t == "audio":
                f.write(chunk["data"])
            elif t == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append(
                    {"word": chunk["text"], "start": round(s, 3),
                     "end": round(s + chunk["duration"] / 1e7, 3)}
                )
            elif t == "SentenceBoundary":
                sentences.append(
                    {"text": chunk["text"], "start": chunk["offset"] / 1e7,
                     "dur": chunk["duration"] / 1e7}
                )

    # ak nemáme word-level, odvodíme ho z viet
    if not words and sentences:
        for s in sentences:
            words.extend(split_sentence(s["text"], s["start"], s["dur"]))

    Path(words_path).write_text(json.dumps(words, ensure_ascii=False, indent=2))


def words_from_chars(chars, starts, ends):
    """Z character-level alignmentu (ElevenLabs) poskladaj slová."""
    words, cur, cs, ce = [], "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": round(cs, 3), "end": round(ce, 3)})
                cur, cs = "", None
        else:
            if cs is None:
                cs = s
            cur += ch
            ce = e
    if cur:
        words.append({"word": cur, "start": round(cs, 3), "end": round(ce, 3)})
    return words


def synth_elevenlabs(text, cfg, api_key, mp3_path, words_path):
    """Voiceover cez ElevenLabs (with-timestamps) — presné časovanie slov."""
    import requests

    voice_id = cfg.get("elevenlabs_voice_id", "nPczCjzI2devNBz1zQrb")  # default: Brian
    model = cfg.get("elevenlabs_model", "eleven_turbo_v2_5")
    payload = {"text": text, "model_id": model, "output_format": "mp3_44100_128"}

    # Jazyk vynútime explicitne — bez neho si model háda jazyk z textu a pri
    # menej zastúpených jazykoch (hu) rozpadne výslovnosť. Podporujú len
    # turbo_v2_5 / flash_v2_5; multilingual_v2 pole ignoruje resp. odmietne.
    lang = cfg.get("elevenlabs_language_code") or cfg.get("language")
    if lang and model in ("eleven_turbo_v2_5", "eleven_flash_v2_5"):
        payload["language_code"] = lang

    vs = cfg.get("elevenlabs_voice_settings")
    if vs:
        payload["voice_settings"] = vs

    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        headers={"xi-api-key": api_key, "content-type": "application/json"},
        json=payload,
        timeout=180,
    )
    if not r.ok:
        print(f"ElevenLabs {r.status_code}: {r.text[:400]}")
    r.raise_for_status()
    data = r.json()
    Path(mp3_path).write_bytes(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or data.get("normalized_alignment") or {}
    words = words_from_chars(
        al.get("characters", []),
        al.get("character_start_times_seconds", []),
        al.get("character_end_times_seconds", []),
    )
    Path(words_path).write_text(json.dumps(words, ensure_ascii=False, indent=2))


def run(script_path: str):
    cfg = load_config()
    script = json.loads(Path(script_path).read_text())
    vid = script["id"]
    mp3_path = CACHE / f"voice_{vid}.mp3"
    words_path = CACHE / f"words_{vid}.json"
    text = full_text(script)

    provider = cfg.get("voice_provider", "edge")
    el_key = cfg.get("elevenlabs_api_key") or os.environ.get("ELEVENLABS_API_KEY")
    use_el = provider == "elevenlabs" and el_key
    if use_el:
        try:
            synth_elevenlabs(text, cfg, el_key, mp3_path, words_path)
            if _pricing:
                model = cfg.get("elevenlabs_model", "eleven_turbo_v2_5")
                _pricing.log_generation({"kind": "voice", "script": vid, "model": model, "chars": len(text),
                                         "cost_usd": _pricing.voice_cost(len(text), model),
                                         "prices_checked": _pricing.PRICES_CHECKED})
        except Exception as e:
            # napr. minuté kredity -> plynulý fallback na edge-tts (free)
            print(f"  (ElevenLabs zlyhal: {e} -> fallback na edge-tts)", file=sys.stderr)
            use_el = False
    if not use_el:
        if provider == "elevenlabs" and not el_key:
            print("  (ElevenLabs kľúč chýba -> používam edge-tts)", file=sys.stderr)
        asyncio.run(synth(text, cfg["voice"], cfg["voice_rate"], mp3_path, words_path))

    print(str(mp3_path))
    return mp3_path, words_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("použitie: step2_voice.py <script_json>", file=sys.stderr)
        sys.exit(1)
    try:
        run(sys.argv[1])
    except Exception as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        sys.exit(1)
