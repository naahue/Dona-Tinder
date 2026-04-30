#!/usr/bin/env bash
set -eu
BIN="$(CDPATH="" cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
ROOT="$(dirname "$BIN")"
cd "$ROOT"

up=false
down=false
vol=false
for a in "$@"; do
  case "$a" in
    up) up=true ;;
    down) down=true ;;
    -v|--volumes) vol=true ;;
  esac
done

if $up; then
  printf '%s\n' '[dc] Antes de compose up: stop + rm (evita bloqueos si quedaron app/media o restos bajo app/)...'
  docker compose stop -t 5 >/dev/null 2>&1 || true
  docker compose rm -f >/dev/null 2>&1 || true
  sleep 3
  purge=true
  if [ "${DOCKER_PRE_UP_CLEAN+x}" = x ]; then
    purge=false
    case "$DOCKER_PRE_UP_CLEAN" in 1|true|yes|TRUE|Yes) purge=true ;; esac
  else
    if [ -f "$ROOT/.env" ] && grep -qE '^[[:space:]]*DOCKER_PRE_UP_CLEAN[[:space:]]*=[[:space:]]*(0|false|no)\b' "$ROOT/.env"; then
      purge=false
    fi
  fi
  if $purge; then
    printf '%s\n' '[dc] Pre-up: limpieza local bajo app/ (media, .compose_data viejo...)...'
    sh "$BIN/clean_local_artifacts.sh"
  fi
fi

docker compose "$@"

if $down && $vol; then
  printf '%s\n' '[dc] down -v OK; pausa breve y limpieza de artefactos bajo app/...'
  sleep 3
  printf '%s\n' '[dc] limpiando artefactos locales...'
  sh "$BIN/clean_local_artifacts.sh"
fi
