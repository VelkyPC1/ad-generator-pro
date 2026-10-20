#!/usr/bin/env bash
# Zostaví video: UGC hook klip (s vlastným SK voiceoverom) + produktová
# sekcia s VO + titulkami + animovanými benefit kartami + CTA (Remotion).
#
# Použitie:  bash scripts/build_hookvideo.sh <id>
# Číta:   cache/script_<id>.json  (musí mať "hook_clip" = názov klipu v footage,
#         prázdny "hook"/"voice_hook", segments, voice_cta, seq_main/seq_outro, overlay)
# Výstup: remotion/out/<id>_FINAL.mp4   (hook + produktová sekcia)
set -euo pipefail

ID="${1:?použitie: build_hookvideo.sh <id>}"
PVF="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PVF"

SCRIPT="cache/script_${ID}.json"
[ -f "$SCRIPT" ] || { echo "chýba $SCRIPT" >&2; exit 1; }

HOOK=$(python3 -c "import json,sys;print(json.load(open('$SCRIPT'))['hook_clip'])")
FOOTAGE="assets/footage"
HOOK_SRC="$FOOTAGE/${HOOK}.mp4"
[ -f "$HOOK_SRC" ] || { echo "chýba hook klip: $HOOK_SRC" >&2; exit 1; }

read W H FPS < <(python3 -c "import json;c=json.load(open('config.json'));print(c['resolution']['w'],c['resolution']['h'],c['fps'])")

echo "▶ 1/4  voiceover (ElevenLabs)…"
python3 scripts/step2_voice.py "$SCRIPT" >/dev/null

echo "▶ 2/4  silent produktová sekvencia…"
python3 scripts/build_silent_seq.py "$ID"

echo "▶ 3/4  Remotion overlay (titulky + karty + CTA + hudba)…"
( cd remotion && bash render_overlay.sh "$ID" )

# lokalizačný podpriečinok rovnako ako render_overlay.sh
case "$ID" in
  *-cz) SUB="remotion/out/CZ" ;;
  *-hu) SUB="remotion/out/HU" ;;
  de-*) SUB="remotion/out/DE" ;;
  *)    SUB="remotion/out" ;;
esac
MAIN="${SUB}/${ID}_REMOTION.mp4"
[ -f "$MAIN" ] || { echo "render zlyhal, chýba $MAIN" >&2; exit 1; }

echo "▶ 4/4  predradenie hook klipu ($HOOK)…"
TMP="cache/work_${ID}"
HOOK_NORM="${TMP}/hook_norm.mp4"
ffmpeg -y -hide_banner -loglevel error -i "$HOOK_SRC" \
  -vf "scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},setsar=1,fps=${FPS}" \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 44100 -ac 2 "$HOOK_NORM"

OUT="${SUB}/${ID}_FINAL.mp4"
ffmpeg -y -hide_banner -loglevel error -i "$HOOK_NORM" -i "$MAIN" \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -pix_fmt yuv420p \
  -c:a aac -b:a 192k "$OUT"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
echo "HOTOVO -> $OUT  (${DUR}s)"
