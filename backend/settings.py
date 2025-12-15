import sqlite3


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )


def get_setting(conn: sqlite3.Connection | None, key: str, default=None):
    if conn is None:
        return default
    _ensure_table(conn)
    cur = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cur.fetchone()
    return row[0] if row else default


def set_setting(conn: sqlite3.Connection | None, key: str, value: str) -> None:
    if conn is None:
        return
    _ensure_table(conn)
    conn.execute(
        """
        INSERT INTO app_settings(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )
    conn.commit()
