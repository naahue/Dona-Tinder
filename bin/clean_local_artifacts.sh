#!/usr/bin/env sh
set -e
ROOT="$(CDPATH='' cd -- "$(dirname -- "$0")/.." >/dev/null 2>&1 && pwd)"
DT="$ROOT/app"
if ! test -d "$DT"; then
  echo "No encuentro app/ (este script debe vivir en bin/ del repo)." >&2
  exit 1
fi
need_compose_stop=false
test -e "$DT/.compose_data" && need_compose_stop=true
test -e "$DT/media" && need_compose_stop=true
if test "$need_compose_stop" = true && test -f "$ROOT/docker-compose.yml" && command -v docker >/dev/null 2>&1; then
  echo 'Deteniendo contenedores de Compose (por locks en app/media o .compose_data)...'
  (cd "$ROOT" && docker compose stop -t 5) >/dev/null 2>&1 || true
  (cd "$ROOT" && docker compose rm -f) >/dev/null 2>&1 || true
  sleep 6
fi
if test -e "$DT/.compose_data" || test -e "$DT/media"; then
  sleep 2
fi
for d in .compose_data media sent_emails staticfiles .run; do
  if test -e "$DT/$d"; then
    chmod -R u+w "$DT/$d" 2>/dev/null || true
    rm -rf "$DT/$d"
    echo "Eliminado: $DT/$d"
  fi
done
if test -f "$DT/db.sqlite3"; then
  rm -f "$DT/db.sqlite3"
  echo "Eliminado: $DT/db.sqlite3"
fi
echo "Listo (artefactos locales). Volúmenes: docker compose down -v o sh bin/dc.sh down -v"
