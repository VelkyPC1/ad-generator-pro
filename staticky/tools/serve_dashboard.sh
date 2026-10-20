#!/bin/bash
# Spustí / reštartuje dashboard server Ad Generator Pro (:8077).
# Nič nebeží automaticky na pozadí — nové kreatívy sa načítajú tlačidlom „⟳ Úplná obnova" v dashboarde
# (alebo samé po každom generovaní cez tools/refresh_and_open.py).
cd "$(dirname "$0")/.." || exit 1
PORT=8077
pkill -f "serve_dashboard.py" 2>/dev/null
pkill -f "http.server $PORT" 2>/dev/null
sleep 0.3
python3 tools/serve_dashboard.py "$PORT" >/dev/null 2>&1 &
sleep 1
# Auto-open vypnutý (2026-07-16 — nerušiť prácu novými kartami).
# Karta sa otvorí len ak výslovne DASHBOARD_OPEN=1.
[ "${DASHBOARD_OPEN:-0}" = "1" ] && open "http://localhost:$PORT/dashboard.html"
echo "Dashboard beží (refreshni si kartu): http://localhost:$PORT/dashboard.html"
echo "Server zastavíš: pkill -f serve_dashboard.py"
