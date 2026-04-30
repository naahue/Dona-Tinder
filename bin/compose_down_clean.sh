#!/usr/bin/env sh
set -e
BIN="$(CDPATH="" cd "$(dirname -- "$0")" >/dev/null 2>&1 && pwd)"
sh "$BIN/dc.sh" down -v
echo "Listo: docker compose down -v y carpetas locales bajo app/."
