#!/usr/bin/env python3
"""
Omni Video Generator — Gemini Omni 1.1 Flash klipy cez Interactions API

Sesterský skript ku generate_videos.py (ten ide cez Veo3 / predictLongRunning).
Tento používa nový model `gemini-omni-1.1-flash` a Interactions REST API
(`POST /v1beta/interactions`) — google-genai SDK ho zatiaľ nemá, takže voláme raw
cez requests (funguje na Python 3.9 + existujúce deps).

Vstup:  video-prompts-{shoot}.json   (rovnaký formát ako pre generate_videos.py)
Výstup: MP4 klipy + manifest-{shoot}-omni.json

Usage:
    python generate_omni.py --shoot moj-shoot
    python generate_omni.py --shoot moj-shoot --clip 131 --variants v1,v2
    python generate_omni.py --shoot moj-shoot --resolution 1080p --duration 8s
    python generate_omni.py --shoot moj-shoot --task image_to_video      # klipy s poľom "image"
    python generate_omni.py --shoot moj-shoot --dry-run
    python generate_omni.py --shoot moj-shoot --output-dir AdGenerator-Pro/video/assets/footage

Per-variant override v JSON (voliteľné):
    "resolution": "1080p", "aspect_ratio": "9:16", "duration": "8s",
    "task": "image_to_video", "image": "refs/start.png"   (cesta relatívne k prompts JSON)

Required:
    GEMINI_API_KEY — načíta sa z staticky/.env
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    _here = Path(__file__).resolve().parent
    for _candidate in (
        _here / "../.env",
        _here / ".env",
        _here.parent / ".env",
    ):
        if _candidate.exists():
            load_dotenv(_candidate)
            break
except ImportError:
    pass

try:
    import requests
except ImportError:
    print("Error: pip install requests")
    sys.exit(1)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

API_BASE        = "https://generativelanguage.googleapis.com/v1beta"
MODEL           = "gemini-omni-1.1-flash"
DEFAULT_ASPECT  = "9:16"
DEFAULT_RES     = "720p"
DEFAULT_DUR     = "8s"          # max 10s
DEFAULT_TASK    = "text_to_video"
POLL_INTERVAL   = 12
MAX_WAIT        = 600
TARGET_DURATION = None          # None = netrimovať; číslo v s = ffmpeg trim po stiahnutí

ASPECTS = {"16:9", "9:16"}
RESOLUTIONS = {"360p", "720p", "1080p", "4k"}
TASKS = {"text_to_video", "image_to_video", "reference_to_video", "edit", "extend"}



# Denník nákladov AdGenerator Pro (staticky/tools/pricing.py) — zlyhanie nikdy nezastaví výrobu
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "staticky" / "tools"))
    import pricing as _pricing
except Exception:
    _pricing = None


def _headers():
    return {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}


def trim_video(src: Path, duration: int):
    """Oreže video na `duration` sekúnd pomocou ffmpeg (in-place)."""
    import subprocess
    tmp = src.with_suffix(".tmp.mp4")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-t", str(duration), "-c", "copy", str(tmp)],
        capture_output=True,
    )
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg trim failed: {result.stderr.decode()[:200]}")
    tmp.replace(src)


def _iter_content_items(payload: dict):
    """Prejde všetky content prvky v steps[] (model_output) + prípadný output_video."""
    for step in payload.get("steps", []) or []:
        if step.get("type") in ("model_output", "tool_output", None):
            for item in step.get("content", []) or []:
                yield item
    if isinstance(payload.get("output_video"), dict):
        yield {**payload["output_video"], "type": "video"}
    if isinstance(payload.get("output"), list):
        for item in payload["output"]:
            if isinstance(item, dict):
                yield item


def extract_video(payload: dict, save_path: Path) -> bool:
    """Nájde v odpovedi video (inline base64 alebo uri) a zapíše ho. True = úspech."""
    for item in _iter_content_items(payload):
        mime = item.get("mime_type") or item.get("mimeType") or ""
        is_video = item.get("type") == "video" or mime.startswith("video/")
        if not is_video:
            continue
        data = item.get("data") or item.get("b64_data")
        if data:
            save_path.write_bytes(base64.b64decode(data))
            return True
        uri = item.get("uri") or item.get("url")
        if uri:
            r = requests.get(uri, headers={"x-goog-api-key": GEMINI_API_KEY},
                             stream=True, timeout=180)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
    return False


def build_body(prompt: str, task: str, aspect: str, resolution: str,
               duration: str, image_b64: str = None, image_mime: str = "image/png"):
    if image_b64:
        inp = [
            {"type": "text", "text": prompt},
            {"type": "image", "mime_type": image_mime, "data": image_b64},
        ]
    else:
        inp = prompt
    return {
        "model": MODEL,
        "input": inp,
        "background": True,
        "generation_config": {"video_config": {"task": task}},
        "response_format": {
            "type": "video",
            "aspect_ratio": aspect,
            "resolution": resolution,
            "duration": duration,
            "delivery": "inline",
        },
    }


def generate_clip(body: dict, debug_path: Path):
    """Spustí interaction, popolluje kým nie je hotová. Vráti (payload, elapsed)."""
    r = requests.post(f"{API_BASE}/interactions", headers=_headers(),
                      json=body, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"create {r.status_code}: {r.text[:400]}")
    payload = r.json()
    interaction_id = payload.get("id")
    status = payload.get("status")

    start = time.time()
    while status not in ("completed", "succeeded", "failed", "cancelled", "error"):
        if not interaction_id:
            break
        elapsed = int(time.time() - start)
        if elapsed > MAX_WAIT:
            raise TimeoutError(f"Timeout po {MAX_WAIT}s (id={interaction_id})")
        print(f"     ⏳ {elapsed}s... [{status}]", flush=True)
        time.sleep(POLL_INTERVAL)
        g = requests.get(f"{API_BASE}/interactions/{interaction_id}",
                         headers=_headers(), timeout=60)
        if g.status_code >= 400:
            raise RuntimeError(f"poll {g.status_code}: {g.text[:400]}")
        payload = g.json()
        status = payload.get("status")

    elapsed = int(time.time() - start)
    if status in ("failed", "cancelled", "error"):
        debug_path.write_text(json.dumps(payload, indent=2))
        raise RuntimeError(f"Interaction {status} — raw: {debug_path.name}")
    return payload, elapsed


def run(shoot, clip_filter, variant_filter, output_dir, cli, dry_run):
    prompts_path = Path(__file__).parent / f"video-prompts-{shoot}.json"
    if not prompts_path.exists():
        print(f"Error: {prompts_path} nenájdený")
        sys.exit(1)

    with open(prompts_path) as f:
        data = json.load(f)

    brand = data.get("brand", "video")
    clips = data.get("clips", [])
    if clip_filter:
        clips = [c for c in clips if str(c["clip_id"]) in clip_filter]

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Omni Video Generator — {brand} / {shoot}")
    print(f"  Model:  {MODEL}")
    print(f"  Cfg:    {cli['aspect']} · {cli['resolution']} · {cli['duration']} · {cli['task']}")
    print(f"  Output: {output_dir}")
    print(f"  Klipy:  {len(clips)}")
    print(f"{'='*60}\n")

    total = sum(len(c["variants"]) for c in clips)
    done = failed = 0
    manifest = []

    for clip in clips:
        clip_id = str(clip["clip_id"])
        slug = clip["slug"]
        desc = clip.get("description", "")
        variants = clip["variants"]
        if variant_filter:
            variants = [v for v in variants
                        if any(v["variant"].startswith(f) for f in variant_filter)]

        print(f"[{clip_id}] {slug}")
        print(f"    {desc}\n")

        for v in variants:
            variant = v["variant"]
            prompt = v["prompt"]
            aspect = v.get("aspect_ratio", cli["aspect"])
            resolution = v.get("resolution", cli["resolution"])
            duration = v.get("duration", cli["duration"])
            task = v.get("task", cli["task"])

            image_b64 = None
            image_mime = "image/png"
            img_ref = v.get("image") or clip.get("image") or cli.get("image")
            if img_ref:
                img_path = (Path(img_ref) if os.path.isabs(img_ref)
                            else prompts_path.parent / img_ref)
                if not img_path.exists():
                    print(f"  → {variant}\n    ❌ image nenájdený: {img_path}\n")
                    failed += 1
                    continue
                image_b64 = base64.b64encode(img_path.read_bytes()).decode()
                image_mime = "image/jpeg" if img_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
                if task == "text_to_video":
                    task = "image_to_video"

            filename = f"{clip_id}_{slug}_{variant}.mp4"
            save_path = output_dir / filename
            debug_path = output_dir / f"{filename}.debug.json"

            print(f"  → {variant}  ({aspect} · {resolution} · {duration} · {task})")
            print(f"    {prompt[:90]}...")

            body = build_body(prompt, task, aspect, resolution, duration,
                              image_b64, image_mime)

            if dry_run:
                preview = {**body, "input": ("<image+text>" if image_b64 else body["input"])}
                print(f"    DRY RUN:\n{json.dumps(preview, indent=2)}\n")
                continue

            if save_path.exists():
                size_mb = save_path.stat().st_size / 1024 / 1024
                print(f"    ⏩ Existuje ({size_mb:.1f} MB) — preskočené\n")
                done += 1
                continue

            try:
                payload, elapsed = generate_clip(body, debug_path)
                if not extract_video(payload, save_path):
                    debug_path.write_text(json.dumps(payload, indent=2))
                    raise RuntimeError(f"V odpovedi nie je video — raw: {debug_path.name}")

                if TARGET_DURATION:
                    trim_video(save_path, TARGET_DURATION)
                size_mb = save_path.stat().st_size / 1024 / 1024
                debug_path.unlink(missing_ok=True)
                print(f"    ✅ {filename} ({size_mb:.1f} MB, {elapsed}s)\n")
                done += 1
                if _pricing:   # Omni účtuje vygenerované sekundy videa (~0,10 $/s pri 720p)
                    try:
                        secs = int(str(duration).rstrip("s"))
                    except ValueError:
                        secs = _pricing.VEO_DEFAULT_SECONDS
                    _pricing.log_generation({"kind": "omni", "model": MODEL, "clip": filename, "seconds": secs,
                                             "resolution": resolution,
                                             "cost_usd": round(secs * _pricing.OMNI_PRICE_PER_SECOND, 4),
                                             "prices_checked": _pricing.PRICES_CHECKED})
                manifest.append({
                    "clip_id": clip_id, "slug": slug, "variant": variant,
                    "file": str(save_path), "resolution": resolution,
                    "aspect_ratio": aspect, "duration": duration,
                })
            except Exception as e:
                print(f"    ❌ Chyba: {e}\n")
                failed += 1

    print(f"{'='*60}")
    print(f"  Hotovo: {done}/{total}  |  Chyby: {failed}")
    print(f"{'='*60}\n")

    if manifest and not dry_run:
        manifest_path = output_dir / f"manifest-{shoot}-omni.json"
        with open(manifest_path, "w") as f:
            json.dump({"shoot": shoot, "model": MODEL, "clips": manifest}, f, indent=2)
        print(f"Manifest: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Gemini Omni 1.1 Flash video generator")
    parser.add_argument("--shoot", required=True, help="Názov shoot sady, napr. 'ritual'")
    parser.add_argument("--clip", type=str, default=None, help="Clip ID(s), napr. '131,132'")
    parser.add_argument("--variants", type=str, default=None, help="Variant(y), napr. 'v1,v2'")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Default: AdGenerator-Pro/video/assets/footage")
    parser.add_argument("--aspect", type=str, default=DEFAULT_ASPECT, choices=sorted(ASPECTS))
    parser.add_argument("--resolution", type=str, default=DEFAULT_RES, choices=sorted(RESOLUTIONS))
    parser.add_argument("--duration", type=str, default=DEFAULT_DUR, help="1s–10s (max 10s)")
    parser.add_argument("--task", type=str, default=DEFAULT_TASK, choices=sorted(TASKS))
    parser.add_argument("--image", type=str, default=None,
                        help="Globálna štartovacia foto pre image_to_video (cesta k súboru)")
    parser.add_argument("--trim", type=int, default=None,
                        help="Orezať výstup na N sekúnd cez ffmpeg")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    global TARGET_DURATION
    TARGET_DURATION = args.trim

    if not GEMINI_API_KEY and not args.dry_run:
        print("Error: GEMINI_API_KEY nie je nastavený. Skontroluj staticky/.env")
        sys.exit(1)

    clip_filter = [x.strip() for x in args.clip.split(",")] if args.clip else []
    variant_filter = [x.strip() for x in args.variants.split(",")] if args.variants else []

    output_dir = (Path(args.output_dir).expanduser() if args.output_dir
                  else Path.home() / "Video Factory" / "assets" / "footage")

    run(
        shoot=args.shoot,
        clip_filter=clip_filter,
        variant_filter=variant_filter,
        output_dir=output_dir,
        cli={"aspect": args.aspect, "resolution": args.resolution,
             "duration": args.duration, "task": args.task, "image": args.image},
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
