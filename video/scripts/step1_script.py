#!/usr/bin/env python3
"""Modul 1 — vygeneruje skript videa cez `claude -p` a uloží ako JSON.

Výstup (cache/script_<id>.json):
{
  "id": "...",
  "title": "...",            # názov videa (pre upload)
  "hook": "...",             # prvá veta, scroll-stop
  "segments": [              # jednotlivé fakty
     {"text": "...", "stock_query": "two-three EN keywords for Pexels"}
  ],
  "cta": "...",              # výzva na konci
  "description": "...",      # popis pre YouTube/IG
  "hashtags": ["#space", ...]
}
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
CACHE.mkdir(exist_ok=True)
USED = CACHE / "used_topics.txt"

# Copy playbook značky (voliteľný) — cesta v config.json → "copy_playbook" (relatívne k video/ alebo absolútne).
# Je to tvoj dokument s pravidlami copy, víťaznými hookmi a tónom značky; prompt ho prečíta ako záväzný kontext.


def load_config():
    return json.loads((ROOT / os.environ.get("FF_CONFIG", "config.json")).read_text())


def recent_topics(limit=60):
    if not USED.exists():
        return []
    lines = [l.strip() for l in USED.read_text().splitlines() if l.strip()]
    return lines[-limit:]


def load_playbook(cfg):
    """Načíta copy playbook značky ako kontext do promptu (ak je v configu nastavený)."""
    path = (cfg.get("copy_playbook") or "").strip()
    if not path:
        return ""
    p = Path(path) if Path(path).is_absolute() else ROOT / path
    try:
        return p.read_text()
    except Exception:
        return ""


def build_prompt(cfg):
    avoid = recent_topics()
    avoid_block = ""
    if avoid:
        avoid_block = (
            "\n\nNEPOUŽI znova tieto už použité hooky/uhly:\n- "
            + "\n- ".join(avoid)
        )

    n = cfg.get("segments_per_video", cfg.get("facts_per_video", 4))
    secs = cfg["target_seconds"]
    # ~2.2 slov/s pre slovenský hovorený prejav
    words = int(secs * 2.2)
    brand = cfg.get("brand_name") or cfg.get("channel_name") or "značka"
    lang = cfg.get("language", "sk")
    brief = os.environ.get("PVF_BRIEF") or cfg.get("brief", "").strip()
    brief_block = (
        f"\n=== BRIEF OD ZADÁVATEĽA (riaď sa ním) ===\n{brief}\n"
        if brief
        else f"\n=== BRIEF ===\n(žiadny konkrétny brief — sprav všeobecné predajné Reels pre {brand}, "
        "vyber silný uhol, napr. Question Hook alebo Announcement)\n"
    )

    playbook = load_playbook(cfg)
    playbook_block = (
        f"\n=== ZNALOSTNÁ BÁZA: copy playbook značky {brand} (záväzná) ===\n{playbook}\n=== KONIEC PLAYBOOKU ===\n"
        if playbook
        else ""
    )

    return f"""Si expert na krátke vertikálne video reklamy (Reels / Shorts) pre značku **{brand}**.

Tvoja úloha: napíš JEDEN tesný skript pre 9:16 video s **hovoreným voiceoverom** v jazyku „{lang}",
dĺžka cca {secs} sekúnd (~{words} slov). Text píš so správnou diakritikou a gramatikou.
{brief_block}{playbook_block}
=== PRAVIDLÁ (NIKDY neporušiť) ===
- Dokonalá gramatika a diakritika. Nikdy nevymýšľaj slová.
- NIKDY meno konkurenčnej značky — len generická kategória.
- Urgency len VŠEOBECNÁ („kým platí ponuka", „neváhajte") — NIKDY konkrétne („len X kusov", „do 24 h").
- Žiadny vágny social proof — len konkrétne, pravdivé čísla, ak vôbec.
- Žiadne nepodložené tvrdenia o zdraví či účinkoch.
- Drž sa pravidiel a víťazných vzorov z playbooku vyššie (ak je).

=== HOOK (prvé 1-2 sekundy — 80 % energie sem) ===
- Jediná úloha hooku: zastaviť scroll a otvoriť zvedavosť. Žiadne "Vedeli ste", žiadny pomalý úvod.
- Hovor divákovi "TY/VY/VÁŠ", pomenuj reálny problém alebo silnú túžbu.
- Krátke, úderné vety. Nedávaj pointu hneď — nechaj slučku otvorenú.

=== TELO ({n} segmentov) ===
- Pravidlo jednej myšlienky: celé video podporuje JEDEN hlavný benefit. Každý segment ho posilní.
- Každý segment = 1-2 hovorené vety, prirodzená hovorová slovenčina, ľahké na čítanie nahlas.
- Emócia pred logikou, konkrétne benefity produktu.
- Každý segment jemne ťahá k ďalšiemu, aby divák dopozeral.
- DÔLEŽITÉ: počet segmentov = PRESNE {n} (každý segment = ~1 videoklip).

=== CTA ===
- Krátka, jeden riadok. Vyzvi na nákup / návštevu e-shopu značky (všeobecná urgency povolená).

Daj aj: pútavý titul (max 60 znakov), 1-2 vetový popis, 6-10 relevantných hashtagov (SK/EN mix ok).

Vráť IBA validný JSON, žiadny markdown, PRESNE v tomto tvare:
{{
  "title": "...",
  "hook": "...",
  "segments": [
    {{"text": "..."}}
  ],
  "cta": "...",
  "description": "...",
  "hashtags": ["#...", "#..."]
}}{avoid_block}
"""


def extract_json(raw: str) -> dict:
    raw = raw.strip()
    # odstráň prípadný ```json ... ``` obal
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.S)
    if fence:
        raw = fence.group(1)
    else:
        # nájdi prvý { ... posledný }
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            raw = raw[start : end + 1]
    return json.loads(raw)


def call_via_api(prompt: str, cfg: dict) -> str:
    """Generovanie cez Anthropic API (vhodné pre cron / plnú automatizáciu).
    Aktivuje sa, ak je nastavená env premenná ANTHROPIC_API_KEY."""
    import requests

    model = cfg.get("anthropic_model", "claude-haiku-5-5")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def call_claude_cli(prompt: str) -> str:
    res = subprocess.run(
        ["claude", "-p", prompt], capture_output=True, text=True, timeout=180
    )
    if res.returncode != 0:
        raise RuntimeError(f"claude -p zlyhal: {res.stderr.strip()}")
    out = res.stdout.strip()
    if not out:
        raise RuntimeError(
            "claude -p vrátil prázdny výstup. Spúšťaš to vnútri inej Claude session? "
            "Spusti pipeline v samostatnom termináli, alebo nastav ANTHROPIC_API_KEY "
            "(potom sa použije API)."
        )
    return out


def call_claude(prompt: str, cfg: dict) -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return call_via_api(prompt, cfg)
    return call_claude_cli(prompt)


def generate():
    cfg = load_config()
    data = extract_json(call_claude(build_prompt(cfg), cfg))

    vid = time.strftime("%Y%m%d_%H%M%S")
    data["id"] = vid

    # ulož tému do dedup logu (krátky popis hooku)
    with USED.open("a") as f:
        f.write(data.get("hook", vid).strip()[:120] + "\n")

    out = CACHE / f"script_{vid}.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(str(out))
    return out


if __name__ == "__main__":
    try:
        generate()
    except Exception as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        sys.exit(1)
