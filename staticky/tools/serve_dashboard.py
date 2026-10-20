#!/usr/bin/env python3
"""
Mini server pre ad-generator dashboard (:8077).

Statické súbory (webroot = ad-generator/) + malé API:
  GET  /api/flags     → obsah flagged.json (normalizovaný na mapu {id: {...}})
  POST /api/flags     → atomicky prepíše flagged.json (mapa {id: {...}})
  GET/POST /api/approved → to isté pre approved.json (v3: bannery s QA stavom PASS)
  POST /api/reveal  → {"file": "brands/..."} → otvorí súbor vo Finderi (open -R)
  POST /api/rebuild → prestaví dashboard.html + vystupy/ (tlačidlo „⟳ Úplná obnova" v hlavičke) — žiadna
                     automatická kontrola na pozadí (2026-10-16: nechce, aby niečo bežalo stále)
  POST /api/save-to-folder → {"items": [{"file", "name"}]} → macOS dialóg „vyber priečinok"
                     a skopíruje tam súbory (záloha pre Safari, ktoré nevie showDirectoryPicker)

Len stdlib, počúva na 127.0.0.1. Spúšťa sa cez tools/serve_dashboard.sh.
"""
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # ad-generator/
FLAGS_PATH = ROOT / "flagged.json"
DASHBOARD = ROOT / "dashboard.html"
_build_lock = threading.Lock()


def rebuild(block=True) -> bool:
    if not _build_lock.acquire(blocking=block):
        return False
    try:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_dashboard.py")], cwd=str(ROOT),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
        return True
    except Exception:
        return False
    finally:
        _build_lock.release()
# v3: flagged.json = len bannery na opravu (FAIL / drobná oprava) — číta ho „oprav flagnuté";
# schválené (PASS) sú zámerne v samostatnom súbore, aby sa nikdy nepregenerovali
STORES = {"/api/flags": FLAGS_PATH, "/api/approved": ROOT / "approved.json"}
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8077


def read_flags(path: Path = FLAGS_PATH) -> dict:
    """Načíta flagged.json / approved.json — akceptuje mapu {id: {...}} aj starý formát {items: [...]}."""
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if isinstance(raw, dict) and "items" in raw:
        return {it["id"]: {k: v for k, v in it.items() if k != "id"}
                for it in raw.get("items", []) if isinstance(it, dict) and "id" in it}
    if isinstance(raw, dict):
        return raw
    return {}


def write_flags(data: dict, path: Path = FLAGS_PATH):
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(path)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass

    def _send_json(self, code: int, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _serve_range(self, rng: str) -> bool:
        """Partial content pre video (Safari bez Range vôbec neprehrá, seeking inde nefunguje).

        True = požiadavka obslúžená, False = nech to dorieši SimpleHTTPRequestHandler.
        """
        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        if not m:
            return False

        path = self.translate_path(self.path)
        if not Path(path).is_file():
            return False

        size = Path(path).stat().st_size
        start_s, end_s = m.group(1), m.group(2)
        if start_s:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
        elif end_s:  # suffix range: bytes=-500
            start, end = max(size - int(end_s), 0), size - 1
        else:
            return False

        if start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return True

        end = min(end, size - 1)
        length = end - start + 1
        ctype = self.guess_type(path)

        self.send_response(206)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()  # Accept-Ranges dopĺňa end_headers() override

        with open(path, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break  # prehliadač preskočil dopredu / zavrel tab
                remaining -= len(chunk)
        return True

    def end_headers(self):
        # Prehliadač musí vedieť, že seeking je možný
        if self.path.lower().split("?")[0].endswith((".mp4", ".mov", ".m4v", ".webm")):
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def do_GET(self):
        route = self.path.split("?")[0].rstrip("/")
        if route == "":
            self.send_response(302)
            self.send_header("Location", "/dashboard.html")
            self.end_headers()
            return
        if route in STORES:
            self._send_json(200, read_flags(STORES[route]))
            return
        rng = self.headers.get("Range")
        if rng and self._serve_range(rng):
            return
        super().do_GET()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._send_json(400, {"error": "bad json"})
            return

        route = self.path.split("?")[0].rstrip("/")
        if route == "/api/rebuild":
            t0 = time.time()
            ok = rebuild(block=True)
            self._send_json(200 if ok else 500, {"ok": ok, "seconds": round(time.time() - t0, 1)})
            return
        if route in STORES:
            if not isinstance(payload, dict):
                self._send_json(400, {"error": "expected object map"})
                return
            try:
                write_flags(payload, STORES[route])
            except Exception as e:
                self._send_json(500, {"error": str(e)})
                return
            self._send_json(200, {"ok": True, "count": len(payload)})
        elif route == "/api/reveal":
            rel = str(payload.get("file", ""))
            target = (ROOT / rel).resolve()
            if ROOT.resolve() not in target.parents or not target.exists():
                self._send_json(400, {"error": "file outside root or missing"})
                return
            subprocess.Popen(["open", "-R", str(target)])
            self._send_json(200, {"ok": True})
        elif route == "/api/save-to-folder":
            items = payload.get("items") or []
            pick = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to activate',
                 "-e", 'POSIX path of (choose folder with prompt "Kam uložiť označené bannery?")'],
                capture_output=True, text=True)
            if pick.returncode != 0:
                self._send_json(200, {"ok": False, "cancelled": True})
                return
            dest = Path(pick.stdout.strip())
            copied, failed = 0, 0
            for it in items:
                src = (ROOT / str(it.get("file", ""))).resolve()
                name = Path(str(it.get("name", "")) or src.name).name  # len názov, žiadne cesty
                if ROOT.resolve() not in src.parents or not src.is_file():
                    failed += 1
                    continue
                try:
                    shutil.copy2(src, dest / name)
                    copied += 1
                except OSError:
                    failed += 1
            subprocess.Popen(["open", str(dest)])
            self._send_json(200, {"ok": True, "dir": str(dest), "copied": copied, "failed": failed})
        else:
            self._send_json(404, {"error": "unknown endpoint"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Dashboard server: http://localhost:{PORT}/dashboard.html")
    server.serve_forever()
