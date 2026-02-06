import argparse
import asyncio
import os
import sqlite3
import urllib.parse

import asyncpg


def load_env_file(path):
    if not path or not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value

def build_dsn(database_url):
    if database_url:
        return database_url
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB", "vpn_bot")
    user = os.getenv("POSTGRES_USER", "vpn_bot")
    password = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
    sslmode = os.getenv("POSTGRES_SSLMODE", "disable")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}"


def normalize_default(value):
    if value is None:
        return None
    text = str(value).strip()
    if text.startswith('"') and text.endswith('"'):
        inner = text[1:-1].replace("'", "''")
        return f"'{inner}'"
    return text

def normalize_default_for_type(value, pg_type):
    default = normalize_default(value)
    if default is None:
        return None
    if pg_type in ("INTEGER", "BIGINT", "DOUBLE PRECISION"):
        text = default.strip()
        if text in ("", "''", '""'):
            return None
        if text.startswith("'") and text.endswith("'"):
            inner = text[1:-1].strip()
            if inner == "":
                return None
            text = inner
        if text.lower() in ("true", "false"):
            return "1" if text.lower() == "true" else "0"
        try:
            float(text)
        except (TypeError, ValueError):
            return None
        return text
    return default


def map_sqlite_type(sqlite_type, is_pk=False):
    if not sqlite_type:
        return "TEXT"
    t = sqlite_type.strip().lower()
    if "bool" in t:
        return "INTEGER"
    if "int" in t or "bitint" in t:
        return "BIGINT" if is_pk or "big" in t else "INTEGER"
    if "real" in t or "floa" in t or "doub" in t:
        return "DOUBLE PRECISION"
    if "blob" in t:
        return "BYTEA"
    if "date" in t or "time" in t:
        return "TEXT"
    return "TEXT"


def _is_numeric_string(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    if text.lower() in ("true", "false"):
        return True
    if text.startswith("-"):
        text = text[1:]
    return text.isdigit()


def convert_row_value(value, pg_type):
    if value is None:
        return None
    if pg_type in ("INTEGER", "BIGINT"):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, str):
            text = value.strip().lower()
            if text == "":
                return None
            if text in ("true", "false"):
                return 1 if text == "true" else 0
            if _is_numeric_string(value):
                return int(value)
            return None
        return int(value)
    if pg_type == "DOUBLE PRECISION":
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    if pg_type == "BYTEA":
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value)
        return str(value).encode("utf-8")
    return str(value)


def should_force_text(value, pg_type):
    if value is None:
        return False
    if pg_type in ("INTEGER", "BIGINT"):
        if isinstance(value, bool):
            return False
        if isinstance(value, str):
            text = value.strip().lower()
            if text in ("true", "false"):
                return False
            return not _is_numeric_string(value)
        try:
            int(value)
            return False
        except (TypeError, ValueError):
            return True
    if pg_type == "DOUBLE PRECISION":
        try:
            float(value)
            return False
        except (TypeError, ValueError):
            return True
    return False


async def ensure_table(conn, table, columns, type_overrides=None):
    type_overrides = type_overrides or {}
    column_defs = []
    pk_columns = [col for col in columns if col["pk"] > 0]
    single_pk = len(pk_columns) == 1
    identity_cols = []

    for col in columns:
        name = col["name"].lower()
        pg_type = type_overrides.get(name, map_sqlite_type(col["type"], is_pk=col["pk"] > 0))
        notnull = " NOT NULL" if col["notnull"] else ""
        default = normalize_default_for_type(col["dflt_value"], pg_type)

        if single_pk and col["pk"] > 0 and pg_type in ("INTEGER", "BIGINT"):
            identity_cols.append(name)
            column_defs.append(
                f'"{name}" {pg_type} GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY{notnull}'
            )
            continue
        col_def = f'"{name}" {pg_type}{notnull}'
        if single_pk and col["pk"] > 0:
            col_def += " PRIMARY KEY"
        if default is not None:
            col_def += f" DEFAULT {default}"
        column_defs.append(col_def)

    if len(pk_columns) > 1:
        pk_list = ", ".join(f'"{col["name"].lower()}"' for col in pk_columns)
        column_defs.append(f"PRIMARY KEY ({pk_list})")

    create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(column_defs)});'
    await conn.execute(create_sql)
    return identity_cols


async def ensure_columns(conn, table, columns, type_overrides=None):
    type_overrides = type_overrides or {}
    rows = await conn.fetch(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = $1",
        table,
    )
    existing = {row[0] for row in rows}
    for col in columns:
        name = col["name"].lower()
        if name in existing:
            continue
        pg_type = type_overrides.get(name, map_sqlite_type(col["type"], is_pk=col["pk"] > 0))
        default = normalize_default_for_type(col["dflt_value"], pg_type)
        notnull = " NOT NULL" if col["notnull"] and default is not None else ""
        sql = f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "{name}" {pg_type}'
        if default is not None:
            sql += f" DEFAULT {default}"
        sql += notnull
        await conn.execute(sql)

async def ensure_bigint_columns(conn, table, force_cols):
    rows = await conn.fetch(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = $1",
        table,
    )
    for row in rows:
        name = row[0]
        data_type = row[1]
        if name in force_cols or name.endswith("_id"):
            if data_type in ("integer", "smallint"):
                await conn.execute(
                    f'ALTER TABLE "{table}" ALTER COLUMN "{name}" TYPE BIGINT'
                )


