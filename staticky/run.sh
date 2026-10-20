#!/usr/bin/env bash
# Generovanie bannerov s kľúčom konkrétneho klienta (oddelené účtovanie).
#
#   ./run.sh <klient>                    # len overí, či má klient kľúč
#   ./run.sh <klient> [args pre generate_ads.py]
#
# Kľúč: brands/<klient>/.env (GEMINI_API_KEY), inak staticky/.env
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Použitie: ./run.sh <klient> [args...]"
  echo "Klienti:"; ls -d brands/*/ 2>/dev/null | sed 's|brands/||;s|/||' | grep -v '^_'
  exit 1
fi
BRAND="$1"; shift
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$DIR/brands/$BRAND/.env"
[ -f "$ENV_FILE" ] || ENV_FILE="$DIR/.env"
[ -d "$DIR/brands/$BRAND" ] || { echo "❌ Klient neexistuje: brands/$BRAND (vzor: brands/_priklad)"; exit 1; }
[ -f "$ENV_FILE" ] || { echo "❌ Chýba .env s GEMINI_API_KEY (brands/$BRAND/.env alebo staticky/.env)"; exit 1; }

set -a; source "$ENV_FILE"; set +a
[ -n "${GEMINI_API_KEY:-}${FAL_KEY:-}" ] || { echo "❌ V $ENV_FILE nie je GEMINI_API_KEY ani FAL_KEY"; exit 1; }
echo "✅ Klient: $BRAND · kľúč z ${ENV_FILE#$DIR/} (***${GEMINI_API_KEY: -4})"

[ $# -eq 0 ] && { echo "ℹ️  Pridaj argumenty pre generate_ads.py, napr. --brand-dir … --templates 1,2 --dry-run"; exit 0; }
python3 "$DIR/06-image-generation/generate_ads.py" "$@"
