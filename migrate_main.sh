#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
  echo "Usage: ./migrate_main.sh [OPTIONS]"
  echo ""
  echo "  --sqlite-main PATH  Path to main SQLite DB (default: data/db.db)"
  echo "  --fresh              Remove Postgres volume (DANGEROUS)."
  echo "  --truncate           Truncate tables before insert."
  echo "  --skip-backup        Skip SQLite file backup."
  echo "  --skip-build         Skip docker image build."
}

FRESH=0
TRUNCATE=0
SKIP_BACKUP=0
SKIP_BUILD=0
SQLITE_MAIN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fresh) FRESH=1; shift ;;
    --truncate) TRUNCATE=1; shift ;;
    --skip-backup) SKIP_BACKUP=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --sqlite-main) SQLITE_MAIN="$2"; shift 2 ;;
    --help|-h) show_help; exit 0 ;;
    *) echo "Unknown argument: $1"; show_help; exit 1 ;;
  esac
done

if [ "$FRESH" -eq 1 ] && [ "$TRUNCATE" -eq 1 ]; then
  echo "Do not use --fresh and --truncate together."
  exit 1
fi

echo "Stopping bot..."
docker compose stop bot || true

if [ "$SKIP_BACKUP" -eq 0 ]; then
  TS="$(date +%Y%m%d_%H%M%S)"
  BACKUP_DIR="${ROOT_DIR}/backups/${TS}"
  mkdir -p "$BACKUP_DIR"

  for ext in "" "-wal" "-shm"; do
    src="${ROOT_DIR}/data/db.db${ext}"
    if [ -f "$src" ]; then
      cp "$src" "${BACKUP_DIR}/db.db${ext}"
    fi
  done

  for ext in "" "-wal" "-shm"; do
    src="${ROOT_DIR}/data/messages.db${ext}"
    if [ -f "$src" ]; then
      cp "$src" "${BACKUP_DIR}/messages.db${ext}"
    fi
  done

  echo "Backup stored in: ${BACKUP_DIR}"
fi

if [ "$FRESH" -eq 1 ]; then
  echo "Removing Postgres volume..."
  docker compose down -v
fi

echo "Starting Postgres..."
docker compose up -d postgres

if [ "$SKIP_BUILD" -eq 0 ]; then
  echo "Building bot image..."
  docker compose build bot
fi

MIGRATE_ARGS=()
if [ "$TRUNCATE" -eq 1 ]; then
  MIGRATE_ARGS+=(--truncate)
fi

# If custom SQLite path provided, copy it into data/ so the container can see it
if [ -n "$SQLITE_MAIN" ]; then
  if [ ! -f "$SQLITE_MAIN" ]; then
    echo "Error: SQLite file not found: $SQLITE_MAIN"
    exit 1
  fi
  cp "$SQLITE_MAIN" "${ROOT_DIR}/data/db.db"
  echo "Copied $SQLITE_MAIN -> data/db.db"
fi

echo "Running migration..."
docker compose run --rm bot python /app/migrate_sqlite_to_postgres.py "${MIGRATE_ARGS[@]}"

echo "Starting bot..."
docker compose up -d --build bot

echo "Done. Check logs:"
echo "  docker compose logs -f bot"
