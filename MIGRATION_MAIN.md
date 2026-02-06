# Main bot migration checklist

This guide migrates SQLite data to Postgres for the main bot.

## Pre-checks
- `.env` has `DB_ENGINE=postgres` and valid `POSTGRES_*` values.
- `bot.py` and `migrate_sqlite_to_postgres.py` are updated.
- SQLite files exist in `data/` (`db.db`, `messages.db`).

## Quick run (recommended)
```
./migrate_main.sh
```

## Fresh Postgres (dangerous, deletes Postgres volume)
```
./migrate_main.sh --fresh
```

## Re-run migration and overwrite data
```
./migrate_main.sh --truncate
```

## Manual steps (if you prefer no script)
```
docker compose stop bot
docker compose down -v            # only if you want a fresh Postgres
docker compose up -d postgres
docker compose build bot
docker compose run --rm bot python /app/migrate_sqlite_to_postgres.py
docker compose up -d --build bot
docker compose logs -f bot
```

## Notes
- `migrate_main.sh` creates a local backup in `backups/` by default.
- Use `--skip-backup` to skip backup.
- Use `--skip-build` if you already built the image.
