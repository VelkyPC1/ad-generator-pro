#!/usr/bin/env bash
# AdGenerator Pro — inštalácia na novom počítači. Bezpečné spúšťať opakovane.
set -uo pipefail
cd "$(dirname "$0")" || exit 1
ROOT="$(pwd)"
ok()   { echo "  ✓ $*"; }
warn() { echo "  ⚠ $*"; }
fail() { echo "  ✗ $*"; MISSING=1; }
MISSING=0

echo "▶ 1/6  Požiadavky"
command -v python3 >/dev/null && ok "python3 $(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:3])))')" || fail "python3 chýba (python.org / xcode-select --install)"
command -v node >/dev/null && ok "node $(node -v)" || fail "node chýba (nodejs.org / brew install node) — potrebné len pre videá"
command -v ffmpeg >/dev/null && ok "ffmpeg" || fail "ffmpeg chýba (brew install ffmpeg) — náhľady videí a strih"
command -v ffprobe >/dev/null && ok "ffprobe" || warn "ffprobe chýba (býva súčasťou ffmpeg)"
if [ "$(uname)" = "Darwin" ]; then command -v sandbox-exec >/dev/null && ok "sandbox-exec (macOS)" || warn "sandbox-exec nenájdený"; fi
[ "$MISSING" = 1 ] && echo "  → doinštaluj chýbajúce a spusti setup.sh znova (bannery fungujú aj bez node)."

echo "▶ 2/6  Python balíky"
python3 -m pip install --user -q -r requirements.txt && ok "requirements.txt nainštalované" || warn "pip zlyhal — skús: python3 -m pip install -r requirements.txt"

echo "▶ 3/6  Remotion (render videí)"
if command -v npm >/dev/null; then
  (cd video/remotion && npm ci --no-audit --no-fund --ignore-scripts >/dev/null 2>&1) && ok "npm závislosti nainštalované" || warn "npm ci zlyhal — spusti ručne: cd video/remotion && npm ci"
else
  warn "npm chýba — preskakujem (videá zatiaľ nepôjdu)"
fi

echo "▶ 4/6  Sandbox, symlinky, priečinky"
sed "s#__HOME__#$HOME#g" video/security/render-sandbox.sb.template > video/security/render-sandbox.sb && ok "sandbox profil pre $HOME"
mkdir -p video/assets/footage video/assets/music video/cache video/remotion/out video/remotion/public vystupy/statiky vystupy/videa staticky/brands
ln -sfn ../../assets/footage video/remotion/public/footage
ln -sfn ../../assets/music video/remotion/public/music
ln -sfn ../../cache video/remotion/public/voice
ln -sfn ../video/remotion/out staticky/video-out
ln -sfn ../video/output staticky/video-compose
ln -sfn ../video/assets staticky/footage
mkdir -p video/output
ok "symlinky pre Remotion a dashboard"

echo "▶ 5/6  Konfigurácia (kľúče doplníš sám)"
[ -f staticky/.env ] || { cp staticky/.env.example staticky/.env; ok "vytvorený staticky/.env — doplň GEMINI_API_KEY"; }
[ -f video/config.json ] || { cp video/config.example.json video/config.json; ok "vytvorený video/config.json — doplň elevenlabs_api_key a elevenlabs_voice_id"; }
chmod +x staticky/run.sh staticky/tools/serve_dashboard.sh video/scripts/*.sh video/remotion/render_overlay.sh 2>/dev/null
grep -q '^GEMINI_API_KEY=.\+' staticky/.env && ok "GEMINI_API_KEY nastavený" || warn "GEMINI_API_KEY ešte nie je v staticky/.env"

echo "▶ 6/6  Prvý dashboard"
python3 staticky/tools/build_dashboard.py >/dev/null 2>&1 && ok "dashboard zostavený" || warn "build dashboardu zlyhal — spusti: python3 staticky/tools/build_dashboard.py"

echo ""
echo "Hotovo. Spusti dashboard:  bash staticky/tools/serve_dashboard.sh  →  http://localhost:8077/dashboard.html"
