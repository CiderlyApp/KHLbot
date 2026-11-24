#!/usr/bin/env sh
# Create a local SQLit3e backup. For hosted PostgreSQL, use pg_dump separately.
set -eu

DB_PATH="${DB_PATH:-data/khlbot.db}"
BACKUP_DIR="${BACKUP_DIR:-backups}"

if [ ! -f "$DB_PATH" ]; then
  echo "SQLite database not found: $DB_PATH" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$BACKUP_DIR/khlbot-$STAMP.db"

if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "$DB_PATH" ".backup '$DEST'"
else
  cp "$DB_PATH" "$DEST"
fi

echo "Backup created: $DEST"
