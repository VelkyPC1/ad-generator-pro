#!/usr/bin/env bash
# Vyrenderuje priehľadný caption overlay (Remotion) a položí ho na footage z PVF.
# Použitie:  bash render_overlay.sh <id>
# Vstup:  ../cache/work_<id>/silent.mp4  +  ../cache/voice_<id>.mp3
# Výstup: out/<id>_REMOTION.mp4
set -euo pipefail
ID="${1:?použitie: render_overlay.sh <id>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PVF="$(cd "$HERE/.." && pwd)"
cd "$HERE"

[ -d node_modules ] || npm install --no-audit --no-fund

# jazykový podpriečinok podľa sufixu (cz/hu) alebo prefixu (de-) ID; SK videá ostávajú priamo v out/
case "$ID" in
  *-cz) SUB="out/CZ" ;;
  *-hu) SUB="out/HU" ;;
  de-*) SUB="out/DE" ;;
  *)    SUB="out" ;;
esac
mkdir -p "$SUB"

# 1) props z reálnych dát videa
python3 make_props.py "$ID"

# 2) Remotion -> priehľadný ProRes 4444 (alpha). PNG image-format je NUTNÝ pre alfu.
npx remotion render src/index.ts Captions "out/cap_${ID}.mov" \
  --props=props.json --codec=prores --prores-profile=4444 \
  --pixel-format=yuva444p10le --image-format=png

# 3) overlay na footage + voiceover + hudobný podmaz (náhodný track z music)
MUSIC_DIR="$PVF/assets/music"
MUSIC=$(python3 - "$MUSIC_DIR" <<'PY'
import sys, os, random
d = sys.argv[1]
tracks = [f for f in os.listdir(d) if f.lower().endswith((".mp3",".m4a",".wav",".aac",".ogg"))] if os.path.isdir(d) else []
print(os.path.join(d, random.choice(tracks)) if tracks else "")
PY
)
MVOL=$(python3 -c "import json,pathlib;print(json.loads(pathlib.Path('$PVF/config.json').read_text()).get('music_volume',0.12))")

if [ -n "$MUSIC" ]; then
  echo "hudba: $(basename "$MUSIC")  (vol=$MVOL)"
  ffmpeg -y -hide_banner -loglevel error \
    -i "$PVF/cache/work_${ID}/silent.mp4" \
    -i "out/cap_${ID}.mov" \
    -i "$PVF/cache/voice_${ID}.mp3" \
    -stream_loop -1 -i "$MUSIC" \
    -filter_complex "[0:v][1:v]overlay=0:0:format=auto:eof_action=pass[v];[2:a]volume=1.0[vo];[3:a]volume=${MVOL}[m];[vo][m]amix=inputs=2:duration=first:dropout_transition=0,apad[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -pix_fmt yuv420p \
    -c:a aac -b:a 192k -shortest "${SUB}/${ID}_REMOTION.mp4"
else
  ffmpeg -y -hide_banner -loglevel error \
    -i "$PVF/cache/work_${ID}/silent.mp4" \
    -i "out/cap_${ID}.mov" \
    -i "$PVF/cache/voice_${ID}.mp3" \
    -filter_complex "[0:v][1:v]overlay=0:0:format=auto:eof_action=pass[v];[2:a]apad[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -pix_fmt yuv420p \
    -c:a aac -b:a 192k -shortest "${SUB}/${ID}_REMOTION.mp4"
fi

# 4) medzikrok (veľký ProRes s alfa) zmaž
rm -f "out/cap_${ID}.mov"
echo "HOTOVO -> ${SUB}/${ID}_REMOTION.mp4"
