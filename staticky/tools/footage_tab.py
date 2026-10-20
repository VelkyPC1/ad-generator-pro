"""
Knižnica footage pre Video Factory — prepínač „Footage knižnica" v tabe 🎬 Video.

Zdroj: AdGenerator-Pro/video/assets/footage_*/*.mp4 (servované cez symlink staticky/footage → ../video/assets).
Ku každému klipu: typ (podľa predpony), zdroj (natočené / AI podľa rozlíšenia), dĺžka, rozlíšenie
a v koľkých videách je použitý (seq_main / seq_outro / hook_clip / clips v cache/script_*.json).
ffprobe výsledky aj náhľady sa cachujú — rebuild po prvom raze trvá zlomok sekundy.
"""

import html
import json
import subprocess
from pathlib import Path

TYPES = [("seq", "Sekvencia"), ("product", "Produkt / outro"), ("hook", "Hook (UGC)"), ("intro", "Intro"), ("other", "Ostatné")]


def esc(s) -> str:
    return html.escape(str(s))


def clip_type(name: str) -> str:
    for prefix, key in (("seq_", "seq"), ("product_", "product"), ("hook_", "hook"), ("intro_", "intro")):
        if name.startswith(prefix):
            return key
    return "other"


def probe(path: Path, cache: dict) -> dict:
    st = path.stat()
    key = str(path)
    hit = cache.get(key)
    if hit and hit.get("_stamp") == [st.st_size, int(st.st_mtime)]:
        return hit
    info = {"w": 0, "h": 0, "dur": 0.0, "enc": ""}
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height:format=duration:format_tags=encoder", "-of", "json", str(path)],
                             capture_output=True, text=True, timeout=15).stdout
        d = json.loads(out or "{}")
        s0 = (d.get("streams") or [{}])[0]
        info.update(w=s0.get("width", 0), h=s0.get("height", 0),
                    dur=float((d.get("format") or {}).get("duration") or 0),
                    enc=((d.get("format") or {}).get("tags") or {}).get("encoder", ""))
    except Exception:
        pass
    info["_stamp"] = [st.st_size, int(st.st_mtime)]
    cache[key] = info
    return info


def source_of(name: str, info: dict) -> str:
    if info["w"] == 716:
        return "other_ai"
    if info["enc"] == "Google" or info["w"] in (720, 704) or name.startswith(("hook_", "intro_")):
        return "ai"
    return "own"


SOURCE_LABEL = {"own": "Natočené", "ai": "AI (Veo / Omni)", "other_ai": "AI (iný nástroj)"}


