#!/usr/bin/env bash
# migrate_sqlite_to_postgres.sh
#
# Usage:
#   ./migrate_sqlite_to_postgres.sh mydb.sqlite postgres_user postgres_password postgres_db target_schema
#
# Example:
#   ./migrate_sqlite_to_postgres.sh ./mydb.sqlite postgres mypassword mydb myschema

set -euo pipefail

# --- Args ---
PG_USER="$1"             # e.g. postgres
PG_PASS="$2"             # e.g. mypassword
PG_DB="$3"               # e.g. targetdb
PG_SCHEMA="$4"           # e.g. myschema
PG_HOST="${5:-localhost}"   # optional, defaults to localhost
PG_PORT="${6:-5432}"       # optional, defaults to 5432

# --- Checks ---
if ! command -v pgloader &> /dev/null; then
  echo "❌ pgloader is not installed. Install it first:"
  echo "   Debian/Ubuntu: sudo apt-get install pgloader"
  echo "   macOS (brew): brew install pgloader"
  exit 1
fi

# --- Ensure schema exists ---
echo "📦 Ensuring schema $PG_SCHEMA exists in PostgreSQL..."
PGPASSWORD="$PG_PASS" psql -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" -d "$PG_DB" \
  -c "CREATE SCHEMA IF NOT EXISTS \"$PG_SCHEMA\";"

# --- Run Migration ---
pgloader --verbose pgloader.load

echo "✅ Migration complete!"