async def insert_rows(conn, table, columns, rows, truncate=False, type_overrides=None):
    type_overrides = type_overrides or {}
    if not rows:
        return
    cols = [col["name"].lower() for col in columns]
    pg_types = [
        type_overrides.get(col["name"].lower(), map_sqlite_type(col["type"], is_pk=col["pk"] > 0))
        for col in columns
    ]
    cols_sql = ", ".join(f'"{col}"' for col in cols)
    placeholders = ", ".join(f"${idx}" for idx in range(1, len(cols) + 1))
    insert_sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'

    if truncate:
        await conn.execute(f'TRUNCATE TABLE "{table}" CASCADE')

    payload = []
    for row in rows:
        converted = []
        for value, pg_type in zip(row, pg_types):
            converted.append(convert_row_value(value, pg_type))
        payload.append(tuple(converted))

    await conn.executemany(insert_sql, payload)
    print(f"  {table}: {len(payload)} rows processed")


async def migrate_sqlite_db(conn, sqlite_path, truncate=False):
    if not os.path.exists(sqlite_path):
        print(f"SQLite file not found: {sqlite_path}")
        return
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    tables = [
        row[0]
        for row in sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    ]

    for table in tables:
        pg_table = table.lower()
        columns = sqlite_conn.execute(f'PRAGMA table_info("{table}")').fetchall()
        columns = [dict(col) for col in columns]
        rename_map = {
            "promocodes": {
                "user": "user_name",
            }
        }
        if pg_table in rename_map:
            mapped = rename_map[pg_table]
            for col in columns:
                name_lower = col["name"].lower()
                if name_lower in mapped:
                    col["name"] = mapped[name_lower]
        rows = sqlite_conn.execute(f'SELECT * FROM "{table}"').fetchall()

        force_bigint_cols = {
            "user_id",
            "id_refer",
            "id_client",
            "id_partner",
            "id_ref",
            "chat_id",
            "my_id",
        }
        type_overrides = {}
        for col in columns:
            name = col["name"].lower()
            if name in force_bigint_cols or name.endswith("_id"):
                type_overrides[name] = "BIGINT"
        if rows:
            for index, col in enumerate(columns):
                name = col["name"].lower()
                pg_type = map_sqlite_type(col["type"], is_pk=col["pk"] > 0)
                if pg_type in ("INTEGER", "BIGINT", "DOUBLE PRECISION"):
                    for row in rows:
                        value = row[index]
                        if should_force_text(value, pg_type):
                            type_overrides[name] = "TEXT"
                            break
                        if pg_type in ("INTEGER", "BIGINT"):
                            if value is None or isinstance(value, bool):
                                continue
                            try:
                                if isinstance(value, str) and value.strip().lower() in ("true", "false"):
                                    continue
                                numeric_value = int(value)
                            except (TypeError, ValueError):
                                continue
                            if numeric_value > 2147483647 or numeric_value < -2147483648:
                                type_overrides[name] = "BIGINT"

        identity_cols = await ensure_table(conn, pg_table, columns, type_overrides=type_overrides)
        await ensure_columns(conn, pg_table, columns, type_overrides=type_overrides)
        await ensure_bigint_columns(conn, pg_table, force_bigint_cols)
        await insert_rows(conn, pg_table, columns, rows, truncate=truncate, type_overrides=type_overrides)

        for identity_col in identity_cols:
            max_val = await conn.fetchval(
                f'SELECT MAX("{identity_col}") FROM "{pg_table}"'
            )
            if max_val is None or int(max_val) < 1:
                await conn.execute(
                    "SELECT setval(pg_get_serial_sequence($1, $2), 1, false)",
                    pg_table,
                    identity_col,
                )
            else:
                await conn.execute(
                    "SELECT setval(pg_get_serial_sequence($1, $2), $3, true)",
                    pg_table,
                    identity_col,
                    int(max_val),
                )

    sqlite_conn.close()


async def cleanup_spurious_columns(conn):
    """Drop spurious 'text' columns of type 'date' created by a bot.py regex bug."""
    rows = await conn.fetch(
        "SELECT table_name, column_name, data_type "
        "FROM information_schema.columns "
        "WHERE table_schema = 'public' AND column_name = 'text' AND data_type = 'date'"
    )
    for row in rows:
        table = row[0]
        print(f"  Dropping spurious column '{table}.text' (type date)")
        await conn.execute(f'ALTER TABLE "{table}" DROP COLUMN IF EXISTS "text"')


async def main():
    load_env_file(os.getenv("ENV_FILE", ".env"))
    parser = argparse.ArgumentParser(description="Migrate SQLite data to Postgres.")
    parser.add_argument(
        "--sqlite-main",
        default=os.getenv("SQLITE_MAIN_PATH", os.path.join("data", "db.db")),
        help="Path to основной SQLite DB (default: data/db.db)",
    )
    parser.add_argument(
        "--sqlite-messages",
        default=os.getenv("SQLITE_MESSAGES_PATH", os.path.join("data", "messages.db")),
        help="Path to messages SQLite DB (default: data/messages.db)",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", ""),
        help="Postgres DSN (optional, overrides POSTGRES_*)",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="TRUNCATE tables before insert (use with caution)",
    )
    args = parser.parse_args()

    dsn = build_dsn(args.database_url)
    conn = await asyncpg.connect(dsn)
    try:
        await migrate_sqlite_db(conn, args.sqlite_main, truncate=args.truncate)
        await migrate_sqlite_db(conn, args.sqlite_messages, truncate=args.truncate)
        print("Cleaning up spurious columns...")
        await cleanup_spurious_columns(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())