#!/usr/bin/env python3
"""
Poster thumbnaily pre video karty v dashboarde.

Z každého .mp4 vytiahne jeden frame (default 1.0s) ako JPEG do video-posters/.
Grid v dashboarde zobrazuje poster (lacné), video sa prehráva až v lightboxe.

Použitie:
    python3 tools/make_video_poster.py                    # všetky videá z pvf-videos/
    python3 tools/make_video_poster.py --force            # pregeneruj aj existujúce
    python3 tools/make_video_poster.py video1.mp4 ...     # konkrétne súbory

Vyžaduje ffmpeg/ffprobe (homebrew). Volá sa automaticky z build_dashboard.py.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # ad-generator/
VIDEO_DIR = ROOT / "pvf-videos"
POSTER_DIR = ROOT / "video-posters"

POSTER_AT_SEC = 1.0  # odkiaľ brať frame (0 = prvý frame býva čierny)


def probe(video: Path) -> dict:
    """Rozmery + dĺžka videa cez ffprobe. {} ak sa nedá prečítať."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration",
             "-of", "json", str(video)],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode != 0:
            return {}
        data = json.loads(out.stdout or "{}")
        stream = (data.get("streams") or [{}])[0]
        dur = float(data.get("format", {}).get("duration") or 0)
        return {
            "w": int(stream.get("width") or 0),
            "h": int(stream.get("height") or 0),
            "duration": round(dur, 1),
        }
    except Exception:
        return {}


def make_poster(video: Path, poster: Path, at_sec: float = POSTER_AT_SEC,
                force: bool = False) -> bool:
    """Vytiahne frame do JPEG. True = poster existuje (nový alebo platný starý)."""
    if poster.exists() and not force:
        # Regeneruj len ak je video novšie ako poster
        if poster.stat().st_mtime >= video.stat().st_mtime:
            return True

    poster.parent.mkdir(parents=True, exist_ok=True)
    meta = probe(video)
    # Krátke video → vezmi frame z tretiny dĺžky, nech netrafíme do prázdna
    dur = meta.get("duration") or 0
    ts = at_sec if dur > at_sec * 2 else max(dur / 3, 0)

    try:
        out = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-ss", f"{ts:.2f}", "-i", str(video),
             "-frames:v", "1", "-q:v", "4",
             "-vf", "scale='min(720,iw)':-2",
             str(poster)],
            capture_output=True, text=True, timeout=60,
        )
        return out.returncode == 0 and poster.exists()
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description="Generuj poster thumbnaily pre videá")
    ap.add_argument("videos", nargs="*", help="Konkrétne .mp4 (default: všetky z pvf-videos/)")
    ap.add_argument("--force", action="store_true", help="Pregeneruj aj existujúce postery")
    args = ap.parse_args()

    if args.videos:
        videos = [Path(v) if Path(v).is_absolute() else (ROOT / v) for v in args.videos]
    elif VIDEO_DIR.exists():
        videos = sorted(VIDEO_DIR.glob("*.mp4"))
    else:
        print(f"⚠ {VIDEO_DIR} neexistuje — symlink na PVF output chýba")
        return 1

    ok = skipped = failed = 0
    for video in videos:
        if not video.exists():
            failed += 1
            continue
        poster = POSTER_DIR / f"{video.stem}.jpg"
        existed = poster.exists()
        if make_poster(video, poster, force=args.force):
            if existed and not args.force:
                skipped += 1
            else:
                ok += 1
        else:
            failed += 1
            print(f"  ✗ poster zlyhal: {video.name}")

    print(f"✓ Postery: {ok} nových · {skipped} existujúcich · {failed} zlyhaní → {POSTER_DIR}")
    return 0 if not failed else 0  # poster zlyhanie nie je fatálne pre build


if __name__ == "__main__":
    sys.exit(main())
