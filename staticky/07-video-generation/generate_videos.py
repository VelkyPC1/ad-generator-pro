#!/usr/bin/env python3
"""
Video Generator — Veo3 stock clip production

Generuje UGC/cinematic stock klipy pre Video Factory.
Vstup: video-prompts-{shoot}.json  |  Výstup: MP4 klipy pripravené pre Video Factory

Usage:
    python generate_videos.py --shoot moj-shoot
    python generate_videos.py --shoot moj-shoot --clip 131
    python generate_videos.py --shoot moj-shoot --clip 131 --variants v1,v2
    python generate_videos.py --shoot moj-shoot --output-dir AdGenerator-Pro/video/assets/footage
    python generate_videos.py --shoot moj-shoot --model veo-3.0-fast-generate-001
    python generate_videos.py --shoot moj-shoot --dry-run

Required:
    GEMINI_API_KEY  — Gemini API key (načíta sa z staticky/.env)
"""

import argparse
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

DEFAULT_MODEL   = "veo-3.0-fast-generate-001"
ASPECT_RATIO    = "9:16"
POLL_INTERVAL   = 15
MAX_WAIT        = 600
TARGET_DURATION = 4  # sekundy — ffmpeg trim po stiahnutí



# Denník nákladov AdGenerator Pro (staticky/tools/pricing.py) — zlyhanie nikdy nezastaví výrobu
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "staticky" / "tools"))
    import pricing as _pricing
except Exception:
    _pricing = None


def trim_video(src: Path, duration: int):
    """Oreže video na `duration` sekúnd pomocou ffmpeg (in-place)."""
    import subprocess
    tmp = src.with_suffix(".tmp.mp4")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-t", str(duration),
         "-c", "copy", str(tmp)],
        capture_output=True,
    )
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg trim failed: {result.stderr.decode()[:200]}")
    tmp.replace(src)


def download_video(uri: str, save_path: Path):
    r = requests.get(
        uri,
        headers={"X-Goog-Api-Key": GEMINI_API_KEY},
        stream=True,
        timeout=120,
    )
    r.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


def generate_clip(prompt: str, model: str):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        config=types.GenerateVideosConfig(aspect_ratio=ASPECT_RATIO),
    )

    start = time.time()
    while not operation.done:
        elapsed = int(time.time() - start)
        if elapsed > MAX_WAIT:
            raise TimeoutError(f"Timeout po {MAX_WAIT}s")
        print(f"     ⏳ {elapsed}s...", flush=True)
        time.sleep(POLL_INTERVAL)
        operation = client.operations.get(operation)

    elapsed = int(time.time() - start)

    if not (operation.response and operation.response.generated_videos):
        raise RuntimeError(f"Veo3 nevrátil video: {operation}")

    video = operation.response.generated_videos[0].video
    if hasattr(video, "video_bytes") and video.video_bytes:
        return None, video.video_bytes, elapsed
    return getattr(video, "uri", None), None, elapsed


def run(shoot, clip_filter, variant_filter, output_dir, model, dry_run):
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
    print(f"  Video Generator — {brand} / {shoot}")
    print(f"  Model:  {model}")
    print(f"  Output: {output_dir}")
    print(f"  Klipy:  {len(clips)}")
    print(f"{'='*60}\n")

    total    = sum(len(c["variants"]) for c in clips)
    done     = 0
    failed   = 0
    manifest = []

    for clip in clips:
        clip_id  = str(clip["clip_id"])
        slug     = clip["slug"]
        desc     = clip.get("description", "")
        variants = clip["variants"]

        if variant_filter:
            variants = [v for v in variants if any(v["variant"].startswith(f) for f in variant_filter)]

        print(f"[{clip_id}] {slug}")
        print(f"    {desc}\n")

        for v in variants:
            variant   = v["variant"]
            prompt    = v["prompt"]
            filename  = f"{clip_id}_{slug}_{variant}.mp4"
            save_path = output_dir / filename

            print(f"  → {variant}")
            print(f"    {prompt[:90]}...")

            if dry_run:
                print(f"    DRY RUN — preskočené\n")
                continue

            if save_path.exists():
                size_mb = save_path.stat().st_size / 1024 / 1024
                print(f"    ⏩ Existuje ({size_mb:.1f} MB) — preskočené\n")
                done += 1
                continue

            try:
                uri, raw_bytes, elapsed = generate_clip(prompt, model)
                if raw_bytes:
                    save_path.write_bytes(raw_bytes)
                elif uri:
                    download_video(uri, save_path)
                else:
                    raise RuntimeError("Žiadne URI ani bytes")

                trim_video(save_path, TARGET_DURATION)
                size_mb = save_path.stat().st_size / 1024 / 1024
                print(f"    ✅ {filename} ({size_mb:.1f} MB, {elapsed}s, trimmed to {TARGET_DURATION}s)\n")
                done += 1
                manifest.append({
                    "clip_id": clip_id,
                    "slug": slug,
                    "variant": variant,
                    "file": str(save_path),
                })
                if _pricing:   # Veo účtuje vygenerované sekundy (8 s), nie orezanú dĺžku
                    secs = _pricing.VEO_DEFAULT_SECONDS
                    price = _pricing.VEO_PRICE_PER_SECOND.get(model, 0.15)
                    _pricing.log_generation({"kind": "veo", "model": model, "clip": filename, "seconds": secs,
                                             "cost_usd": round(secs * price, 4), "prices_checked": _pricing.PRICES_CHECKED})

            except Exception as e:
                print(f"    ❌ Chyba: {e}\n")
                failed += 1

    print(f"{'='*60}")
    print(f"  Hotovo: {done}/{total}  |  Chyby: {failed}")
    print(f"{'='*60}\n")

    if manifest and not dry_run:
        manifest_path = output_dir / f"manifest-{shoot}.json"
        with open(manifest_path, "w") as f:
            json.dump({"shoot": shoot, "model": model, "clips": manifest}, f, indent=2)
        print(f"Manifest: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Veo3 stock clip generator pre Video Factory")
    parser.add_argument("--shoot",      required=True,
                        help="Názov shoot sady, napr. 'ritual'")
    parser.add_argument("--clip",       type=str, default=None,
                        help="Clip ID(s), napr. '131' alebo '131,132'")
    parser.add_argument("--variants",   type=str, default=None,
                        help="Variant(y), napr. 'v1' alebo 'v1,v2'")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Výstupný priečinok (default: AdGenerator-Pro/video/assets/footage)")
    parser.add_argument("--model",      type=str, default=DEFAULT_MODEL,
                        choices=[
                            "veo-3.0-generate-001",
                            "veo-3.0-fast-generate-001",
                            "veo-3.1-generate-preview",
                            "veo-3.1-fast-generate-preview",
                        ])
    parser.add_argument("--dry-run",    action="store_true")

    args = parser.parse_args()

    if not GEMINI_API_KEY and not args.dry_run:
        print("Error: GEMINI_API_KEY nie je nastavený. Skontroluj staticky/.env")
        sys.exit(1)

    clip_filter    = [x.strip() for x in args.clip.split(",")]     if args.clip     else []
    variant_filter = [x.strip() for x in args.variants.split(",")] if args.variants else []

    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else Path.home() / "Video Factory" / "assets" / "footage"
    )

    run(
        shoot          = args.shoot,
        clip_filter    = clip_filter,
        variant_filter = variant_filter,
        output_dir     = output_dir,
        model          = args.model,
        dry_run        = args.dry_run,
    )


if __name__ == "__main__":
    main()
