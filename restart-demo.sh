#!/usr/bin/env sh
# Equivalente manual: docker compose down -v && docker compose up -d
ROOT="$(CDPATH="" cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
cd "$ROOT" || exit 1
docker compose down -v || exit $?
exec docker compose up -d "$@"
