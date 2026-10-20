"""
Tab „Štatistiky" v dashboarde — koľko kreatív vzniklo, koľko stáli a za čo sa platí.

Zdroj cien:
  - cost-log.jsonl (od 2026-10-16): presný záznam každého úspešného generovania vrátane pregenerovaní
  - staršie bannery: odhad z providera (realtime / batch) a reálneho rozlíšenia súboru × cenník v pricing.py
  - videá: voiceover ElevenLabs podľa dĺžky scriptu (1× na script a jazyk) + AI klipy Veo z manifestov footage
Grafy sú čisté HTML/SVG (bez knižníc), farby podľa validovanej palety (dataviz skill).
"""

import html
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pricing
import subprocess


def probe_width(path) -> int:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width",
                              "-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=10).stdout.strip()
        return int(out)
    except Exception:
        return 0


def probe_duration(path) -> float:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return float(out)
    except Exception:
        return 0.0

MONTHS = ["jan", "feb", "mar", "apr", "máj", "jún", "júl", "aug", "sep", "okt", "nov", "dec"]


def esc(s) -> str:
    return html.escape(str(s))


def usd(x: float) -> str:
    if x >= 100:
        return f"{x:,.0f} $".replace(",", " ")
    if 0 < x < 1:
        return f"{x:.3f} $".replace(".", ",")
    return f"{x:,.2f} $".replace(",", " ").replace(".", ",")


def pct(x: float) -> str:
    return f"{x:.1f} %".replace(".", ",")