def usage_map(cache_dir: Path) -> dict:
    """Názov klipu (bez .mp4) → zoznam ID videí, ktoré ho používajú."""
    used = {}
    for f in cache_dir.glob("script_*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        vid = d.get("id") or f.stem[len("script_"):]
        names = list(d.get("seq_main") or []) + list(d.get("seq_outro") or []) + list(d.get("outro_clips") or [])
        if d.get("hook_clip"):
            names.append(d["hook_clip"])
        for c in d.get("clips") or []:
            names.append(c.get("clip") if isinstance(c, dict) else c)
        for n in names:
            if n:
                used.setdefault(Path(str(n)).stem, set()).add(vid)
    return used


def build(root: Path, video_root: Path, make_poster) -> dict:
    """Vráti {"html", "count"} — root = staticky/, video_root = AdGenerator-Pro/video."""
    assets = video_root / "assets"
    cache_path = root / "tools" / ".footage-cache.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
    poster_dir = root / "video-posters" / "footage"
    poster_dir.mkdir(parents=True, exist_ok=True)
    used = usage_map(video_root / "cache")

    clips = []
    for f in sorted(assets.glob("footage*/*.mp4")):
        if ".bak" in f.name:
            continue
        info = probe(f, cache)
        brand = f.parent.name[len("footage_"):] or "footage"
        poster = poster_dir / f"{brand}-{f.stem}.jpg"
        if not poster.exists():
            make_poster(f, poster)
        uses = sorted(used.get(f.stem, []))
        clips.append({"name": f.name, "stem": f.stem, "brand": brand, "type": clip_type(f.name),
                      "src": source_of(f.name, info), "dur": info["dur"], "w": info["w"], "h": info["h"],
                      "url": f"footage/{f.parent.name}/{f.name}",
                      "poster": f"video-posters/footage/{poster.name}" if poster.exists() else "",
                      "uses": uses})
    cache_path.write_text(json.dumps(cache), encoding="utf-8")

    cards = []
    for c in clips:
        n_use = len(c["uses"])
        use_txt = f"v {n_use} {'videu' if n_use == 1 else 'videách'}" if n_use else "nepoužitý"
        tip = ", ".join(c["uses"][:8]) + (" …" if n_use > 8 else "")
        img = f'<img src="{esc(c["poster"])}" loading="lazy" alt="">' if c["poster"] else ""
        cards.append(
            f'<figure class="fg-card" data-brand="{esc(c["brand"])}" data-type="{c["type"]}" data-src="{c["src"]}" '
            f'data-used="{1 if n_use else 0}" data-search="{esc((c["stem"] + " " + " ".join(c["uses"])).lower())}" '
            f'data-url="{esc(c["url"])}">'
            f'<div class="fg-thumb">{img}'
            f'<span class="fg-dur">{c["dur"]:.1f} s</span><span class="fg-play">▶</span></div>'
            f'<figcaption><b title="{esc(c["name"])}">{esc(c["stem"])}</b>'
            f'<span class="fg-chips"><i class="fg-src {c["src"]}">{SOURCE_LABEL[c["src"]]}</i>'
            f'<i>{dict(TYPES)[c["type"]]}</i><i>{c["w"]}×{c["h"]}</i></span>'
            f'<span class="fg-use{" none" if not n_use else ""}" title="{esc(tip)}">{use_txt}</span></figcaption></figure>')

    brands = sorted({c["brand"] for c in clips})
    counts = {k: sum(1 for c in clips if c["type"] == k) for k, _ in TYPES}
    src_counts = {k: sum(1 for c in clips if c["src"] == k) for k in SOURCE_LABEL}
    unused = sum(1 for c in clips if not c["uses"])
    opt = lambda pairs: "".join(f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in pairs)
    html_ = f"""
  <section class="panel-section">
    <div class="panel-head"><h2>Footage knižnica <span class="count">{len(clips)}</span></h2>
      <p>Klipy, z ktorých Video Factory skladá videá (<code>video/assets/footage_*/</code>). Natočené {src_counts['own']} ·
      AI {src_counts['ai'] + src_counts['other_ai']} · nepoužité {unused}. Číslo „v N videách" sa ráta zo scriptov
      (<code>seq_main</code>, <code>seq_outro</code>, <code>hook_clip</code>). Klik prehrá klip.</p></div>
    <div class="fg-filters">
      <label>Klient <select id="fg-brand"><option value="">všetci</option>{opt((b, b) for b in brands)}</select></label>
      <label>Typ <select id="fg-type"><option value="">všetky</option>{opt((k, f"{v} ({counts[k]})") for k, v in TYPES if counts[k])}</select></label>
      <label>Zdroj <select id="fg-src"><option value="">všetky</option>{opt((k, f"{v} ({src_counts[k]})") for k, v in SOURCE_LABEL.items() if src_counts[k])}</select></label>
      <label>Použitie <select id="fg-used"><option value="">všetky</option><option value="1">použité</option><option value="0">nepoužité ({unused})</option></select></label>
      <input type="search" id="fg-search" class="panel-search" placeholder="Hľadať klip alebo video…">
      <span class="fg-count"><b id="fg-visible">{len(clips)}</b> klipov</span>
    </div>
    <div class="fg-grid">{"".join(cards)}</div>
  </section>
  <div class="fg-modal" id="fg-modal"><button class="fg-close" id="fg-close" title="Zavrieť (Esc)">✕</button>
    <video id="fg-video" controls playsinline loop></video><div class="fg-cap" id="fg-cap"></div></div>"""
    return {"html": html_, "count": len(clips)}


CSS = """
  /* ---------- Footage knižnica ---------- */
  .vmode { display: none; gap: 2px; padding: 3px; background: var(--fill); border-radius: 10px; }
  body[data-tab="video"] .vmode { display: inline-flex; }
  .vmode button { background: transparent; border: none; color: var(--label-2); font-size: 0.8rem; font-weight: 600; padding: 5px 12px; border-radius: 8px; cursor: pointer; }
  .vmode button[aria-pressed="true"] { background: var(--bg-elev); color: var(--label); box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
  :root[data-theme="dark"] .vmode button[aria-pressed="true"] { background: #636366; }
  #panel-footage { display: none; }
  body[data-tab="video"][data-vmode="footage"] #panel-footage { display: block; animation: lb-in 0.2s ease; }
  body[data-tab="video"][data-vmode="footage"] #sections,
  body[data-tab="video"][data-vmode="footage"] .filters,
  body[data-tab="video"][data-vmode="footage"] .qa-counts,
  body[data-tab="video"][data-vmode="footage"] .flag-actions,
  body[data-tab="video"][data-vmode="footage"] .stats { display: none !important; }
  .fg-filters { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: center; margin-bottom: 18px; }
  .fg-filters label { font-size: 0.78rem; color: var(--label-2); display: flex; align-items: center; gap: 6px; }
  .fg-filters select { background: var(--fill); border: none; color: var(--label); padding: 6px 10px; border-radius: 9px; font-size: 0.82rem; }
  .fg-filters .panel-search { margin-top: 0; width: 240px; }
  .fg-count { margin-left: auto; font-size: 0.8rem; color: var(--label-2); }
  .fg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 16px; }
  .fg-card { background: var(--bg-elev); border-radius: 14px; overflow: hidden; box-shadow: var(--shadow); cursor: pointer; transition: transform 0.3s cubic-bezier(0.2,0.9,0.3,1), box-shadow 0.3s; }
  .fg-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-sm), var(--shadow-lg); }
  .fg-thumb { position: relative; aspect-ratio: 9/16; background: var(--stage); }
  .fg-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .fg-dur { position: absolute; bottom: 7px; right: 7px; font-size: 0.64rem; font-weight: 600; color: #fff; background: rgba(0,0,0,0.5); backdrop-filter: blur(8px); padding: 2px 7px; border-radius: 999px; font-variant-numeric: tabular-nums; }
  .fg-play { position: absolute; inset: 0; margin: auto; width: 40px; height: 40px; border-radius: 50%; background: rgba(0,0,0,0.4); backdrop-filter: blur(10px); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; opacity: 0; transition: opacity 0.2s; padding-left: 2px; }
  .fg-card:hover .fg-play { opacity: 1; }
  .fg-card figcaption { padding: 8px 10px 10px; display: flex; flex-direction: column; gap: 5px; }
  .fg-card figcaption b { font-size: 0.74rem; font-weight: 600; color: var(--label); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .fg-chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .fg-chips i { font-style: normal; font-size: 0.6rem; font-weight: 600; padding: 1px 6px; border-radius: 999px; background: var(--fill); color: var(--label-2); }
  .fg-chips i.fg-src.ai { background: var(--accent-tint); color: var(--accent); }
  .fg-chips i.fg-src.other_ai { background: color-mix(in srgb, var(--q-stale) 18%, transparent); color: var(--q-stale); }
  .fg-use { font-size: 0.68rem; color: var(--q-pass); font-weight: 600; }
  .fg-use.none { color: var(--label-3); }
  .fg-modal { position: fixed; inset: 0; z-index: 260; display: none; align-items: center; justify-content: center; flex-direction: column; gap: 12px; background: var(--scrim); backdrop-filter: blur(28px); -webkit-backdrop-filter: blur(28px); }
  .fg-modal.open { display: flex; animation: lb-in 0.2s ease; }
  .fg-modal video { max-height: 80vh; max-width: 90vw; border-radius: 14px; box-shadow: var(--shadow-lg); background: #000; }
  .fg-cap { font-size: 0.84rem; color: var(--label); background: var(--material); padding: 7px 16px; border-radius: 999px; max-width: 80vw; text-align: center; }
  .fg-close { position: fixed; top: 18px; right: 24px; width: 44px; height: 44px; border-radius: 50%; border: none; background: var(--glass); color: var(--on-glass); font-size: 1.05rem; cursor: pointer; }
"""

JS = """
  // ---------- Footage knižnica (Video tab) ----------
  (function () {
    const grid = document.querySelector('.fg-grid');
    if (!grid) return;
    const els = { brand: 'fg-brand', type: 'fg-type', src: 'fg-src', used: 'fg-used' };
    const get = id => document.getElementById(id);
    const apply = () => {
      const q = get('fg-search').value.toLowerCase().trim();
      let n = 0;
      grid.querySelectorAll('.fg-card').forEach(c => {
        const ok = Object.entries(els).every(([k, id]) => !get(id).value || c.dataset[k] === get(id).value)
          && (!q || c.dataset.search.includes(q));
        c.style.display = ok ? '' : 'none';
        if (ok) n++;
      });
      get('fg-visible').textContent = n;
    };
    Object.values(els).forEach(id => get(id).addEventListener('change', apply));
    get('fg-search').addEventListener('input', apply);
    const modal = get('fg-modal'), vid = get('fg-video');
    const close = () => { modal.classList.remove('open'); vid.pause(); };
    grid.addEventListener('click', e => {
      const c = e.target.closest('.fg-card');
      if (!c) return;
      vid.src = c.dataset.url;
      get('fg-cap').textContent = c.querySelector('b').textContent + ' · ' + c.querySelector('.fg-use').textContent;
      modal.classList.add('open');
      vid.play().catch(() => {});
    });
    get('fg-close').addEventListener('click', close);
    modal.addEventListener('click', e => { if (e.target === modal) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && modal.classList.contains('open')) close(); });
    // prepínač Hotové videá / Footage knižnica
    document.querySelectorAll('.vmode button').forEach(b => b.addEventListener('click', () => {
      document.body.dataset.vmode = b.dataset.vmode;
      document.querySelectorAll('.vmode button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      try { localStorage.setItem('ad-gen-vmode', b.dataset.vmode); } catch (err) {}
    }));
    let vm = 'videos';
    try { vm = localStorage.getItem('ad-gen-vmode') || 'videos'; } catch (err) {}
    if (new URLSearchParams(location.search).get('vmode') === 'footage') vm = 'footage';
    const btn = document.querySelector('.vmode button[data-vmode="' + vm + '"]');
    if (btn) btn.click();
  })();
"""