def month_key(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m") if ts else "?"


def month_label(key: str) -> str:
    try:
        y, m = key.split("-")
        return f"{MONTHS[int(m) - 1]} {y[2:]}"
    except Exception:
        return key


def compute(sections: dict, video_root: Path) -> dict:
    images, videos, video_cards = [], [], 0
    for section in sections.values():
        for members in section["collections"].values():
            if members and members[0].get("kind") == "video":
                video_cards += 1
                videos.extend(members)
            else:
                images.extend(members)

    full_log = pricing.read_log()
    log = [e for e in full_log if e.get("kind") == "image"]
    vlog = {k: [e for e in full_log if e.get("kind") == k] for k in ("voice", "veo", "omni")}
    logged_scripts = {e.get("script") for e in vlog["voice"]}
    logged_clips = {e.get("clip") for e in vlog["veo"] + vlog["omni"]}
    logged = {e.get("file") for e in log}

    cat = defaultdict(float)          # za čo sa platí
    month_cost = defaultdict(lambda: [0.0, 0.0])   # [statiky, videá]
    month_count = defaultdict(lambda: [0, 0])
    brand = defaultdict(lambda: {"img": 0, "vid": 0, "cost": 0.0})
    fmt = defaultdict(int)
    lang = defaultdict(int)
    mode_tier = defaultdict(int)
    estimated = 0

    for m in images:
        mk = month_key(m.get("mtime", 0))
        month_count[mk][0] += 1
        brand[m["brand"]]["img"] += 1
        fmt[m.get("format", "?")] += 1
        lang[m.get("country", "?")] += 1
        mode = "Batch" if pricing.mode_of(m.get("provider")) == "batch" else "Realtime"
        mode_tier[f"{mode} {m.get('tier', '1K')}"] += 1
        if m.get("file") in logged:
            continue  # zaplatené sa počíta z denníka nižšie
        c = pricing.image_cost(m.get("provider"), m.get("tier", "1K"))
        estimated += 1
        cat["img_out"] += c["output"]
        cat["img_in"] += c["input"]
        month_cost[mk][0] += c["total"]
        brand[m["brand"]]["cost"] += c["total"]

    log_total = 0.0
    for e in log:
        out, inp = e.get("cost_output", 0) or 0, e.get("cost_input", 0) or 0
        cat["img_out"] += out
        cat["img_in"] += inp
        log_total += out + inp
        try:
            mk = e["at"][:7]
        except Exception:
            mk = "?"
        month_cost[mk][0] += out + inp
        if e.get("brand"):
            brand[e["brand"].lower()]["cost"] += out + inp

    # Videá — jeden voiceover na script a jazyk (FINAL aj REMOTION zdieľajú ten istý)
    vo = {}
    for m in videos:
        key = (m.get("ad_id"), m.get("country"))
        vo[key] = max(vo.get(key, (0, 0, ""))[0], m.get("vo_chars", 0)), m.get("mtime", 0), m["brand"]
    unique_videos = len(vo)
    for (ad_id, _), (chars, ts, b) in vo.items():
        mk = month_key(ts)
        month_count[mk][1] += 1
        brand[b]["vid"] += 1
        if ad_id in logged_scripts:
            continue   # presná cena je v denníku (nižšie)
        c = pricing.voice_cost(chars)
        cat["voice"] += c
        month_cost[mk][1] += c
        brand[b]["cost"] += c

    # AI video klipy — Veo: každý variant v 07-video-generation/video-prompts-*.json = 1 request
    # (generate_videos.py generuje všetky varianty shootu); hotové súbory sa potom premenúvajú na seq_*,
    # preto sa nedajú spočítať zo súborov. Omni a ostatné AI klipy sa rozlíšia podľa názvu a metadát vo footage.
    clips = 0
    prompt_dir = video_root.parent / "staticky" / "07-video-generation"
    veo_price = pricing.VEO_PRICE_PER_SECOND.get(pricing.VEO_DEFAULT_MODEL, 0.15)
    for pf in prompt_dir.glob("video-prompts-*.json"):
        try:
            d = json.loads(pf.read_text(encoding="utf-8"))
        except Exception:
            continue
        price = pricing.VEO_PRICE_PER_SECOND.get(d.get("model") or "", veo_price)
        for c in d.get("clips") or d.get("prompts") or []:
            vars_ = c.get("variants") if isinstance(c.get("variants"), list) else [{}]
            # varianty, ktoré už majú presný záznam v denníku, sa neodhadujú
            n = sum(1 for v in vars_ if f"{c.get('clip_id')}_{c.get('slug')}_{v.get('variant')}.mp4" not in logged_clips)
            secs = c.get("duration") or pricing.VEO_DEFAULT_SECONDS
            clips += n
            cat["veo"] += n * secs * price
            month_cost[month_key(pf.stat().st_mtime)][1] += n * secs * price

    omni, other_ai = [], []
    footage = video_root / "assets"
    for f in footage.glob("footage*/*.mp4"):
        name = f.name
        if probe_width(f) == 716:
            other_ai.append(f)                      # iný AI nástroj (716×1284) — mimo Google
        elif name.endswith(("-cz.mp4", "-hu.mp4")):
            continue                             # CZ/HU hooky sú dabing pôvodného klipu, nie nový klip
        elif name.startswith(("hook_", "intro_")):
            omni.append(f)
        elif name.startswith("seq_") and probe_width(f) in (716, 720):
            omni.append(f)                       # AI klip v 720p medzi inak natočenými (1080×1920) zábermi
    for f in omni:
        if f.name in logged_clips:
            continue
        dur = (probe_duration(f) or 7)
        c = dur * pricing.OMNI_PRICE_PER_SECOND
        cat["omni"] += c
        month_cost[month_key(f.stat().st_mtime)][1] += c

    # presné záznamy z denníka (od 2026-10-16): voiceover, Veo, Omni
    video_logged = 0.0
    for kind, key in (("voice", "voice"), ("veo", "veo"), ("omni", "omni")):
        for e in vlog[kind]:
            c = e.get("cost_usd", 0) or 0
            cat[key] += c
            video_logged += c
            month_cost[(e.get("at") or "?")[:7]][1] += c
    clips += len(vlog["veo"])

    # ručne zadaná skutočná útrata z faktúr prebije odhad
    for k, v in (pricing.MANUAL_SPEND or {}).items():
        if v is not None and k in ("img_out", "img_in", "voice", "veo", "omni"):
            cat[k] = float(v)

    total_img = cat["img_out"] + cat["img_in"]
    total_vid = cat["voice"] + cat["veo"] + cat["omni"]
    return {
        "n_images": len(images), "n_image_motifs": sum(1 for s in sections.values() if s["product"] != "pvf-video" for _ in s["collections"]),
        "n_videos": unique_videos, "n_video_files": len(videos), "n_clips": clips,
        "n_omni": len(omni), "n_other_ai": len(other_ai),
        "total": total_img + total_vid, "total_img": total_img, "total_vid": total_vid,
        "cat": dict(cat), "estimated": estimated, "log_entries": len(log), "log_total": log_total,
        "video_log_entries": sum(len(v) for v in vlog.values()), "video_logged": video_logged,
        "month_cost": dict(month_cost), "month_count": dict(month_count),
        "brand": dict(brand), "fmt": dict(fmt), "lang": dict(lang), "mode_tier": dict(mode_tier),
    }


# ---------------------------------------------------------------------------
# Vykreslenie
# ---------------------------------------------------------------------------

def kpi(label, value, sub=""):
    return f'<div class="kpi"><span class="kpi-l">{esc(label)}</span><span class="kpi-v">{value}</span>{f"<span class=kpi-s>{sub}</span>" if sub else ""}</div>'


def barlist(rows, unit_fmt=lambda v: str(v), series="1", tip=lambda r: ""):
    """rows: [(label, value, extra_html)] — vodorovné pruhy s popisom a hodnotou (priame štítky)."""
    if not rows:
        return '<p class="muted">Zatiaľ žiadne dáta.</p>'
    mx = max(v for _, v, _ in rows) or 1
    out = []
    for label, v, extra in rows:
        w = max(v / mx * 100, 0.8)
        out.append(f'<div class="bl-row" data-tip="{esc(tip((label, v, extra)) or f"{label}: {unit_fmt(v)}")}">'
                   f'<span class="bl-label">{esc(label)}</span>'
                   f'<span class="bl-track"><i class="bl-bar s{series}" style="width:{w:.1f}%"></i></span>'
                   f'<span class="bl-val">{unit_fmt(v)}{extra}</span></div>')
    return '<div class="barlist">' + "".join(out) + "</div>"


def month_chart(data: dict, labels=("Statiky", "Videá"), money=False):
    """Zvislé zložené stĺpce po mesiacoch (statiky + videá), hodnota celkom nad stĺpcom."""
    keys = sorted(k for k in data if k != "?")
    if not keys:
        return '<p class="muted">Zatiaľ žiadne dáta.</p>'
    W, H, pad_l, pad_b, pad_t = 640, 220, 8, 26, 22
    n = len(keys)
    slot = (W - pad_l) / n
    bw = min(46, slot * 0.62)
    mx = max(sum(data[k]) for k in keys) or 1
    fmtv = usd if money else (lambda v: f"{int(v):,}".replace(",", " "))
    bars = []
    for i, k in enumerate(keys):
        a, b = data[k]
        x = pad_l + i * slot + (slot - bw) / 2
        ha = (a / mx) * (H - pad_b - pad_t)
        hb = (b / mx) * (H - pad_b - pad_t)
        y0 = H - pad_b
        tip = f"{month_label(k)} — {labels[0]}: {fmtv(a)} · {labels[1]}: {fmtv(b)}"
        g = f'<g class="mc" data-tip="{esc(tip)}"><rect class="hit" x="{x - 4:.1f}" y="{pad_t - 10}" width="{bw + 8:.1f}" height="{H - pad_b - pad_t + 10}"/>'
        if a:
            g += f'<rect class="s1" x="{x:.1f}" y="{y0 - ha:.1f}" width="{bw:.1f}" height="{max(ha, 1):.1f}" rx="4"/>'
        if b:
            g += f'<rect class="s2" x="{x:.1f}" y="{y0 - ha - hb - (2 if a else 0):.1f}" width="{bw:.1f}" height="{max(hb, 1):.1f}" rx="4"/>'
        g += f'<text class="v" x="{x + bw / 2:.1f}" y="{y0 - ha - hb - 6:.1f}">{fmtv(a + b)}</text>'
        g += f'<text class="x" x="{x + bw / 2:.1f}" y="{H - 8}">{esc(month_label(k))}</text></g>'
        bars.append(g)
    legend = (f'<div class="legend"><span><i class="sw s1"></i>{labels[0]}</span>'
              f'<span><i class="sw s2"></i>{labels[1]}</span></div>')
    table = "".join(f"<tr><td>{esc(month_label(k))}</td><td>{fmtv(data[k][0])}</td><td>{fmtv(data[k][1])}</td></tr>" for k in keys)
    return (legend + f'<svg class="mchart" viewBox="0 0 {W} {H}" role="img"><line class="base" x1="0" x2="{W}" y1="{H - pad_b}" y2="{H - pad_b}"/>{"".join(bars)}</svg>'
            f'<details class="tbl"><summary>Tabuľka</summary><table><tr><th>Mesiac</th><th>{labels[0]}</th><th>{labels[1]}</th></tr>{table}</table></details>')


LANG_ORDER = ["SK", "CZ", "HU", "DE", "PL", "RO", "IT", "EN"]


def coverage(sections: dict) -> str:
    """Mapa jazykov: ktorý ad-set (koncept) existuje v ktorom jazyku — klik otvorí bannery."""
    rows = {}
    for (brand, product, adset, lang, variant), sec in sections.items():
        if product == "pvf-video":
            continue
        n = sum(len(m) for m in sec["collections"].values())
        r = rows.setdefault((brand, product, adset), {"langs": {}, "mtime": 0})
        r["langs"][lang.upper()] = r["langs"].get(lang.upper(), 0) + n
        r["mtime"] = max(r["mtime"], sec.get("mtime", 0))
    langs = [l for l in LANG_ORDER if any(l in r["langs"] for r in rows.values())]
    brands = sorted({b for b, _, _ in rows})
    opts = "".join(f'<option value="{esc(b)}">{esc(b)}</option>' for b in brands)
    body = []
    for (brand, product, adset), r in sorted(rows.items(), key=lambda kv: (kv[0][0], -kv[1]["mtime"])):
        cells = []
        for l in langs:
            n = r["langs"].get(l)
            if n:
                href = f"dashboard.html?tab=banners&brand={brand}&product={product}&adset={adset}&country={l.lower()}"
                cells.append(f'<td class="cov-on"><a href="{esc(href)}" data-tip="{esc(adset)} · {l}: {n} bannerov">{n}</a></td>')
            else:
                cells.append('<td class="cov-off">—</td>')
        multi = " multi" if len(r["langs"]) > 1 else ""
        body.append(f'<tr class="cov-row{multi}" data-brand="{esc(brand)}"><td class="cov-name"><b>{esc(adset)}</b>'
                    f'<span>{esc(brand)} · {esc(product)}</span></td>{"".join(cells)}</tr>')
    head = "".join(f"<th>{l}</th>" for l in langs)
    return f"""
    <div class="stat-card"><div class="cov-head"><h3>Pokrytie jazykov</h3>
      <label>Klient <select id="cov-brand"><option value="">všetci</option>{opts}</select></label>
      <label class="cov-check"><input type="checkbox" id="cov-multi"> len viacjazyčné</label></div>
      <p class="note" style="margin:0 0 10px">Riadok = ad-set (koncept), číslo = počet bannerov v danom jazyku, „—" = v tom jazyku chýba. Klik otvorí bannery.</p>
      <div class="cov-wrap"><table class="cov"><thead><tr><th>Ad-set</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div></div>"""


def build(sections: dict, video_root: Path) -> str:
    st = compute(sections, video_root)
    c = st["cat"]
    total = st["total"] or 1
    avg_img = st["total_img"] / st["n_images"] if st["n_images"] else 0
    avg_vid = st["total_vid"] / st["n_videos"] if st["n_videos"] else 0

    kpis = "".join([
        kpi("Bannery", f'{st["n_images"]:,}'.replace(",", " "), f'{st["n_image_motifs"]} motívov'),
        kpi("Videá", f'{st["n_videos"]}', f'{st["n_video_files"]} súborov vrátane verzií'),
        kpi("Náklady spolu", usd(st["total"]), "odhad, USD bez DPH"),
        kpi("Bannery stáli", usd(st["total_img"]), f'≈ {usd(avg_img)} / banner'),
        kpi("Videá stáli", usd(st["total_vid"]), f'≈ {usd(avg_vid)} / video'),
    ])

    pay_rows = [
        ("Gemini — generovanie obrázkov", c.get("img_out", 0), "img_out",
         f"Výstup modelu {pricing.IMAGE_MODEL} (Nano Banana 2): 1K realtime {usd(pricing.IMAGE_PRICE['realtime']['1K'])}, batch {usd(pricing.IMAGE_PRICE['batch']['1K'])} za obrázok"),
        ("Gemini — vstupy (prompt + referencie)", c.get("img_in", 0), "img_in",
         "Text promptu + brand karty, produkt a štýl ako referenčné obrázky (0,50 $ / 1M tokenov)"),
        ("ElevenLabs — voiceover videí", c.get("voice", 0), "voice",
         f"Multilingual {usd(pricing.VOICE_PRICE_BY_MODEL['eleven_multilingual_v2'])}, Turbo {usd(pricing.VOICE_PRICE_BY_MODEL['eleven_turbo_v2_5'])} / 1 000 znakov · 1× na script a jazyk"),
        ("Veo — AI video klipy", c.get("veo", 0), "veo",
         f"{st['n_clips']} {'klip' if st['n_clips'] == 1 else 'klipy' if 2 <= st['n_clips'] <= 4 else 'klipov'} × {pricing.VEO_DEFAULT_SECONDS} s · {pricing.VEO_DEFAULT_MODEL} (všetky varianty z prompt súborov)"),
        ("Gemini Omni — UGC hooky a klipy", c.get("omni", 0), "omni",
         f"{st['n_omni']} klipov vo footage (UGC hooky, intro, AI sekvencie) × reálna dĺžka · {usd(pricing.OMNI_PRICE_PER_SECOND)} / s"),
    ]
    pay = []
    for i, (label, v, key, note) in enumerate(pay_rows, start=1):
        share = v / total * 100
        pay.append(f'<div class="pay-row" data-tip="{esc(label)}: {usd(v)} ({pct(share)})">'
                   f'<i class="sw s{i}"></i><div class="pay-main"><b>{esc(label)}</b><span>{esc(note)}</span></div>'
                   f'<div class="pay-amt"><b>{usd(v)}</b><span>{pct(share)}</span></div></div>')
    stack = "".join(f'<i class="s{i}" style="width:{(v / total * 100):.2f}%" data-tip="{esc(l)}: {usd(v)}"></i>'
                    for i, (l, v, _, _) in enumerate(pay_rows, start=1) if v > 0)
    flat = [
        ("Claude Code", "predplatné", "scripty, prompty, copy, dashboard — paušál, nepočíta sa na kus"),
        ("Remotion + ffmpeg", "zadarmo", "render videí lokálne na Macu"),
    ]
    flat_html = "".join(f'<div class="flat-row"><b>{esc(a)}</b><span class="chip">{esc(b)}</span><span>{esc(d)}</span></div>' for a, b, d in flat)

    brands = sorted(st["brand"].items(), key=lambda kv: -(kv[1]["img"] + kv[1]["vid"]))
    brand_count = barlist([(b, d["img"] + d["vid"], f' <small>({d["img"]} + {d["vid"]} vid.)</small>' if d["vid"] else "") for b, d in brands if d["img"] + d["vid"]],
                          unit_fmt=lambda v: f"{v:,}".replace(",", " "))
    brand_cost = barlist(sorted([(b, round(d["cost"], 2), "") for b, d in brands if d["cost"]], key=lambda r: -r[1]),
                         unit_fmt=usd, series="1")
    fmt_rows = barlist(sorted([(k, v, "") for k, v in st["fmt"].items()], key=lambda r: -r[1]), unit_fmt=str)
    lang_rows = barlist(sorted([(k or "?", v, "") for k, v in st["lang"].items()], key=lambda r: -r[1]), unit_fmt=str)
    mode_rows = barlist(sorted([(k, v, "") for k, v in st["mode_tier"].items()], key=lambda r: -r[1]), unit_fmt=str)

    vlog_note = (f' Videá: {st["video_log_entries"]} presných záznamov za {usd(st["video_logged"])}.' if st["video_log_entries"] else
                 ' Od 16. 10. 2026 sa zapisuje aj každý voiceover (ElevenLabs), Veo a Omni klip.')
    log_note = (f'Od 16. 10. 2026 sa každé generovanie zapisuje do denníka (<code>cost-log.jsonl</code>) — zatiaľ {st["log_entries"]} záznamov za {usd(st["log_total"])}.'
                if st["log_entries"] else 'Od 16. 10. 2026 sa každé nové generovanie zapisuje do denníka <code>cost-log.jsonl</code> s presným modelom, rozlíšením a cenou.')

    return f"""
  <section class="panel-section">
    <div class="panel-head"><h2>Štatistiky</h2>
      <p>Koľko kreatív vzniklo, koľko približne stáli a za čo sa platí. Ceny podľa oficiálnych cenníkov Google a ElevenLabs (overené {pricing.PRICES_CHECKED}), v USD bez DPH.</p></div>
    <div class="kpis">{kpis}</div>
  </section>

  <section class="panel-section">
    <div class="panel-head"><h3>Za čo sa platí</h3></div>
    <div class="stat-card">
      <div class="stackbar">{stack}</div>
      <div class="pay">{"".join(pay)}</div>
      <h4>Bez platby za kus</h4>
      <div class="flat">{flat_html}</div>
    </div>
  </section>

  <section class="panel-section">
    <div class="stat-grid two">
      <div class="stat-card"><h3>Vytvorené kreatívy po mesiacoch</h3>{month_chart(st["month_count"])}</div>
      <div class="stat-card"><h3>Náklady po mesiacoch</h3>{month_chart(st["month_cost"], money=True)}</div>
    </div>
  </section>

  <section class="panel-section">
    <div class="stat-grid two">
      <div class="stat-card"><h3>Kreatívy podľa klienta</h3>{brand_count}</div>
      <div class="stat-card"><h3>Náklady podľa klienta</h3>{brand_cost}</div>
    </div>
    <div class="stat-grid three">
      <div class="stat-card"><h3>Bannery podľa formátu</h3>{fmt_rows}</div>
      <div class="stat-card"><h3>Kreatívy podľa jazyka</h3>{lang_rows}</div>
      <div class="stat-card"><h3>Spôsob generovania</h3>{mode_rows}<p class="note">Realtime = okamžite, plná cena · Batch = hromadne, polovičná cena. Rozlíšenie podľa reálnej veľkosti súboru.</p></div>
    </div>
  </section>

  <section class="panel-section">{coverage(sections)}</section>

  <section class="panel-section">
    <div class="stat-card method"><h3>Ako sa to počíta</h3>
      <ul>
        <li><b>Bannery:</b> {st["estimated"]} existujúcich bannerov je odhadnutých z providera (realtime / batch) a reálneho rozlíšenia × cenník modelu {pricing.IMAGE_MODEL}. {log_note}{vlog_note}</li>
        <li><b>Staršie pregenerovania</b> (prepísané súbory, neúspešné pokusy pred 16. 10.) nie sú nikde zaznamenané — reálna suma za staršie obdobie bola o niečo vyššia.</li>
        <li><b>Videá:</b> voiceover ElevenLabs podľa dĺžky textu scriptu (bez scriptu ~{pricing.VOICE_DEFAULT_CHARS} znakov), 1× na script a jazyk. Ak máš ElevenLabs predplatné, platíš paušál a toto je len prepočet kreditov. AI klipy: Veo podľa všetkých variantov v <code>07-video-generation/video-prompts-*.json</code> (každý variant = 1 request, aj keď sa výsledok nepoužil), Omni podľa klipov vo footage a ich dĺžky. Neúspešné a opakované pokusy nie sú známe — <b>presnú sumu ukáže len faktúra</b> (Google AI Studio → Billing). Keď ju zadáš do <code>MANUAL_SPEND</code> v <code>tools/pricing.py</code>, prebije odhad.</li>
        <li>Cenník je v <code>tools/pricing.py</code> — pri zmene cien stačí upraviť ten súbor.</li>
      </ul></div>
  </section>"""


CSS = """
  /* ---------- Štatistiky ---------- */
  .stats-root { --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; }
  :root[data-theme="dark"] .stats-root { --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; }
  .kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
  .kpi { background: var(--bg-elev); border-radius: 18px; box-shadow: var(--shadow); padding: 16px 18px; display: flex; flex-direction: column; gap: 4px; }
  .kpi-l { font-size: 0.78rem; color: var(--label-2); font-weight: 600; }
  .kpi-v { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; color: var(--label); }
  .kpi-s { font-size: 0.74rem; color: var(--label-3); }
  .panel-head h3, .stat-card h3 { font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif; font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 12px; color: var(--label); }
  .stat-card { background: var(--bg-elev); border-radius: 18px; box-shadow: var(--shadow); padding: 18px 20px; }
  .stat-card h4 { font-size: 0.8rem; font-weight: 600; color: var(--label-2); margin: 18px 0 8px; text-transform: uppercase; letter-spacing: 0.03em; }
  .stat-grid { display: grid; gap: 20px; margin-bottom: 20px; }
  .stat-grid.two { grid-template-columns: 1fr 1fr; } .stat-grid.three { grid-template-columns: 1fr 1fr 1fr; }
  .stats-root .s1 { background: var(--s1); fill: var(--s1); } .stats-root .s2 { background: var(--s2); fill: var(--s2); }
  .stats-root .s3 { background: var(--s3); fill: var(--s3); } .stats-root .s4 { background: var(--s4); fill: var(--s4); }
  .stats-root .s5 { background: var(--s5); fill: var(--s5); }
  .stackbar { display: flex; gap: 2px; height: 14px; border-radius: 999px; overflow: hidden; background: var(--fill); margin-bottom: 14px; }
  .stackbar i { display: block; height: 100%; min-width: 3px; }
  .pay-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-top: 1px solid var(--sep); }
  .pay-row:first-child { border-top: none; }
  .sw { display: inline-block; width: 12px; height: 12px; border-radius: 4px; flex: 0 0 auto; }
  .pay-main { flex: 1; display: flex; flex-direction: column; gap: 2px; }
  .pay-main b { font-size: 0.9rem; color: var(--label); } .pay-main span { font-size: 0.76rem; color: var(--label-2); }
  .pay-amt { text-align: right; display: flex; flex-direction: column; font-variant-numeric: tabular-nums; }
  .pay-amt b { font-size: 1.05rem; color: var(--label); } .pay-amt span { font-size: 0.74rem; color: var(--label-3); }
  .flat { display: flex; flex-direction: column; gap: 6px; }
  .flat-row { display: grid; grid-template-columns: 150px 150px 1fr; gap: 10px; align-items: center; font-size: 0.82rem; color: var(--label-2); }
  .flat-row b { color: var(--label); }
  .flat-row .chip { justify-self: start; }
  .barlist { display: flex; flex-direction: column; gap: 7px; }
  .bl-row { display: grid; grid-template-columns: 110px 1fr auto; gap: 10px; align-items: center; font-size: 0.82rem; }
  .bl-label { color: var(--label); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bl-track { height: 12px; background: var(--fill); border-radius: 999px; overflow: hidden; }
  .bl-bar { display: block; height: 100%; border-radius: 4px; }
  .bl-row:hover .bl-bar { filter: brightness(1.12); }
  .bl-val { color: var(--label); font-variant-numeric: tabular-nums; font-weight: 600; white-space: nowrap; }
  .bl-val small { color: var(--label-3); font-weight: 500; }
  .legend { display: flex; gap: 16px; font-size: 0.78rem; color: var(--label-2); margin-bottom: 6px; }
  .legend span { display: inline-flex; align-items: center; gap: 6px; }
  .mchart { width: 100%; height: auto; overflow: visible; }
  .mchart .base { stroke: var(--sep); stroke-width: 1; }
  .mchart .hit { fill: transparent; }
  .mchart .mc:hover .hit { fill: var(--fill); }
  .mchart text { font-family: -apple-system, system-ui, sans-serif; text-anchor: middle; }
  .mchart text.v { font-size: 11px; font-weight: 700; fill: var(--label); font-variant-numeric: tabular-nums; }
  .mchart text.x { font-size: 11px; fill: var(--label-2); }
  .tbl table { margin-top: 8px; border-collapse: collapse; font-size: 0.8rem; width: 100%; }
  .tbl th, .tbl td { text-align: left; padding: 5px 8px; border-top: 1px solid var(--sep); color: var(--label-2); font-variant-numeric: tabular-nums; }
  .tbl th { color: var(--label-3); font-weight: 600; }
  .note { margin-top: 10px; font-size: 0.74rem; color: var(--label-3); line-height: 1.45; }
  .method ul { margin-left: 18px; font-size: 0.84rem; color: var(--label-2); line-height: 1.6; }
  .method b { color: var(--label); }
  .cov-head { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 6px; }
  .cov-head h3 { margin: 0; margin-right: auto; }
  .cov-head label { font-size: 0.8rem; color: var(--label-2); display: flex; align-items: center; gap: 6px; }
  .cov-head select { background: var(--fill); border: none; color: var(--label); padding: 5px 9px; border-radius: 8px; font-size: 0.82rem; }
  .cov-wrap { max-height: 520px; overflow: auto; border-radius: 12px; }
  .cov { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.82rem; }
  .cov th { position: sticky; top: 0; background: var(--bg-elev); z-index: 1; text-align: center; font-size: 0.72rem; color: var(--label-3); font-weight: 700; padding: 8px 6px; border-bottom: 1px solid var(--sep); }
  .cov th:first-child { text-align: left; }
  .cov td { padding: 7px 6px; border-bottom: 1px solid var(--sep); text-align: center; font-variant-numeric: tabular-nums; }
  .cov-name { text-align: left !important; }
  .cov-name b { display: block; color: var(--label); font-weight: 600; }
  .cov-name span { font-size: 0.72rem; color: var(--label-3); }
  .cov-on a { display: inline-block; min-width: 34px; padding: 3px 8px; border-radius: 999px; background: color-mix(in srgb, var(--s3) 18%, transparent); color: var(--label); font-weight: 700; text-decoration: none; }
  .cov-on a:hover { background: var(--s3); color: #fff; }
  .cov-off { color: var(--label-3); }
  .cov-row:hover td { background: var(--fill); }
  .viz-tip { position: fixed; z-index: 400; pointer-events: none; background: var(--material-strong); color: var(--label); border: 1px solid var(--material-edge); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); box-shadow: var(--shadow-lg); border-radius: 10px; padding: 7px 11px; font-size: 0.8rem; font-weight: 500; max-width: 320px; opacity: 0; transition: opacity 0.12s; }
  .viz-tip.show { opacity: 1; }
  @media (max-width: 1100px) { .kpis { grid-template-columns: repeat(2, 1fr); } .stat-grid.two, .stat-grid.three { grid-template-columns: 1fr; } }
"""

JS = """
  // Pokrytie jazykov — filter klienta a „len viacjazyčné"
  (function () {
    const sel = document.getElementById('cov-brand'), multi = document.getElementById('cov-multi');
    if (!sel) return;
    const apply = () => document.querySelectorAll('.cov-row').forEach(r => {
      r.style.display = (!sel.value || r.dataset.brand === sel.value) && (!multi.checked || r.classList.contains('multi')) ? '' : 'none';
    });
    sel.addEventListener('change', apply); multi.addEventListener('change', apply);
  })();

  // Tooltip pre grafy v Štatistikách (data-tip na prvku)
  (function () {
    const tip = document.createElement('div');
    tip.className = 'viz-tip';
    document.body.appendChild(tip);
    document.addEventListener('mousemove', e => {
      const t = e.target.closest && e.target.closest('#panel-stats [data-tip]');
      if (!t) { tip.classList.remove('show'); return; }
      tip.textContent = t.dataset.tip;
      tip.classList.add('show');
      const x = Math.min(e.clientX + 14, window.innerWidth - tip.offsetWidth - 10);
      tip.style.left = x + 'px';
      tip.style.top = (e.clientY + 16) + 'px';
    });
  })();
"""
